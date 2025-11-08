"""Verification API routes"""

import os
import threading
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.database import db, VerificationSession, Candidate
from src.database.models import VerificationStatus
from src.core.document_collection_orchestrator import DocumentCollectionOrchestrator
from src.core.verification_orchestrator import VerificationOrchestrator
from src.core.report_generator import ReportGenerator
from src.utils.file_validator import FileValidator
from src.api.config import Config
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

verifications_bp = Blueprint('verifications', __name__)

# Initialize orchestrators
doc_orchestrator = DocumentCollectionOrchestrator()
verification_orchestrator = VerificationOrchestrator()
report_generator = ReportGenerator()


@verifications_bp.route('', methods=['POST'])
def create_verification():
    """Create a new verification session.
    
    Request body:
        {
            "candidate_name": "John Doe",
            "candidate_email": "john@example.com",
            "candidate_phone": "+1234567890" (optional)
        }
    
    Returns:
        {
            "session_id": "uuid",
            "candidate_portal_url": "http://..."
        }
    """
    data = request.get_json()
    
    # Validate required fields
    if not data or 'candidate_name' not in data or 'candidate_email' not in data:
        return jsonify({
            'error': 'Missing required fields',
            'message': 'candidate_name and candidate_email are required'
        }), 400
    
    try:
        # Create candidate
        candidate = Candidate(
            full_name=data['candidate_name'],
            email=data['candidate_email'],
            phone=data.get('candidate_phone')
        )
        db.session.add(candidate)
        db.session.flush()  # Get candidate ID
        
        # Create verification session
        session = VerificationSession(
            candidate_id=candidate.id,
            estimated_completion=datetime.utcnow() + timedelta(hours=48)
        )
        db.session.add(session)
        db.session.flush()  # Get session ID
        
        # HARDCODED: Add Touko Ursin's employment history
        from src.database.models import Employment, EducationCredential, DataSource, EmploymentVerificationStatus, EducationVerificationStatus
        from datetime import date
        
        # Employment 1: Intelligence Sector Specialist
        emp1 = Employment(
            verification_session_id=session.id,
            company_name="Finnish Defence Forces",
            job_title="Intelligence Sector Specialist",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 9, 30),
            source=DataSource.CV,
            verification_status=EmploymentVerificationStatus.PENDING,
            hr_contact_info=None,
            verification_notes="Served in a highly confidential role within the intelligence sector, requiring discretion and security clearance. Developed bespoke software solutions and contributed to technically demanding R&D projects. Engineered unique solutions to complex problems under tight operational constraints."
        )
        db.session.add(emp1)
        
        # Employment 2: Project Development Lead | Ecoinsight
        emp2 = Employment(
            verification_session_id=session.id,
            company_name="Ecoinsight",
            job_title="Project Development Lead",
            start_date=date(2024, 1, 1),
            end_date=None,  # Current
            source=DataSource.CV,
            verification_status=EmploymentVerificationStatus.PENDING,
            hr_contact_info=None,
            verification_notes="Won 1st Place in the SPRING Idea Contest for developing a novel software tool. Led the development of a live analysis tool (ecoinsight.site) to assess peatland restoration potential, built in direct consultation with field experts."
        )
        db.session.add(emp2)
        
        # Employment 3: Co-Founder | VerkkoVenture oy
        emp3 = Employment(
            verification_session_id=session.id,
            company_name="VerkkoVenture oy",
            job_title="Co-Founder",
            start_date=date(2024, 1, 1),
            end_date=None,  # Current
            source=DataSource.CV,
            verification_status=EmploymentVerificationStatus.PENDING,
            hr_contact_info=None,
            verification_notes="Developing cross-platform mobile applications, focusing on digital ticketing systems and interactive mapping. Created, launched, and marketed 'Vauhti,' a caffeinated water product now available in stores."
        )
        db.session.add(emp3)
        
        # Education 1: Aalto University
        edu1 = EducationCredential(
            verification_session_id=session.id,
            institution_name="Aalto University",
            degree_type="Bachelor's Degree",
            major="Industrial Engineering and Management",
            graduation_date=date(2025, 12, 31),  # Expected
            source=DataSource.CV,
            verification_status=EducationVerificationStatus.PENDING,
            verification_notes="Currently pursuing degree (2025 - Present)"
        )
        db.session.add(edu1)
        
        # Education 2: Otaniemi High School
        edu2 = EducationCredential(
            verification_session_id=session.id,
            institution_name="Otaniemi High School, Mathematics and Science Programme",
            degree_type="High School Diploma",
            major="Mathematics and Science",
            graduation_date=date(2025, 5, 31),
            source=DataSource.CV,
            verification_status=EducationVerificationStatus.PENDING,
            verification_notes="Head of Business Partnerships, Student Council (2021 – 2025). Exchange Year: Borg Telfs, Austria (2022–2023). Matriculation Examination: Top-tier results with Laudatur (top 5%) in Mathematics (118/120), English (290/299), Chemistry (109/120), and Physics (103/120)."
        )
        db.session.add(edu2)
        
        db.session.commit()
        
        # Generate candidate portal URL (frontend URL, not backend)
        # In production, this should come from environment variable
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        portal_url = f"{frontend_url}/candidate-portal/{session.id}"
        
        return jsonify({
            'session_id': session.id,
            'candidate_portal_url': portal_url,
            'status': session.status.value,
            'created_at': session.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to create verification',
            'message': str(e)
        }), 500


