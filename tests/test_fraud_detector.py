"""
Test suite for fraud detection engine
"""

import sys
import os
from datetime import date, timedelta

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.models import (
    db, VerificationSession, Candidate, Employment, EducationCredential,
    FraudFlag, GitHubAnalysisRecord, VerificationStatus, RiskScore,
    EmploymentVerificationStatus, EducationVerificationStatus,
    DataSource, FraudFlagType, FraudSeverity
)
from src.core.fraud_detector import (
    FraudDetector, TimelineAnalyzer, ClaimValidator, RiskScorer
)
from src.api.app import create_app


def test_timeline_conflicts():
    """Test detection of overlapping employment dates"""
    print("\n=== Testing Timeline Conflict Detection ===")
    
    # Create test employments with overlap
    emp1 = Employment(
        id="emp1",
        verification_session_id="test",
        company_name="Company A",
        job_title="Developer",
        start_date=date(2020, 1, 1),
        end_date=date(2022, 6, 30),
        source=DataSource.CV,
        verification_status=EmploymentVerificationStatus.VERIFIED
    )
    
    emp2 = Employment(
        id="emp2",
        verification_session_id="test",
        company_name="Company B",
        job_title="Senior Developer",
        start_date=date(2022, 3, 1),  # Overlaps with emp1
        end_date=date(2024, 1, 1),
        source=DataSource.CV,
        verification_status=EmploymentVerificationStatus.VERIFIED
    )
    
    analyzer = TimelineAnalyzer()
    conflicts = analyzer.detect_timeline_conflicts([emp1, emp2])
    
    print(f"✓ Found {len(conflicts)} timeline conflict(s)")
    for conflict in conflicts:
        print(f"  - {conflict['description']}")
        print(f"    Overlap: {conflict['overlap_days']} days")
    
    assert len(conflicts) == 1, "Should detect one overlap"
    assert conflicts[0]['overlap_days'] == 121, "Should calculate correct overlap"
    print("✓ Timeline conflict detection working correctly")


def test_employment_gaps():
    """Test detection of employment gaps"""
    print("\n=== Testing Employment Gap Detection ===")
    
    # Create test employments with gap
    emp1 = Employment(
        id="emp1",
        verification_session_id="test",
        company_name="Company A",
        job_title="Developer",
        start_date=date(2020, 1, 1),
        end_date=date(2021, 12, 31),
        source=DataSource.CV,
        verification_status=EmploymentVerificationStatus.VERIFIED
    )
    
    emp2 = Employment(
        id="emp2",
        verification_session_id="test",
        company_name="Company B",
        job_title="Senior Developer",
        start_date=date(2022, 7, 1),  # 6 month gap
        end_date=None,
        source=DataSource.CV,
        verification_status=EmploymentVerificationStatus.VERIFIED
    )
    
    analyzer = TimelineAnalyzer()
    gaps = analyzer.detect_employment_gaps([emp1, emp2], gap_threshold_months=3)
    
    print(f"✓ Found {len(gaps)} employment gap(s)")
    for gap in gaps:
        print(f"  - {gap['description']}")
        print(f"    Gap: {gap['gap_months']} months ({gap['gap_days']} days)")
    
    assert len(gaps) == 1, "Should detect one gap"
    assert gaps[0]['gap_months'] >= 6, "Should detect 6+ month gap"
    print("✓ Employment gap detection working correctly")


def test_future_dates():
    """Test detection of future dates"""
    print("\n=== Testing Future Date Detection ===")
    
    future_date = date.today() + timedelta(days=365)
    
    emp = Employment(
        id="emp1",
        verification_session_id="test",
        company_name="Company A",
        job_title="Developer",
        start_date=future_date,  # Future date
        end_date=None,
        source=DataSource.CV,
        verification_status=EmploymentVerificationStatus.VERIFIED
    )
    
    edu = EducationCredential(
        id="edu1",
        verification_session_id="test",
        institution_name="University",
        degree_type="Bachelor",
        major="Computer Science",
        graduation_date=future_date,  # Future date
        source=DataSource.CV,
        verification_status=EducationVerificationStatus.VERIFIED
    )
    
    analyzer = TimelineAnalyzer()
    violations = analyzer.detect_future_dates([emp], [edu])
    
    print(f"✓ Found {len(violations)} future date violation(s)")
    for violation in violations:
        print(f"  - {violation['description']}")
    
    assert len(violations) == 2, "Should detect two future dates"
    print("✓ Future date detection working correctly")


def test_unverified_claims():
    """Test detection of unverified claims"""
    print("\n=== Testing Unverified Claim Detection ===")
    
    # Create unverified employment
    emp = Employment(
        id="emp1",
        verification_session_id="test",
        company_name="Company A",
        job_title="Developer",
        start_date=date(2020, 1, 1),
        end_date=date(2022, 1, 1),
        source=DataSource.CV,
        verification_status=EmploymentVerificationStatus.UNVERIFIED,
        verification_notes="HR did not respond"
    )
    
    # Create unverified education
    edu = EducationCredential(
        id="edu1",
        verification_session_id="test",
        institution_name="University",
        degree_type="Bachelor",
        major="Computer Science",
        graduation_date=date(2019, 5, 1),
        source=DataSource.CV,
        verification_status=EducationVerificationStatus.UNVERIFIED,
        verification_notes="Institution could not verify"
    )
    
    validator = ClaimValidator()
    employment_issues = validator.validate_employment_claims([emp])
    education_issues = validator.validate_education_claims([edu])
    
    print(f"✓ Found {len(employment_issues)} unverified employment(s)")
    for issue in employment_issues:
        print(f"  - {issue['description']}")
    
    print(f"✓ Found {len(education_issues)} unverified education credential(s)")
    for issue in education_issues:
        print(f"  - {issue['description']}")
    
    assert len(employment_issues) == 1, "Should detect unverified employment"
    assert len(education_issues) == 1, "Should detect unverified education"
    print("✓ Unverified claim detection working correctly")


