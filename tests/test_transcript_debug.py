"""
Debug script to check transcript retrieval from ElevenLabs API.

This script tests the transcript retrieval to see what data is available.
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.elevenlabs_client import ElevenLabsClient


def test_transcript_debug():
    """Test transcript retrieval and show what data is available"""
    print("\n" + "="*80)
    print("Transcript Debug Test")
    print("="*80 + "\n")
    
    # Get a recent conversation ID from transcripts
    transcript_file = "transcripts/touko_ursin/reference_2025-11-08_12-31-57.txt"
    
    if not os.path.exists(transcript_file):
        print(f"❌ Transcript file not found: {transcript_file}")
        return False
    
    # Read the conversation ID from the file
    with open(transcript_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Extract conversation ID
    conv_id = None
    for line in content.split('\n'):
        if 'Conversation ID:' in line:
            conv_id = line.split('Conversation ID:')[1].strip()
            break
    
    if not conv_id:
        print(f"❌ Could not find conversation ID in transcript")
        return False
    
    print(f"Found conversation ID: {conv_id}")
    print(f"\nRetrieving call details from ElevenLabs API...\n")
    
    try:
        # Initialize client
        client = ElevenLabsClient()
        
        # Get the call object directly
        call = client.client.conversational_ai.conversations.get(
            conversation_id=conv_id
        )
        
        print("Call Object Attributes:")
        print("-" * 80)
        
        # Show all available attributes
        for attr in dir(call):
            if not attr.startswith('_'):
                try:
                    value = getattr(call, attr)
                    if not callable(value):
                        print(f"  {attr}: {value}")
                except:
                    pass
        
        print("\n" + "-" * 80)
        print("\nTranscript Content:")
        print("-" * 80)
        
        if hasattr(call, 'transcript'):
            transcript = call.transcript
            print(f"Type: {type(transcript)}")
            
            if isinstance(transcript, list):
                print(f"Length: {len(transcript)} messages\n")
                for i, msg in enumerate(transcript):
                    print(f"Message {i+1}:")
                    for attr in dir(msg):
                        if not attr.startswith('_'):
                            try:
                                value = getattr(msg, attr)
                                if not callable(value):
                                    print(f"  {attr}: {value}")
                            except:
                                pass
                    print()
            else:
                print(f"Content: {transcript}")
        else:
            print("❌ No transcript attribute found")
        
        print("\n" + "="*80)
        print("✅ Debug test completed")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    try:
        success = test_transcript_debug()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted")
        sys.exit(1)


if __name__ == '__main__':
    main()
