"""Employment verification service integrating call and email orchestrators."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from src.core.call_orchestrator import CallOrchestrator
from src.core.email_orchestrator import EmailOrchestrator
from src.core.models import CallResult, EmailResult
from src.database.models import (
    db, Employment, ContactRecord, EmploymentVerificationStatus
)

logger = logging.getLogger(__name__)


def safe_db_commit():
    """Safely commit database changes, catching app context errors"""
    try:
        safe_db_commit()
    except RuntimeError as e:
        if "application context" in str(e).lower():
            logger.warning("Skipping database commit due to app context issue (background thread)")
        else:
            raise


def safe_db_add(obj):
    """Safely add object to database, catching app context errors"""
    try:
        safe_db_add(obj)
    except RuntimeError as e:
        if "application context" in str(e).lower():
            logger.warning("Skipping database add due to app context issue (background thread)")
        else:
            raise


class EmploymentVerificationResult:
    """Result of employment verification attempt"""
    
    def __init__(
        self,
        success: bool,
        employment_id: str,
        verification_status: EmploymentVerificationStatus,
        contact_method: str,
        contact_record_id: Optional[str] = None,
        verified_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        self.success = success
        self.employment_id = employment_id
        self.verification_status = verification_status
        self.contact_method = contact_method
        self.contact_record_id = contact_record_id
        self.verified_data = verified_data or {}
        self.error_message = error_message


class EmploymentVerifier:
    """Verifies employment records using multi-channel contact strategy.
    
    This class extends the existing CallOrchestrator and EmailOrchestrator
    to provide employment verification with automatic fallback from phone to email.
    """
    
    def __init__(
        self,
        call_orchestrator: Optional[CallOrchestrator] = None,
        email_orchestrator: Optional[EmailOrchestrator] = None
    ):
        """Initialize EmploymentVerifier with orchestrators.
        
        Args:
            call_orchestrator: Optional CallOrchestrator instance
            email_orchestrator: Optional EmailOrchestrator instance
        """
        self.call_orchestrator = call_orchestrator or CallOrchestrator()
        self.email_orchestrator = email_orchestrator or EmailOrchestrator()
        
        logger.info("EmploymentVerifier initialized")
    
    def verify_employment(
        self,
        employment: Employment,
        hr_phone: Optional[str] = None,
        hr_email: Optional[str] = None
    ) -> EmploymentVerificationResult:
        """Verify employment using multi-channel contact strategy.
        
        Attempts phone verification first, then falls back to email if phone fails.
        Creates ContactRecord entries for all attempts and updates Employment status.
        
        Args:
            employment: Employment record to verify
            hr_phone: HR phone number (optional)
            hr_email: HR email address (optional)
        
        Returns:
            EmploymentVerificationResult with verification outcome
        """
        logger.info(
            f"Starting employment verification for {employment.company_name} "
            f"(Employment ID: {employment.id})"
        )
        
        # Extract contact info from employment record if not provided
        if employment.hr_contact_info:
            hr_phone = hr_phone or employment.hr_contact_info.get('phone')
            hr_email = hr_email or employment.hr_contact_info.get('email')
        
        # Send email notification first if email is available (always send as notification)
        email_sent = False
        if hr_email:
            logger.info(f"Sending email notification to HR at {hr_email}")
            email_result = self._verify_via_email(employment, hr_email)
            
            if email_result.success:
                email_sent = True
                logger.info("Email notification sent successfully")
            else:
                logger.warning(f"Failed to send email notification: {email_result.error_message}")
        
        # Try phone verification if available
        if hr_phone:
            logger.info(f"Attempting phone verification to {hr_phone}")
            result = self._verify_via_phone(employment, hr_phone)
            
            if result.success:
                logger.info("Phone verification successful")
                return result
            
            logger.warning(f"Phone verification failed: {result.error_message}")
        
        # If phone failed but email was sent, return email result
        if email_sent:
            logger.info("Phone verification failed but email was sent successfully")
            return email_result
        
        # Both methods failed or no contact info available
        logger.error(
            f"Employment verification failed for {employment.company_name}: "
            "No successful contact method"
        )
        
        # Update employment status to UNVERIFIED
        employment.verification_status = EmploymentVerificationStatus.UNVERIFIED
        employment.verification_notes = "Unable to contact HR via phone or email"
        safe_db_commit()
        
        return EmploymentVerificationResult(
            success=False,
            employment_id=employment.id,
            verification_status=EmploymentVerificationStatus.UNVERIFIED,
            contact_method="NONE",
            error_message="No successful contact method available"
        )
    
    def _verify_via_phone(
        self,
        employment: Employment,
        hr_phone: str
    ) -> EmploymentVerificationResult:
        """Verify employment via phone call.
        
        Args:
            employment: Employment record to verify
            hr_phone: HR phone number
        
        Returns:
            EmploymentVerificationResult
        """
        # Get candidate name from verification session
        candidate_name = employment.verification_session.candidate.full_name
        
        # Format dates for call
        start_date = employment.start_date.strftime("%B %Y")
        end_date = employment.end_date.strftime("%B %Y") if employment.end_date else "Present"
        
        # Create contact record for attempt
        contact_record = ContactRecord(
            verification_session_id=employment.verification_session_id,
            contact_type='HR',
            contact_method='PHONE',
            contact_info=hr_phone,
            attempt_timestamp=datetime.utcnow(),
            response_received=False
        )
        safe_db_add(contact_record)
        safe_db_commit()
        
        try:
            # Initiate HR verification call
            call_result: CallResult = self.call_orchestrator.initiate_hr_verification(
                candidate_name=candidate_name,
                job_title=employment.job_title,
                start_date=start_date,
                end_date=end_date,
                hr_phone=hr_phone
            )
            
            if call_result.success:
                # Update contact record with success
                contact_record.response_received = True
                contact_record.response_timestamp = datetime.utcnow()
                contact_record.transcript_url = call_result.transcript_path
                contact_record.response_data = {
                    'call_id': call_result.call_id,
                    'duration_seconds': call_result.duration_seconds
                }
                
                # Parse verification result from transcript
                # For MVP, we'll mark as VERIFIED if call completed successfully
                # In production, would parse transcript for actual verification
                employment.verification_status = EmploymentVerificationStatus.VERIFIED
                employment.verification_notes = f"Verified via phone call on {datetime.utcnow().strftime('%Y-%m-%d')}"
                
                safe_db_commit()
                
                return EmploymentVerificationResult(
                    success=True,
                    employment_id=employment.id,
                    verification_status=EmploymentVerificationStatus.VERIFIED,
                    contact_method='PHONE',
                    contact_record_id=contact_record.id,
                    verified_data={
                        'call_id': call_result.call_id,
                        'transcript_path': call_result.transcript_path,
                        'duration_seconds': call_result.duration_seconds
                    }
                )
            else:
                # Update contact record with failure
                contact_record.notes = call_result.error_message
                safe_db_commit()
                
                return EmploymentVerificationResult(
                    success=False,
                    employment_id=employment.id,
                    verification_status=employment.verification_status,
                    contact_method='PHONE',
                    contact_record_id=contact_record.id,
                    error_message=call_result.error_message
                )
        
        except Exception as e:
            error_msg = f"Phone verification exception: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            contact_record.notes = error_msg
            safe_db_commit()
            
            return EmploymentVerificationResult(
                success=False,
                employment_id=employment.id,
                verification_status=employment.verification_status,
                contact_method='PHONE',
                contact_record_id=contact_record.id,
                error_message=error_msg
            )
    
    def _verify_via_email(
        self,
        employment: Employment,
        hr_email: str
    ) -> EmploymentVerificationResult:
        """Verify employment via email.
        
        Args:
            employment: Employment record to verify
            hr_email: HR email address
        
        Returns:
            EmploymentVerificationResult
        """
        # Get candidate name from verification session
        candidate_name = employment.verification_session.candidate.full_name
        
        # Format dates for email
        start_date = employment.start_date.strftime("%Y-%m-%d")
        end_date = employment.end_date.strftime("%Y-%m-%d") if employment.end_date else "Present"
        
        # Create contact record for attempt
        contact_record = ContactRecord(
            verification_session_id=employment.verification_session_id,
            contact_type='HR',
            contact_method='EMAIL',
            contact_info=hr_email,
            attempt_timestamp=datetime.utcnow(),
            response_received=False
        )
        safe_db_add(contact_record)
        safe_db_commit()
        
        try:
            # Send HR verification email
            email_result: EmailResult = self.email_orchestrator.send_hr_verification_email(
                candidate_name=candidate_name,
                job_title=employment.job_title,
                start_date=start_date,
                end_date=end_date,
                hr_email=hr_email
            )
            
            if email_result.success:
                # Update contact record with success
                contact_record.response_data = {
                    'email_id': email_result.email_id,
                    'log_path': email_result.log_path
                }
                
                # Email sent successfully, but response pending
                # Mark as PENDING until we receive a response
                employment.verification_notes = f"Verification email sent on {datetime.utcnow().strftime('%Y-%m-%d')}, awaiting response"
                
                safe_db_commit()
                
                return EmploymentVerificationResult(
                    success=True,
                    employment_id=employment.id,
                    verification_status=EmploymentVerificationStatus.PENDING,
                    contact_method='EMAIL',
                    contact_record_id=contact_record.id,
                    verified_data={
                        'email_id': email_result.email_id,
                        'log_path': email_result.log_path
                    }
                )
            else:
                # Update contact record with failure
                contact_record.notes = email_result.error_message
                safe_db_commit()
                
                return EmploymentVerificationResult(
                    success=False,
                    employment_id=employment.id,
                    verification_status=employment.verification_status,
                    contact_method='EMAIL',
                    contact_record_id=contact_record.id,
                    error_message=email_result.error_message
                )
        
        except Exception as e:
            error_msg = f"Email verification exception: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            contact_record.notes = error_msg
            safe_db_commit()
            
            return EmploymentVerificationResult(
                success=False,
                employment_id=employment.id,
                verification_status=employment.verification_status,
                contact_method='EMAIL',
                contact_record_id=contact_record.id,
                error_message=error_msg
            )