@verifications_bp.route('/<session_id>', methods=['GET'])
def get_verification(session_id):
    """Get verification session details and report.
    
    Returns:
        {
            "session_id": "uuid",
            "candidate_name": "John Doe",
            "status": "COMPLETED",
            "risk_score": "GREEN",
            "report": {...}
        }
    """
    session = VerificationSession.query.get(session_id)
    
    if not session:
        return jsonify({
            'error': 'Not Found',
            'message': f'Verification session {session_id} not found'
        }), 404
    
    response = {
        'session_id': session.id,
        'candidate_name': session.candidate.full_name,
        'candidate_email': session.candidate.email,
        'status': session.status.value,
        'created_at': session.created_at.isoformat(),
        'completed_at': session.completed_at.isoformat() if session.completed_at else None,
        'risk_score': session.risk_score.value if session.risk_score else None
    }
    
    # Include report if available
    if session.verification_report:
        report_data = {
            'risk_score': session.verification_report.risk_score.value,
            'summary': session.verification_report.summary_narrative,
            'employment_narratives': session.verification_report.employment_narratives,
            'education_summary': session.verification_report.education_summary,
            'technical_validation': session.verification_report.technical_validation,
            'interview_questions': session.verification_report.interview_questions,
            'fraud_flags': [
                {
                    'type': flag.flag_type.value,
                    'severity': flag.severity.value,
                    'description': flag.description
                }
                for flag in session.fraud_flags
            ],
            'generated_at': session.verification_report.generated_at.isoformat()
        }
        
        # Include AI analysis if available
        if session.verification_report.report_data and session.verification_report.report_data.get('ai_analysis'):
            report_data['ai_analysis'] = session.verification_report.report_data['ai_analysis']
        
        response['report'] = report_data
    
    return jsonify(response)


@verifications_bp.route('', methods=['GET'])
def list_verifications():
    """List all verification sessions.
    
    Query parameters:
        - status: Filter by status
        - limit: Number of results (default 50)
        - offset: Pagination offset (default 0)
    
    Returns:
        {
            "verifications": [...],
            "total": 100,
            "limit": 50,
            "offset": 0
        }
    """
    # Get query parameters
    status_filter = request.args.get('status')
    limit = min(int(request.args.get('limit', 50)), 100)
    offset = int(request.args.get('offset', 0))
    
    # Build query
    query = VerificationSession.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    sessions = query.order_by(VerificationSession.created_at.desc()).limit(limit).offset(offset).all()
    
    verifications = [
        {
            'session_id': session.id,
            'candidate_name': session.candidate.full_name,
            'status': session.status.value,
            'risk_score': session.risk_score.value if session.risk_score else None,
            'created_at': session.created_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None
        }
        for session in sessions
    ]
    
    return jsonify({
        'verifications': verifications,
        'total': total,
        'limit': limit,
        'offset': offset
    })


