"""Data models for the Employment Verification Agent."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class CallResult:
    """Result of a verification call attempt.
    
    Attributes:
        success: Whether the call completed successfully
        call_id: Unique identifier for the call session
        transcript_path: File path where the transcript was saved
        duration_seconds: Total duration of the call in seconds
        error_message: Optional error message if call failed
    """
    success: bool
    call_id: str
    transcript_path: str
    duration_seconds: int
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate CallResult data integrity."""
        if not isinstance(self.success, bool):
            raise TypeError("success must be a boolean")
        
        if not self.call_id or not isinstance(self.call_id, str):
            raise ValueError("call_id must be a non-empty string")
        
        if not self.transcript_path or not isinstance(self.transcript_path, str):
            raise ValueError("transcript_path must be a non-empty string")
        
        if not isinstance(self.duration_seconds, int) or self.duration_seconds < 0:
            raise ValueError("duration_seconds must be a non-negative integer")
        
        if self.error_message is not None and not isinstance(self.error_message, str):
            raise TypeError("error_message must be a string or None")


@dataclass
class ConversationConfig:
    """Configuration for a conversational AI call.
    
    Attributes:
        agent_id: ElevenLabs agent ID to use for the call
        first_message: Initial message the agent will speak
        questions: List of questions to ask during the call
        max_duration_seconds: Maximum call duration (default: 600 seconds / 10 minutes)
    """
    agent_id: str
    first_message: str
    questions: List[str]
    max_duration_seconds: int = 600
    
    def __post_init__(self):
        """Validate ConversationConfig data integrity."""
        if not self.agent_id or not isinstance(self.agent_id, str):
            raise ValueError("agent_id must be a non-empty string")
        
        if not self.first_message or not isinstance(self.first_message, str):
            raise ValueError("first_message must be a non-empty string")
        
        if not isinstance(self.questions, list):
            raise TypeError("questions must be a list")
        
        if not self.questions:
            raise ValueError("questions list cannot be empty")
        
        if not all(isinstance(q, str) and q for q in self.questions):
            raise ValueError("all questions must be non-empty strings")
        
        if not isinstance(self.max_duration_seconds, int) or self.max_duration_seconds <= 0:
            raise ValueError("max_duration_seconds must be a positive integer")


@dataclass
class CallTranscript:
    """Transcript of a completed verification call.
    
    Attributes:
        conversation_id: Unique identifier for the conversation
        raw_transcript: Complete text transcript of the conversation
        start_time: When the call started
        end_time: When the call ended
        participant_phone: Phone number of the call participant
    """
    conversation_id: str
    raw_transcript: str
    start_time: datetime
    end_time: datetime
    participant_phone: str
    
    def __post_init__(self):
        """Validate CallTranscript data integrity."""
        if not self.conversation_id or not isinstance(self.conversation_id, str):
            raise ValueError("conversation_id must be a non-empty string")
        
        if not isinstance(self.raw_transcript, str):
            raise TypeError("raw_transcript must be a string")
        
        if not isinstance(self.start_time, datetime):
            raise TypeError("start_time must be a datetime object")
        
        if not isinstance(self.end_time, datetime):
            raise TypeError("end_time must be a datetime object")
        
        if self.end_time < self.start_time:
            raise ValueError("end_time must be after start_time")
        
        if not self.participant_phone or not isinstance(self.participant_phone, str):
            raise ValueError("participant_phone must be a non-empty string")
    
    @property
    def duration_seconds(self) -> int:
        """Calculate call duration in seconds."""
        return int((self.end_time - self.start_time).total_seconds())


@dataclass
class EmailResult:
    """Result of an email send operation.
    
    Attributes:
        success: Whether the email was sent successfully
        email_id: Unique identifier for the email (timestamp-based)
        recipient: Email address of recipient
        log_path: File path where the email was logged
        error_message: Optional error message if send failed
    """
    success: bool
    email_id: str
    recipient: str
    log_path: str
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Validate EmailResult data integrity."""
        if not isinstance(self.success, bool):
            raise TypeError("success must be a boolean")
        
        if not self.email_id or not isinstance(self.email_id, str):
            raise ValueError("email_id must be a non-empty string")
        
        if not self.recipient or not isinstance(self.recipient, str):
            raise ValueError("recipient must be a non-empty string")
        
        if not self.log_path or not isinstance(self.log_path, str):
            raise ValueError("log_path must be a non-empty string")
        
        if self.error_message is not None and not isinstance(self.error_message, str):
            raise TypeError("error_message must be a string or None")
