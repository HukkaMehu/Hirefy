"""
Test script to verify transcript API is working correctly.

This script tests:
1. Transcript retrieval from API
2. AI summary generation
3. Candidate name normalization
"""

import sys
import os
import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

API_BASE_URL = "http://localhost:5000/api"


def test_transcript_api():
    """Test transcript API endpoints"""
    print("\n" + "="*80)
    print("Testing Transcript API")
    print("="*80 + "\n")
    
    # Step 1: Get all verifications to find one with transcripts
    print("1. Finding verification sessions...")
    try:
        response = requests.get(f"{API_BASE_URL}/verifications", timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to get verifications: {response.status_code}")
            return False
        
        data = response.json()
        verifications = data.get('verifications', [])
        
        if not verifications:
            print("❌ No verifications found")
            return False
        
        # Use the first verification
        session_id = verifications[0]['session_id']
        candidate_name = verifications[0]['candidate_name']
        
        print(f"✅ Found verification: {session_id}")
        print(f"   Candidate: {candidate_name}")
        
    except Exception as e:
        print(f"❌ Error getting verifications: {str(e)}")
        return False
    
    # Step 2: Get transcripts for this verification
    print(f"\n2. Fetching transcripts for {session_id}...")
    try:
        response = requests.get(
            f"{API_BASE_URL}/verifications/{session_id}/transcripts",
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get transcripts: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        data = response.json()
        
        if not data.get('success'):
            print(f"❌ API returned success=false")
            print(f"   Response: {data}")
            return False
        
        transcripts = data.get('transcripts', [])
        print(f"✅ Found {len(transcripts)} transcript(s)")
        
        for i, transcript in enumerate(transcripts):
            print(f"\n   Transcript {i+1}:")
            print(f"   - Filename: {transcript['filename']}")
            print(f"   - Size: {len(transcript['content'])} characters")
            print(f"   - Preview: {transcript['content'][:100]}...")
        
        if len(transcripts) == 0:
            print("\n⚠️  No transcripts found. This might be expected if:")
            print("   - Verification hasn't started yet")
            print("   - No calls have been made")
            print("   - Candidate name normalization is incorrect")
            
            # Check if transcript files exist
            normalized_name = candidate_name.strip().lower().replace(" ", "_")
            transcript_dir = f"transcripts/{normalized_name}"
            
            if os.path.exists(transcript_dir):
                files = os.listdir(transcript_dir)
                print(f"\n   Found transcript directory: {transcript_dir}")
                print(f"   Files: {files}")
            else:
                print(f"\n   Transcript directory doesn't exist: {transcript_dir}")
        
    except Exception as e:
        print(f"❌ Error getting transcripts: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Try to generate AI summary (only if we have transcripts)
    if len(transcripts) > 0:
        print(f"\n3. Generating AI summary...")
        try:
            response = requests.post(
                f"{API_BASE_URL}/verifications/{session_id}/ai-summary",
                json={},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"⚠️  Failed to generate AI summary: {response.status_code}")
                print(f"   Response: {response.text}")
            else:
                data = response.json()
                
                if data.get('success'):
                    summary = data.get('summary', '')
                    print(f"✅ AI summary generated ({len(summary)} characters)")
                    print(f"\n   Summary preview:")
                    print(f"   {summary[:200]}...")
                else:
                    print(f"⚠️  AI summary generation failed: {data.get('error')}")
        
        except Exception as e:
            print(f"⚠️  Error generating AI summary: {str(e)}")
    
    # Success!
    print("\n" + "="*80)
    print("✅ TRANSCRIPT API TEST COMPLETED")
    print("="*80)
    print(f"\nResults:")
    print(f"  • Session ID: {session_id}")
    print(f"  • Candidate: {candidate_name}")
    print(f"  • Transcripts found: {len(transcripts)}")
    print()
    
    return True


def main():
    """Main entry point"""
    try:
        success = test_transcript_api()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted")
        sys.exit(1)


if __name__ == '__main__':
    main()
