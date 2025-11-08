"""Transcript management for employment verification calls."""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from src.core.models import CallTranscript

# Configure logging
logger = logging.getLogger(__name__)


class TranscriptManager:
    """Manages saving and formatting of call transcripts.
    
    This class handles the creation of transcript files with proper formatting,
    metadata headers, and organized directory structure by candidate name.
    """
    
    def __init__(self, output_dir: str = "./transcripts"):
        """Initialize the TranscriptManager.
        
        Args:
            output_dir: Base directory for storing transcripts (default: ./transcripts)
        """
        self.output_dir = Path(output_dir)
    
    def save_transcript(
        self,
        candidate_name: str,
        call_type: str,
        transcript: CallTranscript,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Save a call transcript to a file with proper formatting.
        
        Creates a directory structure organized by candidate name and saves
        the transcript with a filename that includes call type and timestamp.
        Logs warnings for partial or empty transcripts.
        
        Args:
            candidate_name: Name of the candidate being verified
            call_type: Type of call ("hr_verification" or "reference")
            transcript: CallTranscript object containing conversation data
            metadata: Optional additional metadata to include in the transcript
        
        Returns:
            str: Full path to the saved transcript file
        
        Raises:
            ValueError: If candidate_name or call_type is empty
            OSError: If directory creation or file writing fails
        """
        if not candidate_name or not candidate_name.strip():
            error_msg = "candidate_name must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not call_type or not call_type.strip():
            error_msg = "call_type must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Saving transcript for {candidate_name}, call type: {call_type}")
        
        # Check for partial or empty transcripts
        if not transcript.raw_transcript or len(transcript.raw_transcript.strip()) < 10:
            logger.warning(
                f"Partial or empty transcript detected for {candidate_name} "
                f"(conversation_id: {transcript.conversation_id}). "
                f"Call may have been terminated early or timed out."
            )
        
        # Normalize candidate name for directory (replace spaces with underscores, lowercase)
        normalized_name = candidate_name.strip().lower().replace(" ", "_")
        
        try:
            # Create candidate-specific directory
            candidate_dir = self.output_dir / normalized_name
            candidate_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created/verified directory: {candidate_dir}")
            
            # Generate filename with call type and timestamp
            timestamp = transcript.start_time.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"{call_type}_{timestamp}.txt"
            file_path = candidate_dir / filename
            
            # Format the transcript with metadata
            formatted_content = self.format_transcript(transcript, call_type, candidate_name, metadata)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            logger.info(f"Transcript saved successfully: {file_path}")
            return str(file_path)
            
        except OSError as e:
            error_msg = f"Failed to save transcript for {candidate_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise OSError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error saving transcript for {candidate_name}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise
    
    def format_transcript(
        self,
        transcript: CallTranscript,
        call_type: str,
        candidate_name: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """Format a transcript with metadata header and conversation body.
        
        Creates a formatted text document with:
        - Header section with call metadata
        - Conversation section with the full transcript
        - Clear section separators
        
        Args:
            transcript: CallTranscript object containing conversation data
            call_type: Type of call for the header
            candidate_name: Name of the candidate for the header
            metadata: Optional additional metadata to include
        
        Returns:
            str: Formatted transcript text
        """
        # Calculate duration
        duration_seconds = transcript.duration_seconds
        duration_minutes = duration_seconds // 60
        duration_secs = duration_seconds % 60
        duration_str = f"{duration_minutes}m {duration_secs}s"
        
        # Format call type for display
        call_type_display = call_type.replace("_", " ").title()
        
        # Build metadata header
        lines = []
        lines.append("=" * 50)
        lines.append(f"EMPLOYMENT VERIFICATION CALL")
        lines.append("=" * 50)
        lines.append(f"Candidate: {candidate_name}")
        lines.append(f"Call Type: {call_type_display}")
        lines.append(f"Date: {transcript.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Duration: {duration_str}")
        lines.append(f"Contact: {transcript.participant_phone}")
        lines.append(f"Conversation ID: {transcript.conversation_id}")
        
        # Add any additional metadata
        if metadata:
            for key, value in metadata.items():
                lines.append(f"{key}: {value}")
        
        lines.append("")
        lines.append("-" * 50)
        lines.append("CONVERSATION")
        lines.append("-" * 50)
        lines.append("")
        
        # Add the raw transcript
        lines.append(transcript.raw_transcript)
        
        lines.append("")
        lines.append("-" * 50)
        lines.append("END CONVERSATION")
        lines.append("-" * 50)
        
        return "\n".join(lines)
