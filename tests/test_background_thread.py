"""
Test the background thread AI analysis
"""
import time
import requests
import os
from pathlib import Path

print("=" * 80)
print("TESTING BACKGROUND THREAD AI ANALYSIS")
print("=" * 80)

# Create a new verification
print("\n1. Creating new verification...")
response = requests.post('http://localhost:5000/api/verifications', json={
    'candidate_name': 'Test Background Thread',
    'candidate_email': 'test@example.com'
})

if response.status_code != 201:
    print(f"❌ Failed to create verification: {response.text}")
    exit(1)

data = response.json()
session_id = data['session_id']
print(f"✅ Created verification: {session_id}")

# Start verification
print("\n2. Starting verification (this will run in background thread)...")
response = requests.post(f'http://localhost:5000/api/verifications/{session_id}/start-verification')

if response.status_code != 202:
    print(f"❌ Failed to start verification: {response.text}")
    exit(1)

print("✅ Verification started in background")

# Wait and check for log file
print("\n3. Waiting for background thread to complete...")
print("   Checking for thread log file...")

log_file = f"verification_thread_{session_id}.log"
max_wait = 120  # 2 minutes
waited = 0

while waited < max_wait:
    time.sleep(2)
    waited += 2
    
    # Check if log file exists
    if Path(log_file).exists():
        print(f"\n📄 Thread log file found! Reading contents...")
        with open(log_file, 'r', encoding='utf-8') as f:
            log_contents = f.read()
        
        print("\n" + "=" * 80)
        print("THREAD LOG CONTENTS:")
        print("=" * 80)
        print(log_contents)
        print("=" * 80)
        
        # Check if AI analysis completed
        if "AI analysis stored in database" in log_contents:
            print("\n✅ SUCCESS! AI analysis completed and stored!")
            break
        elif "AI analysis exception" in log_contents or "AI analysis failed" in log_contents:
            print("\n❌ AI analysis failed - see log above")
            break
        elif "Background thread exiting" in log_contents:
            if "Starting AI analysis" not in log_contents:
                print("\n❌ Thread exited before AI analysis started!")
            else:
                print("\n⚠️ Thread exited but AI analysis status unclear")
            break
    
    # Show progress
    if waited % 10 == 0:
        print(f"   Still waiting... ({waited}s / {max_wait}s)")

if waited >= max_wait:
    print(f"\n⏱️ Timeout after {max_wait}s")
    if Path(log_file).exists():
        print("\n📄 Partial log file contents:")
        with open(log_file, 'r', encoding='utf-8') as f:
            print(f.read())

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
