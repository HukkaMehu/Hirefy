"""Test script to verify call timeout logic works correctly."""

import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from handlers.reference_call_handler import ReferenceCallHandler
from core.models import CallTranscript


def test_call_timeout_on_stuck_initiated():
    """Test that calls stuck in 'initiated' status timeout after 60 seconds."""
    
    print("Testing call timeout for stuck 'initiated' status...")
    
    # Set required environment variable
    os.environ['ELEVENLABS_REFERENCE_AGENT_ID'] = 'test_agent_123'
    
    # Create a mock ElevenLabs client
    mock_client = Mock()
    
    # Mock the conversation get to always return 'initiated' status
    mock_call = Mock()
    mock_call.status = 'initiated'
    mock_call.transcript = None
    mock_call.start_time = datetime.now()
    mock_call.end_time = None
    
    mock_client.client.conversational_ai.conversations.get.return_value = mock_call
    
    # Mock get_conversation_transcript to return empty transcript
    mock_transcript = CallTranscript(
        conversation_id="test_conv_123",
        raw_transcript="",
        start_time=datetime.now(),
        end_time=datetime.now(),
        participant_phone="+1234567890"
    )
    mock_client.get_conversation_transcript.return_value = mock_transcript
    
    # Create handler with mocked client
    handler = ReferenceCallHandler(elevenlabs_client=mock_client)
    
    # Test that timeout occurs
    try:
        # This should timeout after 60 seconds (we'll use a shorter timeout for testing)
        handler._wait_for_call_completion(
            conversation_id="test_conv_123",
            participant_phone="+1234567890",
            max_wait_seconds=70,  # Give it time to hit the 60s initiated timeout
            poll_interval=1  # Check every second for faster testing
        )
        print("❌ FAILED: Expected TimeoutError but call completed")
        return False
    except TimeoutError as e:
        if "initiated" in str(e).lower():
            print(f"✅ PASSED: Call correctly timed out with message: {e}")
            return True
        else:
            print(f"❌ FAILED: Got TimeoutError but wrong message: {e}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Got unexpected exception: {type(e).__name__}: {e}")
        return False


def test_call_completes_normally():
    """Test that calls that complete normally are handled correctly."""
    
    print("\nTesting normal call completion...")
    
    # Set required environment variable
    os.environ['ELEVENLABS_REFERENCE_AGENT_ID'] = 'test_agent_123'
    
    # Create a mock ElevenLabs client
    mock_client = Mock()
    
    # Mock the conversation to transition from initiated to completed
    call_count = [0]
    
    def mock_get_call(conversation_id):
        call_count[0] += 1
        mock_call = Mock()
        # After 3 calls, mark as completed
        if call_count[0] > 3:
            mock_call.status = 'completed'
        else:
            mock_call.status = 'initiated'
        mock_call.transcript = []
        mock_call.start_time = datetime.now()
        mock_call.end_time = datetime.now()
        return mock_call
    
    mock_client.client.conversational_ai.conversations.get.side_effect = mock_get_call
    
    # Mock get_conversation_transcript to return transcript after a few calls
    def mock_get_transcript(conversation_id, participant_phone):
        if call_count[0] > 3:
            return CallTranscript(
                conversation_id=conversation_id,
                raw_transcript="Agent: Hello\nUser: Hi there",
                start_time=datetime.now(),
                end_time=datetime.now(),
                participant_phone=participant_phone
            )
        else:
            return CallTranscript(
                conversation_id=conversation_id,
                raw_transcript="",
                start_time=datetime.now(),
                end_time=datetime.now(),
                participant_phone=participant_phone
            )
    
    mock_client.get_conversation_transcript.side_effect = mock_get_transcript
    
    # Create handler with mocked client
    handler = ReferenceCallHandler(elevenlabs_client=mock_client)
    
    # Test that call completes normally
    try:
        transcript = handler._wait_for_call_completion(
            conversation_id="test_conv_456",
            participant_phone="+1234567890",
            max_wait_seconds=30,
            poll_interval=1
        )
        
        if transcript.raw_transcript:
            print(f"✅ PASSED: Call completed normally with transcript")
            return True
        else:
            print(f"❌ FAILED: Call completed but no transcript")
            return False
    except Exception as e:
        print(f"❌ FAILED: Got unexpected exception: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Call Timeout Logic Tests")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(test_call_timeout_on_stuck_initiated())
    results.append(test_call_completes_normally())
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