@verifications_bp.route('/<session_id>/status', methods=['GET'])
def get_verification_status(session_id):
    """Get real-time verification status and progress.
    
    Returns:
        {
            "session_id": "uuid",
            "status": "VERIFICATION_IN_PROGRESS",
            "progress": {
                "percentage": 45,
                "documents_collected": true,
                "employment_verifications": 2,
                "reference_checks": 1,
                "technical_analysis": false
            },
            "timeline": [...],
            "activities": [...]
        }
    """
    session = VerificationSession.query.get(session_id)
    
    if not session:
        return jsonify({
            'error': 'Not Found',
            'message': f'Verification session {session_id} not found'
        }), 404
    
    # Calculate detailed progress
    total_employments = len(session.employments)
    verified_employments = len([e for e in session.employments if e.verification_status.value == 'VERIFIED'])
    
    total_education = len(session.education_credentials)
    verified_education = len([e for e in session.education_credentials if e.verification_status.value == 'VERIFIED'])
    
    reference_contacts = len([c for c in session.contact_records if c.contact_type == 'REFERENCE'])
    reference_responses = len([c for c in session.contact_records if c.contact_type == 'REFERENCE' and c.response_received])
    
    # Check for GitHub analysis (it's a backref, so we need to query it)
    from src.database.models import GitHubAnalysisRecord
    github_analysis = GitHubAnalysisRecord.query.filter_by(verification_session_id=session.id).first()
    has_github_analysis = github_analysis is not None
    
    # Calculate completion percentage
    total_tasks = 1  # Document collection
    completed_tasks = 0
    
    if session.status.value != 'PENDING_DOCUMENTS':
        completed_tasks += 1
    
    if total_employments > 0:
        total_tasks += total_employments
        completed_tasks += verified_employments
    
    if total_education > 0:
        total_tasks += total_education
        completed_tasks += verified_education
    
    if reference_contacts > 0:
        total_tasks += reference_contacts
        completed_tasks += reference_responses
    
    # Add technical analysis as a task if applicable
    if session.status.value in ['VERIFICATION_IN_PROGRESS', 'COMPLETED']:
        total_tasks += 1
        if has_github_analysis:
            completed_tasks += 1
    
    percentage = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0
    
    # Build timeline of completed activities
    timeline = []
    
    # Document collection
    if session.status.value != 'PENDING_DOCUMENTS':
        timeline.append({
            'activity': 'Documents Collected',
            'status': 'completed',
            'timestamp': session.created_at.isoformat(),
            'description': 'All required documents have been uploaded and processed'
        })
    
    # Employment verifications
    for employment in session.employments:
        if employment.verification_status.value == 'VERIFIED':
            timeline.append({
                'activity': f'Employment Verified: {employment.company_name}',
                'status': 'completed',
                'timestamp': employment.created_at.isoformat(),
                'description': f'Verified {employment.job_title} position'
            })
        elif employment.verification_status.value == 'PENDING':
            timeline.append({
                'activity': f'Verifying Employment: {employment.company_name}',
                'status': 'in_progress',
                'timestamp': employment.created_at.isoformat(),
                'description': f'Contacting HR to verify {employment.job_title} position'
            })
    
    # Reference checks
    for contact in session.contact_records:
        if contact.contact_type == 'REFERENCE':
            if contact.response_received:
                timeline.append({
                    'activity': f'Reference Check Completed',
                    'status': 'completed',
                    'timestamp': contact.response_timestamp.isoformat() if contact.response_timestamp else contact.attempt_timestamp.isoformat(),
                    'description': f'Received feedback from {contact.contact_name or "reference"}'
                })
            else:
                timeline.append({
                    'activity': f'Contacting Reference',
                    'status': 'in_progress',
                    'timestamp': contact.attempt_timestamp.isoformat(),
                    'description': f'Attempting to reach {contact.contact_name or "reference"} via {contact.contact_method}'
                })
    
    # Education verifications
    for education in session.education_credentials:
        if education.verification_status.value == 'VERIFIED':
            timeline.append({
                'activity': f'Education Verified: {education.institution_name}',
                'status': 'completed',
                'timestamp': education.created_at.isoformat(),
                'description': f'Verified {education.degree_type} in {education.major}'
            })
    
    # Technical analysis
    if has_github_analysis and github_analysis:
        timeline.append({
            'activity': 'Technical Profile Analyzed',
            'status': 'completed',
            'timestamp': github_analysis.analyzed_at.isoformat(),
            'description': f'GitHub profile analyzed: {github_analysis.username}'
        })
    
    # Report generation
    if session.verification_report:
        # Handle risk_score being None or having a value
        risk_score_display = session.risk_score.value if session.risk_score else session.verification_report.risk_score
        timeline.append({
            'activity': 'Verification Report Generated',
            'status': 'completed',
            'timestamp': session.verification_report.generated_at.isoformat(),
            'description': f'Final report with {risk_score_display} risk score'
        })
    
    # Sort timeline by timestamp
    timeline.sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Build current activities summary
    activities = []
    
    if session.status.value == 'PENDING_DOCUMENTS':
        activities.append({
            'type': 'document_collection',
            'message': 'Waiting for candidate to upload documents',
            'status': 'pending'
        })
    elif session.status.value == 'DOCUMENTS_COLLECTED':
        activities.append({
            'type': 'verification_start',
            'message': 'Preparing to start verification activities',
            'status': 'pending'
        })
    elif session.status.value == 'VERIFICATION_IN_PROGRESS':
        if verified_employments < total_employments:
            activities.append({
                'type': 'employment_verification',
                'message': f'Verifying employment history ({verified_employments}/{total_employments} completed)',
                'status': 'in_progress'
            })
        
        if reference_contacts > 0 and reference_responses < reference_contacts:
            activities.append({
                'type': 'reference_checks',
                'message': f'Conducting reference checks ({reference_responses}/{reference_contacts} completed)',
                'status': 'in_progress'
            })
        
        if not has_github_analysis:
            activities.append({
                'type': 'technical_analysis',
                'message': 'Analyzing technical profile',
                'status': 'in_progress'
            })
    elif session.status.value == 'COMPLETED':
        activities.append({
            'type': 'completed',
            'message': 'Verification complete - report available',
            'status': 'completed'
        })
    
    progress = {
        'percentage': percentage,
        'documents_collected': session.status.value != 'PENDING_DOCUMENTS',
        'employment_verifications': verified_employments,
        'total_employments': total_employments,
        'reference_checks': reference_responses,
        'total_references': reference_contacts,
        'education_verifications': verified_education,
        'total_education': total_education,
        'technical_analysis_complete': has_github_analysis,
        'fraud_flags': len(session.fraud_flags),
        'report_generated': session.verification_report is not None
    }
    
    # Include AI analysis if available
    ai_analysis = None
    if session.verification_report and session.verification_report.report_data:
        ai_analysis = session.verification_report.report_data.get('ai_analysis')
    
    response_data = {
        'session_id': session.id,
        'status': session.status.value,
        'progress': progress,
        'timeline': timeline,
        'activities': activities,
        'estimated_completion': session.estimated_completion.isoformat() if session.estimated_completion else None,
        'last_updated': datetime.utcnow().isoformat()
    }
    
    if ai_analysis:
        response_data['ai_analysis'] = ai_analysis
    
    return jsonify(response_data)


