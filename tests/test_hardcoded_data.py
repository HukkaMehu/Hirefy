"""
Test script to verify hardcoded candidate data is created correctly.

This script creates a new verification session and checks that:
1. Employment records are created with Touko Ursin's job history
2. Education records are created with Touko Ursin's education
3. GitHub username is set to ToukoUrsin

Usage:
    python test_hardcoded_data.py
"""

import sys
import os
import requests
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

API_BASE_URL = "http://localhost:5000/api"


def test_hardcoded_data():
    """Test that hardcoded data is created correctly"""
    print("\n" + "="*80)
    print("Testing Hardcoded Candidate Data")
    print("="*80 + "\n")
    
    # Step 1: Create a new verification session
    print("1. Creating new verification session...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/verifications",
            json={
                "candidate_name": "Test Candidate",
                "candidate_email": "test@example.com"
            },
            timeout=10
        )
        
        if response.status_code != 201:
            print(f"❌ Failed to create verification: {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        session_id = data['session_id']
        print(f"✅ Created session: {session_id}")
        
    except Exception as e:
        print(f"❌ Error creating session: {str(e)}")
        return False
    
    # Step 2: Get session details and check employment/education
    print("\n2. Checking hardcoded employment and education data...")
    try:
        from database.models import db, VerificationSession
        from api.app import create_app
        
        app = create_app()
        with app.app_context():
            session = VerificationSession.query.get(session_id)
            
            if not session:
                print(f"❌ Session not found: {session_id}")
                return False
            
            # Check employments
            print(f"\n   Employment Records ({len(session.employments)}):")
            expected_companies = ["Finnish Defence Forces", "Ecoinsight", "VerkkoVenture oy"]
            
            for emp in session.employments:
                print(f"   ✓ {emp.company_name} - {emp.job_title}")
                print(f"     Dates: {emp.start_date} to {emp.end_date or 'Present'}")
            
            if len(session.employments) != 3:
                print(f"   ❌ Expected 3 employment records, got {len(session.employments)}")
                return False
            
            for expected in expected_companies:
                if not any(emp.company_name == expected for emp in session.employments):
                    print(f"   ❌ Missing expected company: {expected}")
                    return False
            
            print(f"   ✅ All employment records created correctly")
            
            # Check education
            print(f"\n   Education Records ({len(session.education_credentials)}):")
            expected_institutions = ["Aalto University", "Otaniemi High School, Mathematics and Science Programme"]
            
            for edu in session.education_credentials:
                print(f"   ✓ {edu.institution_name} - {edu.degree_type}")
                print(f"     Major: {edu.major}, Graduation: {edu.graduation_date}")
            
            if len(session.education_credentials) != 2:
                print(f"   ❌ Expected 2 education records, got {len(session.education_credentials)}")
                return False
            
            for expected in expected_institutions:
                if not any(edu.institution_name == expected for edu in session.education_credentials):
                    print(f"   ❌ Missing expected institution: {expected}")
                    return False
            
            print(f"   ✅ All education records created correctly")
            
    except Exception as e:
        print(f"❌ Error checking data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Check GitHub username in verification plan
    print("\n3. Checking GitHub username in verification plan...")
    try:
        from core.verification_orchestrator import VerificationOrchestrator
        
        with app.app_context():
            orchestrator = VerificationOrchestrator()
            plan = orchestrator.initiate_verification(session_id)
            
            print(f"\n   Technical Verifications: {len(plan.technical_verifications)}")
            
            github_found = False
            for tech in plan.technical_verifications:
                if tech.get('github_username') == 'ToukoUrsin':
                    print(f"   ✓ GitHub: @{tech['github_username']}")
                    print(f"     Skills: {', '.join(tech.get('claimed_skills', []))}")
                    github_found = True
            
            if not github_found:
                print(f"   ❌ GitHub username 'ToukoUrsin' not found in verification plan")
                return False
            
            print(f"   ✅ GitHub username hardcoded correctly")
            
    except Exception as e:
        print(f"❌ Error checking GitHub: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Success!
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print(f"\nHardcoded data is working correctly:")
    print(f"  • 3 employment records (Finnish Defence Forces, Ecoinsight, VerkkoVenture oy)")
    print(f"  • 2 education records (Aalto University, Otaniemi High School)")
    print(f"  • GitHub username: ToukoUrsin")
    print(f"\nSession ID: {session_id}")
    print(f"You can now start verification with:")
    print(f"  python test_start_verification.py {session_id}")
    print()
    
    return True


def main():
    """Main entry point"""
    try:
        success = test_hardcoded_data()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted")
        sys.exit(1)


if __name__ == '__main__':
    main()
