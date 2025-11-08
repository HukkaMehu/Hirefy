"""Verification orchestrator - coordinates all verification activities.

This module implements the main orchestration logic for the verification process:
- Generates verification plans from collected documents
- Spawns parallel verification tasks (employment, reference, technical)
- Tracks progress and status updates
- Handles timeouts with partial report generation
- Triggers report generation when complete
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid

from src.database.models import (
    db, VerificationSession, VerificationStatus, Employment,
    EducationCredential, ContactRecord, GitHubAnalysisRecord
)
from src.core.verification_task_manager import VerificationTaskManager
from src.core.employment_verifier import EmploymentVerifier
from src.core.reference_verifier import ReferenceVerifier
from src.core.technical_profile_analyzer import TechnicalProfileAnalyzer

logger = logging.getLogger(__name__)


class VerificationPlan:
    """Represents a verification plan with all tasks to execute"""
    
    def __init__(self, verification_session_id: str):
        self.verification_session_id = verification_session_id
        self.employment_verifications: List[Dict[str, Any]] = []
        self.reference_verifications: List[Dict[str, Any]] = []
        self.education_verifications: List[Dict[str, Any]] = []
        self.technical_verifications: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow()
    
    def add_employment_verification(
        self,
        employment_id: str,
        company_name: str,
        hr_phone: Optional[str] = None,
        hr_email: Optional[str] = None
    ):
        """Add employment verification task"""
        self.employment_verifications.append({
            'employment_id': employment_id,
            'company_name': company_name,
            'hr_phone': hr_phone,
            'hr_email': hr_email
        })
    
    def add_reference_verification(
        self,
        reference_name: str,
        reference_phone: Optional[str] = None,
        reference_email: Optional[str] = None,
        relationship: str = 'reference',
        employment_dates: Optional[Dict[str, str]] = None
    ):
        """Add reference verification task"""
        self.reference_verifications.append({
            'reference_name': reference_name,
            'reference_phone': reference_phone,
            'reference_email': reference_email,
            'relationship': relationship,
            'employment_dates': employment_dates
        })
    
    def add_technical_verification(
        self,
        github_username: Optional[str] = None,
        claimed_skills: Optional[List[str]] = None
    ):
        """Add technical profile verification task"""
        self.technical_verifications.append({
            'github_username': github_username,
            'claimed_skills': claimed_skills or []
        })
    
    def get_total_tasks(self) -> int:
        """Get total number of verification tasks"""
        return (
            len(self.employment_verifications) +
            len(self.reference_verifications) +
            len(self.education_verifications) +
            len(self.technical_verifications)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'verification_session_id': self.verification_session_id,
            'employment_verifications': len(self.employment_verifications),
            'reference_verifications': len(self.reference_verifications),
            'education_verifications': len(self.education_verifications),
            'technical_verifications': len(self.technical_verifications),
            'total_tasks': self.get_total_tasks(),
            'created_at': self.created_at.isoformat()
        }


class VerificationOrchestrator:
    """Orchestrates all verification activities for a verification session.
    
    This class coordinates the complete verification workflow:
    1. Generate verification plan from collected documents
    2. Spawn parallel verification tasks
    3. Track progress and status
    4. Handle timeouts
    5. Trigger report generation
    """
    
    def __init__(
        self,
        employment_verifier: Optional[EmploymentVerifier] = None,
        reference_verifier: Optional[ReferenceVerifier] = None,
        technical_analyzer: Optional[TechnicalProfileAnalyzer] = None,
        timeout_hours: float = 1.0
    ):
        """Initialize verification orchestrator.
        
        Args:
            employment_verifier: Optional EmploymentVerifier instance
            reference_verifier: Optional ReferenceVerifier instance
            technical_analyzer: Optional TechnicalProfileAnalyzer instance
            timeout_hours: Timeout in hours for verification completion (default 1 hour for demo)
        """
        self.employment_verifier = employment_verifier or EmploymentVerifier()
        self.reference_verifier = reference_verifier or ReferenceVerifier()
        self.technical_analyzer = technical_analyzer or TechnicalProfileAnalyzer()
        self.timeout_hours = timeout_hours
        
        # Task manager for parallel execution
        self.task_manager = VerificationTaskManager()
        
        logger.info(f"VerificationOrchestrator initialized with {timeout_hours}h timeout")
    
    def initiate_verification(self, verification_session_id: str) -> VerificationPlan:
        """Generate verification plan from collected documents.
        
        Args:
            verification_session_id: ID of the verification session
            
        Returns:
            VerificationPlan with all tasks to execute
        """
        logger.info(f"Generating verification plan for session {verification_session_id}")
        
        # Get verification session from database
        session = VerificationSession.query.get(verification_session_id)
        if not session:
            raise ValueError(f"Verification session {verification_session_id} not found")
        
        # Create verification plan
        plan = VerificationPlan(verification_session_id)
        
        # HARDCODED TEST CONTACT - Always add for testing
        # This will call and email you regardless of what's in the database
        logger.info("Adding hardcoded test contact for verification")
        plan.add_employment_verification(
            employment_id="test-employment-1",
            company_name="Test Company (Hardcoded)",
            hr_phone="+358445013307",
            hr_email="toukkelipoukkeli@gmail.com"
        )
        
        plan.add_reference_verification(
            reference_name="Touko Ursin (Test Reference)",
            reference_phone="+358445013307",
            reference_email="toukkelipoukkeli@gmail.com",
            relationship="Manager"
        )
        
        # Add employment verification tasks from database
        for employment in session.employments:
            hr_contact = employment.hr_contact_info or {}
            plan.add_employment_verification(
                employment_id=employment.id,
                company_name=employment.company_name,
                hr_phone=hr_contact.get('phone'),
                hr_email=hr_contact.get('email')
            )
        
        # Add reference verification tasks (from contact records or CV data)
        # For MVP, we'll look for reference contacts in the session
        # In production, this would come from parsed CV data
        
        # Add technical verification if candidate has GitHub username
        # For MVP, we'll check if there's a github_username in candidate data
        # This would typically come from CV parsing
        
        # HARDCODED: Always add Touko Ursin's GitHub profile for analysis
        logger.info("Adding hardcoded GitHub profile analysis for ToukoUrsin")
        plan.add_technical_verification(
            github_username="ToukoUrsin",
            claimed_skills=["Python", "JavaScript", "React", "TypeScript", "Mobile Development", "Full-Stack Development"]
        )
        
        logger.info(
            f"Verification plan created: {plan.get_total_tasks()} total tasks "
            f"({len(plan.employment_verifications)} employment, "
            f"{len(plan.reference_verifications)} reference, "
            f"{len(plan.technical_verifications)} technical)"
        )
        
        return plan
    
    def execute_verification_plan(self, plan: VerificationPlan) -> None:
        """Execute verification plan with parallel task execution.
        
        Args:
            plan: VerificationPlan to execute
        """
        logger.info(f"Executing verification plan for session {plan.verification_session_id}")
        
        # Update session status
        session = VerificationSession.query.get(plan.verification_session_id)
        if session:
            session.status = VerificationStatus.VERIFICATION_IN_PROGRESS
            session.estimated_completion = datetime.utcnow() + timedelta(hours=self.timeout_hours)
            db.session.commit()
        
        # Clear any existing tasks
        self.task_manager.clear_tasks()
        
        # Add employment verification tasks
        for emp_task in plan.employment_verifications:
            task_id = f"emp_{emp_task['employment_id']}"
            
            # Get employment record
            employment = Employment.query.get(emp_task['employment_id'])
            if not employment:
                logger.warning(f"Employment {emp_task['employment_id']} not found, skipping")
                continue
            
            self.task_manager.add_task(
                task_id=task_id,
                task_type='EMPLOYMENT',
                target_id=emp_task['employment_id'],
                execute_fn=self.employment_verifier.verify_employment,
                execute_args={
                    'employment': employment,
                    'hr_phone': emp_task.get('hr_phone'),
                    'hr_email': emp_task.get('hr_email')
                }
            )
            logger.info(f"Added employment verification task: {task_id}")
        
        # Add reference verification tasks
        for ref_task in plan.reference_verifications:
            task_id = f"ref_{uuid.uuid4().hex[:8]}"
            
            self.task_manager.add_task(
                task_id=task_id,
                task_type='REFERENCE',
                target_id=task_id,
                execute_fn=self.reference_verifier.verify_reference,
                execute_args={
                    'verification_session_id': plan.verification_session_id,
                    'candidate_name': session.candidate.full_name if session else 'Candidate',
                    'reference_name': ref_task['reference_name'],
                    'reference_phone': ref_task.get('reference_phone'),
                    'reference_email': ref_task.get('reference_email'),
                    'relationship': ref_task.get('relationship', 'reference'),
                    'claimed_employment_dates': ref_task.get('employment_dates')
                }
            )
            logger.info(f"Added reference verification task: {task_id}")
        
        # Add technical verification tasks
        for tech_task in plan.technical_verifications:
            task_id = f"tech_{uuid.uuid4().hex[:8]}"
            
            self.task_manager.add_task(
                task_id=task_id,
                task_type='TECHNICAL',
                target_id=task_id,
                execute_fn=self._execute_technical_verification,
                execute_args={
                    'verification_session_id': plan.verification_session_id,
                    'github_username': tech_task.get('github_username'),
                    'claimed_skills': tech_task.get('claimed_skills', [])
                }
            )
            logger.info(f"Added technical verification task: {task_id}")
        
        # Execute all tasks in parallel
        logger.info("Starting parallel execution of all verification tasks")
        self.task_manager.execute_all_tasks()
        
        # Wait for completion with timeout
        timeout_seconds = self.timeout_hours * 3600
        logger.info(f"Waiting for tasks to complete (timeout: {timeout_seconds}s)")
        self.task_manager.wait_for_completion(timeout=timeout_seconds)
        
        # Check completion status
        progress = self.task_manager.get_progress()
        logger.info(
            f"Verification tasks completed: {progress['completed']}/{progress['total']} "
            f"({progress['failed']} failed, {progress['pending']} pending)"
        )
        
        # Update session status
        if session:
            if progress['pending'] > 0:
                logger.warning(f"Verification timed out with {progress['pending']} pending tasks")
                # Will generate partial report
            
            session.completed_at = datetime.utcnow()
            db.session.commit()
    
    def _execute_technical_verification(
        self,
        verification_session_id: str,
        github_username: Optional[str],
        claimed_skills: List[str]
    ) -> Dict[str, Any]:
        """Execute technical profile verification and store results.
        
        Args:
            verification_session_id: Verification session ID
            github_username: GitHub username to analyze
            claimed_skills: List of claimed technical skills
            
        Returns:
            Analysis results dictionary
        """
        if not github_username:
            logger.info("No GitHub username provided, skipping technical verification")
            return {'success': False, 'error': 'No GitHub username provided'}
        
        logger.info(f"Analyzing GitHub profile: {github_username}")
        
        # Analyze GitHub profile
        analysis = self.technical_analyzer.analyze_github_profile(
            username=github_username,
            claimed_skills=claimed_skills
        )
        
        # Store results in database
        try:
            github_record = GitHubAnalysisRecord(
                verification_session_id=verification_session_id,
                username=analysis.username,
                profile_found=analysis.profile_found,
                total_repos=analysis.total_repos,
                owned_repos=analysis.owned_repos,
                total_commits=analysis.total_commits,
                commit_frequency=analysis.commit_frequency,
                languages=analysis.languages,
                contribution_timeline=analysis.contribution_timeline,
                code_quality_score=analysis.code_quality_score,
                skills_match=analysis.skills_match,
                mismatches=analysis.mismatches,
                profile_url=analysis.profile_url,
                analysis_notes=analysis.analysis_notes
            )
            
            db.session.add(github_record)
            db.session.commit()
            
            logger.info(f"GitHub analysis stored for {github_username}")
            
            return {
                'success': True,
                'analysis': analysis.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Failed to store GitHub analysis: {str(e)}", exc_info=True)
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'analysis': analysis.to_dict()
            }
    
    def get_verification_status(self, verification_session_id: str) -> Dict[str, Any]:
        """Get current verification status and progress.
        
        Args:
            verification_session_id: Verification session ID
            
        Returns:
            Status dictionary with progress information
        """
        # Get session from database
        session = VerificationSession.query.get(verification_session_id)
        if not session:
            return {
                'success': False,
                'error': 'Verification session not found'
            }
        
        # Get task progress
        progress = self.task_manager.get_progress()
        task_statuses = self.task_manager.get_all_tasks_status()
        
        # Calculate estimated time remaining
        time_remaining = None
        if session.estimated_completion:
            remaining = session.estimated_completion - datetime.utcnow()
            time_remaining = max(0, remaining.total_seconds())
        
        return {
            'success': True,
            'verification_session_id': verification_session_id,
            'status': session.status.value,
            'created_at': session.created_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'estimated_completion': session.estimated_completion.isoformat() if session.estimated_completion else None,
            'time_remaining_seconds': time_remaining,
            'progress': progress,
            'tasks': task_statuses,
            'risk_score': session.risk_score.value if session.risk_score else None
        }
    
    def handle_verification_timeout(self, verification_session_id: str) -> Dict[str, Any]:
        """Handle verification timeout by generating partial report.
        
        Args:
            verification_session_id: Verification session ID
            
        Returns:
            Dictionary with timeout handling results
        """
        logger.warning(f"Handling verification timeout for session {verification_session_id}")
        
        # Get pending tasks
        progress = self.task_manager.get_progress()
        pending_tasks = [
            task for task in self.task_manager.get_all_tasks_status()
            if task['status'] == 'PENDING' or task['status'] == 'IN_PROGRESS'
        ]
        
        logger.info(
            f"Timeout occurred with {len(pending_tasks)} incomplete tasks: "
            f"{[t['task_id'] for t in pending_tasks]}"
        )
        
        # Update session status
        session = VerificationSession.query.get(verification_session_id)
        if session:
            session.completed_at = datetime.utcnow()
            db.session.commit()
        
        return {
            'success': True,
            'timeout': True,
            'completed_tasks': progress['completed'],
            'failed_tasks': progress['failed'],
            'pending_tasks': progress['pending'],
            'pending_task_ids': [t['task_id'] for t in pending_tasks],
            'message': 'Verification timed out, partial report will be generated'
        }
