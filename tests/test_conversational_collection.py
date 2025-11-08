"""Test conversational document collection system"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.conversational_agent import ConversationalAgent
from src.core.consistency_validator import ConsistencyValidator, Inconsistency, EmploymentGap
from src.core.collection_session import CollectionSession, CollectionStage
from src.core.document_collection_orchestrator import DocumentCollectionOrchestrator
from src.core.document_models import CVData, EmploymentHistory, EducationEntry, EmploymentEvidence, EducationCredential
from datetime import date, datetime


def test_conversational_agent():
    """Test ConversationalAgent basic functionality"""
    print("\n=== Testing ConversationalAgent ===")
    
    # Check if API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipping ConversationalAgent tests (no API key)")
        return
    
    # Test initial greeting
    agent = ConversationalAgent()
    greeting = agent.generate_initial_greeting("John Doe")
    print(f"✓ Initial greeting: {greeting[:100]}...")
    assert "John Doe" in greeting or "Hi" in greeting
    
    # Test CV processed message
    cv_data = {
        'candidate_name': 'John Doe',
        'employment_history': [{'company_name': 'Tech Corp'}],
        'education': [{'institution_name': 'MIT'}]
    }
    message = agent.generate_cv_processed_message(cv_data)
    print(f"✓ CV processed message: {message[:100]}...")
    assert "John Doe" in message or "employment" in message.lower()
    
    # Test document request
    request = agent.generate_document_request('paystub', company_name='Tech Corp', start_date='2020-01', end_date='2022-12')
    print(f"✓ Document request: {request[:100]}...")
    assert "Tech Corp" in request
    
    # Test conflict question
    conflict = {
        'type': 'job_title_mismatch',
        'cv_value': 'Senior Developer',
        'document_value': 'Developer'
    }
    question = agent.generate_conflict_question(conflict)
    print(f"✓ Conflict question: {question[:100]}...")
    assert "Senior Developer" in question or "Developer" in question
    
    # Test gap question
    gap = {
        'start_date': '2020-01-01',
        'end_date': '2020-06-01',
        'duration_months': 5
    }
    gap_q = agent.generate_gap_question(gap)
    print(f"✓ Gap question: {gap_q[:100]}...")
    assert "gap" in gap_q.lower() or "2020" in gap_q
    
    print("✅ ConversationalAgent tests passed!")


def test_consistency_validator():
    """Test ConsistencyValidator functionality"""
    print("\n=== Testing ConsistencyValidator ===")
    
    validator = ConsistencyValidator()
    
    # Create test CV data
    cv_data = CVData(
        candidate_name="John Doe",
        employment_history=[
            EmploymentHistory(
                company_name="Tech Corp",
                job_title="Senior Developer",
                start_date=date(2020, 1, 1),
                end_date=date(2022, 12, 31)
            ),
            EmploymentHistory(
                company_name="StartupXYZ",
                job_title="Developer",
                start_date=date(2018, 6, 1),
                end_date=date(2019, 12, 31)
            )
        ],
        education=[
            EducationEntry(
                institution_name="MIT",
                degree_type="Bachelor's",
                major="Computer Science",
                graduation_date=date(2018, 5, 1)
            )
        ]
    )
    
    # Test employment validation with matching paystub
    paystubs = [
        EmploymentEvidence(
            company_name="Tech Corp",
            employee_name="John Doe",
            job_title="Senior Developer",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 12, 31)
        )
    ]
    
    inconsistencies = validator.validate_employment_dates(cv_data, paystubs)
    print(f"✓ Employment validation (matching): {len(inconsistencies)} inconsistencies")
    assert len(inconsistencies) == 0
    
    # Test with mismatched dates
    paystubs_mismatch = [
        EmploymentEvidence(
            company_name="Tech Corp",
            employee_name="John Doe",
            job_title="Developer",  # Different title
            start_date=date(2020, 2, 1),  # Different start date
            end_date=date(2022, 12, 31)
        )
    ]
    
    inconsistencies = validator.validate_employment_dates(cv_data, paystubs_mismatch)
    print(f"✓ Employment validation (mismatched): {len(inconsistencies)} inconsistencies")
    assert len(inconsistencies) > 0
    
    # Test gap detection
    gaps = validator.detect_gaps(cv_data.employment_history)
    print(f"✓ Gap detection: {len(gaps)} gaps found")
    # Should find gap between 2019-12-31 and 2020-01-01 (but it's < 3 months, so no gap)
    
    # Test education validation
    diplomas = [
        EducationCredential(
            institution_name="MIT",
            degree_type="Bachelor of Science",
            major="Computer Science",
            graduation_date=date(2018, 5, 1)
        )
    ]
    
    edu_inconsistencies = validator.validate_education(cv_data, diplomas)
    print(f"✓ Education validation: {len(edu_inconsistencies)} inconsistencies")
    
    print("✅ ConsistencyValidator tests passed!")


def test_collection_session():
    """Test CollectionSession functionality"""
    print("\n=== Testing CollectionSession ===")
    
    session = CollectionSession(
        session_id="test-123",
        verification_session_id="verify-456",
        candidate_name="John Doe"
    )
    
    # Test adding messages
    session.add_message('assistant', 'Hello!')
    session.add_message('user', 'Hi there')
    print(f"✓ Added messages: {len(session.conversation_history)} messages")
    assert len(session.conversation_history) == 2
    
    # Test adding documents
    doc = session.add_document(
        document_id="doc-1",
        document_type="cv",
        filename="resume.pdf",
        confidence_score=0.95
    )
    print(f"✓ Added document: {doc.document_type}")
    assert len(session.documents) == 1
    
    # Test conversation formatting
    conv = session.get_conversation_for_ai()
    print(f"✓ Conversation for AI: {len(conv)} messages")
    assert len(conv) == 2
    assert conv[0]['role'] == 'assistant'
    
    # Test context generation
    context = session.get_context_for_ai()
    print(f"✓ Context for AI: {list(context.keys())}")
    assert 'stage' in context
    assert 'documents_collected' in context
    
    # Test serialization
    session_dict = session.to_dict()
    print(f"✓ Session serialization: {list(session_dict.keys())}")
    assert 'session_id' in session_dict
    assert 'stage' in session_dict
    
    print("✅ CollectionSession tests passed!")


def test_document_collection_orchestrator():
    """Test DocumentCollectionOrchestrator functionality"""
    print("\n=== Testing DocumentCollectionOrchestrator ===")
    
    # Check if API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Skipping DocumentCollectionOrchestrator tests (no API key)")
        return
    
    orchestrator = DocumentCollectionOrchestrator()
    
    # Test starting a session
    session_id, initial_message = orchestrator.start_session(
        verification_session_id="verify-789",
        candidate_name="Jane Smith"
    )
    print(f"✓ Started session: {session_id}")
    print(f"  Initial message: {initial_message[:100]}...")
    assert session_id is not None
    assert "Jane Smith" in initial_message or "Hi" in initial_message
    
    # Test getting session
    session = orchestrator.get_session(session_id)
    print(f"✓ Retrieved session: {session['session_id']}")
    assert session is not None
    assert session['stage'] == 'AWAITING_CV'
    
    # Test processing a message
    result = orchestrator.process_message(session_id, "I'm ready to upload my CV")
    print(f"✓ Processed message: {result['success']}")
    assert result['success'] is True
    assert 'message' in result
    
    print("✅ DocumentCollectionOrchestrator tests passed!")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Conversational Document Collection System")
    print("=" * 60)
    
    try:
        test_conversational_agent()
        test_consistency_validator()
        test_collection_session()
        test_document_collection_orchestrator()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
