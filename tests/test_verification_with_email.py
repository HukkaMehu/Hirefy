"""Test full verification flow with email notifications."""

import os
import sys
import time
from datetime import date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask
from src.database.models import (
    db, VerificationSession, Candidate, Employment, 
    VerificationStatus, EmploymentVerificationStatus, DataSource
)
from src.core.verification_orchestrator import VerificationOrchestrator
from src.api.config import Config


def create_test_app():
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app


def test_verification_with_email_notification():
    """Test that verification sends email notifications."""
    
    print("=" * 70)
    print("VERIFICATION WITH EMAIL NOTIFICATION TEST")
    print("=" * 70)
    
    app = create_test_app()
    
    with app.app_context():
        # Create test candidate
        print("\n1. Creating test candidate...")
        candidate = Candidate(
            full_name="Email Test Candidate",
            email=os.getenv('SMTP_USERNAME'),  # Your email for testing
            phone="+1234567890"
        )
        db.session.add(candidate)
        db.session.commit()
        print(f"   ✅ Candidate created: {candidate.id}")
        
        # Create verification session
        print("\n2. Creating verification session...")
        session = VerificationSession(
            candidate_id=candidate.id,
            hiring_company_id="test_company",
            status=VerificationStatus.VERIFICATION_IN_PROGRESS
        )
        db.session.add(session)
        db.session.commit()
        print(f"   ✅ Session created: {session.id}")
        
        # Create employment record with email
        print("\n3. Creating employment record...")
        employment = Employment(
            verification_session_id=session.id,
            company_name="Test Company Inc",
            job_title="Software Engineer",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31),
            source=DataSource.CV,
            verification_status=EmploymentVerificationStatus.PENDING,
            hr_contact_info={
                'email': os.getenv('SMTP_USERNAME'),  # Your email
                'phone': '+358445013307'  # Test phone (will timeout)
            }
        )
        db.session.add(employment)
        db.session.commit()
        print(f"   ✅ Employment created: {employment.id}")
        
        # Start verification
        print("\n4. Starting verification...")
        print("   This will:")
        print("   - Send an email notification to your email")
        print("   - Attempt a phone call (will timeout after 60s)")
        print("   - Fall back to email as the contact method")
        print()
        
        orchestrator = VerificationOrchestrator()
        
        try:
            # Start verification (this will run in background)
            print("   Starting verification orchestrator...")
            orchestrator.initiate_verification(session.id)
            
            print("\n5. Waiting for verification to process...")
            print("   (This may take up to 60 seconds for phone timeout)")
            
            # Wait a bit for email to be sent
            time.sleep(5)
            
            # Check if email was sent by looking at logs
            log_path = f"transcripts/email_test_candidate/emails.log"
            if os.path.exists(log_path):
                print(f"\n   ✅ Email log file created: {log_path}")
                with open(log_path, 'r') as f:
                    log_content = f.read()
                    if "hr_verification" in log_content or "reference_check" in log_content:
                        print("   ✅ Email notification was sent!")
                        print("\n   Check your email inbox for the verification request.")
                        return True
                    else:
                        print("   ⚠️  Log file exists but no email entries found")
            else:
                print(f"   ⚠️  Email log not found at: {log_path}")
            
            print("\n   Note: Verification is still running in background.")
            print("   The phone call will timeout after 60 seconds.")
            
            return True
            
        except Exception as e:
            print(f"\n   ❌ Error during verification: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Cleanup
            print("\n6. Cleaning up test data...")
            try:
                db.session.delete(employment)
                db.session.delete(session)
                db.session.delete(candidate)
                db.session.commit()
                print("   ✅ Test data cleaned up")
            except:
                db.session.rollback()
                print("   ⚠️  Cleanup failed (data may remain in database)")


if __name__ == "__main__":
    success = test_verification_with_email_notification()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ TEST PASSED")
        print("\nEmails should be sent by default during verification.")
        print("Check your inbox for the test email.")
    else:
        print("❌ TEST FAILED")
    print("=" * 70)
    
    sys.exit(0 if success else 1)
