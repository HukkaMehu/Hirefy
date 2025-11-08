"""Session management for document collection"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

from src.core.document_models import CVData, EmploymentEvidence, EducationCredential
from src.core.consistency_validator import Inconsistency, EmploymentGap


class CollectionStage(Enum):
    """Stages of document collection process"""
    INITIAL = "INITIAL"
    AWAITING_CV = "AWAITING_CV"
    CV_PROCESSED = "CV_PROCESSED"
    COLLECTING_EMPLOYMENT_DOCS = "COLLECTING_EMPLOYMENT_DOCS"
    COLLECTING_EDUCATION_DOCS = "COLLECTING_EDUCATION_DOCS"
    RESOLVING_CONFLICTS = "RESOLVING_CONFLICTS"
    EXPLAINING_GAPS = "EXPLAINING_GAPS"
    FINAL_CONFIRMATION = "FINAL_CONFIRMATION"
    COMPLETED = "COMPLETED"


@dataclass
class DocumentRecord:
    """Record of an uploaded document"""
    document_id: str
    document_type: str  # cv, paystub, diploma
    filename: str
    uploaded_at: datetime
    file_path: Optional[str] = None
    extracted_data: Optional[Any] = None
    confidence_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'document_id': self.document_id,
            'document_type': self.document_type,
            'filename': self.filename,
            'uploaded_at': self.uploaded_at.isoformat(),
            'file_path': self.file_path,
            'confidence_score': self.confidence_score
        }


@dataclass
class ConversationMessage:
    """Single message in conversation"""
    role: str  # user or assistant
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class CollectionSession:
    """Manages state for a document collection session"""
    session_id: str
    verification_session_id: str
    candidate_name: Optional[str] = None
    stage: CollectionStage = CollectionStage.INITIAL
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Conversation history
    conversation_history: List[ConversationMessage] = field(default_factory=list)
    
    # Uploaded documents
    documents: List[DocumentRecord] = field(default_factory=list)
    
    # Extracted data
    cv_data: Optional[CVData] = None
    paystubs: List[EmploymentEvidence] = field(default_factory=list)
    diplomas: List[EducationCredential] = field(default_factory=list)
    
    # Validation results
    inconsistencies: List[Inconsistency] = field(default_factory=list)
    employment_gaps: List[EmploymentGap] = field(default_factory=list)
    
    # Tracking
    pending_employment_docs: List[Dict[str, Any]] = field(default_factory=list)
    pending_education_docs: List[Dict[str, Any]] = field(default_factory=list)
    resolved_conflicts: List[str] = field(default_factory=list)
    explained_gaps: List[str] = field(default_factory=list)
    
    # Flags
    cv_uploaded: bool = False
    conflicts_resolved: bool = False
    gaps_explained: bool = False
    final_confirmation: bool = False
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to conversation history.
        
        Args:
            role: Message role (user or assistant)
            content: Message content
            metadata: Optional metadata
        """
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        self.conversation_history.append(message)
        self.updated_at = datetime.utcnow()
    
    def add_document(
        self,
        document_id: str,
        document_type: str,
        filename: str,
        file_path: Optional[str] = None,
        extracted_data: Optional[Any] = None,
        confidence_score: float = 0.0
    ) -> DocumentRecord:
        """Add a document record.
        
        Args:
            document_id: Unique document ID
            document_type: Type of document
            filename: Original filename
            file_path: Path where file is stored
            extracted_data: Extracted data from document
            confidence_score: Confidence score
            
        Returns:
            Created document record
        """
        doc = DocumentRecord(
            document_id=document_id,
            document_type=document_type,
            filename=filename,
            uploaded_at=datetime.utcnow(),
            file_path=file_path,
            extracted_data=extracted_data,
            confidence_score=confidence_score
        )
        self.documents.append(doc)
        self.updated_at = datetime.utcnow()
        return doc
    
    def get_conversation_for_ai(self) -> List[Dict[str, str]]:
        """Get conversation history formatted for AI.
        
        Returns:
            List of message dictionaries
        """
        return [
            {'role': msg.role, 'content': msg.content}
            for msg in self.conversation_history
        ]
    
    def get_context_for_ai(self) -> Dict[str, Any]:
        """Get current context for AI.
        
        Returns:
            Context dictionary
        """
        context = {
            'stage': self.stage.value,
            'documents_collected': [doc.document_type for doc in self.documents],
            'cv_uploaded': self.cv_uploaded
        }
        
        # Add CV data if available
        if self.cv_data:
            context['cv_data'] = {
                'candidate_name': self.cv_data.candidate_name,
                'employment_history': [
                    {
                        'company_name': emp.company_name,
                        'job_title': emp.job_title,
                        'start_date': emp.start_date.isoformat() if emp.start_date else None,
                        'end_date': emp.end_date.isoformat() if emp.end_date else None
                    }
                    for emp in self.cv_data.employment_history
                ],
                'education': [
                    {
                        'institution_name': edu.institution_name,
                        'degree_type': edu.degree_type,
                        'graduation_date': edu.graduation_date.isoformat() if edu.graduation_date else None
                    }
                    for edu in self.cv_data.education
                ]
            }
        
        # Add pending requests
        if self.pending_employment_docs:
            context['pending_requests'] = [
                f"Paystub for {doc['company_name']}"
                for doc in self.pending_employment_docs
            ]
        
        if self.pending_education_docs:
            if 'pending_requests' not in context:
                context['pending_requests'] = []
            context['pending_requests'].extend([
                f"Diploma from {doc['institution_name']}"
                for doc in self.pending_education_docs
            ])
        
        # Add conflicts
        if self.inconsistencies:
            context['conflicts'] = [inc.to_dict() for inc in self.inconsistencies]
        
        # Add gaps
        if self.employment_gaps:
            context['gaps'] = [gap.to_dict() for gap in self.employment_gaps]
        
        # Add next action
        if self.stage == CollectionStage.AWAITING_CV:
            context['next_action'] = "Request CV upload"
        elif self.stage == CollectionStage.COLLECTING_EMPLOYMENT_DOCS:
            context['next_action'] = "Request employment verification documents"
        elif self.stage == CollectionStage.COLLECTING_EDUCATION_DOCS:
            context['next_action'] = "Request education credentials"
        elif self.stage == CollectionStage.RESOLVING_CONFLICTS:
            context['next_action'] = "Resolve detected conflicts"
        elif self.stage == CollectionStage.EXPLAINING_GAPS:
            context['next_action'] = "Get explanations for employment gaps"
        elif self.stage == CollectionStage.FINAL_CONFIRMATION:
            context['next_action'] = "Get final confirmation"
        
        return context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            'session_id': self.session_id,
            'verification_session_id': self.verification_session_id,
            'candidate_name': self.candidate_name,
            'stage': self.stage.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'conversation_history': [msg.to_dict() for msg in self.conversation_history],
            'documents': [doc.to_dict() for doc in self.documents],
            'cv_uploaded': self.cv_uploaded,
            'conflicts_resolved': self.conflicts_resolved,
            'gaps_explained': self.gaps_explained,
            'final_confirmation': self.final_confirmation,
            'inconsistencies_count': len(self.inconsistencies),
            'gaps_count': len(self.employment_gaps)
        }
