"""Test that email notifications are sent by default during verification."""

import os
import sys
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.reference_verifier import ReferenceVerifier
from core.employment_verifier import EmploymentVerifier
from core.models import CallResult, EmailResult
from database.models import Employment, EmploymentVerificationStatus


def test_reference_verifier_sends_email_first():
    """Test that reference verifier sends email notification before attempting phone call."""
    
    print("Testing reference verifier email notification...")
    
    # Create mock orchestrators
    mock_call_orchestrator = Mock()
    mock_email_orchestrator = Mock()
    
    # Mock email sending to succeed
    mock_email_orchestrator.send_reference_email.return_value = EmailResult(
        success=True,
        email_id="email_123",
        recipient="reference@example.com",
        log_path="/path/to/log",
        error_message=None
    )
    
    # Mock phone call to fail (timeout)
    mock_call_orchestrator.initiate_reference_call.return_value = CallResult(
        success=False,
        call_id="call_123",
        transcript_path="",
        duration_seconds=0,
        error_message="Call failed to connect after 60s in 'initiated' status"
    )
    
    # Create verifier with mocked orchestrators
    verifier = ReferenceVerifier(
        call_orchestrator=mock_call_orchestrator,
        email_orchestrator=mock_email_orchestrator,
        openai_api_key="test_key"
    )
    
    # Mock database operations and file reading
    with patch('core.reference_verifier.safe_db_commit'):
        with patch('core.reference_verifier.safe_db_add'):
            with patch('core.reference_verifier.ContactRecord'):
                with patch.object(verifier, '_read_transcript', return_value=None):
                    # Execute verification
                    result = verifier.verify_reference(
                        verification_session_id="session_123",
                        candidate_name="John Doe",
                        reference_name="Jane Smith",
                        reference_phone="+1234567890",
                        reference_email="reference@example.com",
                        relationship="manager"
                    )
    
    # Verify email was sent FIRST
    assert mock_email_orchestrator.send_reference_email.called, "Email should be sent"
    email_call = mock_email_orchestrator.send_reference_email.call_args
    assert email_call[1]['candidate_name'] == "John Doe"
    assert email_call[1]['reference_email'] == "reference@example.com"
    
    # Verify phone was attempted AFTER email
    assert mock_call_orchestrator.initiate_reference_call.called, "Phone call should be attempted"
    
    # Verify result shows success (because email was sent)
    assert result['success'] == True, "Verification should succeed when email is sent"
    assert result['contact_method'] == "email", "Contact method should be email"
    
    print("✅ PASSED: Reference verifier sends email notification first")
    return True


def test_employment_verifier_sends_email_first():
    """Test that employment verifier sends email notification before attempting phone call."""
    
    print("\nTesting employment verifier email notification...")
    
    # Create mock orchestrators
    mock_call_orchestrator = Mock()
    mock_email_orchestrator = Mock()
    
    # Mock email sending to succeed
    mock_email_orchestrator.send_hr_verification_email.return_value = EmailResult(
        success=True,
        email_id="email_456",
        recipient="hr@company.com",
        log_path="/path/to/log",
        error_message=None
    )
    
    # Mock phone call to fail (timeout)
    mock_call_orchestrator.initiate_hr_verification.return_value = CallResult(
        success=False,
        call_id="call_456",
        transcript_path="",
        duration_seconds=0,
        error_message="Call failed to connect after 60s in 'initiated' status"
    )
    
    # Create verifier with mocked orchestrators
    verifier = EmploymentVerifier(
        call_orchestrator=mock_call_orchestrator,
        email_orchestrator=mock_email_orchestrator
    )
    
    # Create mock employment record
    mock_employment = Mock(spec=Employment)
    mock_employment.id = "emp_123"
    mock_employment.company_name = "Test Company"
    mock_employment.job_title = "Software Engineer"
    mock_employment.start_date = "2020-01-01"
    mock_employment.end_date = "2022-12-31"
    mock_employment.hr_contact_info = {
        'phone': '+1234567890',
        'email': 'hr@company.com'
    }
    mock_employment.verification_status = EmploymentVerificationStatus.PENDING
    mock_employment.verification_notes = None
    
    # Mock database operations
    with patch('core.employment_verifier.safe_db_commit'):
        with patch('core.employment_verifier.safe_db_add'):
            with patch('core.employment_verifier.ContactRecord'):
                # Execute verification
                result = verifier.verify_employment(
                    employment=mock_employment,
                    hr_phone="+1234567890",
                    hr_email="hr@company.com"
                )
    
    # Verify email was sent FIRST
    assert mock_email_orchestrator.send_hr_verification_email.called, "Email should be sent"
    email_call = mock_email_orchestrator.send_hr_verification_email.call_args
    assert email_call[1]['hr_email'] == "hr@company.com"
    
    # Verify phone was attempted AFTER email
    assert mock_call_orchestrator.initiate_hr_verification.called, "Phone call should be attempted"
    
    # Verify result shows success (because email was sent)
    assert result.success == True, "Verification should succeed when email is sent"
    assert result.contact_method == "EMAIL", "Contact method should be EMAIL"
    
    print("✅ PASSED: Employment verifier sends email notification first")
    return True


def test_email_only_when_no_phone():
    """Test that email is sent even when no phone number is provided."""
    
    print("\nTesting email-only verification (no phone)...")
    
    # Create mock orchestrators
    mock_call_orchestrator = Mock()
    mock_email_orchestrator = Mock()
    
    # Mock email sending to succeed
    mock_email_orchestrator.send_reference_email.return_value = EmailResult(
        success=True,
        email_id="email_789",
        recipient="reference@example.com",
        log_path="/path/to/log",
        error_message=None
    )
    
    # Create verifier with mocked orchestrators
    verifier = ReferenceVerifier(
        call_orchestrator=mock_call_orchestrator,
        email_orchestrator=mock_email_orchestrator,
        openai_api_key="test_key"
    )
    
    # Mock database operations
    with patch('core.reference_verifier.safe_db_commit'):
        with patch('core.reference_verifier.safe_db_add'):
            with patch('core.reference_verifier.ContactRecord'):
                # Execute verification with NO phone number
                result = verifier.verify_reference(
                    verification_session_id="session_789",
                    candidate_name="John Doe",
                    reference_name="Jane Smith",
                    reference_phone=None,  # No phone!
                    reference_email="reference@example.com",
                    relationship="manager"
                )
    
    # Verify email was sent
    assert mock_email_orchestrator.send_reference_email.called, "Email should be sent"
    
    # Verify phone was NOT attempted (no phone number)
    assert not mock_call_orchestrator.initiate_reference_call.called, "Phone should not be attempted"
    
    # Verify result shows success
    assert result['success'] == True, "Verification should succeed with email only"
    assert result['contact_method'] == "email", "Contact method should be email"
    
    print("✅ PASSED: Email sent successfully when no phone number provided")
    return True


if __name__ == "__main__":
    print("=" * 70)
    print("Email Notification Tests")
    print("=" * 70)
    
    results = []
    
    # Run tests
    try:
        results.append(test_reference_verifier_sends_email_first())
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results.append(False)
    
    try:
        results.append(test_employment_verifier_sends_email_first())
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results.append(False)
    
    try:
        results.append(test_email_only_when_no_phone())
    except Exception as e:
        print(f"❌ FAILED: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 70)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 70)
    
    if all(results):
        print("\n✅ All tests passed! Emails are sent by default.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
