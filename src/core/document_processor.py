"""Document processing and OCR extraction using OpenAI GPT-4 Vision"""

import base64
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from io import BytesIO

from openai import OpenAI
import PyPDF2
from PIL import Image

from src.core.document_models import (
    CVData, EducationCredential, EmploymentEvidence,
    EmploymentHistory, EducationEntry, DocumentProcessingResult
)


class DocumentProcessor:
    """Processes documents using OpenAI GPT-4 Vision for OCR and extraction"""
    
    # Confidence threshold for extracted data
    CONFIDENCE_THRESHOLD = 0.85
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize document processor.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def _encode_image(self, image_data: bytes) -> str:
        """Encode image data to base64.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Base64 encoded string
        """
        return base64.b64encode(image_data).decode('utf-8')
    
    def _pdf_to_images(self, pdf_data: bytes) -> list[bytes]:
        """Convert PDF pages to images.
        
        Args:
            pdf_data: Raw PDF bytes
            
        Returns:
            List of image bytes (one per page)
        """
        images = []
        
        try:
            # For MVP, we'll just extract text from PDF
            # In production, would use pdf2image or similar
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            
            # For now, return empty list - will process as text
            # TODO: Implement proper PDF to image conversion
            return images
            
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return images
    
    def _extract_with_vision(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """Extract structured data from image using GPT-4 Vision.
        
        Args:
            image_data: Raw image bytes
            prompt: Extraction prompt
            
        Returns:
            Extracted data as dictionary
        """
        try:
            # Encode image
            base64_image = self._encode_image(image_data)
            print(f"[DocumentProcessor] Encoded image: {len(base64_image)} chars")
            
            # Call GPT-4 Vision API with JSON mode
            # Note: Vision API with response_format requires the system message approach
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a document extraction assistant. Extract structured data from documents and return ONLY valid JSON without any markdown formatting or code blocks."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt + "\n\nIMPORTANT: Return ONLY the JSON object, no markdown code blocks or additional text."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000,
                temperature=0.1  # Low temperature for consistent extraction
            )
            
            # Parse response
            content = response.choices[0].message.content
            print(f"[DocumentProcessor] Vision API response: {content[:500]}")
            
            # Try to parse as JSON
            try:
                parsed = json.loads(content)
                print(f"[DocumentProcessor] Parsed JSON keys: {list(parsed.keys())}")
                return parsed
            except json.JSONDecodeError:
                print(f"[DocumentProcessor] Failed to parse as JSON, extracting from markdown")
                # If not JSON, try to extract JSON from markdown code blocks
                import re
                
                # Try to find JSON in code blocks (```json ... ``` or ``` ... ```)
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(1))
                        print(f"[DocumentProcessor] Extracted JSON from markdown, keys: {list(parsed.keys())}")
                        return parsed
                    except json.JSONDecodeError as e:
                        print(f"[DocumentProcessor] Failed to parse extracted JSON: {e}")
                
                # Try to find any JSON object in the text
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(0))
                        print(f"[DocumentProcessor] Found JSON in text, keys: {list(parsed.keys())}")
                        return parsed
                    except json.JSONDecodeError:
                        pass
                
                # Return as text if all else fails
                print(f"[DocumentProcessor] Could not extract JSON, returning as raw text")
                return {"raw_text": content, "parsed": False}
                
        except Exception as e:
            print(f"[DocumentProcessor] Vision API error: {str(e)}")
            raise Exception(f"Error extracting data with vision: {str(e)}")
    
    def _extract_from_pdf_text(self, pdf_data: bytes, prompt: str) -> Dict[str, Any]:
        """Extract structured data from PDF text using GPT-4.
        
        Args:
            pdf_data: Raw PDF bytes
            prompt: Extraction prompt
            
        Returns:
            Extracted data as dictionary
        """
        try:
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_data))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            if not text.strip():
                raise Exception("No text could be extracted from PDF")
            
            print(f"[DocumentProcessor] Extracted {len(text)} characters from PDF")
            print(f"[DocumentProcessor] First 200 chars: {text[:200]}")
            
            # Call GPT-4 for structured extraction
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a document extraction assistant. Extract structured data from documents and return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nDocument text:\n{text}"
                    }
                ],
                max_tokens=2000,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            content = response.choices[0].message.content
            print(f"[DocumentProcessor] OpenAI response: {content[:500]}")
            
            parsed_data = json.loads(content)
            print(f"[DocumentProcessor] Parsed data keys: {list(parsed_data.keys())}")
            
            return parsed_data
            
        except Exception as e:
            print(f"[DocumentProcessor] Error: {str(e)}")
            raise Exception(f"Error extracting data from PDF: {str(e)}")

    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            datetime object or None
        """
        if not date_str or date_str.lower() in ['present', 'current', 'ongoing', 'n/a', 'none']:
            return None
        
        # Try common date formats
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%B %Y',
            '%b %Y',
            '%Y-%m',
            '%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue
        
        return None
    
    def _extract_pdf_with_vision(self, pdf_data: bytes, prompt: str) -> Dict[str, Any]:
        """Extract data from PDF using Vision API (for scanned/image PDFs).
        
        Args:
            pdf_data: Raw PDF bytes
            prompt: Extraction prompt
            
        Returns:
            Extracted data as dictionary
        """
        try:
            # Try using PyMuPDF (fitz) first - no external dependencies
            try:
                import fitz  # PyMuPDF
                
                # Open PDF from bytes
                pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
                
                # Get first page (usually contains most CV info)
                page = pdf_document[0]
                
                # Convert page to image (PNG)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")
                
                pdf_document.close()
                
                print(f"[DocumentProcessor] Converted PDF page to image using PyMuPDF")
                
                # Use vision API
                return self._extract_with_vision(img_data, prompt)
                
            except ImportError:
                # Fallback to pdf2image if PyMuPDF not available
                try:
                    from pdf2image import convert_from_bytes
                    
                    # Convert PDF to images (first page only for CV)
                    images = convert_from_bytes(pdf_data, first_page=1, last_page=1)
                    
                    if not images:
                        raise Exception("Could not convert PDF to images")
                    
                    print(f"[DocumentProcessor] Converted PDF to image using pdf2image")
                    
                    # Process first page
                    img_byte_arr = BytesIO()
                    images[0].save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Use vision API
                    return self._extract_with_vision(img_byte_arr, prompt)
                    
                except ImportError:
                    raise Exception("Neither PyMuPDF nor pdf2image is installed. Install with: pip install PyMuPDF")
                
        except Exception as e:
            raise Exception(f"Error extracting PDF with vision: {str(e)}")
    
    def _is_text_readable(self, text: str) -> bool:
        """Check if extracted text is readable (not garbled).
        
        Args:
            text: Extracted text
            
        Returns:
            True if text appears readable
        """
        if not text or len(text.strip()) < 50:
            return False
        
        # Count readable ASCII characters
        readable_chars = sum(1 for c in text if c.isalnum() or c.isspace() or c in '.,;:!?-()[]{}')
        total_chars = len(text)
        
        # If less than 60% readable characters, consider it garbled
        readable_ratio = readable_chars / total_chars if total_chars > 0 else 0
        return readable_ratio > 0.6
    
    def extract_from_cv(self, file_data: bytes, file_extension: str) -> DocumentProcessingResult:
        """Extract structured data from CV/Resume.
        
        Args:
            file_data: Raw file bytes
            file_extension: File extension (pdf, jpg, png, etc.)
            
        Returns:
            DocumentProcessingResult with CVData
        """
        try:
            prompt = """Extract the following information from this CV/Resume and return as JSON:
{
  "candidate_name": "Full name",
  "email": "Email address",
  "phone": "Phone number",
  "summary": "Professional summary or objective",
  "linkedin_url": "LinkedIn profile URL",
  "github_url": "GitHub profile URL",
  "portfolio_url": "Portfolio website URL",
  "skills": ["skill1", "skill2", ...],
  "certifications": ["cert1", "cert2", ...],
  "employment_history": [
    {
      "company_name": "Company name",
      "job_title": "Job title",
      "start_date": "YYYY-MM-DD or YYYY-MM or YYYY",
      "end_date": "YYYY-MM-DD or 'Present' if current",
      "location": "City, State/Country",
      "description": "Job description and achievements",
      "is_current": true/false
    }
  ],
  "education": [
    {
      "institution_name": "University/School name",
      "degree_type": "Bachelor's, Master's, PhD, etc.",
      "major": "Field of study",
      "graduation_date": "YYYY-MM-DD or YYYY",
      "gpa": 3.5,
      "location": "City, State/Country"
    }
  ],
  "confidence_score": 0.95
}