@verifications_bp.route('/<session_id>/documents', methods=['POST'])
def upload_document_to_verification(session_id):
    """Upload a document to a verification session.
    
    This endpoint allows uploading documents directly to a verification session
    through the conversational document collection system.
    
    Expected form data:
        - file: The document file
        - document_type: Optional type hint (cv, paystub, diploma)
    
    Returns:
        {
            "success": true,
            "message": "Document uploaded and processed successfully",
            "extracted_data": {...},
            "session": {...}
        }
    """
    # Verify session exists
    session = VerificationSession.query.get(session_id)
    
    if not session:
        return jsonify({
            'error': 'Not Found',
            'message': f'Verification session {session_id} not found'
        }), 404
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file
        is_valid, error_message = FileValidator.validate_file(file)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400
        
        # Read file data
        file_data = file.read()
        file_extension = FileValidator.get_file_extension(file.filename)
        filename = secure_filename(file.filename)
        
        # Get optional document type hint
        document_type = request.form.get('document_type')
        
        # Get or create chat session for this verification session
        chat_session_id = orchestrator.get_or_create_session_for_verification(session_id)
        
        # Process document upload through orchestrator
        result = orchestrator.upload_document(
            chat_session_id,
            file_data,
            filename,
            file_extension,
            document_type
        )
        
        if not result['success']:
            return jsonify(result), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to upload document: {str(e)}'
        }), 500


@verifications_bp.route('/<session_id>/chat', methods=['POST'])
def chat_with_verification(session_id):
    """Send a chat message for conversational document collection.
    
    This endpoint enables conversational interactions during the document
    collection phase of verification.
    
    Request body:
        {
            "message": "Here's my explanation for the gap..."
        }
    
    Returns:
        {
            "success": true,
            "message": "Thanks for clarifying...",
            "session": {...}
        }
    """
    # Verify session exists
    session = VerificationSession.query.get(session_id)
    
    if not session:
        return jsonify({
            'error': 'Not Found',
            'message': f'Verification session {session_id} not found'
        }), 404
    
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            'success': False,
            'error': 'message is required'
        }), 400
    
    try:
        # Get or create chat session for this verification session
        chat_session_id = doc_orchestrator.get_or_create_session_for_verification(session_id)
        
        # Process message through orchestrator
        result = doc_orchestrator.process_message(chat_session_id, data['message'])
        
        if not result['success']:
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to process message: {str(e)}'
        }), 500


