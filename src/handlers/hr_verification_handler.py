"""HR verification call handler for employment verification."""

import os
import time
import logging
from typing import Optional
from src.core.models import ConversationConfig, CallTranscript
from src.core.elevenlabs_client import ElevenLabsClient

# Configure logging
logger = logging.getLogger(__name__)


class HRVerificationHandler:
    """Handler for HR verification calls.
    
    This handler manages the conversation flow for HR verification calls,
    which focus on confirming factual employment information such as
    employment dates, job title, and employment confirmation.
    """
    
    def __init__(self, elevenlabs_client: Optional[ElevenLabsClient] = None):
        """Initialize the HR verification handler.
        
        Args:
            elevenlabs_client: Optional ElevenLabsClient instance. If not provided,
                             creates a new client using environment variables.
        """
        self.client = elevenlabs_client or ElevenLabsClient()
        self.agent_id = os.getenv('ELEVENLABS_HR_AGENT_ID', '')
        
        if not self.agent_id:
            raise ValueError(
                "ELEVENLABS_HR_AGENT_ID must be set in environment variables"
            )
    
    def build_conversation_config(
        self,
        candidate_name: str,
        job_title: str,
        start_date: str,
        end_date: str
    ) -> ConversationConfig:
        """Build conversation configuration for HR verification call.
        
        Creates a structured conversation flow with introduction and questions
        designed to verify employment information with HR representatives.
        
        Args:
            candidate_name: Full name of the candidate being verified
            job_title: Job title claimed by the candidate
            start_date: Employment start date (e.g., "January 2020")
            end_date: Employment end date (e.g., "December 2022")
        
        Returns:
            ConversationConfig: Configuration object for the HR verification call
        
        Raises:
            ValueError: If any required parameter is empty or invalid
        """
        if not candidate_name or not candidate_name.strip():
            raise ValueError("candidate_name must be a non-empty string")
        
        if not job_title or not job_title.strip():
            raise ValueError("job_title must be a non-empty string")
        
        if not start_date or not start_date.strip():
            raise ValueError("start_date must be a non-empty string")
        
        if not end_date or not end_date.strip():
            raise ValueError("end_date must be a non-empty string")
        
        # Build introduction message
        first_message = (
            f"Hello, this is an automated employment verification call "
            f"regarding {candidate_name}. I need to verify some employment "
            f"information for our records. This will only take a few minutes."
        )
        
        # Define structured questions for HR verification
        questions = [
            f"Can you confirm if {candidate_name} worked at your organization?",
            f"What was their official job title?",
            f"What were their employment start and end dates?",
            "Thank you for your time and assistance with this verification."
        ]
        
        # Create and return conversation config
        return ConversationConfig(
            agent_id=self.agent_id,
            first_message=first_message,
            questions=questions,
            max_duration_seconds=int(os.getenv('MAX_CALL_DURATION_SECONDS', 600))  # 10 minutes maximum
        )
    
    def execute_call(
        self,
        phone_number: str,
        config: ConversationConfig
    ) -> CallTranscript:
        """Execute an HR verification call.
        
        Initiates a phone call using the ElevenLabs client with the provided
        configuration and retrieves the complete conversation transcript.
        Handles graceful termination and timeout scenarios.
        
        Args:
            phone_number: Phone number to call in E.164 format (e.g., +1-555-0100)
            config: Conversation configuration with agent ID and questions
        
        Returns:
            CallTranscript: Complete transcript of the verification call
        
        Raises:
            ValueError: If phone_number or config is invalid
            ElevenLabsClientError: If the call fails or transcript retrieval fails
        """
        if not phone_number or not phone_number.strip():
            error_msg = "phone_number must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not isinstance(config, ConversationConfig):
            error_msg = "config must be a ConversationConfig instance"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Executing HR verification call to {phone_number}")
        
        try:
            # Start the conversation
            conversation_id = self.client.start_conversation(
                phone_number=phone_number,
                config=config
            )
            
            logger.info(f"HR verification call started: {conversation_id}")
            
            # Wait for the call to complete by polling the conversation status
            logger.info("Waiting for call to complete...")
            transcript = self._wait_for_call_completion(
                conversation_id=conversation_id,
                participant_phone=phone_number,
                max_wait_seconds=config.max_duration_seconds + 60  # Add buffer
            )
            
            logger.info(
                f"HR verification call completed: {conversation_id}, "
                f"Duration: {transcript.duration_seconds}s"
            )
            
            return transcript
            
        except Exception as e:
            logger.error(
                f"HR verification call failed for {phone_number}: {str(e)}",
                exc_info=True
            )
            raise
    
    def _wait_for_call_completion(
        self,
        conversation_id: str,
        participant_phone: str,
        max_wait_seconds: int = 660,
        poll_interval: int = 5
    ) -> CallTranscript:
        """Wait for a call to complete and retrieve the transcript.
        
        Polls the conversation status until it's no longer in 'initiated' or 'in_progress'
        status, then retrieves the complete transcript.
        
        Args:
            conversation_id: Unique identifier of the conversation
            participant_phone: Phone number of the call participant
            max_wait_seconds: Maximum time to wait for call completion (default: 11 minutes)
            poll_interval: Seconds between status checks (default: 5 seconds)
        
        Returns:
            CallTranscript: Complete transcript of the call
        
        Raises:
            TimeoutError: If call doesn't complete within max_wait_seconds
        """
        start_time = time.time()
        elapsed = 0
        
        while elapsed < max_wait_seconds:
            try:
                # Try to get the transcript
                transcript = self.client.get_conversation_transcript(
                    conversation_id=conversation_id,
                    participant_phone=participant_phone
                )
                
                # Check if call has completed (has actual content and duration)
                if transcript.duration_seconds > 0 or transcript.raw_transcript:
                    logger.info(f"Call completed after {elapsed}s")
                    return transcript
                
                # Call still in progress, wait before next check
                logger.info(f"Call in progress... ({elapsed}s elapsed)")
                time.sleep(poll_interval)
                elapsed = int(time.time() - start_time)
                
            except Exception as e:
                # If we get an error, wait a bit and try again
                logger.warning(f"Error checking call status: {str(e)}, retrying...")
                time.sleep(poll_interval)
                elapsed = int(time.time() - start_time)
        
        # Timeout reached - get whatever transcript is available
        logger.warning(
            f"Call did not complete within {max_wait_seconds}s. "
            "Retrieving partial transcript..."
        )
        return self.client.get_conversation_transcript(
            conversation_id=conversation_id,
            participant_phone=participant_phone
        )
