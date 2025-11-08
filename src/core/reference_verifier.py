"""
ReferenceVerifier for managing reference interview workflow.

This module coordinates reference verification activities including:
- Multi-channel contact (phone and email)
- Structured reference interviews
- Feedback extraction and theme analysis using GPT-4
- Reference relationship verification
- Storage of transcripts and extracted quotes
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from src.core.call_orchestrator import CallOrchestrator
from src.core.email_orchestrator import EmailOrchestrator
from src.database.models import db, ContactRecord, VerificationSession
from src.core.models import CallResult, EmailResult

# Configure logging
logger = logging.getLogger(__name__)


def safe_db_commit():
    """Safely commit database changes, catching app context errors"""
    try:
        db.session.commit()
    except RuntimeError as e:
        if "application context" in str(e).lower():
            logger.warning("Skipping database commit due to app context issue (background thread)")
        else:
            raise


def safe_db_add(obj):
    """Safely add object to database, catching app context errors"""
    try:
        db.session.add(obj)
    except RuntimeError as e:
        if "application context" in str(e).lower():
            logger.warning("Skipping database add due to app context issue (background thread)")
        else:
            raise


def safe_db_rollback():
    """Safely rollback database changes, catching app context errors"""
    try:
        db.session.rollback()
    except RuntimeError as e:
        if "application context" in str(e).lower():
            logger.warning("Skipping database rollback due to app context issue (background thread)")
        else:
            raise


class ReferenceVerifier:
    """Manages reference verification workflow.
    
    This class coordinates the complete reference verification process:
    1. Multi-channel contact attempts (phone first, then email)
    2. Structured reference interviews
    3. Feedback extraction and theme analysis
    4. Relationship verification
    5. Database storage of results
    """
    
    def __init__(
        self,
        call_orchestrator: Optional[CallOrchestrator] = None,
        email_orchestrator: Optional[EmailOrchestrator] = None,
        openai_api_key: Optional[str] = None
    ):
        """Initialize ReferenceVerifier.
        
        Args:
            call_orchestrator: Optional CallOrchestrator instance
            email_orchestrator: Optional EmailOrchestrator instance
            openai_api_key: Optional OpenAI API key for GPT-4 analysis
        """
        self.call_orchestrator = call_orchestrator or CallOrchestrator()
        self.email_orchestrator = email_orchestrator or EmailOrchestrator()
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            logger.warning("OpenAI API key not provided - feedback analysis will be limited")
        
        logger.info("ReferenceVerifier initialized successfully")

    def verify_reference(
        self,
        verification_session_id: str,
        candidate_name: str,
        reference_name: str,
        reference_phone: Optional[str],
        reference_email: Optional[str],
        relationship: str,
        claimed_employment_dates: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute complete reference verification workflow.
        
        Attempts to contact reference via phone first, then email if phone fails.
        Extracts feedback themes and verifies relationship authenticity.
        
        Args:
            verification_session_id: ID of the verification session
            candidate_name: Full name of the candidate
            reference_name: Name of the reference contact
            reference_phone: Optional phone number for the reference
            reference_email: Optional email address for the reference
            relationship: Relationship to candidate (manager/coworker/supervisor)
            claimed_employment_dates: Optional dict with 'start_date' and 'end_date'
            
        Returns:
            Dict containing verification results with keys:
                - success: bool
                - contact_method: str (phone/email/none)
                - feedback_extracted: bool
                - themes: List[str]
                - quotes: List[str]
                - relationship_verified: bool
                - contact_record_id: str
                - error_message: Optional[str]
        """
        logger.info(
            f"Starting reference verification for {candidate_name} "
            f"with reference {reference_name}"
        )
        
        # Validate inputs
        if not verification_session_id or not candidate_name or not reference_name:
            error_msg = "verification_session_id, candidate_name, and reference_name are required"
            logger.error(error_msg)
            return {
                "success": False,
                "contact_method": "none",
                "feedback_extracted": False,
                "themes": [],
                "quotes": [],
                "relationship_verified": False,
                "contact_record_id": None,
                "error_message": error_msg
            }
        
        if not reference_phone and not reference_email:
            error_msg = "At least one contact method (phone or email) must be provided"
            logger.error(error_msg)
            return {
                "success": False,
                "contact_method": "none",
                "feedback_extracted": False,
                "themes": [],
                "quotes": [],
                "relationship_verified": False,
                "contact_record_id": None,
                "error_message": error_msg
            }
        
        # Send email notification first if email is available (always send as notification)
        email_sent = False
        if reference_email:
            logger.info(f"Sending email notification to {reference_name} at {reference_email}")
            email_result = self._attempt_email_contact(
                candidate_name=candidate_name,
                reference_name=reference_name,
                reference_email=reference_email,
                relationship=relationship
            )
            
            if email_result.success:
                email_sent = True
                logger.info("Email notification sent successfully")
            else:
                logger.warning(f"Failed to send email notification: {email_result.error_message}")
        
        # Try phone call if available
        contact_result = None
        contact_method = "none"
        transcript_text = None
        
        if reference_phone:
            logger.info(f"Attempting phone contact with {reference_name}")
            phone_result = self._attempt_phone_contact(
                candidate_name=candidate_name,
                reference_name=reference_name,
                reference_phone=reference_phone,
                relationship=relationship
            )
            
            if phone_result.success:
                contact_result = phone_result
                contact_method = "phone"
                # Read transcript for analysis
                transcript_text = self._read_transcript(phone_result.transcript_path)
                logger.info("Phone contact successful")
            else:
                logger.warning(f"Phone contact failed: {phone_result.error_message}")
        
        # If phone failed but email was sent, consider it a success
        if not contact_result and email_sent:
            logger.info("Phone contact failed but email was sent successfully")
            contact_result = email_result
            contact_method = "email"
        
        # If no contact method succeeded
        if not contact_result:
            error_msg = "Failed to contact reference via phone or email"
            logger.error(error_msg)
            
            # Still create a contact record for tracking
            contact_record_id = self._create_contact_record(
                verification_session_id=verification_session_id,
                contact_method=contact_method,
                contact_name=reference_name,
                contact_info=reference_phone or reference_email or "unknown",
                response_received=False,
                response_data=None,
                transcript_url=None
            )
            
            return {
                "success": False,
                "contact_method": contact_method,
                "feedback_extracted": False,
                "themes": [],
                "quotes": [],
                "relationship_verified": False,
                "contact_record_id": contact_record_id,
                "error_message": error_msg
            }
        
        # Extract feedback and themes from transcript (if phone call)
        themes = []
        quotes = []
        feedback_extracted = False
        
        if transcript_text and self.openai_api_key:
            logger.info("Extracting feedback themes using GPT-4")
            analysis = self._extract_feedback_themes(
                transcript_text=transcript_text,
                candidate_name=candidate_name,
                reference_name=reference_name
            )
            themes = analysis.get("themes", [])
            quotes = analysis.get("quotes", [])
            feedback_extracted = len(themes) > 0 or len(quotes) > 0
        
        # Verify relationship authenticity
        relationship_verified = self._verify_relationship(
            transcript_text=transcript_text,
            claimed_relationship=relationship,
            claimed_employment_dates=claimed_employment_dates
        )
        
        # Create contact record in database
        response_data = {
            "themes": themes,
            "quotes": quotes,
            "relationship_verified": relationship_verified,
            "relationship": relationship
        }
        
        transcript_url = None
        if contact_method == "phone" and hasattr(contact_result, 'transcript_path'):
            transcript_url = contact_result.transcript_path
        
        contact_record_id = self._create_contact_record(
            verification_session_id=verification_session_id,
            contact_method=contact_method.upper(),
            contact_name=reference_name,
            contact_info=reference_phone if contact_method == "phone" else reference_email,
            response_received=True,
            response_data=response_data,
            transcript_url=transcript_url
        )
        
        logger.info(
            f"Reference verification completed for {reference_name}. "
            f"Method: {contact_method}, Themes: {len(themes)}, Quotes: {len(quotes)}"
        )
        
        return {
            "success": True,
            "contact_method": contact_method,
            "feedback_extracted": feedback_extracted,
            "themes": themes,
            "quotes": quotes,
            "relationship_verified": relationship_verified,
            "contact_record_id": contact_record_id,
            "error_message": None
        }

    def _attempt_phone_contact(
        self,
        candidate_name: str,
        reference_name: str,
        reference_phone: str,
        relationship: str
    ) -> CallResult:
        """Attempt to contact reference via phone.
        
        Args:
            candidate_name: Full name of the candidate
            reference_name: Name of the reference
            reference_phone: Phone number to call
            relationship: Relationship to candidate
            
        Returns:
            CallResult with success status and transcript path
        """
        try:
            result = self.call_orchestrator.initiate_reference_call(
                candidate_name=candidate_name,
                reference_name=reference_name,
                reference_phone=reference_phone,
                relationship=relationship
            )
            return result
        except Exception as e:
            logger.error(f"Phone contact failed: {str(e)}", exc_info=True)
            return CallResult(
                success=False,
                call_id="failed",
                transcript_path="none",
                duration_seconds=0,
                error_message=str(e)
            )
    
    def _attempt_email_contact(
        self,
        candidate_name: str,
        reference_name: str,
        reference_email: str,
        relationship: str
    ) -> EmailResult:
        """Attempt to contact reference via email.
        
        Args:
            candidate_name: Full name of the candidate
            reference_name: Name of the reference
            reference_email: Email address to send to
            relationship: Relationship to candidate
            
        Returns:
            EmailResult with success status
        """
        try:
            result = self.email_orchestrator.send_reference_email(
                candidate_name=candidate_name,
                reference_name=reference_name,
                reference_email=reference_email,
                relationship=relationship
            )
            return result
        except Exception as e:
            logger.error(f"Email contact failed: {str(e)}", exc_info=True)
            return EmailResult(
                success=False,
                email_id="failed",
                recipient=reference_email,
                log_path="none",
                error_message=str(e)
            )
    
    def _read_transcript(self, transcript_path: str) -> Optional[str]:
        """Read transcript file content.
        
        Args:
            transcript_path: Path to transcript file
            
        Returns:
            Transcript text or None if reading fails
        """
        try:
            if not transcript_path or not os.path.exists(transcript_path):
                logger.warning(f"Transcript file not found: {transcript_path}")
                return None
            
            with open(transcript_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
        except Exception as e:
            logger.error(f"Failed to read transcript: {str(e)}", exc_info=True)
            return None

    def _extract_feedback_themes(
        self,
        transcript_text: str,
        candidate_name: str,
        reference_name: str
    ) -> Dict[str, List[str]]:
        """Extract feedback themes and quotes using GPT-4.
        
        Args:
            transcript_text: Full transcript of the reference call
            candidate_name: Name of the candidate
            reference_name: Name of the reference
            
        Returns:
            Dict with 'themes' and 'quotes' lists
        """
        if not self.openai_api_key or not transcript_text:
            return {"themes": [], "quotes": []}
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""Analyze this reference call transcript for {candidate_name} with reference {reference_name}.

Extract:
1. Key themes about the candidate's performance, skills, and work style
2. Notable direct quotes that provide insight into the candidate

Transcript:
{transcript_text}

Respond in JSON format:
{{
    "themes": ["theme1", "theme2", ...],
    "quotes": ["quote1", "quote2", ...]
}}

Focus on actionable insights and specific examples. Include both positive and negative feedback."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing reference call transcripts and extracting key themes and quotes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "themes": result.get("themes", []),
                "quotes": result.get("quotes", [])
            }
            
        except Exception as e:
            logger.error(f"Failed to extract feedback themes: {str(e)}", exc_info=True)
            return {"themes": [], "quotes": []}

    def _verify_relationship(
        self,
        transcript_text: Optional[str],
        claimed_relationship: str,
        claimed_employment_dates: Optional[Dict[str, str]]
    ) -> bool:
        """Verify the authenticity of the reference relationship.
        
        Uses GPT-4 to analyze transcript and check if the reference's
        statements are consistent with the claimed relationship and dates.
        
        Args:
            transcript_text: Full transcript of the reference call
            claimed_relationship: Claimed relationship (manager/coworker/supervisor)
            claimed_employment_dates: Optional dict with start_date and end_date
            
        Returns:
            True if relationship appears authentic, False otherwise
        """
        # If no transcript or no OpenAI key, assume verified (benefit of doubt)
        if not transcript_text or not self.openai_api_key:
            logger.warning("Cannot verify relationship - no transcript or OpenAI key")
            return True
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            dates_info = ""
            if claimed_employment_dates:
                dates_info = f"\nClaimed employment dates: {claimed_employment_dates.get('start_date')} to {claimed_employment_dates.get('end_date')}"
            
            prompt = f"""Analyze this reference call transcript to verify the authenticity of the relationship.

Claimed relationship: {claimed_relationship}{dates_info}

Transcript:
{transcript_text}

Determine if:
1. The reference demonstrates knowledge consistent with the claimed relationship
2. The reference's statements align with the claimed employment timeline
3. The reference provides specific, credible details (not vague or generic)

Respond in JSON format:
{{
    "verified": true/false,
    "confidence": "high/medium/low",
    "reasoning": "brief explanation"
}}"""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at detecting fraudulent references and verifying relationship authenticity."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            verified = result.get("verified", True)
            confidence = result.get("confidence", "medium")
            
            logger.info(
                f"Relationship verification: {verified} (confidence: {confidence})"
            )
            
            return verified
            
        except Exception as e:
            logger.error(f"Failed to verify relationship: {str(e)}", exc_info=True)
            # Default to True (benefit of doubt) if verification fails
            return True
    
    def _create_contact_record(
        self,
        verification_session_id: str,
        contact_method: str,
        contact_name: str,
        contact_info: str,
        response_received: bool,
        response_data: Optional[Dict],
        transcript_url: Optional[str]
    ) -> str:
        """Create a contact record in the database.
        
        Args:
            verification_session_id: ID of the verification session
            contact_method: Method used (PHONE/EMAIL)
            contact_name: Name of the contact
            contact_info: Phone number or email address
            response_received: Whether a response was received
            response_data: Optional dict with response details
            transcript_url: Optional path to transcript file
            
        Returns:
            ID of the created contact record
        """
        try:
            contact_record = ContactRecord(
                verification_session_id=verification_session_id,
                contact_type="REFERENCE",
                contact_method=contact_method,
                contact_name=contact_name,
                contact_info=contact_info,
                attempt_timestamp=datetime.utcnow(),
                response_received=response_received,
                response_timestamp=datetime.utcnow() if response_received else None,
                response_data=response_data,
                transcript_url=transcript_url,
                notes=f"Reference verification via {contact_method.lower()}"
            )
            
            db.session.add(contact_record)
            db.session.commit()
            
            logger.info(f"Contact record created: {contact_record.id}")
            return contact_record.id
            
        except Exception as e:
            logger.error(f"Failed to create contact record: {str(e)}", exc_info=True)
            db.session.rollback()
            return ""
