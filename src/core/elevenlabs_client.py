"""ElevenLabs API client wrapper for conversational AI phone calls."""

import os
import logging
from typing import Optional
from datetime import datetime
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from .models import ConversationConfig, CallTranscript

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class ElevenLabsClientError(Exception):
    """Base exception for ElevenLabs client errors."""
    pass


class APIConnectionError(ElevenLabsClientError):
    """Raised when connection to ElevenLabs API fails."""
    pass


class InvalidResponseError(ElevenLabsClientError):
    """Raised when API returns invalid or unexpected response."""
    pass


class CallTimeoutError(ElevenLabsClientError):
    """Raised when a call exceeds the maximum duration."""
    pass


class CallTerminatedError(ElevenLabsClientError):
    """Raised when a call is terminated by the recipient."""
    pass


class ElevenLabsClient:
    """Client wrapper for ElevenLabs Conversational AI API.
    
    This client handles phone call initiation using ElevenLabs conversational AI
    agents and retrieves call transcripts after completion.
    
    Attributes:
        api_key: ElevenLabs API key for authentication
        client: Initialized ElevenLabs SDK client
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the ElevenLabs client.
        
        Args:
            api_key: ElevenLabs API key. If not provided, reads from 
                    ELEVENLABS_API_KEY environment variable.
        
        Raises:
            ValueError: If API key is not provided and not in environment
            APIConnectionError: If client initialization fails
        """
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
        
        if not self.api_key:
            error_msg = (
                "ElevenLabs API key must be provided or set in "
                "ELEVENLABS_API_KEY environment variable"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            self.client = ElevenLabs(api_key=self.api_key)
            self._phone_number_id_cache = None  # Cache for phone number ID
            logger.info("ElevenLabs client initialized successfully")
        except Exception as e:
            error_msg = f"Failed to initialize ElevenLabs client: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise APIConnectionError(error_msg) from e
    
    def _get_phone_number_id_from_elevenlabs(self) -> str:
        """Get the first available phone number ID from ElevenLabs account.
        
        Returns:
            str: ElevenLabs phone number ID
        
        Raises:
            InvalidResponseError: If no phone numbers found in ElevenLabs
        """
        # Return cached value if available
        if self._phone_number_id_cache:
            return self._phone_number_id_cache
        
        try:
            # List all phone numbers in ElevenLabs account
            phone_numbers = self.client.conversational_ai.phone_numbers.list()
            
            # Get the first available phone number
            if phone_numbers and len(phone_numbers) > 0:
                first_number = phone_numbers[0]
                if hasattr(first_number, 'phone_number_id'):
                    self._phone_number_id_cache = first_number.phone_number_id
                    logger.info(f"Using phone number ID: {self._phone_number_id_cache}")
                    return self._phone_number_id_cache
            
            # No phone numbers found
            error_msg = (
                "No phone numbers found in ElevenLabs account. "
                "Please import a Twilio phone number via the ElevenLabs dashboard first. "
                "Go to: https://elevenlabs.io/app/conversational-ai/phone-numbers"
            )
            logger.error(error_msg)
            raise InvalidResponseError(error_msg)
            
        except InvalidResponseError:
            raise
        except Exception as e:
            error_msg = f"Failed to get phone number ID: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise APIConnectionError(error_msg) from e
    
    def start_conversation(
        self,
        phone_number: str,
        config: ConversationConfig
    ) -> str:
        """Initiate a phone call using ElevenLabs conversational AI.
        
        This method starts a phone conversation with the specified number using
        the configured ElevenLabs agent directly through their phone calling API.
        
        Args:
            phone_number: Phone number to call in E.164 format (e.g., +1-555-0100)
            config: Configuration for the conversation including agent ID and questions
        
        Returns:
            conversation_id: Unique identifier for the initiated conversation
        
        Raises:
            ValueError: If phone_number or config is invalid
            APIConnectionError: If API call fails
            InvalidResponseError: If API response is missing required data
            CallTimeoutError: If call exceeds maximum duration
        """
        if not phone_number or not isinstance(phone_number, str):
            error_msg = "phone_number must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not isinstance(config, ConversationConfig):
            error_msg = "config must be a ConversationConfig instance"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(
            f"Starting conversation with {phone_number} using agent {config.agent_id}, "
            f"max duration: {config.max_duration_seconds}s"
        )
        
        try:
            # Get the phone number ID from ElevenLabs (your imported Twilio number)
            # You need to import a Twilio phone number in ElevenLabs dashboard first
            phone_number_id = self._get_phone_number_id_from_elevenlabs()
            
            # Initiate outbound call using ElevenLabs Twilio integration
            response = self.client.conversational_ai.twilio.outbound_call(
                agent_id=config.agent_id,
                agent_phone_number_id=phone_number_id,
                to_number=phone_number
            )
            
            # Check for conversation_id or call_id in response
            conversation_id = None
            if hasattr(response, 'conversation_id'):
                conversation_id = response.conversation_id
            elif hasattr(response, 'call_id'):
                conversation_id = response.call_id
            elif hasattr(response, 'id'):
                conversation_id = response.id
            
            if not conversation_id:
                # Log response for debugging
                logger.error(f"Unexpected API response structure: {response}")
                error_msg = "API response missing conversation_id or call_id"
                logger.error(error_msg)
                raise InvalidResponseError(error_msg)
            
            logger.info(f"Outbound call initiated successfully: {conversation_id}")
            return conversation_id
            
        except (ValueError, InvalidResponseError):
            raise
        except Exception as e:
            error_msg = f"Failed to start conversation with {phone_number}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise APIConnectionError(error_msg) from e
    
    def get_conversation_transcript(
        self,
        conversation_id: str,
        participant_phone: str
    ) -> CallTranscript:
        """Retrieve the transcript of a completed phone call.
        
        This method fetches the full transcript of a phone call after it has
        completed. The transcript includes all exchanges between the AI agent
        and the call participant. Handles partial transcripts for calls that
        were terminated early or timed out.
        
        Args:
            conversation_id: Unique identifier of the call (call_id)
            participant_phone: Phone number of the call participant
        
        Returns:
            CallTranscript: Object containing the complete conversation transcript
                          and metadata
        
        Raises:
            ValueError: If conversation_id is invalid
            APIConnectionError: If API call fails
            InvalidResponseError: If transcript data is incomplete or invalid
            CallTimeoutError: If call exceeded maximum duration
            CallTerminatedError: If call was terminated by recipient
        """
        if not conversation_id or not isinstance(conversation_id, str):
            error_msg = "conversation_id must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not participant_phone or not isinstance(participant_phone, str):
            error_msg = "participant_phone must be a non-empty string"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Retrieving transcript for call: {conversation_id}")
        
        try:
            # Retrieve conversation details from API
            call = self.client.conversational_ai.conversations.get(
                conversation_id=conversation_id
            )
            
            if not call:
                error_msg = f"No call found with ID: {conversation_id}"
                logger.error(error_msg)
                raise InvalidResponseError(error_msg)
            
            # Check call status for early termination or timeout
            status = getattr(call, 'status', 'unknown')
            
            if status == 'timeout' or status == 'max_duration_exceeded':
                logger.warning(
                    f"Call {conversation_id} exceeded maximum duration. "
                    "Saving partial transcript."
                )
            
            if status == 'terminated_by_recipient' or status == 'ended_early':
                logger.info(
                    f"Call {conversation_id} was terminated by recipient. "
                    "Saving partial transcript."
                )
            
            # Extract transcript - it's a list of message objects
            raw_transcript = ""
            
            # Log the call object structure for debugging
            logger.debug(f"Call object attributes: {dir(call)}")
            
            if hasattr(call, 'transcript') and call.transcript:
                # Check if transcript is a list or string
                if isinstance(call.transcript, list):
                    raw_transcript = self._build_transcript_from_messages(call.transcript)
                    logger.info(f"Built transcript from {len(call.transcript)} messages")
                elif isinstance(call.transcript, str):
                    raw_transcript = call.transcript
                else:
                    logger.warning(
                        f"Unexpected transcript type: {type(call.transcript)}. "
                        f"Attempting to convert to string."
                    )
                    raw_transcript = str(call.transcript)
            else:
                logger.warning(
                    f"Call {conversation_id} has no transcript data available yet. "
                    f"Status: {status}"
                )
            
            # Extract timing information
            start_time = self._parse_timestamp(
                getattr(call, 'start_time', None) or getattr(call, 'created_at', None)
            )
            end_time = self._parse_timestamp(
                getattr(call, 'end_time', None) or getattr(call, 'ended_at', None)
            )
            
            # Calculate duration - try to get from API first, then calculate
            duration = 0
            if hasattr(call, 'duration_seconds'):
                duration = call.duration_seconds
            elif hasattr(call, 'duration'):
                duration = call.duration
            else:
                # Calculate from timestamps
                duration = (end_time - start_time).total_seconds()
            
            # Log timing info for debugging
            logger.debug(
                f"Call timing - Start: {start_time}, End: {end_time}, "
                f"Duration: {duration}s, Has duration field: {hasattr(call, 'duration_seconds')}"
            )
            logger.info(
                f"Retrieved transcript for call {conversation_id}. "
                f"Duration: {duration:.1f}s, Status: {status}"
            )
            
            # Create and return CallTranscript object
            return CallTranscript(
                conversation_id=conversation_id,
                raw_transcript=raw_transcript,
                start_time=start_time,
                end_time=end_time,
                participant_phone=participant_phone
            )
            
        except (ValueError, InvalidResponseError):
            raise
        except Exception as e:
            error_msg = f"Failed to retrieve call transcript for {conversation_id}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise APIConnectionError(error_msg) from e
    
    def _build_transcript_from_messages(self, messages: list) -> str:
        """Build a transcript string from a list of message objects.
        
        Args:
            messages: List of message objects from the API
        
        Returns:
            str: Formatted transcript text
        """
        transcript_lines = []
        for msg in messages:
            role = getattr(msg, 'role', 'unknown')
            # Try different possible message field names
            content = (
                getattr(msg, 'message', '') or 
                getattr(msg, 'content', '') or 
                getattr(msg, 'text', '')
            )
            if content:
                # Format role nicely
                role_display = role.upper() if role in ['agent', 'user'] else role.title()
                transcript_lines.append(f"{role_display}: {content}")
        
        return "\n\n".join(transcript_lines)
    
    def _parse_timestamp(self, timestamp: Optional[any]) -> datetime:
        """Parse timestamp from API response.
        
        Args:
            timestamp: Timestamp value from API (could be datetime, string, or None)
        
        Returns:
            datetime: Parsed datetime object, or current time if parsing fails
        """
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                # Try ISO format first
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                pass
        
        # Fallback to current time if timestamp is invalid or missing
        return datetime.now()
