"""Consistency validation for cross-referencing extracted data"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from src.core.document_models import CVData, EmploymentEvidence, EducationCredential, EmploymentHistory, EducationEntry


@dataclass
class Inconsistency:
    """Represents a detected inconsistency between documents"""
    type: str  # job_title_mismatch, date_mismatch, company_name_mismatch, etc.
    severity: str  # critical, moderate, minor
    description: str
    cv_value: Optional[Any] = None
    document_value: Optional[Any] = None
    field: Optional[str] = None
    employment_index: Optional[int] = None
    education_index: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'type': self.type,
            'severity': self.severity,
            'description': self.description,
            'cv_value': str(self.cv_value) if self.cv_value else None,
            'document_value': str(self.document_value) if self.document_value else None,
            'field': self.field,
            'employment_index': self.employment_index,
            'education_index': self.education_index
        }


@dataclass
class EmploymentGap:
    """Represents a gap in employment history"""
    start_date: date
    end_date: date
    duration_months: int
    previous_company: Optional[str] = None
    next_company: Optional[str] = None
    explanation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'duration_months': self.duration_months,
            'previous_company': self.previous_company,
            'next_company': self.next_company,
            'explanation': self.explanation
        }


class ConsistencyValidator:
    """Validates consistency between CV data and supporting documents"""
    
    # Threshold for considering dates as matching (in days)
    DATE_TOLERANCE_DAYS = 31  # ~1 month tolerance
    
    # Minimum gap duration to flag (in months)
    MIN_GAP_MONTHS = 3
    
    def __init__(self):
        """Initialize consistency validator"""
        pass
    
    def validate_employment_dates(
        self,
        cv_data: CVData,
        paystubs: List[EmploymentEvidence]
    ) -> List[Inconsistency]:
        """Validate employment dates between CV and paystubs.
        
        Args:
            cv_data: Extracted CV data
            paystubs: List of employment evidence documents
            
        Returns:
            List of detected inconsistencies
        """
        inconsistencies = []
        
        for emp_idx, employment in enumerate(cv_data.employment_history):
            # Find matching paystubs for this employment
            matching_paystubs = self._find_matching_paystubs(employment, paystubs)
            
            for paystub in matching_paystubs:
                # Check start date
                if employment.start_date and paystub.start_date:
                    if not self._dates_match(employment.start_date, paystub.start_date):
                        inconsistencies.append(Inconsistency(
                            type='date_mismatch',
                            severity='moderate',
                            description=f"Start date mismatch for {employment.company_name}",
                            cv_value=employment.start_date,
                            document_value=paystub.start_date,
                            field='start_date',
                            employment_index=emp_idx
                        ))
                
                # Check end date
                if employment.end_date and paystub.end_date:
                    if not self._dates_match(employment.end_date, paystub.end_date):
                        inconsistencies.append(Inconsistency(
                            type='date_mismatch',
                            severity='moderate',
                            description=f"End date mismatch for {employment.company_name}",
                            cv_value=employment.end_date,
                            document_value=paystub.end_date,
                            field='end_date',
                            employment_index=emp_idx
                        ))
                
                # Check job title
                if employment.job_title and paystub.job_title:
                    if not self._titles_match(employment.job_title, paystub.job_title):
                        inconsistencies.append(Inconsistency(
                            type='job_title_mismatch',
                            severity='minor',
                            description=f"Job title mismatch for {employment.company_name}",
                            cv_value=employment.job_title,
                            document_value=paystub.job_title,
                            field='job_title',
                            employment_index=emp_idx
                        ))
                
                # Check company name
                if not self._company_names_match(employment.company_name, paystub.company_name):
                    inconsistencies.append(Inconsistency(
                        type='company_name_mismatch',
                        severity='critical',
                        description=f"Company name mismatch",
                        cv_value=employment.company_name,
                        document_value=paystub.company_name,
                        field='company_name',
                        employment_index=emp_idx
                    ))
        
        return inconsistencies
    
    def validate_education(
        self,
        cv_data: CVData,
        diplomas: List[EducationCredential]
    ) -> List[Inconsistency]:
        """Validate education credentials between CV and diplomas.
        
        Args:
            cv_data: Extracted CV data
            diplomas: List of education credentials
            
        Returns:
            List of detected inconsistencies
        """
        inconsistencies = []
        
        for edu_idx, education in enumerate(cv_data.education):
            # Find matching diplomas
            matching_diplomas = self._find_matching_diplomas(education, diplomas)
            
            for diploma in matching_diplomas:
                # Check graduation date
                if education.graduation_date and diploma.graduation_date:
                    if not self._dates_match(education.graduation_date, diploma.graduation_date):
                        inconsistencies.append(Inconsistency(
                            type='date_mismatch',
                            severity='moderate',
                            description=f"Graduation date mismatch for {education.institution_name}",
                            cv_value=education.graduation_date,
                            document_value=diploma.graduation_date,
                            field='graduation_date',
                            education_index=edu_idx
                        ))
                
                # Check degree type
                if education.degree_type and diploma.degree_type:
                    if not self._degree_types_match(education.degree_type, diploma.degree_type):
                        inconsistencies.append(Inconsistency(
                            type='degree_mismatch',
                            severity='moderate',
                            description=f"Degree type mismatch for {education.institution_name}",
                            cv_value=education.degree_type,
                            document_value=diploma.degree_type,
                            field='degree_type',
                            education_index=edu_idx
                        ))
                
                # Check institution name
                if not self._institution_names_match(education.institution_name, diploma.institution_name):
                    inconsistencies.append(Inconsistency(
                        type='institution_mismatch',
                        severity='critical',
                        description=f"Institution name mismatch",
                        cv_value=education.institution_name,
                        document_value=diploma.institution_name,
                        field='institution_name',
                        education_index=edu_idx
                    ))
                
                # Check major
                if education.major and diploma.major:
                    if not self._majors_match(education.major, diploma.major):
                        inconsistencies.append(Inconsistency(
                            type='major_mismatch',
                            severity='minor',
                            description=f"Major/field mismatch for {education.institution_name}",
                            cv_value=education.major,
                            document_value=diploma.major,
                            field='major',
                            education_index=edu_idx
                        ))
        
        return inconsistencies
    
    def detect_gaps(self, employment_history: List[EmploymentHistory]) -> List[EmploymentGap]:
        """Detect gaps in employment history.
        
        Args:
            employment_history: List of employment entries from CV
            
        Returns:
            List of detected employment gaps
        """
        gaps = []
        
        # Sort employment by start date
        sorted_employment = sorted(
            [e for e in employment_history if e.start_date],
            key=lambda x: x.start_date
        )
        
        # Check for gaps between consecutive employments
        for i in range(len(sorted_employment) - 1):
            current = sorted_employment[i]
            next_emp = sorted_employment[i + 1]
            
            # Get end date of current employment
            end_date = current.end_date if current.end_date else date.today()
            
            # Calculate gap
            if next_emp.start_date > end_date:
                gap_days = (next_emp.start_date - end_date).days
                gap_months = gap_days // 30
                
                # Only flag gaps longer than threshold
                if gap_months >= self.MIN_GAP_MONTHS:
                    gaps.append(EmploymentGap(
                        start_date=end_date,
                        end_date=next_emp.start_date,
                        duration_months=gap_months,
                        previous_company=current.company_name,
                        next_company=next_emp.company_name
                    ))
        
        return gaps
    
    def _find_matching_paystubs(
        self,
        employment: EmploymentHistory,
        paystubs: List[EmploymentEvidence]
    ) -> List[EmploymentEvidence]:
        """Find paystubs that match an employment entry.
        
        Args:
            employment: Employment entry from CV
            paystubs: List of paystubs
            
        Returns:
            List of matching paystubs
        """
        matches = []
        
        for paystub in paystubs:
            # Check if company names match (fuzzy)
            if self._company_names_match(employment.company_name, paystub.company_name):
                matches.append(paystub)
            # Or if dates overlap
            elif employment.start_date and paystub.pay_period_start:
                if self._date_ranges_overlap(
                    employment.start_date,
                    employment.end_date or date.today(),
                    paystub.pay_period_start,
                    paystub.pay_period_end or paystub.pay_period_start
                ):
                    matches.append(paystub)
        
        return matches
    
    def _find_matching_diplomas(
        self,
        education: EducationEntry,
        diplomas: List[EducationCredential]
    ) -> List[EducationCredential]:
        """Find diplomas that match an education entry.
        
        Args:
            education: Education entry from CV
            diplomas: List of diplomas
            
        Returns:
            List of matching diplomas
        """
        matches = []
        
        for diploma in diplomas:
            # Check if institution names match (fuzzy)
            if self._institution_names_match(education.institution_name, diploma.institution_name):
                matches.append(diploma)
        
        return matches
    
    def _dates_match(self, date1: date, date2: date) -> bool:
        """Check if two dates match within tolerance.
        
        Args:
            date1: First date
            date2: Second date
            
        Returns:
            True if dates match within tolerance
        """
        diff_days = abs((date1 - date2).days)
        return diff_days <= self.DATE_TOLERANCE_DAYS
    
    def _date_ranges_overlap(
        self,
        start1: date,
        end1: date,
        start2: date,
        end2: date
    ) -> bool:
        """Check if two date ranges overlap.
        
        Args:
            start1: Start of first range
            end1: End of first range
            start2: Start of second range
            end2: End of second range
            
        Returns:
            True if ranges overlap
        """
        return start1 <= end2 and start2 <= end1
    
    def _company_names_match(self, name1: str, name2: str) -> bool:
        """Check if company names match (fuzzy).
        
        Args:
            name1: First company name
            name2: Second company name
            
        Returns:
            True if names likely refer to same company
        """
        # Normalize names
        n1 = self._normalize_name(name1)
        n2 = self._normalize_name(name2)
        
        # Exact match
        if n1 == n2:
            return True
        
        # Check if one contains the other
        if n1 in n2 or n2 in n1:
            return True
        
        # Check similarity (simple approach)
        return self._string_similarity(n1, n2) > 0.8
    
    def _institution_names_match(self, name1: str, name2: str) -> bool:
        """Check if institution names match (fuzzy).
        
        Args:
            name1: First institution name
            name2: Second institution name
            
        Returns:
            True if names likely refer to same institution
        """
        return self._company_names_match(name1, name2)
    
    def _titles_match(self, title1: str, title2: str) -> bool:
        """Check if job titles match (fuzzy).
        
        Args:
            title1: First job title
            title2: Second job title
            
        Returns:
            True if titles are similar enough
        """
        # Normalize titles
        t1 = self._normalize_name(title1)
        t2 = self._normalize_name(title2)
        
        # Exact match
        if t1 == t2:
            return True
        
        # Check similarity
        return self._string_similarity(t1, t2) > 0.7
    
    def _degree_types_match(self, degree1: str, degree2: str) -> bool:
        """Check if degree types match.
        
        Args:
            degree1: First degree type
            degree2: Second degree type
            
        Returns:
            True if degree types match
        """
        # Normalize
        d1 = self._normalize_name(degree1)
        d2 = self._normalize_name(degree2)
        
        # Common abbreviations
        abbreviations = {
            'bachelor': ['bs', 'ba', 'bsc', 'bachelor'],
            'master': ['ms', 'ma', 'msc', 'master'],
            'phd': ['phd', 'doctorate', 'doctoral'],
            'associate': ['aa', 'as', 'associate']
        }
        
        # Check if both belong to same category
        for category, variants in abbreviations.items():
            if any(v in d1 for v in variants) and any(v in d2 for v in variants):
                return True
        
        return d1 == d2
    
    def _majors_match(self, major1: str, major2: str) -> bool:
        """Check if majors match.
        
        Args:
            major1: First major
            major2: Second major
            
        Returns:
            True if majors match
        """
        return self._titles_match(major1, major2)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize a name for comparison.
        
        Args:
            name: Name to normalize
            
        Returns:
            Normalized name
        """
        # Convert to lowercase
        normalized = name.lower().strip()
        
        # Remove common suffixes
        suffixes = [' inc', ' inc.', ' llc', ' ltd', ' ltd.', ' corp', ' corp.', ' co', ' co.']
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
        
        # Remove punctuation
        normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate simple string similarity.
        
        Args:
            s1: First string
            s2: Second string
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        # Simple Jaccard similarity on words
        words1 = set(s1.split())
        words2 = set(s2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
