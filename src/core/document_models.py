"""Data models for document extraction results"""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict, Any


@dataclass
class EmploymentEvidence:
    """Evidence of employment from paystub or offer letter"""
    company_name: str
    employee_name: str
    job_title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    pay_period_start: Optional[date] = None
    pay_period_end: Optional[date] = None
    document_type: str = "PAYSTUB"  # PAYSTUB, OFFER_LETTER, etc.
    confidence_score: float = 0.0
    raw_data: Dict[str, Any] = field(default_factory=dict)
    extraction_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'company_name': self.company_name,
            'employee_name': self.employee_name,
            'job_title': self.job_title,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'pay_period_start': self.pay_period_start.isoformat() if self.pay_period_start else None,
            'pay_period_end': self.pay_period_end.isoformat() if self.pay_period_end else None,
            'document_type': self.document_type,
            'confidence_score': self.confidence_score,
            'raw_data': self.raw_data,
            'extraction_notes': self.extraction_notes
        }


@dataclass
class EducationCredential:
    """Education credential from diploma or transcript"""
    institution_name: str
    degree_type: str
    major: Optional[str] = None
    graduation_date: Optional[date] = None
    gpa: Optional[float] = None
    honors: Optional[str] = None
    document_type: str = "DIPLOMA"  # DIPLOMA, TRANSCRIPT, CERTIFICATE
    confidence_score: float = 0.0
    raw_data: Dict[str, Any] = field(default_factory=dict)
    extraction_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'institution_name': self.institution_name,
            'degree_type': self.degree_type,
            'major': self.major,
            'graduation_date': self.graduation_date.isoformat() if self.graduation_date else None,
            'gpa': self.gpa,
            'honors': self.honors,
            'document_type': self.document_type,
            'confidence_score': self.confidence_score,
            'raw_data': self.raw_data,
            'extraction_notes': self.extraction_notes
        }


@dataclass
class EmploymentHistory:
    """Single employment entry from CV"""
    company_name: str
    job_title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    description: str = ""
    location: Optional[str] = None
    is_current: bool = False
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'company_name': self.company_name,
            'job_title': self.job_title,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'description': self.description,
            'location': self.location,
            'is_current': self.is_current,
            'confidence_score': self.confidence_score
        }


@dataclass
class EducationEntry:
    """Single education entry from CV"""
    institution_name: str
    degree_type: str
    major: Optional[str] = None
    graduation_date: Optional[date] = None
    gpa: Optional[float] = None
    location: Optional[str] = None
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'institution_name': self.institution_name,
            'degree_type': self.degree_type,
            'major': self.major,
            'graduation_date': self.graduation_date.isoformat() if self.graduation_date else None,
            'gpa': self.gpa,
            'location': self.location,
            'confidence_score': self.confidence_score
        }


@dataclass
class CVData:
    """Structured data extracted from CV/Resume"""
    candidate_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    employment_history: List[EmploymentHistory] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    summary: str = ""
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    confidence_score: float = 0.0
    raw_data: Dict[str, Any] = field(default_factory=dict)
    extraction_notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'candidate_name': self.candidate_name,
            'email': self.email,
            'phone': self.phone,
            'employment_history': [emp.to_dict() for emp in self.employment_history],
            'education': [edu.to_dict() for edu in self.education],
            'skills': self.skills,
            'certifications': self.certifications,
            'summary': self.summary,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'confidence_score': self.confidence_score,
            'raw_data': self.raw_data,
            'extraction_notes': self.extraction_notes
        }


@dataclass
class DocumentProcessingResult:
    """Result of document processing operation"""
    success: bool
    document_type: str
    data: Optional[Any] = None  # CVData, EducationCredential, or EmploymentEvidence
    confidence_score: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            'success': self.success,
            'document_type': self.document_type,
            'confidence_score': self.confidence_score,
            'error_message': self.error_message,
            'warnings': self.warnings
        }
        
        if self.data:
            if hasattr(self.data, 'to_dict'):
                result['data'] = self.data.to_dict()
            else:
                result['data'] = self.data
        
        return result