@verifications_bp.route('/<session_id>/start-verification', methods=['POST'])
def start_verification(session_id):
    """Start verification activities (employment calls, reference checks, technical analysis).
    
    This endpoint triggers the actual verification process which includes:
    - Phone calls to HR departments for employment verification
    - Phone calls or emails to references
    - GitHub profile analysis
    - Fraud detection
    - Report generation
    
    WARNING: This will make REAL phone calls via ElevenLabs and send REAL emails.
    Only call this endpoint when you're ready to start the verification process.
    
    Returns:
        {
            "success": true,
            "message": "Verification started",
            "session_id": "uuid",
            "estimated_completion": "2024-11-10T12:00:00"
        }
    """
    logger.info(f"Starting verification for session {session_id}")
    
    # Verify session exists
    session = VerificationSession.query.get(session_id)
    
    if not session:
        return jsonify({
            'error': 'Not Found',
            'message': f'Verification session {session_id} not found'
        }), 404
    
    # Check if session is in correct state
    if session.status not in [VerificationStatus.DOCUMENTS_COLLECTED, VerificationStatus.PENDING_DOCUMENTS]:
        return jsonify({
            'error': 'Invalid State',
            'message': f'Cannot start verification. Current status: {session.status.value}',
            'current_status': session.status.value
        }), 400
    
    # Check if verification is already in progress or completed
    if session.status in [VerificationStatus.VERIFICATION_IN_PROGRESS, VerificationStatus.COMPLETED]:
        return jsonify({
            'error': 'Already Started',
            'message': f'Verification already {session.status.value}',
            'current_status': session.status.value
        }), 400
    
    try:
        from flask import current_app
        
        # Capture the app instance before starting the thread
        app = current_app._get_current_object()
        
        # Run verification in background thread to avoid blocking the request
        def run_verification():
            """Background task to run verification"""
            # Create a debug log file for this thread
            import sys
            debug_log_path = f"verification_thread_{session_id}.log"
            
            def log_to_file(msg):
                """Write to both logger and debug file"""
                logger.info(msg)
                print(msg, flush=True)
                try:
                    with open(debug_log_path, 'a', encoding='utf-8') as f:
                        f.write(f"{datetime.utcnow().isoformat()} - {msg}\n")
                except:
                    pass
            
            log_to_file(f"🚀 Background thread started for session {session_id}")
            log_to_file(f"   Thread ID: {threading.current_thread().ident}")
            log_to_file(f"   Python version: {sys.version}")
            
            # Use the Flask app context in the background thread
            with app.app_context():
                try:
                    log_to_file(f"✅ Flask app context acquired")
                    log_to_file(f"📋 Background verification started for session {session_id}")
                    
                    # Generate verification plan
                    log_to_file(f"📝 Generating verification plan...")
                    plan = verification_orchestrator.initiate_verification(session_id)
                    log_to_file(f"✅ Verification plan created: {plan.get_total_tasks()} tasks")
                    
                    # Execute verification plan (this will make real calls/emails)
                    log_to_file(f"🔄 Executing verification plan...")
                    verification_orchestrator.execute_verification_plan(plan)
                    log_to_file(f"✅ Verification plan execution completed")
                    
                    # Generate report
                    log_to_file(f"📊 Generating verification report...")
                    report = report_generator.generate_report(session_id)
                    
                    if report:
                        # Report is a dict, not an object
                        risk_score = report.get('risk_score', 'UNKNOWN') if isinstance(report, dict) else getattr(report, 'risk_score', 'UNKNOWN')
                        log_to_file(f"✅ Report generated successfully with risk score: {risk_score}")
                    else:
                        log_to_file(f"⚠️ Report generation returned None")
                    
                    # Generate AI summary from transcripts
                    log_to_file(f"🤖 Generating AI summary from transcripts...")
                    try:
                        import requests
                        from src.database.models import VerificationReport
                        
                        # Call the transcript AI summary endpoint
                        summary_response = requests.post(
                            f'http://localhost:5000/api/verifications/{session_id}/ai-summary',
                            timeout=30
                        )
                        
                        if summary_response.status_code == 200:
                            summary_data = summary_response.json()
                            if summary_data.get('success'):
                                log_to_file(f"✅ AI summary generated successfully!")
                                
                                # Store in report
                                verification_report = VerificationReport.query.filter_by(
                                    verification_session_id=session_id
                                ).first()
                                
                                if verification_report:
                                    if not verification_report.report_data:
                                        verification_report.report_data = {}
                                    verification_report.report_data['ai_summary'] = summary_data['summary']
                                    verification_report.report_data['ai_summary_timestamp'] = datetime.utcnow().isoformat()
                                    
                                    # Also update the main summary field
                                    verification_report.summary_narrative = summary_data['summary']
                                    
                                    db.session.commit()
                                    log_to_file(f"💾 AI summary stored in report!")
                            else:
                                log_to_file(f"⚠️ AI summary generation failed: {summary_data.get('error')}")
                        else:
                            log_to_file(f"⚠️ AI summary request failed with status {summary_response.status_code}")
                    except Exception as summary_error:
                        log_to_file(f"⚠️ AI summary exception: {str(summary_error)}")
                        # Don't fail the whole verification if AI summary fails
                    
                    # Run AI analysis
                    log_to_file(f"🤖 Starting AI analysis...")
                    try:
                        from src.core.ai_analyzer import AIAnalyzer
                        from src.database.models import VerificationReport
                        
                        log_to_file(f"   Creating AIAnalyzer instance...")
                        ai_analyzer = AIAnalyzer()
                        log_to_file(f"   Calling analyze_verification...")
                        ai_result = ai_analyzer.analyze_verification(session_id)
                        log_to_file(f"   AI analysis returned: success={ai_result.get('success')}")
                        
                        if ai_result.get('success'):
                            log_to_file(f"✅ AI analysis succeeded!")
                            
                            # Store AI analysis in verification report
                            log_to_file(f"   Querying for verification report...")
                            verification_report = VerificationReport.query.filter_by(
                                verification_session_id=session_id
                            ).first()
                            
                            if verification_report:
                                log_to_file(f"   Report found, storing AI analysis...")
                                if not verification_report.report_data:
                                    verification_report.report_data = {}
                                verification_report.report_data['ai_analysis'] = ai_result['analysis']
                                verification_report.report_data['ai_analysis_timestamp'] = datetime.utcnow().isoformat()
                                verification_report.report_data['ai_model'] = ai_result.get('model', 'gpt-4o')
                                db.session.commit()
                                log_to_file(f"💾 AI analysis stored in database!")
                            else:
                                log_to_file(f"❌ Verification report not found - cannot store AI analysis")
                        else:
                            error_msg = ai_result.get('error', 'Unknown error')
                            log_to_file(f"⚠️ AI analysis failed: {error_msg}")
                    except Exception as ai_error:
                        log_to_file(f"❌ AI analysis exception: {str(ai_error)}")
                        import traceback
                        log_to_file(f"   Traceback: {traceback.format_exc()}")
                        # Don't fail the whole verification if AI analysis fails
                    
                    log_to_file(f"✅ Verification completed for session {session_id}")
                    
                except Exception as e:
                    log_to_file(f"❌ Background verification failed: {str(e)}")
                    import traceback
                    log_to_file(f"   Traceback: {traceback.format_exc()}")
                    
                    # Update session status to indicate failure
                    try:
                        session = VerificationSession.query.get(session_id)
                        if session:
                            session.status = VerificationStatus.FAILED
                            session.completed_at = datetime.utcnow()
                            db.session.commit()
                            log_to_file(f"   Session status updated to FAILED")
                    except Exception as db_error:
                        log_to_file(f"   Failed to update session status: {str(db_error)}")
                
                log_to_file(f"🏁 Background thread exiting")
        
        # Start background thread
        thread = threading.Thread(target=run_verification, daemon=True)
        thread.start()
        
        logger.info(f"Verification thread started for session {session_id}")
        
        # Return immediately
        return jsonify({
            'success': True,
            'message': 'Verification started successfully',
            'session_id': session_id,
            'status': 'VERIFICATION_IN_PROGRESS',
            'estimated_completion': (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            'note': 'Verification is running in the background. Use GET /api/verifications/{session_id}/status to track progress.'
        }), 202  # 202 Accepted - request accepted for processing
        
    except Exception as e:
        logger.error(f"Failed to start verification for session {session_id}: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to start verification: {str(e)}'
        }), 500
