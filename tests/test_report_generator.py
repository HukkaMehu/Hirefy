"""
Test suite for Report Generation System

Tests the comprehensive report generation including:
- ReportGenerator main coordinator
- NarrativeSynthesizer for human-readable summaries
- InterviewQuestionGenerator for targeted questions
- Complete report generation workflow
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from flask import Flask
from src.database.models import (
    db, VerificationSession, Candidate, Employment, EducationCredential,
    FraudFlag, ContactRecord, GitHubAnalysisRecord, VerificationReport,
    VerificationStatus, EmploymentVerificationStatus, EducationVerificationStatus,
    FraudFlagType, FraudSeverity, RiskScore, DataSource
)
from src.core.report_generator import (
    ReportGenerator, NarrativeSynthesizer, InterviewQuestionGenerator
)


def create_test_app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    # Use absolute path for database
    db_path = os.path.abspath('data/verification_platform.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    return app


def create_test_session():
    """Create a test verification session with sample data"""
    # Create candidate
    candidate = Candidate(
        full_name="John Doe",
        email="john.doe@example.com",
        phone="+1234567890"
    )
    db.session.add(candidate)
    db.session.flush()
    
    # Create verification session
    session = VerificationSession(
        candidate_id=candidate.id,
        status=VerificationStatus.VERIFICATION_IN_PROGRESS,
        risk_score=RiskScore.YELLOW
    )
    db.session.add(session)
    db.session.flush()
    
    # Add employment records
    emp1 = Employment(
        verification_session_id=session.id,
        company_name="Tech Corp",
        job_title="Senior Software Engineer",
        start_date=date(2020, 1, 1),
        end_date=date(2023, 6, 30),
        source=DataSource.CV,
        verification_status=EmploymentVerificationStatus.VERIFIED,
        verification_notes="Verified via HR phone call"
    )
    db.session.add(emp1)
    
    emp2 = Employment(
        verification_session_id=session.id,
        company_name="Startup Inc",
        job_title="Lead Developer",
        start_date=date(2023, 7, 1),
        end_date=None,
        source=DataSource.CV,
        verification_status=EmploymentVerificationStatus.PENDING
    )
    db.session.add(emp2)
    
    # Add education credential
    edu = EducationCredential(
        verification_session_id=session.id,
        institution_name="State University",
        degree_type="Bachelor of Science",
        major="Computer Science",
        graduation_date=date(2019, 5, 15),
        source=DataSource.DIPLOMA,
        verification_status=EducationVerificationStatus.VERIFIED
    )
    db.session.add(edu)
    
    # Add fraud flags
    flag1 = FraudFlag(
        verification_session_id=session.id,
        flag_type=FraudFlagType.TIMELINE_CONFLICT,
        severity=FraudSeverity.MINOR,
        description="Gap of 3.5 months between Tech Corp and Startup Inc",
        evidence={'gap_months': 3.5}
    )
    db.session.add(flag1)
    
    # Add contact records with reference feedback
    contact1 = ContactRecord(
        verification_session_id=session.id,
        contact_type='REFERENCE',
        contact_method='PHONE',
        contact_name='Jane Smith',
        contact_info='+1987654321',
        response_received=True,
        response_timestamp=datetime.utcnow(),
        response_data={
            'themes': ['Strong technical skills', 'Good team player', 'Needs improvement in communication'],
            'quotes': [
                'John was one of the best developers on our team',
                'He consistently delivered high-quality code',
                'Sometimes struggled with explaining technical concepts to non-technical stakeholders'
            ]
        },
        transcript_url='transcripts/john_doe_reference_1.txt'
    )
    db.session.add(contact1)
    
    # Add GitHub analysis
    github = GitHubAnalysisRecord(
        verification_session_id=session.id,
        username='johndoe',
        profile_found=True,
        total_repos=25,
        owned_repos=15,
        total_commits=450,
        commit_frequency=12.5,
        languages={'Python': 10, 'JavaScript': 8, 'TypeScript': 5},
        contribution_timeline={'2023-01': 25, '2023-02': 30, '2023-03': 28},
        code_quality_score=7,
        skills_match={'matched_skills': ['Python', 'JavaScript'], 'unmatched_skills': []},
        mismatches=[],
        profile_url='https://github.com/johndoe'
    )
    db.session.add(github)
    
    db.session.commit()
    
    return session.id


def test_narrative_synthesizer():
    """Test NarrativeSynthesizer"""
    print("\n=== Testing NarrativeSynthesizer ===")
    
    app = create_test_app()
    
    with app.app_context():
        # Create test data
        session_id = create_test_session()
        session = db.session.get(VerificationSession, session_id)
        
        synthesizer = NarrativeSynthesizer()
        
        # Test employment narrative
        print("\n1. Testing employment narrative generation...")
        employment = session.employments[0]
        contact_records = [r for r in session.contact_records if r.contact_type == 'REFERENCE']
        
        narrative = synthesizer.synthesize_employment_narrative(employment, contact_records)
        print(f"Employment Narrative:\n{narrative}")
        assert len(narrative) > 0, "Employment narrative should not be empty"
        assert employment.company_name in narrative, "Narrative should mention company name"
        
        # Test technical narrative
        print("\n2. Testing technical narrative generation...")
        github_analysis = GitHubAnalysisRecord.query.filter_by(verification_session_id=session_id).first()
        claimed_skills = ['Python', 'JavaScript', 'React']
        
        tech_narrative = synthesizer.synthesize_technical_narrative(github_analysis, claimed_skills)
        print(f"Technical Narrative:\n{tech_narrative}")
        assert len(tech_narrative) > 0, "Technical narrative should not be empty"
        assert github_analysis.username in tech_narrative, "Narrative should mention GitHub username"
        
        # Test red flags summary
        print("\n3. Testing red flags summary...")
        red_flags_summary = synthesizer.synthesize_red_flags_summary(session.fraud_flags)
        print(f"Red Flags Summary:\n{red_flags_summary}")
        assert len(red_flags_summary) > 0, "Red flags summary should not be empty"
        
        print("\n✓ NarrativeSynthesizer tests passed!")


def test_interview_question_generator():
    """Test InterviewQuestionGenerator"""
    print("\n=== Testing InterviewQuestionGenerator ===")
    
    app = create_test_app()
    
    with app.app_context():
        # Create test data
        session_id = create_test_session()
        session = db.session.get(VerificationSession, session_id)
        
        generator = InterviewQuestionGenerator()
        
        print("\n1. Generating interview questions...")
        github_analysis = GitHubAnalysisRecord.query.filter_by(verification_session_id=session_id).first()
        questions = generator.generate_questions(
            employments=session.employments,
            fraud_flags=session.fraud_flags,
            contact_records=session.contact_records,
            github_analysis=github_analysis
        )
        
        print(f"\nGenerated {len(questions)} questions:")
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
        
        assert len(questions) >= 5, "Should generate at least 5 questions"
        assert len(questions) <= 10, "Should generate at most 10 questions"
        assert all(isinstance(q, str) for q in questions), "All questions should be strings"
        assert all(len(q) > 10 for q in questions), "Questions should be substantive"
        
        print("\n✓ InterviewQuestionGenerator tests passed!")


def test_report_generator():
    """Test complete ReportGenerator workflow"""
    print("\n=== Testing ReportGenerator ===")
    
    app = create_test_app()
    
    with app.app_context():
        # Create test data
        session_id = create_test_session()
        
        generator = ReportGenerator()
        
        print("\n1. Generating comprehensive report...")
        result = generator.generate_report(session_id)
        
        assert result['success'], f"Report generation should succeed: {result.get('error')}"
        assert 'report_id' in result, "Result should include report_id"
        assert 'risk_score' in result, "Result should include risk_score"
        assert 'report_data' in result, "Result should include report_data"
        
        report_data = result['report_data']
        
        print("\n2. Validating report structure...")
        required_fields = [
            'candidate_id', 'candidate_name', 'verification_session_id',
            'risk_score', 'summary', 'employment_history', 'education',
            'technical_validation', 'red_flags', 'red_flags_summary',
            'interview_questions', 'generated_at'
        ]
        
        for field in required_fields:
            assert field in report_data, f"Report should include {field}"
            print(f"✓ {field}: present")
        
        print("\n3. Validating report content...")
        
        # Check employment narratives
        assert len(report_data['employment_history']) == 2, "Should have 2 employment records"
        for emp_narrative in report_data['employment_history']:
            assert 'company' in emp_narrative
            assert 'title' in emp_narrative
            assert 'narrative' in emp_narrative
            assert 'verification_status' in emp_narrative
            print(f"✓ Employment narrative for {emp_narrative['company']}")
        
        # Check education summary
        assert len(report_data['education']) > 0, "Should have education summary"
        print(f"✓ Education summary: {report_data['education'][:100]}...")
        
        # Check technical validation
        assert report_data['technical_validation'] is not None, "Should have technical validation"
        assert report_data['technical_validation']['profile_found'], "GitHub profile should be found"
        print(f"✓ Technical validation for @{report_data['technical_validation']['github_username']}")
        
        # Check red flags
        assert len(report_data['red_flags']) > 0, "Should have red flags"
        print(f"✓ {len(report_data['red_flags'])} red flag(s) documented")
        
        # Check interview questions
        assert len(report_data['interview_questions']) >= 5, "Should have at least 5 interview questions"
        print(f"✓ {len(report_data['interview_questions'])} interview questions generated")
        
        # Check summary narrative
        assert len(report_data['summary']) > 0, "Should have summary narrative"
        print(f"✓ Summary: {report_data['summary'][:150]}...")
        
        print("\n4. Verifying database storage...")
        report = VerificationReport.query.filter_by(verification_session_id=session_id).first()
        assert report is not None, "Report should be stored in database"
        assert report.risk_score == RiskScore.YELLOW, "Risk score should match"
        assert report.summary_narrative is not None, "Summary narrative should be stored"
        assert report.employment_narratives is not None, "Employment narratives should be stored"
        assert report.interview_questions is not None, "Interview questions should be stored"
        assert report.report_data is not None, "Full report data should be stored"
        print("✓ Report successfully stored in database")
        
        print("\n5. Testing report retrieval...")
        retrieved_report = db.session.get(VerificationReport, report.id)
        assert retrieved_report is not None, "Should be able to retrieve report"
        assert retrieved_report.report_data['candidate_name'] == "John Doe"
        print("✓ Report successfully retrieved from database")
        
        print("\n✓ ReportGenerator tests passed!")
        
        # Print full report summary
        print("\n" + "="*80)
        print("GENERATED REPORT SUMMARY")
        print("="*80)
        print(f"Candidate: {report_data['candidate_name']}")
        print(f"Risk Score: {report_data['risk_score']}")
        print(f"\nSummary:\n{report_data['summary']}")
        print(f"\nRed Flags Summary:\n{report_data['red_flags_summary']}")
        print(f"\nInterview Questions:")
        for i, q in enumerate(report_data['interview_questions'][:5], 1):
            print(f"{i}. {q}")
        print("="*80)


def test_report_without_openai():
    """Test report generation without OpenAI API key (fallback mode)"""
    print("\n=== Testing Report Generation (Fallback Mode) ===")
    
    # Temporarily remove OpenAI key
    original_key = os.environ.get('OPENAI_API_KEY')
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    try:
        app = create_test_app()
        
        with app.app_context():
            # Create test data
            session_id = create_test_session()
            
            generator = ReportGenerator(openai_api_key=None)
            
            print("\n1. Generating report without OpenAI...")
            result = generator.generate_report(session_id)
            
            assert result['success'], "Report generation should succeed in fallback mode"
            assert 'report_data' in result
            
            report_data = result['report_data']
            
            # Verify all sections are still generated
            assert len(report_data['employment_history']) > 0
            assert len(report_data['interview_questions']) >= 5
            assert len(report_data['summary']) > 0
            
            print("✓ Report generated successfully in fallback mode")
            print(f"✓ Generated {len(report_data['interview_questions'])} questions")
            print(f"✓ Generated {len(report_data['employment_history'])} employment narratives")
    
    finally:
        # Restore OpenAI key
        if original_key:
            os.environ['OPENAI_API_KEY'] = original_key


if __name__ == '__main__':
    print("="*80)
    print("REPORT GENERATION SYSTEM TEST SUITE")
    print("="*80)
    
    try:
        # Run all tests
        test_narrative_synthesizer()
        test_interview_question_generator()
        test_report_generator()
        test_report_without_openai()
        
        print("\n" + "="*80)
        print("ALL TESTS PASSED! ✓")
        print("="*80)
        print("\nReport generation system is working correctly!")
        print("- NarrativeSynthesizer creates human-readable summaries")
        print("- InterviewQuestionGenerator creates targeted questions")
        print("- ReportGenerator coordinates complete report generation")
        print("- Reports are stored in database with full JSON structure")
        print("- Fallback mode works without OpenAI API key")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
