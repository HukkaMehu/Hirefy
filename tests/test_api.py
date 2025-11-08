#!/usr/bin/env python3
"""Simple API test script"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_verification():
    """Test creating a verification"""
    print("Testing create verification...")
    data = {
        "candidate_name": "John Doe",
        "candidate_email": "john.doe@example.com",
        "candidate_phone": "+1234567890"
    }
    response = requests.post(f"{BASE_URL}/api/verifications", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get('session_id')

def test_get_verification(session_id):
    """Test getting a verification"""
    print(f"\nTesting get verification {session_id}...")
    response = requests.get(f"{BASE_URL}/api/verifications/{session_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_list_verifications():
    """Test listing verifications"""
    print("\nTesting list verifications...")
    response = requests.get(f"{BASE_URL}/api/verifications")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == '__main__':
    print("=" * 60)
    print("API TEST SUITE")
    print("=" * 60)
    print("\nMake sure the Flask app is running: python app.py\n")
    
    try:
        test_health()
        session_id = test_create_verification()
        if session_id:
            test_get_verification(session_id)
        test_list_verifications()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("Make sure the Flask app is running: python app.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
