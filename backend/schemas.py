from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class VerificationResponseV1(BaseModel):
    verification_id: str
    status: Literal["processing", "complete", "failed"]
    message: str
    created_at: datetime

class Employment(BaseModel):
    company: str
    title: str
    start_date: str  # YYYY-MM format
    end_date: str
    description: str

class Education(BaseModel):
    school: str
    degree: str
    field: str
    graduation_year: int

class ParsedResume(BaseModel):
    name: str
    email: Optional[str] = None
    employment_history: list[Employment]
    education: list[Education]
    skills: list[str]
    github_username: Optional[str] = None
