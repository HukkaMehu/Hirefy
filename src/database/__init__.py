"""Database package for AI Recruitment Verification Platform"""

from .models import db, VerificationSession, Candidate, Employment, EducationCredential, FraudFlag, VerificationReport, ContactRecord
from .init_db import init_database

__all__ = [
    'db',
    'VerificationSession',
    'Candidate',
    'Employment',
    'EducationCredential',
    'FraudFlag',
    'VerificationReport',
    'ContactRecord',
    'init_database'
]
