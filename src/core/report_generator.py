"""
Comprehensive Report Generation System for AI Recruitment Verification Platform

This module synthesizes all verification data into comprehensive reports including:
- Risk-scored summaries
- Employment narratives with verification status and reference quotes
- Technical validation narratives with GitHub analysis
- Red flags summary with severity indicators
- Targeted interview questions based on findings
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from src.database.models import (
    db, VerificationSession, VerificationReport, Employment, EducationCredential,
    FraudFlag, ContactRecord, GitHubAnalysisRecord, RiskScore,
    EmploymentVerificationStatus, EducationVerificationStatus
)

logger = logging.getLogger(__name__)


class NarrativeSynthesizer:
    """Uses GPT-4 to create human-readable summaries from verification data"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize NarrativeSynthesizer with OpenAI API key"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            logger.warning("OpenAI API key not provided - narrative synthesis will be limited")
    
    def synthesize_employment_narrative(
        self,
        employment: Employment,
        contact_records: List[ContactRecord]
    ) -> str:
        """
        Generate narrative for a single employment period
        
        Args:
            employment: Employment record
            contact_records: List of contact records for this employment
            
        Returns:
            Human-readable narrative string
        """
        # Extract reference quotes from contact records
        reference_quotes = []
        for record in contact_records:
            if record.contact_type == 'REFERENCE' and record.response_received:
                if record.response_data and 'quotes' in record.response_data:
                    reference_quotes.extend(record.response_data['quotes'])
        
        # Build context for GPT-4
        context = {
            'company': employment.company_name,
            'title': employment.job_title,
            'start_date': employment.start_date.strftime('%B %Y'),
            'end_date': employment.end_date.strftime('%B %Y') if employment.end_date else 'Present',
            'verification_status': employment.verification_status.value,
            'verification_notes': employment.verification_notes or '',
            'reference_quotes': reference_quotes
        }
        
        if not self.openai_api_key:
            # Fallback to template-based narrative
            return self._template_employment_narrative(context)
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""Create a concise, professional narrative for this employment period:

Company: {context['company']}
Title: {context['title']}
Period: {context['start_date']} to {context['end_date']}
Verification Status: {context['verification_status']}
Notes: {context['verification_notes']}

Reference Quotes:
{chr(10).join(f'- "{quote}"' for quote in reference_quotes) if reference_quotes else 'No reference quotes available'}

Write a 2-3 sentence narrative that:
1. States the verification status clearly
2. Incorporates relevant reference quotes if available
3. Highlights any concerns or positive findings
4. Uses professional, objective language

