"""File upload validation utilities"""

import os
from typing import Tuple, Optional
from werkzeug.datastructures import FileStorage

# Try to import magic, but make it optional
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False


class FileValidator:
    """Validates uploaded files for format and size"""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'heic'}
    
    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # MIME type mappings
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/heic',
        'image/heif'
    }
    
    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if extension is allowed, False otherwise
        """
        if not filename or '.' not in filename:
            return False
        
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in FileValidator.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file_size(file: FileStorage) -> Tuple[bool, Optional[str]]:
        """Validate file size.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Seek to end to get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > FileValidator.MAX_FILE_SIZE:
            size_mb = file_size / (1024 * 1024)
            return False, f"File size ({size_mb:.2f}MB) exceeds maximum allowed size (10MB)"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    @staticmethod
    def validate_mime_type(file: FileStorage) -> Tuple[bool, Optional[str]]:
        """Validate file MIME type using python-magic.
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not MAGIC_AVAILABLE:
            # Skip MIME validation if magic is not available
            return True, None
        
        try:
            # Read first 2048 bytes for magic detection
            file_header = file.read(2048)
            file.seek(0)  # Reset to beginning
            
            # Detect MIME type
            mime = magic.from_buffer(file_header, mime=True)
            
            if mime not in FileValidator.ALLOWED_MIME_TYPES:
                return False, f"File type '{mime}' is not allowed. Allowed types: PDF, JPG, PNG, HEIC"
            
            return True, None
            
        except Exception as e:
            # If magic fails, fall back to extension check
            return True, None  # Allow if magic detection fails
    
    @staticmethod
    def validate_file(file: FileStorage, filename: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Comprehensive file validation.
        
        Args:
            file: Uploaded file object
            filename: Optional filename override
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file:
            return False, "No file provided"
        
        # Use provided filename or file's filename
        fname = filename or file.filename
        
        if not fname:
            return False, "No filename provided"
        
        # Check extension
        if not FileValidator.allowed_file(fname):
            return False, f"File extension not allowed. Allowed extensions: {', '.join(FileValidator.ALLOWED_EXTENSIONS)}"
        
        # Check file size
        size_valid, size_error = FileValidator.validate_file_size(file)
        if not size_valid:
            return False, size_error
        
        # Check MIME type (optional, can be disabled if python-magic not available)
        try:
            mime_valid, mime_error = FileValidator.validate_mime_type(file)
            if not mime_valid:
                return False, mime_error
        except:
            # If MIME validation fails, continue with extension check only
            pass
        
        return True, None
    
    @staticmethod
    def get_file_extension(filename: str) -> Optional[str]:
        """Extract file extension from filename.
        
        Args:
            filename: Name of the file
            
        Returns:
            File extension in lowercase, or None if no extension
        """
        if not filename or '.' not in filename:
            return None
        
        return filename.rsplit('.', 1)[1].lower()
