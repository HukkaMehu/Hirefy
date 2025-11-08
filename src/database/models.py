"""SQLAlchemy database models for AI Recruitment Verification Platform"""

from datetime import datetime
from enum import Enum as PyEnum
import uuid
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Enums
class VerificationStatus(PyEnum):
    """Status of a verification session"""
    PENDING_DOCUMENTS = "PENDING_DOCUMENTS"
    DOCUMENTS_COLLECTED = "DOCUMENTS_COLLECTED"
    VERIFICATION_IN_PROGRESS = "VERIFICATION_IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EmploymentVerificationStatus(PyEnum):
    """Status of employment verification"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTED = "CONFLICTED"


class EducationVerificationStatus(PyEnum):
    """Status of education credential verification"""
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class FraudFlagType(PyEnum):
    """Types of fraud flags"""
    TIMELINE_CONFLICT = "TIMELINE_CONFLICT"
    UNVERIFIED_CREDENTIAL = "UNVERIFIED_CREDENTIAL"
    TECHNICAL_MISMATCH = "TECHNICAL_MISMATCH"
    DOCUMENT_ANOMALY = "DOCUMENT_ANOMALY"


class FraudSeverity(PyEnum):
    """Severity levels for fraud flags"""
    CRITICAL = "CRITICAL"
    MODERATE = "MODERATE"
    MINOR = "MINOR"


class RiskScore(PyEnum):
    """Risk score colors"""
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class DataSource(PyEnum):
    """Source of data"""
    CV = "CV"
    PAYSTUB = "PAYSTUB"
    DIPLOMA = "DIPLOMA"
    VERIFIED = "VERIFIED"


# Models
class VerificationSession(db.Model):
    """Main verification session tracking"""
    __tablename__ = 'verification_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_id = db.Column(db.String(36), db.ForeignKey('candidates.id'), nullable=False)
    hiring_company_id = db.Column(db.String(36), nullable=True)  # Optional for MVP
    status = db.Column(db.Enum(VerificationStatus), nullable=False, default=VerificationStatus.PENDING_DOCUMENTS)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    estimated_completion = db.Column(db.DateTime, nullable=True)
    risk_score = db.Column(db.Enum(RiskScore), nullable=True)
    
    # Relationships
    candidate = db.relationship('Candidate', back_populates='verification_sessions')
    employments = db.relationship('Employment', back_populates='verification_session', cascade='all, delete-orphan')
    education_credentials = db.relationship('EducationCredential', back_populates='verification_session', cascade='all, delete-orphan')
    fraud_flags = db.relationship('FraudFlag', back_populates='verification_session', cascade='all, delete-orphan')
    verification_report = db.relationship('VerificationReport', back_populates='verification_session', uselist=False, cascade='all, delete-orphan')
    contact_records = db.relationship('ContactRecord', back_populates='verification_session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VerificationSession {self.id} - {self.status.value}>'


class Candidate(db.Model):
    """Candidate information"""
    __tablename__ = 'candidates'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=True)
    consent_signed_at = db.Column(db.DateTime, nullable=True)
    consent_document_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    verification_sessions = db.relationship('VerificationSession', back_populates='candidate', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Candidate {self.full_name}>'


class Employment(db.Model):
    """Employment history record"""
    __tablename__ = 'employments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    verification_session_id = db.Column(db.String(36), db.ForeignKey('verification_sessions.id'), nullable=False)
    company_name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    source = db.Column(db.Enum(DataSource), nullable=False, default=DataSource.CV)
    verification_status = db.Column(db.Enum(EmploymentVerificationStatus), nullable=False, default=EmploymentVerificationStatus.PENDING)
    hr_contact_info = db.Column(db.JSON, nullable=True)  # Store contact details as JSON
    verification_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    verification_session = db.relationship('VerificationSession', back_populates='employments')
    
    def __repr__(self):
        return f'<Employment {self.company_name} - {self.job_title}>'


class EducationCredential(db.Model):
    """Education credential record"""
    __tablename__ = 'education_credentials'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    verification_session_id = db.Column(db.String(36), db.ForeignKey('verification_sessions.id'), nullable=False)
    institution_name = db.Column(db.String(255), nullable=False)
    degree_type = db.Column(db.String(100), nullable=False)
    major = db.Column(db.String(255), nullable=True)
    graduation_date = db.Column(db.Date, nullable=False)
    source = db.Column(db.Enum(DataSource), nullable=False, default=DataSource.CV)
    verification_status = db.Column(db.Enum(EducationVerificationStatus), nullable=False, default=EducationVerificationStatus.PENDING)
    verification_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    verification_session = db.relationship('VerificationSession', back_populates='education_credentials')
    
    def __repr__(self):
        return f'<EducationCredential {self.degree_type} from {self.institution_name}>'


class FraudFlag(db.Model):
    """Fraud detection flag"""
    __tablename__ = 'fraud_flags'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    verification_session_id = db.Column(db.String(36), db.ForeignKey('verification_sessions.id'), nullable=False)
    flag_type = db.Column(db.Enum(FraudFlagType), nullable=False)
    severity = db.Column(db.Enum(FraudSeverity), nullable=False)
    description = db.Column(db.Text, nullable=False)
    evidence = db.Column(db.JSON, nullable=True)  # Store supporting evidence as JSON
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    verification_session = db.relationship('VerificationSession', back_populates='fraud_flags')
    
    def __repr__(self):
        return f'<FraudFlag {self.flag_type.value} - {self.severity.value}>'


class VerificationReport(db.Model):
    """Final verification report"""
    __tablename__ = 'verification_reports'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    verification_session_id = db.Column(db.String(36), db.ForeignKey('verification_sessions.id'), nullable=False, unique=True)
    risk_score = db.Column(db.Enum(RiskScore), nullable=False)
    summary_narrative = db.Column(db.Text, nullable=True)
    employment_narratives = db.Column(db.JSON, nullable=True)  # List of employment narratives
    education_summary = db.Column(db.Text, nullable=True)
    technical_validation = db.Column(db.JSON, nullable=True)  # Technical profile analysis
    interview_questions = db.Column(db.JSON, nullable=True)  # List of suggested questions
    report_data = db.Column(db.JSON, nullable=True)  # Full report as JSON
    report_pdf_url = db.Column(db.String(500), nullable=True)
    generated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    verification_session = db.relationship('VerificationSession', back_populates='verification_report')
    
    def __repr__(self):
        return f'<VerificationReport {self.id} - {self.risk_score.value}>'


class ContactRecord(db.Model):
    """Record of all verification contact attempts"""
    __tablename__ = 'contact_records'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    verification_session_id = db.Column(db.String(36), db.ForeignKey('verification_sessions.id'), nullable=False)
    contact_type = db.Column(db.String(50), nullable=False)  # 'HR', 'REFERENCE', 'EDUCATION'
    contact_method = db.Column(db.String(50), nullable=False)  # 'PHONE', 'EMAIL', 'FAX'
    contact_name = db.Column(db.String(255), nullable=True)
    contact_info = db.Column(db.String(255), nullable=False)  # Phone/email/fax
    attempt_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    response_received = db.Column(db.Boolean, nullable=False, default=False)
    response_timestamp = db.Column(db.DateTime, nullable=True)
    response_data = db.Column(db.JSON, nullable=True)  # Store response details
    transcript_url = db.Column(db.String(500), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    verification_session = db.relationship('VerificationSession', back_populates='contact_records')
    
    def __repr__(self):
        return f'<ContactRecord {self.contact_type} via {self.contact_method}>'


class GitHubAnalysisRecord(db.Model):
    """GitHub profile analysis results"""
    __tablename__ = 'github_analyses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    verification_session_id = db.Column(db.String(36), db.ForeignKey('verification_sessions.id'), nullable=False, unique=True)
    username = db.Column(db.String(255), nullable=False)
    profile_found = db.Column(db.Boolean, nullable=False, default=False)
    total_repos = db.Column(db.Integer, nullable=False, default=0)
    owned_repos = db.Column(db.Integer, nullable=False, default=0)
    total_commits = db.Column(db.Integer, nullable=False, default=0)
    commit_frequency = db.Column(db.Float, nullable=False, default=0.0)
    languages = db.Column(db.JSON, nullable=True)  # Language distribution
    contribution_timeline = db.Column(db.JSON, nullable=True)  # Year-month commit counts
    code_quality_score = db.Column(db.Integer, nullable=False, default=0)
    skills_match = db.Column(db.JSON, nullable=True)  # Skills comparison results
    mismatches = db.Column(db.JSON, nullable=True)  # List of skill mismatches
    profile_url = db.Column(db.String(500), nullable=True)
    analysis_notes = db.Column(db.Text, nullable=True)
    analyzed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    verification_session = db.relationship('VerificationSession', backref='github_analysis', uselist=False)
    
    def __repr__(self):
        return f'<GitHubAnalysisRecord {self.username} - Score: {self.code_quality_score}>'