Do not use JSON format. Write plain text only."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at writing professional employment verification narratives for hiring reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            narrative = response.choices[0].message.content.strip()
            return narrative
            
        except Exception as e:
            logger.error(f"Failed to synthesize employment narrative: {str(e)}", exc_info=True)
            return self._template_employment_narrative(context)
    
    def _template_employment_narrative(self, context: Dict[str, Any]) -> str:
        """Fallback template-based employment narrative"""
        status = context['verification_status']
        
        if status == 'VERIFIED':
            narrative = f"Employment at {context['company']} as {context['title']} from {context['start_date']} to {context['end_date']} has been verified."
        elif status == 'UNVERIFIED':
            narrative = f"Employment at {context['company']} as {context['title']} from {context['start_date']} to {context['end_date']} could not be verified."
        elif status == 'CONFLICTED':
            narrative = f"Employment at {context['company']} as {context['title']} from {context['start_date']} to {context['end_date']} shows conflicting information."
        else:
            narrative = f"Employment at {context['company']} as {context['title']} from {context['start_date']} to {context['end_date']} is pending verification."
        
        if context['reference_quotes']:
            narrative += f" References provided feedback: \"{context['reference_quotes'][0]}\""
        
        return narrative
    
    def synthesize_technical_narrative(
        self,
        github_analysis: Optional[GitHubAnalysisRecord],
        claimed_skills: List[str]
    ) -> str:
        """
        Generate narrative for technical profile validation
        
        Args:
            github_analysis: GitHubAnalysisRecord or None
            claimed_skills: List of claimed technical skills
            
        Returns:
            Human-readable narrative string
        """
        if not github_analysis or not github_analysis.profile_found:
            return "No GitHub profile found to validate technical claims."
        
        context = {
            'username': github_analysis.username,
            'total_repos': github_analysis.total_repos,
            'owned_repos': github_analysis.owned_repos,
            'total_commits': github_analysis.total_commits,
            'commit_frequency': github_analysis.commit_frequency,
            'languages': list(github_analysis.languages.keys()) if github_analysis.languages else [],
            'code_quality_score': github_analysis.code_quality_score,
            'skills_match': github_analysis.skills_match or {},
            'claimed_skills': claimed_skills
        }
        
        if not self.openai_api_key:
            return self._template_technical_narrative(context)
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            prompt = f"""Create a concise technical validation narrative:

GitHub Username: {context['username']}
Repositories: {context['total_repos']} total, {context['owned_repos']} owned
Commits: {context['total_commits']} total ({context['commit_frequency']} per month)
Languages: {', '.join(context['languages'])}
Code Quality Score: {context['code_quality_score']}/10
Claimed Skills: {', '.join(claimed_skills) if claimed_skills else 'Not specified'}

Write a 2-3 sentence narrative that:
1. Summarizes the GitHub activity level
2. Compares claimed skills against actual code contributions
3. Mentions the code quality assessment
4. Uses professional, objective language

Do not use JSON format. Write plain text only."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing technical profiles and writing professional assessment narratives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            narrative = response.choices[0].message.content.strip()
            return narrative
            
        except Exception as e:
            logger.error(f"Failed to synthesize technical narrative: {str(e)}", exc_info=True)
            return self._template_technical_narrative(context)
    
    def _template_technical_narrative(self, context: Dict[str, Any]) -> str:
        """Fallback template-based technical narrative"""
        narrative = f"GitHub profile @{context['username']} shows {context['total_commits']} commits across {context['owned_repos']} owned repositories"
        
        if context['languages']:
            narrative += f", primarily using {', '.join(context['languages'][:3])}"
        
        narrative += f". Code quality score: {context['code_quality_score']}/10."
        
        if context['commit_frequency'] < 1:
            narrative += " Activity level is minimal."
        elif context['commit_frequency'] < 5:
            narrative += " Activity level is moderate."
        else:
            narrative += " Activity level is strong."
        
        return narrative
    
    def synthesize_red_flags_summary(self, fraud_flags: List[FraudFlag]) -> str:
        """
        Generate summary of red flags
        
        Args:
            fraud_flags: List of FraudFlag records
            
        Returns:
            Human-readable summary string
        """
        if not fraud_flags:
            return "No red flags identified during verification."
        
        # Group by severity
        critical = [f for f in fraud_flags if f.severity.value == 'CRITICAL']
        moderate = [f for f in fraud_flags if f.severity.value == 'MODERATE']
        minor = [f for f in fraud_flags if f.severity.value == 'MINOR']
        
        summary_parts = []
        
        if critical:
            summary_parts.append(f"{len(critical)} critical issue(s)")
        if moderate:
            summary_parts.append(f"{len(moderate)} moderate concern(s)")
        if minor:
            summary_parts.append(f"{len(minor)} minor flag(s)")
        
        summary = f"Identified {', '.join(summary_parts)} during verification."
        
        # Add top issues
        if critical:
            summary += f" Critical: {critical[0].description}"
        elif moderate:
            summary += f" Primary concern: {moderate[0].description}"
        
        return summary


class InterviewQuestionGenerator:
    """Generates targeted interview questions based on verification findings"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize InterviewQuestionGenerator with OpenAI API key"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            logger.warning("OpenAI API key not provided - question generation will be limited")
    
    def generate_questions(
        self,
        employments: List[Employment],
        fraud_flags: List[FraudFlag],
        contact_records: List[ContactRecord],
        github_analysis: Optional[GitHubAnalysisRecord]
    ) -> List[str]:
        """
        Generate 5-10 targeted interview questions based on findings
        
        Args:
            employments: List of Employment records
            fraud_flags: List of FraudFlag records
            contact_records: List of ContactRecord records
            github_analysis: Optional GitHubAnalysisRecord
            
        Returns:
            List of interview question strings
        """
        if not self.openai_api_key:
            return self._template_questions(employments, fraud_flags)
        
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            
            # Build context
            employment_summary = []
            for emp in employments:
                employment_summary.append({
                    'company': emp.company_name,
                    'title': emp.job_title,
                    'status': emp.verification_status.value
                })
            
            flag_summary = [
                {
                    'type': flag.flag_type.value,
                    'severity': flag.severity.value,
                    'description': flag.description
                }
                for flag in fraud_flags
            ]
            
            # Extract reference themes
            reference_themes = []
            for record in contact_records:
                if record.contact_type == 'REFERENCE' and record.response_data:
                    themes = record.response_data.get('themes', [])
                    reference_themes.extend(themes)
            
            github_summary = None
            if github_analysis and github_analysis.profile_found:
                github_summary = {
                    'code_quality_score': github_analysis.code_quality_score,
                    'total_commits': github_analysis.total_commits,
                    'mismatches': github_analysis.mismatches or []
                }
            
            prompt = f"""Generate 5-10 targeted interview questions for a candidate based on verification findings.

Employment History:
{json.dumps(employment_summary, indent=2)}

Red Flags:
{json.dumps(flag_summary, indent=2) if flag_summary else 'None'}

Reference Themes:
{json.dumps(reference_themes, indent=2) if reference_themes else 'None'}

GitHub Analysis:
{json.dumps(github_summary, indent=2) if github_summary else 'Not available'}

Generate questions that:
1. Probe any red flags or concerns
2. Follow up on reference feedback themes
3. Validate technical claims if applicable
4. Explore employment gaps or transitions
5. Are open-ended and behavioral
6. Are professional and non-accusatory

Respond in JSON format:
{{
    "questions": ["question1", "question2", ...]
}}

Generate 5-10 questions total."""

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert at creating behavioral interview questions based on background verification findings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            questions = result.get('questions', [])
            
            # Ensure we have 5-10 questions
            if len(questions) < 5:
                questions.extend(self._template_questions(employments, fraud_flags))
                questions = questions[:10]
            
            return questions[:10]
            
        except Exception as e:
            logger.error(f"Failed to generate interview questions: {str(e)}", exc_info=True)
            return self._template_questions(employments, fraud_flags)
    
    def _template_questions(
        self,
        employments: List[Employment],
        fraud_flags: List[FraudFlag]
    ) -> List[str]:
        """Fallback template-based questions"""
        questions = []
        
        # Questions about unverified employment
        unverified = [e for e in employments if e.verification_status == EmploymentVerificationStatus.UNVERIFIED]
        for emp in unverified[:2]:
            questions.append(
                f"Can you tell me more about your role at {emp.company_name} and why we might have had difficulty verifying your employment there?"
            )
        
        # Questions about fraud flags
        for flag in fraud_flags[:3]:
            if flag.flag_type.value == 'TIMELINE_CONFLICT':
                questions.append("Can you walk me through your employment timeline and explain any overlapping positions?")
            elif flag.flag_type.value == 'TECHNICAL_MISMATCH':
                questions.append("Can you describe some specific projects where you used the technical skills listed on your resume?")
            elif flag.flag_type.value == 'UNVERIFIED_CREDENTIAL':
                questions.append("Can you provide more details about your educational background and how it prepared you for this role?")
        
        # Generic behavioral questions
        questions.extend([
            "Tell me about a challenging project you worked on and how you overcame obstacles.",
            "Describe your collaboration style and how you work with team members.",
            "What are your greatest strengths and areas for improvement?",
            "Why are you interested in this position and what do you hope to achieve?"
        ])
        
        return questions[:10]


