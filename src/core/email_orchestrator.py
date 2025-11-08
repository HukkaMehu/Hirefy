"""
EmailOrchestrator for coordinating email-based verification requests.

This module provides high-level coordination for sending HR verification
and reference check emails, integrating EmailClient, TemplateManager,
and EmailLogger components.
"""

import os
import logging
import smtplib
from datetime import datetime
from typing import Optional

from src.core.email_client import EmailClient
from src.core.models import EmailResult
from src.utils.template_manager import TemplateManager
from src.utils.email_logger import EmailLogger

# Configure logging
logger = logging.getLogger(__name__)


class EmailOrchestrator:
    """Orchestrates email-based verification requests.
    
    This class coordinates the sending of HR verification and reference check
    emails by integrating the EmailClient, TemplateManager, and EmailLogger
    components. It handles input validation, template rendering, email sending,
    and logging of results.
    """
    
    def __init__(
        self,
        email_client: Optional[EmailClient] = None,
        template_manager: Optional[TemplateManager] = None,
        email_logger: Optional[EmailLogger] = None
    ):
        """Initialize EmailOrchestrator with required components.
        
        Args:
            email_client: EmailClient instance (creates new if None)
            template_manager: TemplateManager instance (creates new if None)
            email_logger: EmailLogger instance (creates new if None)
        """
        self.email_client = email_client or EmailClient()
        self.template_manager = template_manager or TemplateManager()
        self.email_logger = email_logger or EmailLogger()
        
        # Get sender information from environment
        self.sender_name = os.getenv('SMTP_FROM_NAME', 'Employment Verification')
        self.sender_email = os.getenv('SMTP_FROM_EMAIL', '')
        
        logger.info("EmailOrchestrator initialized successfully")
    
    def send_hr_verification_email(
        self,
        candidate_name: str,
        job_title: str,
        start_date: str,
        end_date: str,
        hr_email: str
    ) -> EmailResult:
        """Send HR verification email requesting employment dates and job title.
        
        This method sends a professional email to an HR department requesting
        verification of a candidate's employment information including job title,
        start date, and end date.
        
        Args:
            candidate_name: Full name of candidate
            job_title: Job title to verify
            start_date: Employment start date (YYYY-MM-DD format)
            end_date: Employment end date (YYYY-MM-DD format)
            hr_email: HR contact email address
            
        Returns:
            EmailResult with success status and details
            
        Raises:
            ValueError: If any parameter is invalid or email address is malformed
        """
        logger.info(f"Initiating HR verification email for {candidate_name}")
        
        # Validate inputs
        self._validate_required_string(candidate_name, "candidate_name")
        self._validate_required_string(job_title, "job_title")
        self._validate_required_string(start_date, "start_date")
        self._validate_required_string(end_date, "end_date")
        self._validate_required_string(hr_email, "hr_email")
        
        # Validate email address format
        if not self.email_client.validate_email_address(hr_email):
            error_msg = f"Invalid email address format: {hr_email}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate date formats (basic check for YYYY-MM-DD)
        self._validate_date_format(start_date, "start_date")
        self._validate_date_format(end_date, "end_date")
        
        # Generate unique email ID
        email_id = self._generate_email_id("hr_verification")
        
        try:
            # Load and render template
            logger.debug("Loading HR verification template")
            template_content = self.template_manager.load_template("hr_verification")
            
            template_vars = {
                "candidate_name": candidate_name,
                "job_title": job_title,
                "start_date": start_date,
                "end_date": end_date,
                "sender_name": self.sender_name,
                "sender_email": self.sender_email
            }
            
            logger.debug("Rendering template with candidate data")
            rendered_content = self.template_manager.render_template(
                template_content,
                template_vars
            )
            
            # Extract subject from rendered content (first line after "Subject:")
            subject = self._extract_subject(rendered_content)
            body = self._extract_body(rendered_content)
            
            # Send email
            logger.info(f"Sending HR verification email to {hr_email}")
            success = self.email_client.send_email(
                to_address=hr_email,
                subject=subject,
                body=body
            )
            
            # Log the email
            log_path = self.email_logger.log_sent_email(
                candidate_name=candidate_name,
                email_type="hr_verification",
                recipient=hr_email,
                subject=subject,
                success=success,
                error_message=None
            )
            
            logger.info(f"HR verification email sent successfully: {email_id}")
            
            return EmailResult(
                success=True,
                email_id=email_id,
                recipient=hr_email,
                log_path=log_path,
                error_message=None
            )
            
        except (FileNotFoundError, KeyError) as e:
            # Template errors
            error_msg = f"Template error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Log failed attempt
            log_path = self._log_failed_email(
                candidate_name=candidate_name,
                email_type="hr_verification",
                recipient=hr_email,
                subject=f"Employment Verification Request for {candidate_name}",
                error_message=error_msg
            )
            
            return EmailResult(
                success=False,
                email_id=email_id,
                recipient=hr_email,
                log_path=log_path,
                error_message=error_msg
            )
            
        except smtplib.SMTPException as e:
            # SMTP errors
            error_msg = f"Email sending failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Log failed attempt
            log_path = self._log_failed_email(
                candidate_name=candidate_name,
                email_type="hr_verification",
                recipient=hr_email,
                subject=f"Employment Verification Request for {candidate_name}",
                error_message=error_msg
            )
            
            return EmailResult(
                success=False,
                email_id=email_id,
                recipient=hr_email,
                log_path=log_path,
                error_message=error_msg
            )
            
        except Exception as e:
            # Unexpected errors
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Log failed attempt
            log_path = self._log_failed_email(
                candidate_name=candidate_name,
                email_type="hr_verification",
                recipient=hr_email,
                subject=f"Employment Verification Request for {candidate_name}",
                error_message=error_msg
            )
            
            return EmailResult(
                success=False,
                email_id=email_id,
                recipient=hr_email,
                log_path=log_path,
                error_message=error_msg
            )
    
    def send_reference_email(
        self,
        candidate_name: str,
        reference_name: str,
        reference_email: str,
        relationship: str
    ) -> EmailResult:
        """Send reference check email requesting qualitative feedback.
        
        This method sends a professional email to a reference contact requesting
        feedback about a candidate's work performance, skills, and professional
        conduct.
        
        Args:
            candidate_name: Full name of candidate
            reference_name: Name of reference contact
            reference_email: Reference email address
            relationship: Relationship to candidate (manager/coworker/supervisor)
            
        Returns:
            EmailResult with success status and details
            
        Raises:
            ValueError: If any parameter is invalid, email address is malformed,
                       or relationship is not valid
        """
        logger.info(f"Initiating reference check email for {candidate_name}")
        
        # Validate inputs
        self._validate_required_string(candidate_name, "candidate_name")
        self._validate_required_string(reference_name, "reference_name")
        self._validate_required_string(reference_email, "reference_email")
        self._validate_required_string(relationship, "relationship")
        
        # Validate email address format
        if not self.email_client.validate_email_address(reference_email):
            error_msg = f"Invalid email address format: {reference_email}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate relationship
        valid_relationships = ["manager", "coworker", "supervisor"]
        if relationship.lower() not in valid_relationships:
            error_msg = (
                f"Invalid relationship: {relationship}. "
                f"Must be one of: {', '.join(valid_relationships)}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Generate unique email ID
        email_id = self._generate_email_id("reference_check")
        
        try:
            # Load and render template
            logger.debug("Loading reference check template")
            template_content = self.template_manager.load_template("reference_check")
            
            template_vars = {
                "candidate_name": candidate_name,
                "reference_name": reference_name,
                "relationship": relationship,
                "sender_name": self.sender_name,
                "sender_email": self.sender_email
            }
            
            logger.debug("Rendering template with candidate data")
            rendered_content = self.template_manager.render_template(
                template_content,
                template_vars
            )
            
            # Extract subject and body
            subject = self._extract_subject(rendered_content)
            body = self._extract_body(rendered_content)
            
            # Send email
            logger.info(f"Sending reference check email to {reference_email}")
            success = self.email_client.send_email(
                to_address=reference_email,
                subject=subject,
                body=body
            )
            
            # Log the email
            log_path = self.email_logger.log_sent_email(
                candidate_name=candidate_name,
                email_type="reference_check",
                recipient=reference_email,
                subject=subject,
                success=success,
                error_message=None
            )
            
            logger.info(f"Reference check email sent successfully: {email_id}")
            
            return EmailResult(
                success=True,
                email_id=email_id,
                recipient=reference_email,
                log_path=log_path,
                error_message=None
            )
            
        except (FileNotFoundError, KeyError) as e:
            # Template errors
            error_msg = f"Template error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Log failed attempt
            log_path = self._log_failed_email(
                candidate_name=candidate_name,
                email_type="reference_check",
                recipient=reference_email,
                subject=f"Reference Request for {candidate_name}",
                error_message=error_msg
            )
            
            return EmailResult(
                success=False,
                email_id=email_id,
                recipient=reference_email,
                log_path=log_path,
                error_message=error_msg
            )
            
        except smtplib.SMTPException as e:
            # SMTP errors
            error_msg = f"Email sending failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Log failed attempt
            log_path = self._log_failed_email(
                candidate_name=candidate_name,
                email_type="reference_check",
                recipient=reference_email,
                subject=f"Reference Request for {candidate_name}",
                error_message=error_msg
            )
            
            return EmailResult(
                success=False,
                email_id=email_id,
                recipient=reference_email,
                log_path=log_path,
                error_message=error_msg
            )
            
        except Exception as e:
            # Unexpected errors
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Log failed attempt
            log_path = self._log_failed_email(
                candidate_name=candidate_name,
                email_type="reference_check",
                recipient=reference_email,
                subject=f"Reference Request for {candidate_name}",
                error_message=error_msg
            )
            
            return EmailResult(
                success=False,
                email_id=email_id,
                recipient=reference_email,
                log_path=log_path,
                error_message=error_msg
            )
    
    def _validate_required_string(self, value: str, param_name: str) -> None:
        """Validate that a parameter is a non-empty string.
        
        Args:
            value: Value to validate
            param_name: Name of parameter for error messages
            
        Raises:
            ValueError: If value is None, empty, or not a string
        """
        if value is None:
            raise ValueError(f"{param_name} cannot be None")
        
        if not isinstance(value, str):
            raise ValueError(f"{param_name} must be a string")
        
        if not value.strip():
            raise ValueError(f"{param_name} cannot be empty")
    
    def _validate_date_format(self, date_str: str, param_name: str) -> None:
        """Validate date string format (YYYY-MM-DD).
        
        Args:
            date_str: Date string to validate
            param_name: Name of parameter for error messages
            
        Raises:
            ValueError: If date format is invalid
        """
        try:
            # Try to parse the date
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"{param_name} must be in YYYY-MM-DD format, got: {date_str}"
            )
    
    def _generate_email_id(self, email_type: str) -> str:
        """Generate unique email ID based on timestamp and type.
        
        Args:
            email_type: Type of email (hr_verification or reference_check)
            
        Returns:
            Unique email ID string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{email_type}_{timestamp}"
    
    def _extract_subject(self, rendered_content: str) -> str:
        """Extract email subject from rendered template.
        
        Args:
            rendered_content: Rendered template content
            
        Returns:
            Email subject line
        """
        lines = rendered_content.split("\n")
        for line in lines:
            if line.startswith("Subject:"):
                return line.replace("Subject:", "").strip()
        
        # Default subject if not found
        return "Verification Request"
    
    def _extract_body(self, rendered_content: str) -> str:
        """Extract email body from rendered template.
        
        Args:
            rendered_content: Rendered template content
            
        Returns:
            Email body text
        """
        lines = rendered_content.split("\n")
        
        # Find the line after "Subject:" and use everything after that
        subject_found = False
        body_lines = []
        
        for line in lines:
            if subject_found:
                body_lines.append(line)
            elif line.startswith("Subject:"):
                subject_found = True
        
        # Join and strip extra whitespace
        body = "\n".join(body_lines).strip()
        
        return body
    
    def _log_failed_email(
        self,
        candidate_name: str,
        email_type: str,
        recipient: str,
        subject: str,
        error_message: str
    ) -> str:
        """Log a failed email attempt.
        
        Args:
            candidate_name: Candidate's full name
            email_type: Type of email
            recipient: Email recipient address
            subject: Email subject line
            error_message: Error message describing the failure
            
        Returns:
            Path to log file
        """
        try:
            return self.email_logger.log_sent_email(
                candidate_name=candidate_name,
                email_type=email_type,
                recipient=recipient,
                subject=subject,
                success=False,
                error_message=error_message
            )
        except Exception as e:
            logger.error(f"Failed to log failed email: {str(e)}", exc_info=True)
            return ""