Return ONLY valid JSON. Use null for missing fields. Confidence score should be 0.0-1.0 based on document clarity."""
            
            # Extract data based on file type
            if file_extension.lower() == 'pdf':
                # Try text extraction first
                try:
                    # Extract text to check if it's readable
                    pdf_reader = PyPDF2.PdfReader(BytesIO(file_data))
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    
                    # Check if text is readable
                    if self._is_text_readable(text):
                        print("[DocumentProcessor] PDF text is readable, using text extraction")
                        extracted_data = self._extract_from_pdf_text(file_data, prompt)
                    else:
                        print("[DocumentProcessor] PDF text is garbled, falling back to Vision API")
                        # Convert PDF to images and use Vision API
                        extracted_data = self._extract_pdf_with_vision(file_data, prompt)
                except Exception as e:
                    print(f"[DocumentProcessor] Text extraction failed: {e}, trying Vision API")
                    extracted_data = self._extract_pdf_with_vision(file_data, prompt)
            else:
                extracted_data = self._extract_with_vision(file_data, prompt)
            
            # Parse employment history
            employment_history = []
            emp_data = extracted_data.get('employment_history', [])
            print(f"[DocumentProcessor] Processing {len(emp_data)} employment entries")
            
            for emp in emp_data:
                if not emp.get('company_name') or not emp.get('job_title'):
                    print(f"[DocumentProcessor] Skipping invalid employment entry: {emp}")
                    continue
                    
                start_date = self._parse_date(emp.get('start_date'))
                end_date = self._parse_date(emp.get('end_date'))
                
                employment_history.append(EmploymentHistory(
                    company_name=emp.get('company_name', ''),
                    job_title=emp.get('job_title', ''),
                    start_date=start_date.date() if start_date else None,
                    end_date=end_date.date() if end_date else None,
                    description=emp.get('description', ''),
                    location=emp.get('location'),
                    is_current=emp.get('is_current', False),
                    confidence_score=extracted_data.get('confidence_score', 0.0)
                ))
            
            # Parse education
            education = []
            edu_data = extracted_data.get('education', [])
            print(f"[DocumentProcessor] Processing {len(edu_data)} education entries")
            
            for edu in edu_data:
                if not edu.get('institution_name'):
                    print(f"[DocumentProcessor] Skipping invalid education entry: {edu}")
                    continue
                
                # Use major as degree_type if degree_type is missing
                degree_type = edu.get('degree_type') or edu.get('major') or 'Degree'
                    
                grad_date = self._parse_date(edu.get('graduation_date'))
                
                education.append(EducationEntry(
                    institution_name=edu.get('institution_name', ''),
                    degree_type=degree_type,
                    major=edu.get('major'),
                    graduation_date=grad_date.date() if grad_date else None,
                    gpa=edu.get('gpa'),
                    location=edu.get('location'),
                    confidence_score=extracted_data.get('confidence_score', 0.0)
                ))
            
            # Create CVData object
            cv_data = CVData(
                candidate_name=extracted_data.get('candidate_name') or '',
                email=extracted_data.get('email'),
                phone=extracted_data.get('phone'),
                employment_history=employment_history,
                education=education,
                skills=extracted_data.get('skills') or [],
                certifications=extracted_data.get('certifications') or [],
                summary=extracted_data.get('summary') or '',
                linkedin_url=extracted_data.get('linkedin_url'),
                github_url=extracted_data.get('github_url'),
                portfolio_url=extracted_data.get('portfolio_url'),
                confidence_score=extracted_data.get('confidence_score', 0.0),
                raw_data=extracted_data
            )
            
            # Check confidence threshold
            warnings = []
            if cv_data.confidence_score < self.CONFIDENCE_THRESHOLD:
                warnings.append(f"Confidence score ({cv_data.confidence_score:.2f}) below threshold ({self.CONFIDENCE_THRESHOLD})")
            
            return DocumentProcessingResult(
                success=True,
                document_type='CV',
                data=cv_data,
                confidence_score=cv_data.confidence_score,
                warnings=warnings
            )
            
        except Exception as e:
            return DocumentProcessingResult(
                success=False,
                document_type='CV',
                error_message=f"Failed to extract CV data: {str(e)}"
            )
    
    def extract_from_diploma(self, file_data: bytes, file_extension: str) -> DocumentProcessingResult:
        """Extract structured data from diploma or transcript.
        
        Args:
            file_data: Raw file bytes
            file_extension: File extension (pdf, jpg, png, etc.)
            
        Returns:
            DocumentProcessingResult with EducationCredential
        """
        try:
            prompt = """Extract the following information from this diploma/transcript and return as JSON:
{
  "institution_name": "University or school name",
  "degree_type": "Bachelor's, Master's, PhD, Associate's, Certificate, etc.",
  "major": "Field of study or major",
  "graduation_date": "YYYY-MM-DD or YYYY",
  "gpa": 3.5,
  "honors": "Cum Laude, Magna Cum Laude, etc. or null",
  "document_type": "DIPLOMA or TRANSCRIPT",
  "confidence_score": 0.95
}

