"""API routes for conversational document collection"""

import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from src.core.document_collection_orchestrator import DocumentCollectionOrchestrator
from src.utils.file_validator import FileValidator
from src.api.config import Config

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize orchestrator (singleton for MVP)
orchestrator = DocumentCollectionOrchestrator()


@chat_bp.route('/sessions', methods=['POST'])
def create_chat_session():
    """Create a new document collection chat session.
    
    Request body:
        {
            "verification_session_id": "uuid",
            "candidate_name": "John Doe" (optional)
        }
    
    Returns:
        {
            "session_id": "uuid",
            "initial_message": "Hi John! ..."
        }
    """
    data = request.get_json()
    
    if not data or 'verification_session_id' not in data:
        return jsonify({
            'success': False,
            'error': 'verification_session_id is required'
        }), 400
    
    try:
        verification_session_id = data['verification_session_id']
        candidate_name = data.get('candidate_name')
        
        # Start new session
        session_id, initial_message = orchestrator.start_session(
            verification_session_id,
            candidate_name
        )
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'initial_message': initial_message
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create chat session: {str(e)}'
        }), 500


@chat_bp.route('/sessions/<session_id>/messages', methods=['POST'])
def send_message(session_id):
    """Send a message in the chat conversation.
    
    Request body:
        {
            "message": "Here's my CV..."
        }
    
    Returns:
        {
            "success": true,
            "message": "Thanks! I've reviewed...",
            "session": {...}
        }
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({
            'success': False,
            'error': 'message is required'
        }), 400
    
    try:
        result = orchestrator.process_message(session_id, data['message'])
        
        if not result['success']:
            return jsonify(result), 404
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to process message: {str(e)}'
        }), 500


@chat_bp.route('/sessions/<session_id>/documents', methods=['POST'])
def upload_document_to_chat(session_id):
    """Upload a document in the chat session.
    
    Expected form data:
        - file: The document file
        - document_type: Optional type hint (cv, paystub, diploma)
    
    Returns:
        {
            "success": true,
            "message": "Thanks for uploading...",
            "extracted_data": {...},
            "session": {...}
        }
    """
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
        
        # Process document upload
        result = orchestrator.upload_document(
            session_id,
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


@chat_bp.route('/sessions/<session_id>', methods=['GET'])
def get_chat_session(session_id):
    """Get chat session state.
    
    Returns:
        {
            "session_id": "uuid",
            "stage": "CV_PROCESSED",
            "conversation_history": [...],
            "documents": [...],
            ...
        }
    """
    try:
        session = orchestrator.get_session(session_id)
        
        if not session:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        return jsonify({
            'success': True,
            'session': session
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get session: {str(e)}'
        }), 500


@chat_bp.route('/sessions/<session_id>/finalize', methods=['POST'])
def finalize_chat_session(session_id):
    """Finalize document collection and prepare for verification.
    
    Returns:
        {
            "success": true,
            "session_id": "uuid",
            "verification_session_id": "uuid",
            "documents_collected": 5,
            "cv_data": {...},
            "paystubs": [...],
            "diplomas": [...],
            "inconsistencies": [...],
            "employment_gaps": [...]
        }
    """
    try:
        result = orchestrator.finalize_collection(session_id)
        
        if not result['success']:
            return jsonify(result), 404
        
        # Update the verification session status to indicate documents are collected
        verification_session_id = result.get('verification_session_id')
        if verification_session_id:
            try:
                from src.database.models import VerificationSession, VerificationStatus, db
                
                verification_session = VerificationSession.query.filter_by(
                    id=verification_session_id
                ).first()
                
                if verification_session:
                    # Update status to indicate document collection is complete
                    verification_session.status = VerificationStatus.DOCUMENTS_COLLECTED
                    
                    db.session.commit()
                    
                    print(f"[Chat API] Updated verification session {verification_session_id} status to DOCUMENTS_COLLECTED")
                else:
                    print(f"[Chat API] Warning: Verification session {verification_session_id} not found")
            except Exception as e:
                print(f"[Chat API] Error updating verification session: {str(e)}")
                # Don't fail the whole request if status update fails
                pass
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to finalize session: {str(e)}'
        }), 500
