"""
Fraud Detection Engine for AI Recruitment Verification Platform

This module implements comprehensive fraud detection including:
- Timeline analysis for impossible date overlaps and suspicious gaps
- Claim validation against verification results
- Technical profile mismatch detection
- Risk scoring and color determination (Green/Yellow/Red)
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Tuple
from collections import defaultdict

from src.database.models import (
    db, VerificationSession, Employment, EducationCredential, FraudFlag,
    FraudFlagType, FraudSeverity, RiskScore, EmploymentVerificationStatus,
    EducationVerificationStatus, GitHubAnalysisRecord
)

logger = logging.getLogger(__name__)


class TimelineAnalyzer:
    """Analyzes employment and education timelines for conflicts and gaps"""
    
    @staticmethod
    def detect_timeline_conflicts(employments: List[Employment]) -> List[Dict[str, Any]]:
        """
        Detect impossible date overlaps in employment history
        
        Args:
            employments: List of Employment records
            
        Returns:
            List of conflict dictionaries with details
        """
        conflicts = []
        
        # Sort employments by start date
        sorted_employments = sorted(employments, key=lambda e: e.start_date)
        
        for i in range(len(sorted_employments)):
            for j in range(i + 1, len(sorted_employments)):
                emp1 = sorted_employments[i]
                emp2 = sorted_employments[j]
                
                # Skip if emp1 has no end date (current job)
                if not emp1.end_date:
                    continue
                
                # Check for overlap
                if emp1.end_date > emp2.start_date:
                    overlap_days = (emp1.end_date - emp2.start_date).days
                    
                    conflicts.append({
                        'type': 'overlap',
                        'employment1': {
                            'id': emp1.id,
                            'company': emp1.company_name,
                            'title': emp1.job_title,
                            'start_date': emp1.start_date.isoformat(),
                            'end_date': emp1.end_date.isoformat()
                        },
                        'employment2': {
                            'id': emp2.id,
                            'company': emp2.company_name,
                            'title': emp2.job_title,
                            'start_date': emp2.start_date.isoformat(),
                            'end_date': emp2.end_date.isoformat() if emp2.end_date else None
                        },
                        'overlap_days': overlap_days,
                        'description': f"Employment at {emp1.company_name} overlaps with {emp2.company_name} by {overlap_days} days"
                    })
        
        return conflicts
    
    @staticmethod
    def detect_employment_gaps(employments: List[Employment], gap_threshold_months: int = 3) -> List[Dict[str, Any]]:
        """
        Detect suspicious gaps in employment history
        
        Args:
            employments: List of Employment records
            gap_threshold_months: Minimum gap in months to flag (default: 3)
            
        Returns:
            List of gap dictionaries with details
        """
        gaps = []
        
        # Sort employments by start date
        sorted_employments = sorted(employments, key=lambda e: e.start_date)
        
        for i in range(len(sorted_employments) - 1):
            current_emp = sorted_employments[i]
            next_emp = sorted_employments[i + 1]
            
            # Skip if current employment has no end date
            if not current_emp.end_date:
                continue
            
            # Calculate gap
            gap_days = (next_emp.start_date - current_emp.end_date).days
            gap_months = gap_days / 30.0
            
            if gap_months >= gap_threshold_months:
                gaps.append({
                    'type': 'gap',
                    'previous_employment': {
                        'company': current_emp.company_name,
                        'end_date': current_emp.end_date.isoformat()
                    },
                    'next_employment': {
                        'company': next_emp.company_name,
                        'start_date': next_emp.start_date.isoformat()
                    },
                    'gap_days': gap_days,
                    'gap_months': round(gap_months, 1),
                    'description': f"Gap of {round(gap_months, 1)} months between {current_emp.company_name} and {next_emp.company_name}"
                })
        
        return gaps
    
    @staticmethod
    def detect_future_dates(employments: List[Employment], education: List[EducationCredential]) -> List[Dict[str, Any]]:
        """
        Detect dates in the future (impossible)
        
        Args:
            employments: List of Employment records
            education: List of EducationCredential records
            
        Returns:
            List of future date violations
        """
        violations = []
        today = date.today()
        
        # Check employment dates
        for emp in employments:
            if emp.start_date > today:
                violations.append({
                    'type': 'future_date',
                    'category': 'employment',
                    'company': emp.company_name,
                    'date': emp.start_date.isoformat(),
                    'description': f"Employment start date at {emp.company_name} is in the future"
                })
            
            if emp.end_date and emp.end_date > today:
                violations.append({
                    'type': 'future_date',
                    'category': 'employment',
                    'company': emp.company_name,
                    'date': emp.end_date.isoformat(),
                    'description': f"Employment end date at {emp.company_name} is in the future"
                })
        
        # Check education dates
        for edu in education:
            if edu.graduation_date > today:
                violations.append({
                    'type': 'future_date',
                    'category': 'education',
                    'institution': edu.institution_name,
                    'date': edu.graduation_date.isoformat(),
                    'description': f"Graduation date from {edu.institution_name} is in the future"
                })
        
        return violations


class ClaimValidator:
    """Validates claims against verification results"""
    
    @staticmethod
    def validate_employment_claims(employments: List[Employment]) -> List[Dict[str, Any]]:
        """
        Validate employment claims against verification status
        
        Args:
            employments: List of Employment records
            
        Returns:
            List of unverified or conflicted employment claims
        """
        issues = []
        
        for emp in employments:
            if emp.verification_status == EmploymentVerificationStatus.UNVERIFIED:
                issues.append({
                    'type': 'unverified_employment',
                    'severity': 'critical',
                    'company': emp.company_name,
                    'title': emp.job_title,
                    'dates': f"{emp.start_date.isoformat()} to {emp.end_date.isoformat() if emp.end_date else 'Present'}",
                    'description': f"Employment at {emp.company_name} could not be verified",
                    'evidence': {
                        'employment_id': emp.id,
                        'verification_status': emp.verification_status.value,
                        'notes': emp.verification_notes
                    }
                })
            
            elif emp.verification_status == EmploymentVerificationStatus.CONFLICTED:
                issues.append({
                    'type': 'conflicted_employment',
                    'severity': 'critical',
                    'company': emp.company_name,
                    'title': emp.job_title,
                    'dates': f"{emp.start_date.isoformat()} to {emp.end_date.isoformat() if emp.end_date else 'Present'}",
                    'description': f"Employment verification at {emp.company_name} shows conflicting information",
                    'evidence': {
                        'employment_id': emp.id,
                        'verification_status': emp.verification_status.value,
                        'notes': emp.verification_notes
                    }
                })
        
        return issues
    
    @staticmethod
    def validate_education_claims(education: List[EducationCredential]) -> List[Dict[str, Any]]:
        """
        Validate education claims against verification status
        
        Args:
            education: List of EducationCredential records
            
        Returns:
            List of unverified education claims
        """
        issues = []
        
        for edu in education:
            if edu.verification_status == EducationVerificationStatus.UNVERIFIED:
                issues.append({
                    'type': 'unverified_education',
                    'severity': 'critical',
                    'institution': edu.institution_name,
                    'degree': f"{edu.degree_type} in {edu.major}" if edu.major else edu.degree_type,
                    'graduation_date': edu.graduation_date.isoformat(),
                    'description': f"Degree from {edu.institution_name} could not be verified",
                    'evidence': {
                        'education_id': edu.id,
                        'verification_status': edu.verification_status.value,
                        'notes': edu.verification_notes
                    }
                })
        
        return issues
    
    @staticmethod
    def validate_technical_claims(
        github_analysis: Optional[GitHubAnalysisRecord],
        claimed_skills: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Validate technical claims against GitHub activity
        
        Args:
            github_analysis: GitHubAnalysisRecord or None
            claimed_skills: List of claimed technical skills
            
        Returns:
            List of technical mismatches
        """
        issues = []
        
        if not github_analysis:
            if claimed_skills:
                issues.append({
                    'type': 'no_technical_profile',
                    'severity': 'moderate',
                    'description': "No GitHub profile found to verify technical claims",
                    'evidence': {
                        'claimed_skills': claimed_skills
                    }
                })
            return issues
        
        if not github_analysis.profile_found:
            if claimed_skills:
                issues.append({
                    'type': 'profile_not_found',
                    'severity': 'moderate',
                    'description': f"GitHub profile '{github_analysis.username}' not found",
                    'evidence': {
                        'username': github_analysis.username,
                        'claimed_skills': claimed_skills
                    }
                })
            return issues
        
        # Check for skill mismatches
        if github_analysis.mismatches:
            for mismatch in github_analysis.mismatches:
                issues.append({
                    'type': 'technical_mismatch',
                    'severity': 'moderate',
                    'description': mismatch,
                    'evidence': {
                        'username': github_analysis.username,
                        'skills_match': github_analysis.skills_match,
                        'code_quality_score': github_analysis.code_quality_score
                    }
                })
        
        # Check for low code quality score
        if github_analysis.code_quality_score < 4:
            issues.append({
                'type': 'low_code_quality',
                'severity': 'minor',
                'description': f"Low code quality score: {github_analysis.code_quality_score}/10",
                'evidence': {
                    'username': github_analysis.username,
                    'code_quality_score': github_analysis.code_quality_score,
                    'total_repos': github_analysis.total_repos,
                    'owned_repos': github_analysis.owned_repos
                }
            })
        
        # Check for minimal activity
        if github_analysis.total_commits < 10:
            issues.append({
                'type': 'minimal_activity',
                'severity': 'minor',
                'description': f"Minimal GitHub activity: only {github_analysis.total_commits} commits found",
                'evidence': {
                    'username': github_analysis.username,
                    'total_commits': github_analysis.total_commits,
                    'commit_frequency': github_analysis.commit_frequency
                }
            })
        
        return issues


