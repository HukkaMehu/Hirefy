"""Integration test to verify email notifications are sent during verification."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.email_orchestrator import EmailOrchestrator


def test_send_reference_email():
    """Test sending a reference check email."""
    
    print("Testing reference email sending...")
    print("=" * 70)
    
    # Check if SMTP is configured
    smtp_host = os.getenv('SMTP_HOST')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not all([smtp_host, smtp_username, smtp_password]):
        print("❌ SMTP not configured in .env file")
        print("   Required: SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD")
        return False
    
    print(f"SMTP Host: {smtp_host}")
    print(f"SMTP Username: {smtp_username}")
    print(f"From Email: {os.getenv('SMTP_FROM_EMAIL')}")
    print()
    
    # Create email orchestrator
    try:
        orchestrator = EmailOrchestrator()
        print("✅ EmailOrchestrator initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize EmailOrchestrator: {e}")
        return False
    
    # Send test email
    print("\nSending test reference email...")
    print(f"To: {smtp_username} (sending to yourself for testing)")
    
    try:
        result = orchestrator.send_reference_email(
            candidate_name="Test Candidate",
            reference_name="Test Reference",
            reference_email=smtp_username,  # Send to yourself for testing
            relationship="manager"
        )
        
        if result.success:
            print(f"✅ Email sent successfully!")
            print(f"   Email ID: {result.email_id}")
            print(f"   Recipient: {result.recipient}")
            print(f"   Log Path: {result.log_path}")
            return True
        else:
            print(f"❌ Email sending failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during email sending: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_send_hr_email():
    """Test sending an HR verification email."""
    
    print("\n" + "=" * 70)
    print("Testing HR verification email sending...")
    print("=" * 70)
    
    smtp_username = os.getenv('SMTP_USERNAME')
    
    # Create email orchestrator
    try:
        orchestrator = EmailOrchestrator()
    except Exception as e:
        print(f"❌ Failed to initialize EmailOrchestrator: {e}")
        return False
    
    # Send test email
    print(f"\nSending test HR verification email...")
    print(f"To: {smtp_username} (sending to yourself for testing)")
    
    try:
        result = orchestrator.send_hr_verification_email(
            candidate_name="Test Candidate",
            job_title="Software Engineer",
            start_date="2020-01-01",
            end_date="2022-12-31",
            hr_email=smtp_username  # Send to yourself for testing
        )
        
        if result.success:
            print(f"✅ Email sent successfully!")
            print(f"   Email ID: {result.email_id}")
            print(f"   Recipient: {result.recipient}")
            print(f"   Log Path: {result.log_path}")
            return True
        else:
            print(f"❌ Email sending failed: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during email sending: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("EMAIL INTEGRATION TEST")
    print("=" * 70)
    print("\nThis test will send actual emails to verify SMTP configuration.")
    print("Emails will be sent to your own email address for testing.")
    print()
    
    results = []
    
    # Run tests
    results.append(test_send_reference_email())
    results.append(test_send_hr_email())
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("\n✅ All email tests passed!")
        print("   Check your inbox for the test emails.")
        sys.exit(0)
    else:
        print("\n❌ Some email tests failed")
        print("   Check SMTP configuration in .env file")
        sys.exit(1)
