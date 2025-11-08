"""API routes for document upload and processing"""

import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from src.core.document_processor import DocumentProcessor
from src.utils.file_validator import FileValidator
from src.api.config import Config

documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')


@documents_bp.route('/upload', methods=['POST'])
def upload_document():
    """Upload and process a document.
    
    Expected form data:
        - file: The document file
        - document_type: Type of document (cv, diploma, paystub)
        - session_id: Verification session ID (optional)
    
    Returns:
        JSON response with extracted data
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
        
        # Get document type
        document_type = request.form.get('document_type', '').lower()
        if document_type not in ['cv', 'diploma', 'paystub']:
            return jsonify({
                'success': False,
                'error': 'Invalid document_type. Must be: cv, diploma, or paystub'
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
        
        # Save file to storage (optional)
        session_id = request.form.get('session_id')
        if session_id:
            config = Config()
            config.ensure_directories()
            
            filename = secure_filename(file.filename)
            file_path = os.path.join(config.DOCUMENT_STORAGE_DIR, session_id, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
        
        # Process document
        processor = DocumentProcessor()
        
        if document_type == 'cv':
            result = processor.extract_from_cv(file_data, file_extension)
        elif document_type == 'diploma':
            result = processor.extract_from_diploma(file_data, file_extension)
        elif document_type == 'paystub':
            result = processor.extract_from_paystub(file_data, file_extension)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid document type'
            }), 400
        
        # Return result
        return jsonify(result.to_dict()), 200 if result.success else 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500


@documents_bp.route('/validate', methods=['POST'])
def validate_document():
    """Validate a document without processing.
    
    Expected form data:
        - file: The document file
    
    Returns:
        JSON response with validation result
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'valid': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'valid': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file
        is_valid, error_message = FileValidator.validate_file(file)
        
        if is_valid:
            return jsonify({
                'valid': True,
                'filename': file.filename,
                'extension': FileValidator.get_file_extension(file.filename)
            }), 200
        else:
            return jsonify({
                'valid': False,
                'error': error_message
            }), 400
            
    except Exception as e:
        return jsonify({
            'valid': False,
            'error': f'Server error: {str(e)}'
        }), 500