class ReportGenerator:
    """Main coordinator for generating comprehensive verification reports"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize ReportGenerator"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.narrative_synthesizer = NarrativeSynthesizer(self.openai_api_key)
        self.question_generator = InterviewQuestionGenerator(self.openai_api_key)
        
        logger.info("ReportGenerator initialized")
    
    def generate_report(self, verification_session_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive verification report
        
        Args:
            verification_session_id: ID of the verification session
            
        Returns:
            Dictionary with report generation results
        """
        logger.info(f"Starting report generation for session {verification_session_id}")
        
        # Load verification session
        session = db.session.get(VerificationSession, verification_session_id)
        if not session:
            logger.error(f"Verification session {verification_session_id} not found")
            return {
                'success': False,
                'error': 'Verification session not found'
            }
        
        try:
            # Generate employment narratives
            employment_narratives = self._generate_employment_narratives(session)
            
            # Generate education summary
            education_summary = self._generate_education_summary(session)
            
            # Generate technical validation narrative
            technical_validation = self._generate_technical_validation(session)
            
            # Generate red flags summary
            red_flags_summary = self.narrative_synthesizer.synthesize_red_flags_summary(
                session.fraud_flags
            )
            
            # Generate interview questions
            interview_questions = self.question_generator.generate_questions(
                employments=session.employments,
                fraud_flags=session.fraud_flags,
                contact_records=session.contact_records,
                github_analysis=session.github_analysis
            )
            
            # Generate overall summary narrative
            summary_narrative = self._generate_summary_narrative(
                session,
                employment_narratives,
                technical_validation
            )
            
            # Build complete report data
            report_data = {
                'candidate_id': session.candidate_id,
                'candidate_name': session.candidate.full_name,
                'verification_session_id': session.id,
                'risk_score': session.risk_score.value if session.risk_score else 'YELLOW',
                'summary': summary_narrative,
                'employment_history': employment_narratives,
                'education': education_summary,
                'technical_validation': technical_validation,
                'red_flags': [
                    {
                        'id': flag.id,
                        'type': flag.flag_type.value,
                        'severity': flag.severity.value,
                        'description': flag.description,
                        'evidence': flag.evidence
                    }
                    for flag in session.fraud_flags
                ],
                'red_flags_summary': red_flags_summary,
                'interview_questions': interview_questions,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Store report in database
            report = VerificationReport.query.filter_by(
                verification_session_id=verification_session_id
            ).first()
            
            if not report:
                report = VerificationReport(
                    verification_session_id=verification_session_id,
                    risk_score=session.risk_score or RiskScore.YELLOW,
                    summary_narrative=summary_narrative,
                    employment_narratives=employment_narratives,
                    education_summary=education_summary,
                    technical_validation=technical_validation,
                    interview_questions=interview_questions,
                    report_data=report_data
                )
                db.session.add(report)
            else:
                # Update existing report
                report.risk_score = session.risk_score or RiskScore.YELLOW
                report.summary_narrative = summary_narrative
                report.employment_narratives = employment_narratives
                report.education_summary = education_summary
                report.technical_validation = technical_validation
                report.interview_questions = interview_questions
                report.report_data = report_data
                report.generated_at = datetime.utcnow()
            
            db.session.commit()
            
            logger.info(f"Report generated successfully for session {verification_session_id}")
            
            return {
                'success': True,
                'verification_session_id': verification_session_id,
                'report_id': report.id,
                'risk_score': report.risk_score.value,
                'report_data': report_data
            }
            
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}", exc_info=True)
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_employment_narratives(
        self,
        session: VerificationSession
    ) -> List[Dict[str, Any]]:
        """Generate narratives for all employment periods"""
        narratives = []
        
        for employment in session.employments:
            # Get contact records for this employment
            contact_records = [
                record for record in session.contact_records
                if record.contact_type in ['HR', 'REFERENCE']
            ]
            
            narrative_text = self.narrative_synthesizer.synthesize_employment_narrative(
                employment,
                contact_records
            )
            
            # Extract reference quotes
            reference_quotes = []
            for record in contact_records:
                if record.contact_type == 'REFERENCE' and record.response_received:
                    if record.response_data and 'quotes' in record.response_data:
                        reference_quotes.extend(record.response_data['quotes'])
            
            narratives.append({
                'company': employment.company_name,
                'title': employment.job_title,
                'start_date': employment.start_date.isoformat(),
                'end_date': employment.end_date.isoformat() if employment.end_date else None,
                'verification_status': employment.verification_status.value,
                'narrative': narrative_text,
                'reference_quotes': reference_quotes[:3]  # Limit to top 3 quotes
            })
        
        return narratives
    
    def _generate_education_summary(self, session: VerificationSession) -> str:
        """Generate summary of education credentials"""
        if not session.education_credentials:
            return "No education credentials provided."
        
        verified = [e for e in session.education_credentials if e.verification_status == EducationVerificationStatus.VERIFIED]
        unverified = [e for e in session.education_credentials if e.verification_status == EducationVerificationStatus.UNVERIFIED]
        
        summary = f"Candidate claims {len(session.education_credentials)} education credential(s). "
        
        if verified:
            summary += f"{len(verified)} verified. "
        
        if unverified:
            summary += f"{len(unverified)} could not be verified. "
        
        # List credentials
        for edu in session.education_credentials:
            status = "✓" if edu.verification_status == EducationVerificationStatus.VERIFIED else "✗"
            summary += f"{status} {edu.degree_type} from {edu.institution_name} ({edu.graduation_date.year}). "
        
        return summary.strip()
    
    def _generate_technical_validation(
        self,
        session: VerificationSession
    ) -> Optional[Dict[str, Any]]:
        """Generate technical validation section"""
        github_analysis = GitHubAnalysisRecord.query.filter_by(
            verification_session_id=session.id
        ).first()
        
        if not github_analysis:
            return None
        
        # Extract claimed skills (simplified for MVP)
        claimed_skills = []
        
        narrative = self.narrative_synthesizer.synthesize_technical_narrative(
            github_analysis,
            claimed_skills
        )
        
        return {
            'github_username': github_analysis.username,
            'profile_found': github_analysis.profile_found,
            'total_repos': github_analysis.total_repos,
            'owned_repos': github_analysis.owned_repos,
            'total_commits': github_analysis.total_commits,
            'commit_frequency': github_analysis.commit_frequency,
            'languages': github_analysis.languages,
            'code_quality_score': github_analysis.code_quality_score,
            'narrative': narrative,
            'profile_url': github_analysis.profile_url
        }
    
    def _generate_summary_narrative(
        self,
        session: VerificationSession,
        employment_narratives: List[Dict[str, Any]],
        technical_validation: Optional[Dict[str, Any]]
    ) -> str:
        """Generate overall summary narrative"""
        risk_score = session.risk_score.value if session.risk_score else 'YELLOW'
        
        summary = f"Verification completed for {session.candidate.full_name}. "
        summary += f"Risk Assessment: {risk_score}. "
        
        # Employment summary
        verified_count = sum(
            1 for emp in session.employments
            if emp.verification_status == EmploymentVerificationStatus.VERIFIED
        )
        summary += f"{verified_count} of {len(session.employments)} employment period(s) verified. "
        
        # Fraud flags summary
        if session.fraud_flags:
            critical_count = sum(1 for f in session.fraud_flags if f.severity.value == 'CRITICAL')
            if critical_count > 0:
                summary += f"{critical_count} critical issue(s) identified. "
        else:
            summary += "No red flags identified. "
        
        # Technical summary
        if technical_validation and technical_validation['profile_found']:
            summary += f"GitHub profile shows {technical_validation['total_commits']} commits with code quality score {technical_validation['code_quality_score']}/10."
        
        return summary.strip()
