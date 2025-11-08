"""Tests for verification orchestrator"""

import os
import sys
from datetime import datetime, date

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.models import (
    db, VerificationSession, Candidate, Employment,
    VerificationStatus, EmploymentVerificationStatus, DataSource
)
from src.core.verification_orchestrator import (
    VerificationOrchestrator, VerificationPlan
)
from src.api.app import create_app


def test_verification_plan_creation():
    """Test creating a verification plan"""
    print("\n=== Test: Verification Plan Creation ===")
    
    plan = VerificationPlan("test-session-123")
    
    # Add employment verifications
    plan.add_employment_verification(
        employment_id="emp-1",
        company_name="Tech Corp",
        hr_phone="+1234567890",
        hr_email="hr@techcorp.com"
    )
    
    plan.add_employment_verification(
        employment_id="emp-2",
        company_name="StartupXYZ",
        hr_email="hr@startupxyz.com"
    )
    
    # Add reference verifications
    plan.add_reference_verification(
        reference_name="John Manager",
        reference_phone="+1987654321",
        relationship="manager",
        employment_dates={'start_date': '2020-01', 'end_date': '2022-12'}
    )
    
    # Add technical verification
    plan.add_technical_verification(
        github_username="testdev",
        claimed_skills=["Python", "JavaScript", "React"]
    )
    
    print(f"✓ Plan created with {plan.get_total_tasks()} tasks")
    print(f"  - Employment verifications: {len(plan.employment_verifications)}")
    print(f"  - Reference verifications: {len(plan.reference_verifications)}")
    print(f"  - Technical verifications: {len(plan.technical_verifications)}")
    
    plan_dict = plan.to_dict()
    print(f"✓ Plan dictionary: {plan_dict}")
    
    assert plan.get_total_tasks() == 4
    assert len(plan.employment_verifications) == 2
    assert len(plan.reference_verifications) == 1
    assert len(plan.technical_verifications) == 1
    
    print("✓ Verification plan creation test passed!")


def test_verification_plan_generation_from_session():
    """Test generating verification plan from database session"""
    print("\n=== Test: Verification Plan Generation from Session ===")
    
    # Create Flask app and initialize database
    app = create_app()
    
    with app.app_context():
        # Create test candidate
        candidate = Candidate(
            full_name="Jane Doe",
            email="jane@example.com"
        )
        db.session.add(candidate)
        db.session.flush()
        
        # Create verification session
        session = VerificationSession(
            candidate_id=candidate.id,
            status=VerificationStatus.DOCUMENTS_COLLECTED
        )
        db.session.add(session)
        db.session.flush()
        
        # Add employment records
        emp1 = Employment(
            verification_session_id=session.id,
            company_name="Tech Solutions Inc",
            job_title="Senior Developer",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
            source=DataSource.CV,
            verification_status=EmploymentVerificationStatus.PENDING,
            hr_contact_info={
                'phone': '+1234567890',
                'email': 'hr@techsolutions.com'
            }
        )
        db.session.add(emp1)
        
        emp2 = Employment(
            verification_session_id=session.id,
            company_name="Innovation Labs",
            job_title="Lead Engineer",
            start_date=date(2023, 1, 1),
            end_date=None,
            source=DataSource.CV,
            verification_status=EmploymentVerificationStatus.PENDING,
            hr_contact_info={
                'email': 'hr@innovationlabs.com'
            }
        )
        db.session.add(emp2)
        
        db.session.commit()
        
        print(f"✓ Created test session: {session.id}")
        print(f"✓ Created candidate: {candidate.full_name}")
        print(f"✓ Created {len(session.employments)} employment records")
        
        # Generate verification plan
        orchestrator = VerificationOrchestrator(timeout_hours=0.5)
        plan = orchestrator.initiate_verification(session.id)
        
        print(f"✓ Generated plan with {plan.get_total_tasks()} tasks")
        print(f"  - Employment verifications: {len(plan.employment_verifications)}")
        
        assert plan.verification_session_id == session.id
        assert len(plan.employment_verifications) == 2
        assert plan.employment_verifications[0]['company_name'] == "Tech Solutions Inc"
        assert plan.employment_verifications[1]['company_name'] == "Innovation Labs"
        
        # Cleanup
        db.session.delete(session)
        db.session.delete(candidate)
        db.session.commit()
        
        print("✓ Verification plan generation test passed!")


def test_verification_status_tracking():
    """Test verification status tracking"""
    print("\n=== Test: Verification Status Tracking ===")
    
    app = create_app()
    
    with app.app_context():
        # Create test data
        candidate = Candidate(
            full_name="Bob Smith",
            email="bob@example.com"
        )
        db.session.add(candidate)
        db.session.flush()
        
        session = VerificationSession(
            candidate_id=candidate.id,
            status=VerificationStatus.DOCUMENTS_COLLECTED
        )
        db.session.add(session)
        db.session.commit()
        
        print(f"✓ Created test session: {session.id}")
        
        # Create orchestrator and get status
        orchestrator = VerificationOrchestrator()
        status = orchestrator.get_verification_status(session.id)
        
        print(f"✓ Retrieved status: {status['status']}")
        print(f"  - Session ID: {status['verification_session_id']}")
        print(f"  - Created at: {status['created_at']}")
        print(f"  - Progress: {status['progress']}")
        
        assert status['success'] is True
        assert status['verification_session_id'] == session.id
        assert status['status'] == VerificationStatus.DOCUMENTS_COLLECTED.value
        assert 'progress' in status
        
        # Cleanup
        db.session.delete(session)
        db.session.delete(candidate)
        db.session.commit()
        
        print("✓ Verification status tracking test passed!")


def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    print("\n=== Test: Orchestrator Initialization ===")
    
    orchestrator = VerificationOrchestrator(timeout_hours=2.0)
    
    print(f"✓ Orchestrator initialized")
    print(f"  - Timeout: {orchestrator.timeout_hours} hours")
    print(f"  - Employment verifier: {orchestrator.employment_verifier.__class__.__name__}")
    print(f"  - Reference verifier: {orchestrator.reference_verifier.__class__.__name__}")
    print(f"  - Technical analyzer: {orchestrator.technical_analyzer.__class__.__name__}")
    print(f"  - Task manager: {orchestrator.task_manager.__class__.__name__}")
    
    assert orchestrator.timeout_hours == 2.0
    assert orchestrator.employment_verifier is not None
    assert orchestrator.reference_verifier is not None
    assert orchestrator.technical_analyzer is not None
    assert orchestrator.task_manager is not None
    
    print("✓ Orchestrator initialization test passed!")


if __name__ == '__main__':
    print("=" * 60)
    print("VERIFICATION ORCHESTRATOR TESTS")
    print("=" * 60)
    
    try:
        test_orchestrator_initialization()
        test_verification_plan_creation()
        test_verification_plan_generation_from_session()
        test_verification_status_tracking()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