Return ONLY valid JSON. Use null for missing fields. Confidence score should be 0.0-1.0 based on document clarity."""
            
            # Extract data based on file type
            if file_extension.lower() == 'pdf':
                extracted_data = self._extract_from_pdf_text(file_data, prompt)
            else:
                extracted_data = self._extract_with_vision(file_data, prompt)
            
            # Parse graduation date
            grad_date = self._parse_date(extracted_data.get('graduation_date'))
            
            # Create EducationCredential object
            credential = EducationCredential(
                institution_name=extracted_data.get('institution_name', ''),
                degree_type=extracted_data.get('degree_type', ''),
                major=extracted_data.get('major'),
                graduation_date=grad_date.date() if grad_date else None,
                gpa=extracted_data.get('gpa'),
                honors=extracted_data.get('honors'),
                document_type=extracted_data.get('document_type', 'DIPLOMA'),
                confidence_score=extracted_data.get('confidence_score', 0.0),
                raw_data=extracted_data
            )
            
            # Check confidence threshold
            warnings = []
            if credential.confidence_score < self.CONFIDENCE_THRESHOLD:
                warnings.append(f"Confidence score ({credential.confidence_score:.2f}) below threshold ({self.CONFIDENCE_THRESHOLD})")
            
            return DocumentProcessingResult(
                success=True,
                document_type='DIPLOMA',
                data=credential,
                confidence_score=credential.confidence_score,
                warnings=warnings
            )
            
        except Exception as e:
            return DocumentProcessingResult(
                success=False,
                document_type='DIPLOMA',
                error_message=f"Failed to extract diploma data: {str(e)}"
            )
    
    def extract_from_paystub(self, file_data: bytes, file_extension: str) -> DocumentProcessingResult:
        """Extract structured data from paystub or offer letter.
        
        Args:
            file_data: Raw file bytes
            file_extension: File extension (pdf, jpg, png, etc.)
            
        Returns:
            DocumentProcessingResult with EmploymentEvidence
        """
        try:
            prompt = """Extract the following information from this paystub/offer letter and return as JSON:
{
  "company_name": "Employer company name",
  "employee_name": "Employee full name",
  "job_title": "Job title or position",
  "pay_period_start": "YYYY-MM-DD",
  "pay_period_end": "YYYY-MM-DD",
  "start_date": "Employment start date YYYY-MM-DD if available",
  "end_date": "Employment end date YYYY-MM-DD if available",
  "document_type": "PAYSTUB or OFFER_LETTER",
  "confidence_score": 0.95
}

