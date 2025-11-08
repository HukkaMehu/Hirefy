"""Call orchestrator for coordinating employment verification calls."""

import logging
from typing import Optional
from src.core.models import CallResult
from src.core.elevenlabs_client import ElevenLabsClient
from src.handlers.hr_verification_handler import HRVerificationHandler
from src.handlers.reference_call_handler import ReferenceCallHandler
from src.utils.transcript_manager import TranscriptManager

# Configure logging
logger = logging.getLogger(__name__)


class CallOrchestrator:
    """Main coordination layer for employment verification calls.
    
    This class serves as the primary entry point for initiating verification calls.
    It handles input validation, routes calls to appropriate handlers (HR or Reference),
    and manages transcript saving through the TranscriptManager.
    """
    
    def __init__(
        self,
        elevenlabs_client: Optional[ElevenLabsClient] = None,
        transcript_manager: Optional[TranscriptManager] = None
    ):
        """Initialize the CallOrchestrator.
        
        Args:
            elevenlabs_client: Optional ElevenLabsClient instance. If not provided,
                             handlers will create their own clients.
            transcript_manager: Optional TranscriptManager instance. If not provided,
                              creates a new manager with default settings.
        """
        self.elevenlabs_client = elevenlabs_client
        self.transcript_manager = transcript_manager or TranscriptManager()
        
        # Initialize handlers (they will create their own clients if needed)
        self.hr_handler = HRVerificationHandler(elevenlabs_client=self.elevenlabs_client)
        self.reference_handler = ReferenceCallHandler(elevenlabs_client=self.elevenlabs_client)
    
    def initiate_hr_verification(
        self,
        candidate_name: str,
        job_title: str,
        start_date: str,
        end_date: str,
        hr_phone: str
    ) -> CallResult:
        """Initiate an HR verification call.
        
        Validates input parameters, builds conversation configuration,
        executes the call through the HR handler, and saves the transcript.
        
        Args:
            candidate_name: Full name of the candidate being verified
            job_title: Job title claimed by the candidate
            start_date: Employment start date (e.g., "January 2020")
            end_date: Employment end date (e.g., "December 2022")
            hr_phone: Phone number of HR department in E.164 format
        
        Returns:
            CallResult: Result object with success status, call ID, and transcript path
        
        Raises:
            ValueError: If any required parameter is empty or invalid
        """
        # Input validation
        if not candidate_name or not candidate_name.strip():
            raise ValueError("candidate_name must be a non-empty string")
        
        if not job_title or not job_title.strip():
            raise ValueError("job_title must be a non-empty string")
        
        if not start_date or not start_date.strip():
            raise ValueError("start_date must be a non-empty string")
        
        if not end_date or not end_date.strip():
            raise ValueError("end_date must be a non-empty string")
        
        if not hr_phone or not hr_phone.strip():
            raise ValueError("hr_phone must be a non-empty string")
        
        logger.info(
            f"Initiating HR verification call for {candidate_name} at {hr_phone}"
        )
        
        try:
            # Build conversation configuration
            config = self.hr_handler.build_conversation_config(
                candidate_name=candidate_name,
                job_title=job_title,
                start_date=start_date,
                end_date=end_date
            )
            
            # Execute the call
            transcript = self.hr_handler.execute_call(
                phone_number=hr_phone,
                config=config
            )
            
            # Save transcript with metadata
            metadata = {
                "Job Title": job_title,
                "Start Date": start_date,
                "End Date": end_date,
                "HR Phone": hr_phone
            }
            
            transcript_path = self.transcript_manager.save_transcript(
                candidate_name=candidate_name,
                call_type="hr_verification",
                transcript=transcript,
                metadata=metadata
            )
            
            logger.info(
                f"HR verification call completed successfully for {candidate_name}. "
                f"Duration: {transcript.duration_seconds}s, Transcript: {transcript_path}"
            )
            
            # Return successful result
            return CallResult(
                success=True,
                call_id=transcript.conversation_id,
                transcript_path=transcript_path,
                duration_seconds=transcript.duration_seconds,
                error_message=None
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"HR verification call failed for {candidate_name}: {error_msg}",
                exc_info=True
            )
            
            # Return failed result with error message
            return CallResult(
                success=False,
                call_id="",
                transcript_path="",
                duration_seconds=0,
                error_message=error_msg
            )
    
    def initiate_reference_call(
        self,
        candidate_name: str,
        reference_name: str,
        reference_phone: str,
        relationship: str
    ) -> CallResult:
        """Initiate a reference call.
        
        Validates input parameters, builds conversation configuration,
        executes the call through the Reference handler, and saves the transcript.
        
        Args:
            candidate_name: Full name of the candidate being referenced
            reference_name: Name of the reference being called
            reference_phone: Phone number of reference in E.164 format
            relationship: Relationship to candidate ("manager", "coworker", or "supervisor")
        
        Returns:
            CallResult: Result object with success status, call ID, and transcript path
        
        Raises:
            ValueError: If any required parameter is empty or invalid
        """
        # Input validation
        if not candidate_name or not candidate_name.strip():
            raise ValueError("candidate_name must be a non-empty string")
        
        if not reference_name or not reference_name.strip():
            raise ValueError("reference_name must be a non-empty string")
        
        if not reference_phone or not reference_phone.strip():
            raise ValueError("reference_phone must be a non-empty string")
        
        if not relationship or not relationship.strip():
            raise ValueError("relationship must be a non-empty string")
        
        # Validate relationship type
        valid_relationships = ["manager", "coworker", "supervisor"]
        if relationship.lower() not in valid_relationships:
            raise ValueError(
                f"relationship must be one of: {', '.join(valid_relationships)}"
            )
        
        logger.info(
            f"Initiating reference call for {candidate_name} with {reference_name} "
            f"({relationship}) at {reference_phone}"
        )
        
        try:
            # Build conversation configuration
            config = self.reference_handler.build_conversation_config(
                candidate_name=candidate_name,
                reference_name=reference_name,
                relationship=relationship
            )
            
            # Execute the call
            transcript = self.reference_handler.execute_call(
                phone_number=reference_phone,
                config=config
            )
            
            # Save transcript with metadata
            metadata = {
                "Reference Name": reference_name,
                "Relationship": relationship.title(),
                "Reference Phone": reference_phone
            }
            
            transcript_path = self.transcript_manager.save_transcript(
                candidate_name=candidate_name,
                call_type="reference",
                transcript=transcript,
                metadata=metadata
            )
            
            logger.info(
                f"Reference call completed successfully for {candidate_name}. "
                f"Duration: {transcript.duration_seconds}s, Transcript: {transcript_path}"
            )
            
            # Return successful result
            return CallResult(
                success=True,
                call_id=transcript.conversation_id,
                transcript_path=transcript_path,
                duration_seconds=transcript.duration_seconds,
                error_message=None
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(
                f"Reference call failed for {candidate_name} with {reference_name}: {error_msg}",
                exc_info=True
            )
            
            # Return failed result with error message
            return CallResult(
                success=False,
                call_id="",
                transcript_path="",
                duration_seconds=0,
                error_message=error_msg
            )
