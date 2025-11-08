"""
EmailClient for SMTP operations.

This module provides email sending capabilities using SMTP with proper
authentication and error handling.
"""

import os
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


class EmailClient:
    """Client for sending emails via SMTP."""
    
    def __init__(self):
        """Initialize EmailClient with SMTP configuration from environment variables.
        
        Raises:
            ValueError: If required SMTP configuration is missing.
        """
        self.smtp_host = os.getenv('SMTP_HOST')
        self.smtp_port = os.getenv('SMTP_PORT')
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_from_email = os.getenv('SMTP_FROM_EMAIL')
        self.smtp_from_name = os.getenv('SMTP_FROM_NAME', 'Employment Verification')
        
        # Validate required configuration
        missing_vars = []
        if not self.smtp_host:
            missing_vars.append('SMTP_HOST')
        if not self.smtp_port:
            missing_vars.append('SMTP_PORT')
        if not self.smtp_username:
            missing_vars.append('SMTP_USERNAME')
        if not self.smtp_password:
            missing_vars.append('SMTP_PASSWORD')
        if not self.smtp_from_email:
            missing_vars.append('SMTP_FROM_EMAIL')
        
        if missing_vars:
            raise ValueError(
                f"Missing required SMTP configuration: {', '.join(missing_vars)}. "
                "Please configure these variables in your .env file."
            )
        
        # Convert port to integer
        try:
            self.smtp_port = int(self.smtp_port)
        except ValueError:
            raise ValueError(f"SMTP_PORT must be a valid integer, got: {self.smtp_port}")
    
    def validate_email_address(self, email: str) -> bool:
        """Validate email address format using regex.
        
        Uses RFC 5322 compliant regex pattern for email validation.
        
        Args:
            email: Email address to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        if not email or not isinstance(email, str):
            return False
        
        # RFC 5322 compliant email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None
    
    def send_email(
        self,
        to_address: str,
        subject: str,
        body: str,
        from_address: Optional[str] = None
    ) -> bool:
        """Send an email via SMTP.
        
        Args:
            to_address: Recipient email address.
            subject: Email subject line.
            body: Email body content (plain text).
            from_address: Sender email (defaults to configured sender).
            
        Returns:
            True if email sent successfully, False otherwise.
            
        Raises:
            ValueError: If email address format is invalid.
            smtplib.SMTPException: If SMTP connection or authentication fails.
        """
        # Validate recipient email address
        if not self.validate_email_address(to_address):
            raise ValueError(f"Invalid email address format: {to_address}")
        
        # Use configured from_address if not provided
        if from_address is None:
            from_address = self.smtp_from_email
        
        # Validate from_address
        if not self.validate_email_address(from_address):
            raise ValueError(f"Invalid sender email address format: {from_address}")
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.smtp_from_name} <{from_address}>"
            msg['To'] = to_address
            msg['Subject'] = subject
            msg['Reply-To'] = from_address
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                # Start TLS encryption
                server.starttls()
                
                # Authenticate
                server.login(self.smtp_username, self.smtp_password)
                
                # Send email
                server.send_message(msg)
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            raise smtplib.SMTPException(
                "SMTP authentication failed. Please verify your SMTP credentials."
            ) from e
        
        except smtplib.SMTPConnectError as e:
            raise smtplib.SMTPException(
                f"Failed to connect to SMTP server {self.smtp_host}:{self.smtp_port}. "
                "Please verify your SMTP host and port configuration."
            ) from e
        
        except smtplib.SMTPException as e:
            # Re-raise SMTP exceptions with context
            raise smtplib.SMTPException(f"Failed to send email: {str(e)}") from e
        
        except Exception as e:
            # Catch any other unexpected errors
            raise smtplib.SMTPException(f"Unexpected error sending email: {str(e)}") from e