Return ONLY valid JSON. Use null for missing fields. Confidence score should be 0.0-1.0 based on document clarity."""
            
            # Extract data based on file type
            if file_extension.lower() == 'pdf':
                extracted_data = self._extract_from_pdf_text(file_data, prompt)
            else:
                extracted_data = self._extract_with_vision(file_data, prompt)
            
            # Parse dates
            pay_period_start = self._parse_date(extracted_data.get('pay_period_start'))
            pay_period_end = self._parse_date(extracted_data.get('pay_period_end'))
            start_date = self._parse_date(extracted_data.get('start_date'))
            end_date = self._parse_date(extracted_data.get('end_date'))
            
            # Create EmploymentEvidence object
            evidence = EmploymentEvidence(
                company_name=extracted_data.get('company_name', ''),
                employee_name=extracted_data.get('employee_name', ''),
                job_title=extracted_data.get('job_title', ''),
                start_date=start_date.date() if start_date else None,
                end_date=end_date.date() if end_date else None,
                pay_period_start=pay_period_start.date() if pay_period_start else None,
                pay_period_end=pay_period_end.date() if pay_period_end else None,
                document_type=extracted_data.get('document_type', 'PAYSTUB'),
                confidence_score=extracted_data.get('confidence_score', 0.0),
                raw_data=extracted_data
            )
            
            # Check confidence threshold
            warnings = []
            if evidence.confidence_score < self.CONFIDENCE_THRESHOLD:
                warnings.append(f"Confidence score ({evidence.confidence_score:.2f}) below threshold ({self.CONFIDENCE_THRESHOLD})")
            
            return DocumentProcessingResult(
                success=True,
                document_type='PAYSTUB',
                data=evidence,
                confidence_score=evidence.confidence_score,
                warnings=warnings
            )
            
        except Exception as e:
            return DocumentProcessingResult(
                success=False,
                document_type='PAYSTUB',
                error_message=f"Failed to extract paystub data: {str(e)}"
            )
