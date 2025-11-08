"""
Test script for Wave 2 Backend API
Tests resume upload, parsing, and verification endpoints
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
RESUME_PATH = Path(__file__).parent.parent / "resume_examples" / "resume1.pdf"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✓ Health check passed")

def test_upload_resume():
    """Test resume upload and verification creation"""
    print("\n=== Testing Resume Upload ===")
    
    if not RESUME_PATH.exists():
        print(f"✗ Resume file not found at {RESUME_PATH}")
        return None
    
    with open(RESUME_PATH, "rb") as f:
        files = {"resume": ("resume1.pdf", f, "application/pdf")}
        data = {"github_username": "testuser"}
        
        response = requests.post(
            f"{BASE_URL}/api/v1/verify",
            files=files,
            data=data
        )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, default=str)}")
        print(f"✓ Verification created: {result['verification_id']}")
        return result['verification_id']
    else:
        print(f"✗ Upload failed: {response.text}")
        return None

def test_get_verification(verification_id: str):
    """Test getting verification status"""
    print(f"\n=== Testing Get Verification ===")
    print(f"Verification ID: {verification_id}")
    
    response = requests.get(f"{BASE_URL}/api/v1/verify/{verification_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, default=str)}")
        print(f"✓ Status: {result['status']}")
        print(f"✓ Candidate: {result.get('candidate_name', 'N/A')}")
        print(f"✓ Email: {result.get('candidate_email', 'N/A')}")
        print(f"✓ GitHub: {result.get('github_username', 'N/A')}")
        
        if result.get('parsed_data'):
            parsed = result['parsed_data']
            print(f"\n✓ Parsed Data:")
            print(f"  - Name: {parsed.get('name')}")
            print(f"  - Email: {parsed.get('email')}")
            print(f"  - Skills: {', '.join(parsed.get('skills', []))[:100]}")
            print(f"  - Employment History: {len(parsed.get('employment_history', []))} entries")
            print(f"  - Education: {len(parsed.get('education', []))} entries")
    else:
        print(f"✗ Failed to get verification: {response.text}")

def test_get_steps(verification_id: str):
    """Test getting verification steps"""
    print(f"\n=== Testing Get Steps ===")
    print(f"Verification ID: {verification_id}")
    
    response = requests.get(f"{BASE_URL}/api/v1/verify/{verification_id}/steps")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        steps = result.get('steps', [])
        print(f"✓ Found {len(steps)} steps")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step.get('agent_name')}: {step.get('status')} - {step.get('message')}")
    else:
        print(f"✗ Failed to get steps: {response.text}")

def main():
    """Run all tests"""
    print("=" * 60)
    print("WAVE 2 Backend API Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Health check
        test_health()
        
        # Test 2: Upload resume
        verification_id = test_upload_resume()
        
        if verification_id:
            # Test 3: Get verification status
            test_get_verification(verification_id)
            
            # Test 4: Get verification steps
            test_get_steps(verification_id)
            
            print("\n" + "=" * 60)
            print("✓ All tests completed successfully!")
            print(f"✓ Verification ID: {verification_id}")
            print("=" * 60)
        else:
            print("\n✗ Tests failed - could not create verification")
    
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to server. Make sure FastAPI is running:")
        print("  cd backend && ..\\venv\\Scripts\\python.exe -m uvicorn main:app --reload")
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
