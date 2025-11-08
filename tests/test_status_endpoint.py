"""Test the enhanced status endpoint with progress tracking"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.api.app import create_app
from src.database import db
from src.database.models import (
    VerificationSession, Candidate, Employment, EducationCredential,
    ContactRecord, GitHubAnalysisRecord, VerificationStatus,
    EmploymentVerificationStatus, EducationVerificationStatus
)
from datetime import datetime, timedelta

def test_status_endpoint():
    """Test the enhanced status endpoint"""
    app = create_app()
    
    with app.app_context():
        # Create test data
        candidate = Candidate(
            full_name="Test Candidate",
            email="test@example.com"
        )
        db.session.add(candidate)
        db.session.flush()
        
        session = VerificationSession(
            candidate_id=candidate.id,
            status=VerificationStatus.VERIFICATION_IN_PROGRESS,
            estimated_completion=datetime.utcnow() + timedelta(hours=24)
        )
        db.session.add(session)
        db.session.flush()
        
        # Add employment records
        employment1 = Employment(
            verification_session_id=session.id,
            company_name="Tech Corp",
            job_title="Senior Developer",
            start_date=datetime(2020, 1, 1).date(),
            end_date=datetime(2022, 12, 31).date(),
            verification_status=EmploymentVerificationStatus.VERIFIED
        )
        db.session.add(employment1)
        
        employment2 = Employment(
            verification_session_id=session.id,
            company_name="Startup Inc",
            job_title="Lead Engineer",
            start_date=datetime(2023, 1, 1).date(),
            end_date=None,
            verification_status=EmploymentVerificationStatus.PENDING
        )
        db.session.add(employment2)
        
        # Add education record
        education = EducationCredential(
            verification_session_id=session.id,
            institution_name="University of Tech",
            degree_type="Bachelor of Science",
            major="Computer Science",
            graduation_date=datetime(2019, 5, 15).date(),
            verification_status=EducationVerificationStatus.VERIFIED
        )
        db.session.add(education)
        
        # Add contact records
        contact1 = ContactRecord(
            verification_session_id=session.id,
            contact_type="REFERENCE",
            contact_method="PHONE",
            contact_name="John Manager",
            contact_info="+1234567890",
            response_received=True,
            response_timestamp=datetime.utcnow()
        )
        db.session.add(contact1)
        
        contact2 = ContactRecord(
            verification_session_id=session.id,
            contact_type="REFERENCE",
            contact_method="EMAIL",
            contact_name="Jane Colleague",
            contact_info="jane@example.com",
            response_received=False
        )
        db.session.add(contact2)
        
        # Add GitHub analysis
        github = GitHubAnalysisRecord(
            verification_session_id=session.id,
            username="testuser",
            profile_found=True,
            total_repos=25,
            total_commits=1500,
            commit_frequency=45.5,
            code_quality_score=8
        )
        db.session.add(github)
        
        db.session.commit()
        
        # Test the endpoint
        with app.test_client() as client:
            response = client.get(f'/api/verifications/{session.id}/status')
            
            assert response.status_code == 200
            data = response.get_json()
            
            print("\n✅ Status Endpoint Response:")
            print(f"Session ID: {data['session_id']}")
            print(f"Status: {data['status']}")
            print(f"\nProgress:")
            print(f"  Overall: {data['progress']['percentage']}%")
            print(f"  Employment: {data['progress']['employment_verifications']}/{data['progress']['total_employments']}")
            print(f"  References: {data['progress']['reference_checks']}/{data['progress']['total_references']}")
            print(f"  Education: {data['progress']['education_verifications']}/{data['progress']['total_education']}")
            print(f"  Technical Analysis: {data['progress']['technical_analysis_complete']}")
            
            print(f"\nTimeline Items: {len(data['timeline'])}")
            for item in data['timeline'][:3]:
                print(f"  - {item['activity']} ({item['status']})")
            
            print(f"\nCurrent Activities: {len(data['activities'])}")
            for activity in data['activities']:
                print(f"  - {activity['message']} ({activity['status']})")
            
            # Verify progress calculation
            assert data['progress']['percentage'] > 0
            assert data['progress']['employment_verifications'] == 1
            assert data['progress']['total_employments'] == 2
            assert data['progress']['reference_checks'] == 1
            assert data['progress']['total_references'] == 2
            assert data['progress']['technical_analysis_complete'] == True
            
            print("\n✅ All assertions passed!")
        
        # Cleanup - delete in correct order
        db.session.delete(github)
        db.session.delete(contact1)
        db.session.delete(contact2)
        db.session.delete(education)
        db.session.delete(employment1)
        db.session.delete(employment2)
        db.session.delete(session)
        db.session.delete(candidate)
        db.session.commit()

if __name__ == '__main__':
    test_status_endpoint()
    print("\n✅ Status endpoint test completed successfully!")