def test_risk_scoring():
    """Test risk score calculation"""
    print("\n=== Testing Risk Score Calculation ===")
    
    scorer = RiskScorer()
    
    # Test GREEN (no flags)
    risk = scorer.calculate_risk_score([])
    print(f"✓ No flags → {risk.value}")
    assert risk == RiskScore.GREEN
    
    # Test YELLOW (1 minor flag)
    minor_flag = FraudFlag(
        verification_session_id="test",
        flag_type=FraudFlagType.TIMELINE_CONFLICT,
        severity=FraudSeverity.MINOR,
        description="Small gap in employment"
    )
    risk = scorer.calculate_risk_score([minor_flag])
    print(f"✓ 1 minor flag → {risk.value}")
    assert risk == RiskScore.YELLOW
    
    # Test YELLOW (1 moderate flag)
    moderate_flag = FraudFlag(
        verification_session_id="test",
        flag_type=FraudFlagType.TECHNICAL_MISMATCH,
        severity=FraudSeverity.MODERATE,
        description="Some skills not verified"
    )
    risk = scorer.calculate_risk_score([moderate_flag])
    print(f"✓ 1 moderate flag → {risk.value}")
    assert risk == RiskScore.YELLOW
    
    # Test RED (1 critical flag)
    critical_flag = FraudFlag(
        verification_session_id="test",
        flag_type=FraudFlagType.UNVERIFIED_CREDENTIAL,
        severity=FraudSeverity.CRITICAL,
        description="Employment could not be verified"
    )
    risk = scorer.calculate_risk_score([critical_flag])
    print(f"✓ 1 critical flag → {risk.value}")
    assert risk == RiskScore.RED
    
    # Test RED (2 moderate flags)
    risk = scorer.calculate_risk_score([moderate_flag, moderate_flag])
    print(f"✓ 2 moderate flags → {risk.value}")
    assert risk == RiskScore.RED
    
    print("✓ Risk scoring working correctly")


def test_full_fraud_analysis():
    """Test complete fraud analysis on a verification session"""
    print("\n=== Testing Full Fraud Analysis ===")
    
    app = create_app()
    
    with app.app_context():
        # Create test candidate
        candidate = Candidate(
            full_name="Test Candidate",
            email="test@example.com"
        )
        db.session.add(candidate)
        db.session.flush()
        
        # Create verification session
        session = VerificationSession(
            candidate_id=candidate.id,
            status=VerificationStatus.VERIFICATION_IN_PROGRESS
        )
        db.session.add(session)
        db.session.flush()
        
        # Add overlapping employments
        emp1 = Employment(
            verification_session_id=session.id,
            company_name="Company A",
            job_title="Developer",
            start_date=date(2020, 1, 1),
            end_date=date(2022, 6, 30),
            source=DataSource.CV,
            verification_status=EmploymentVerificationStatus.VERIFIED
        )
        db.session.add(emp1)
        
        emp2 = Employment(
            verification_session_id=session.id,
            company_name="Company B",
            job_title="Senior Developer",
            start_date=date(2022, 3, 1),  # Overlaps
            end_date=None,
            source=DataSource.CV,
            verification_status=EmploymentVerificationStatus.UNVERIFIED
        )
        db.session.add(emp2)
        
        # Add unverified education
        edu = EducationCredential(
            verification_session_id=session.id,
            institution_name="Test University",
            degree_type="Bachelor",
            major="Computer Science",
            graduation_date=date(2019, 5, 1),
            source=DataSource.CV,
            verification_status=EducationVerificationStatus.UNVERIFIED
        )
        db.session.add(edu)
        
        db.session.commit()
        
        # Run fraud detection
        detector = FraudDetector()
        result = detector.analyze_session(session.id)
        
        print(f"\n✓ Fraud Analysis Results:")
        print(f"  - Risk Score: {result['risk_score']}")
        print(f"  - Total Flags: {result['total_flags']}")
        print(f"  - Critical: {result['risk_summary']['critical_count']}")
        print(f"  - Moderate: {result['risk_summary']['moderate_count']}")
        print(f"  - Minor: {result['risk_summary']['minor_count']}")
        
        print(f"\n  Fraud Flags:")
        for flag in result['fraud_flags']:
            print(f"    - [{flag['severity']}] {flag['type']}: {flag['description']}")
        
        assert result['success'], "Analysis should succeed"
        assert result['total_flags'] > 0, "Should detect fraud flags"
        assert result['risk_score'] == 'RED', "Should be RED risk with critical flags"
        
        # Verify session risk score was updated
        db.session.refresh(session)
        assert session.risk_score == RiskScore.RED
        
        print("\n✓ Full fraud analysis working correctly")
        
        # Cleanup
        db.session.delete(session)
        db.session.delete(candidate)
        db.session.commit()


if __name__ == "__main__":
    print("=" * 60)
    print("FRAUD DETECTION ENGINE TEST SUITE")
    print("=" * 60)
    
    try:
        # Run unit tests
        test_timeline_conflicts()
        test_employment_gaps()
        test_future_dates()
        test_unverified_claims()
        test_risk_scoring()
        
        # Run integration test
        test_full_fraud_analysis()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
