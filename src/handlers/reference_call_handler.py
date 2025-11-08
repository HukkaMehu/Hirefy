"""Reference call handler for employment verification."""

import os
import time
import logging
from typing import Optional
from src.core.models import ConversationConfig, CallTranscript
from src.core.elevenlabs_client import ElevenLabsClient

# Configure logging
logger = logging.getLogger(__name__)


class ReferenceCallHandler:
    """Handler for reference calls.
    
    This handler manages the conversation flow for reference calls,
    which focus on gathering qualitative feedback about a candidate's
    work performance, skills, and professional conduct from former
    managers, coworkers, or supervisors.
    """
    
    def __init__(self, elevenlabs_client: Optional[ElevenLabsClient] = None):
        """Initialize the reference call handler.
        
        Args:
            elevenlabs_client: Optional ElevenLabsClient instance. If not provided,
                             creates a new client using environment variables.
        """
        self.client = elevenlabs_client or ElevenLabsClient()
        self.agent_id = os.getenv('ELEVENLABS_REFERENCE_AGENT_ID', '')
        
        if not self.agent_id:
            raise ValueError(
                "ELEVENLABS_REFERENCE_AGENT_ID must be set in environment variables"
            )
    
    def build_conversation_config(
        self,
        candidate_name: str,
        reference_name: str,
        relationship: str
    ) -> ConversationConfig:
        """Build conversation configuration for reference call.
        
        Creates a structured conversation flow with introduction and questions
        designed to gather qualitative feedback from references about the
        candidate's work performance, skills, and professional behavior.
        
        Args:
            candidate_name: Full name of the candidate being referenced
            reference_name: Name of the reference being called
            relationship: Relationship to candidate ("manager", "coworker", or "supervisor")
        
        Returns:
            ConversationConfig: Configuration object for the reference call
        
        Raises:
            ValueError: If any required parameter is empty or invalid
        """
        if not candidate_name or not candidate_name.strip():
            raise ValueError("candidate_name must be a non-empty string")
        
        if not reference_name or not reference_name.strip():
            raise ValueError("reference_name must be a non-empty string")
        
        if not relationship or not relationship.strip():
            raise ValueError("relationship must be a non-empty string")
        
        # Validate relationship type
        valid_relationships = ["manager", "coworker", "supervisor"]
        if relationship.lower() not in valid_relationships:
            raise ValueError(
                f"relationship must be one of: {', '.join(valid_relationships)}"
            )
        
        # Build introduction message
        first_message = (
            f"Hello {reference_name}, this is an automated reference check call "
            f"for {candidate_name}. Thank you for taking the time to speak with me. "
            f"I have a few questions about your experience working with {candidate_name}. "
            f"This should only take about 10 minutes."
        )
        
        # Define structured questions for reference call
        questions = [
            f"What projects did {candidate_name} work on during their time with you?",
            f"What programming languages or technical skills did {candidate_name} use?",
            f"Can you describe {candidate_name}'s motivation and work ethic?",
            f"How would you rate {candidate_name}'s overall performance?",
            f"Did {candidate_name} receive any promotions or recognition during their time with you?",
            f"What areas could {candidate_name} improve in?",
            "Thank you so much for your valuable feedback. This has been very helpful."
        ]
        
        # Create and return conversation config
        return ConversationConfig(
            agent_id=self.agent_id,
            first_message=first_message,
            questions=questions,
            max_duration_seconds=600  # 10 minutes maximum
        )
    
    def execute_call(
        self,
        phone_number: str,
        config: ConversationConfig
    ) -> CallTranscript:
        """Execute a reference call.
        
        Initiates a phone call using the ElevenLabs client with the provided
        configuration and retrieves the complete conversation transcript.
        Handles graceful termination and timeout scenarios.
        
        Args:
            phone_number: Phone number to call in E.164 format (e.g., +1-555-0100)
            config: Conversation configuration with agent ID and questions
        
        Returns:
            CallTranscript: Complete transcript of the reference call
        
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
        
        logger.info(f"Executing reference call to {phone_number}")
        
        try:
            # Start the conversation
            conversation_id = self.client.start_conversation(
                phone_number=phone_number,
                config=config
            )
            
            logger.info(f"Reference call started: {conversation_id}")
            
            # Wait for the call to complete by polling the conversation status
            logger.info("Waiting for call to complete...")
            transcript = self._wait_for_call_completion(
                conversation_id=conversation_id,
                participant_phone=phone_number,
                max_wait_seconds=config.max_duration_seconds + 60  # Add buffer
            )
            
            logger.info(
                f"Reference call completed: {conversation_id}, "
                f"Duration: {transcript.duration_seconds}s"
            )
            
            return transcript
            
        except Exception as e:
            logger.error(
                f"Reference call failed for {phone_number}: {str(e)}",
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