class RiskScorer:
    """Calculates overall risk score and determines color (Green/Yellow/Red)"""
    
    @staticmethod
    def calculate_risk_score(fraud_flags: List[FraudFlag]) -> RiskScore:
        """
        Calculate risk score based on fraud flags
        
        Scoring logic:
        - Any CRITICAL flag → RED
        - 2+ MODERATE flags → RED
        - 1 MODERATE flag or 3+ MINOR flags → YELLOW
        - Only MINOR flags (1-2) → YELLOW
        - No flags → GREEN
        
        Args:
            fraud_flags: List of FraudFlag records
            
        Returns:
            RiskScore enum (GREEN, YELLOW, or RED)
        """
        if not fraud_flags:
            return RiskScore.GREEN
        
        # Count flags by severity
        critical_count = sum(1 for flag in fraud_flags if flag.severity == FraudSeverity.CRITICAL)
        moderate_count = sum(1 for flag in fraud_flags if flag.severity == FraudSeverity.MODERATE)
        minor_count = sum(1 for flag in fraud_flags if flag.severity == FraudSeverity.MINOR)
        
        # Apply scoring logic
        if critical_count > 0:
            return RiskScore.RED
        
        if moderate_count >= 2:
            return RiskScore.RED
        
        if moderate_count == 1 or minor_count >= 3:
            return RiskScore.YELLOW
        
        if minor_count > 0:
            return RiskScore.YELLOW
        
        return RiskScore.GREEN
    
    @staticmethod
    def get_risk_summary(fraud_flags: List[FraudFlag]) -> Dict[str, Any]:
        """
        Get detailed risk summary
        
        Args:
            fraud_flags: List of FraudFlag records
            
        Returns:
            Dictionary with risk summary details
        """
        critical_flags = [f for f in fraud_flags if f.severity == FraudSeverity.CRITICAL]
        moderate_flags = [f for f in fraud_flags if f.severity == FraudSeverity.MODERATE]
        minor_flags = [f for f in fraud_flags if f.severity == FraudSeverity.MINOR]
        
        # Group by type
        flags_by_type = defaultdict(list)
        for flag in fraud_flags:
            flags_by_type[flag.flag_type.value].append(flag)
        
        return {
            'total_flags': len(fraud_flags),
            'critical_count': len(critical_flags),
            'moderate_count': len(moderate_flags),
            'minor_count': len(minor_flags),
            'flags_by_type': {
                flag_type: len(flags) for flag_type, flags in flags_by_type.items()
            },
            'critical_issues': [
                {
                    'type': f.flag_type.value,
                    'description': f.description
                }
                for f in critical_flags
            ],
            'moderate_issues': [
                {
                    'type': f.flag_type.value,
                    'description': f.description
                }
                for f in moderate_flags
            ]
        }


