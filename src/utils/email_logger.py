"""Email logging for verification email audit trail."""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)


class EmailLogger:
    """Manages logging of sent verification emails for audit trail.
    
    This class handles the creation and management of email log files,
    organized by candidate name in the transcript directory structure.
    Logs include email metadata, delivery status, and timestamps.
    """
    
    def __init__(self, base_dir: str = "./transcripts"):
        """Initialize the EmailLogger.
        
        Args:
            base_dir: Base directory for storing email logs (default: ./transcripts)
        """
        self.base_dir = Path(base_dir)
        logger.debug(f"EmailLogger initialized with base_dir: {self.base_dir}")
    
    def log_sent_email(
        self,
        candidate_name: str,
        email_type: str,
        recipient: str,
        subject: str,
        success: bool,
        error_message: Optional[str] = None
    ) -> str:
        """Log a sent email to the candidate's log file.
        
        Creates or appends to an emails.log file in the candidate's directory.
        Each log entry includes timestamp, email type, recipient, subject,
        delivery status, and any error messages.
        
        Args:
            candidate_name: Candidate's full name
            email_type: Type of email (hr_verification or reference_check)
            recipient: Email recipient address
            subject: Email subject line
            success: Whether email was sent successfully
            error_message: Error message if send failed (optional)
        
        Returns:
            str: Path to the log file
        
        Raises:
            ValueError: If candidate_name, email_type, recipient, or subject is empty
            OSError: If directory creation or file writing fails
        """
        # Validate inputs
        if not candidate_name or not candidate_name.strip():
            error_msg = "candidate_name must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not email_type or not email_type.strip():
            error_msg = "email_type must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not recipient or not recipient.strip():
            error_msg = "recipient must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not subject or not subject.strip():
            error_msg = "subject must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Logging email for {candidate_name}, type: {email_type}, recipient: {recipient}")
        
        # Normalize candidate name for directory
        normalized_name = candidate_name.strip().lower().replace(" ", "_")
        
        try:
            # Create candidate-specific directory
            candidate_dir = self.base_dir / normalized_name
            candidate_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created/verified directory: {candidate_dir}")
            
            # Path to emails.log file
            log_file_path = candidate_dir / "emails.log"
            
            # Check if this is a new log file
            is_new_file = not log_file_path.exists()
            
            # Format the log entry
            log_entry = self._format_log_entry(
                email_type=email_type,
                recipient=recipient,
                subject=subject,
                success=success,
                error_message=error_message
            )
            
            # Write to log file (append mode)
            with open(log_file_path, 'a', encoding='utf-8') as f:
                # Add header if this is a new file
                if is_new_file:
                    f.write("=== EMAIL LOG ===\n")
                    f.write(f"Candidate: {candidate_name}\n\n")
                
                f.write(log_entry)
            
            logger.info(f"Email logged successfully: {log_file_path}")
            return str(log_file_path)
            
        except OSError as e:
            error_msg = f"Failed to log email for {candidate_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise OSError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error logging email for {candidate_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
    
    def _format_log_entry(
        self,
        email_type: str,
        recipient: str,
        subject: str,
        success: bool,
        error_message: Optional[str] = None
    ) -> str:
        """Format a single log entry with timestamp and email details.
        
        Args:
            email_type: Type of email
            recipient: Email recipient address
            subject: Email subject line
            success: Whether email was sent successfully
            error_message: Error message if send failed
        
        Returns:
            str: Formatted log entry
        """
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format email type for display
        email_type_display = email_type.replace("_", " ").title()
        
        # Determine status
        status = "SENT" if success else "FAILED"
        
        # Build log entry
        lines = []
        lines.append(f"[{timestamp}]")
        lines.append(f"Type: {email_type_display}")
        lines.append(f"Recipient: {recipient}")
        lines.append(f"Subject: {subject}")
        lines.append(f"Status: {status}")
        
        # Add error message if present
        if error_message:
            lines.append(f"Error: {error_message}")
        
        lines.append("---\n")
        
        return "\n".join(lines)
    
    def get_email_history(self, candidate_name: str) -> List[Dict[str, str]]:
        """Retrieve email history for a candidate.
        
        Reads the emails.log file for the candidate and parses it into
        a list of email log entries with their details.
        
        Args:
            candidate_name: Candidate's full name
        
        Returns:
            List of dictionaries containing email log entries.
            Each dictionary has keys: timestamp, type, recipient, subject, status, error
            Returns empty list if no log file exists.
        
        Raises:
            ValueError: If candidate_name is empty
        """
        if not candidate_name or not candidate_name.strip():
            error_msg = "candidate_name must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Normalize candidate name for directory
        normalized_name = candidate_name.strip().lower().replace(" ", "_")
        
        # Path to emails.log file
        log_file_path = self.base_dir / normalized_name / "emails.log"
        
        # Return empty list if log file doesn't exist
        if not log_file_path.exists():
            logger.info(f"No email log found for {candidate_name}")
            return []
        
        try:
            # Read and parse the log file
            with open(log_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse log entries
            entries = self._parse_log_content(content)
            
            logger.info(f"Retrieved {len(entries)} email log entries for {candidate_name}")
            return entries
            
        except Exception as e:
            error_msg = f"Failed to read email history for {candidate_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
    
    def _parse_log_content(self, content: str) -> List[Dict[str, str]]:
        """Parse log file content into structured entries.
        
        Args:
            content: Raw log file content
        
        Returns:
            List of dictionaries containing parsed log entries
        """
        entries = []
        
        # Split content into lines and process
        lines = content.split("\n")
        current_entry = {}
        
        for line in lines:
            line = line.strip()
            
            # Skip header lines
            if line.startswith("=== EMAIL LOG ===") or line.startswith("Candidate:"):
                continue
            
            # Empty line - skip
            if not line:
                continue
            
            # Entry separator - save current entry and start new one
            if line == "---":
                if current_entry:
                    entries.append(current_entry)
                    current_entry = {}
                continue
            
            # Extract timestamp
            if line.startswith("[") and line.endswith("]"):
                current_entry["timestamp"] = line[1:-1]
            # Extract key-value pairs
            elif ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                current_entry[key] = value
        
        # Add last entry if exists
        if current_entry:
            entries.append(current_entry)
        
        return entries