class FraudDetector:
    """Main fraud detection coordinator"""
    
    def __init__(self):
        """Initialize FraudDetector"""
        self.timeline_analyzer = TimelineAnalyzer()
        self.claim_validator = ClaimValidator()
        self.risk_scorer = RiskScorer()
        logger.info("FraudDetector initialized")
    
    def analyze_session(self, verification_session_id: str) -> Dict[str, Any]:
        """
        Perform comprehensive fraud analysis on a verification session
        
        Args:
            verification_session_id: ID of the verification session
            
        Returns:
            Dictionary with analysis results including fraud flags and risk score
        """
        logger.info(f"Starting fraud analysis for session {verification_session_id}")
        
        # Load verification session
        session = db.session.get(VerificationSession, verification_session_id)
        if not session:
            logger.error(f"Verification session {verification_session_id} not found")
            return {
                'success': False,
                'error': 'Verification session not found'
            }
        
        # Clear existing fraud flags for this session
        FraudFlag.query.filter_by(verification_session_id=verification_session_id).delete()
        db.session.commit()
        
        # Run all fraud detection checks
        fraud_flags_created = []
        
        # 1. Timeline analysis
        timeline_flags = self._detect_timeline_fraud(session)
        fraud_flags_created.extend(timeline_flags)
        
        # 2. Credential validation
        credential_flags = self._detect_credential_fraud(session)
        fraud_flags_created.extend(credential_flags)
        
        # 3. Technical profile validation
        technical_flags = self._detect_technical_fraud(session)
        fraud_flags_created.extend(technical_flags)
        
        # Calculate risk score
        all_flags = FraudFlag.query.filter_by(verification_session_id=verification_session_id).all()
        risk_score = self.risk_scorer.calculate_risk_score(all_flags)
        risk_summary = self.risk_scorer.get_risk_summary(all_flags)
        
        # Update session risk score
        session.risk_score = risk_score
        db.session.commit()
        
        logger.info(
            f"Fraud analysis completed for session {verification_session_id}. "
            f"Risk Score: {risk_score.value}, Flags: {len(all_flags)}"
        )
        
        return {
            'success': True,
            'verification_session_id': verification_session_id,
            'risk_score': risk_score.value,
            'total_flags': len(all_flags),
            'flags_created': len(fraud_flags_created),
            'risk_summary': risk_summary,
            'fraud_flags': [
                {
                    'id': flag.id,
                    'type': flag.flag_type.value,
                    'severity': flag.severity.value,
                    'description': flag.description,
                    'evidence': flag.evidence
                }
                for flag in all_flags
            ]
        }
    
    def _detect_timeline_fraud(self, session: VerificationSession) -> List[FraudFlag]:
        """Detect timeline-related fraud"""
        flags = []
        
        # Check for overlapping employment
        conflicts = self.timeline_analyzer.detect_timeline_conflicts(session.employments)
        for conflict in conflicts:
            flag = FraudFlag(
                verification_session_id=session.id,
                flag_type=FraudFlagType.TIMELINE_CONFLICT,
                severity=FraudSeverity.CRITICAL,
                description=conflict['description'],
                evidence=conflict
            )
            db.session.add(flag)
            flags.append(flag)
        
        # Check for suspicious gaps
        gaps = self.timeline_analyzer.detect_employment_gaps(session.employments)
        for gap in gaps:
            flag = FraudFlag(
                verification_session_id=session.id,
                flag_type=FraudFlagType.TIMELINE_CONFLICT,
                severity=FraudSeverity.MINOR,
                description=gap['description'],
                evidence=gap
            )
            db.session.add(flag)
            flags.append(flag)
        
        # Check for future dates
        future_dates = self.timeline_analyzer.detect_future_dates(
            session.employments,
            session.education_credentials
        )
        for violation in future_dates:
            flag = FraudFlag(
                verification_session_id=session.id,
                flag_type=FraudFlagType.TIMELINE_CONFLICT,
                severity=FraudSeverity.CRITICAL,
                description=violation['description'],
                evidence=violation
            )
            db.session.add(flag)
            flags.append(flag)
        
        db.session.commit()
        return flags
    
    def _detect_credential_fraud(self, session: VerificationSession) -> List[FraudFlag]:
        """Detect credential-related fraud"""
        flags = []
        
        # Validate employment claims
        employment_issues = self.claim_validator.validate_employment_claims(session.employments)
        for issue in employment_issues:
            severity = FraudSeverity.CRITICAL if issue['severity'] == 'critical' else FraudSeverity.MODERATE
            flag = FraudFlag(
                verification_session_id=session.id,
                flag_type=FraudFlagType.UNVERIFIED_CREDENTIAL,
                severity=severity,
                description=issue['description'],
                evidence=issue['evidence']
            )
            db.session.add(flag)
            flags.append(flag)
        
        # Validate education claims
        education_issues = self.claim_validator.validate_education_claims(session.education_credentials)
        for issue in education_issues:
            flag = FraudFlag(
                verification_session_id=session.id,
                flag_type=FraudFlagType.UNVERIFIED_CREDENTIAL,
                severity=FraudSeverity.CRITICAL,
                description=issue['description'],
                evidence=issue['evidence']
            )
            db.session.add(flag)
            flags.append(flag)
        
        db.session.commit()
        return flags
    
    def _detect_technical_fraud(self, session: VerificationSession) -> List[FraudFlag]:
        """Detect technical profile fraud"""
        flags = []
        
        # Get GitHub analysis if available
        github_analysis = GitHubAnalysisRecord.query.filter_by(
            verification_session_id=session.id
        ).first()
        
        # Extract claimed skills from employments (simplified for MVP)
        claimed_skills = []
        for emp in session.employments:
            # In production, would extract from CV or structured data
            # For now, just check if GitHub analysis exists
            pass
        
        # Validate technical claims
        technical_issues = self.claim_validator.validate_technical_claims(
            github_analysis,
            claimed_skills
        )
        
        for issue in technical_issues:
            severity_map = {
                'critical': FraudSeverity.CRITICAL,
                'moderate': FraudSeverity.MODERATE,
                'minor': FraudSeverity.MINOR
            }
            severity = severity_map.get(issue['severity'], FraudSeverity.MODERATE)
            
            flag = FraudFlag(
                verification_session_id=session.id,
                flag_type=FraudFlagType.TECHNICAL_MISMATCH,
                severity=severity,
                description=issue['description'],
                evidence=issue.get('evidence', {})
            )
            db.session.add(flag)
            flags.append(flag)
        
        db.session.commit()
        return flags
