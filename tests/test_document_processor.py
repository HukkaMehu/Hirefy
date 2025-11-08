"""Test script for document processor functionality"""

import os
from src.core.document_processor import DocumentProcessor
from src.utils.file_validator import FileValidator


def test_file_validator():
    """Test file validation"""
    print("\n=== Testing File Validator ===")
    
    # Test allowed extensions
    print("\n1. Testing allowed extensions:")
    test_files = [
        "resume.pdf",
        "diploma.jpg",
        "paystub.png",
        "document.heic",
        "invalid.doc",
        "test.txt"
    ]
    
    for filename in test_files:
        is_allowed = FileValidator.allowed_file(filename)
        status = "✅ ALLOWED" if is_allowed else "❌ REJECTED"
        print(f"   {filename}: {status}")
    
    # Test extension extraction
    print("\n2. Testing extension extraction:")
    for filename in test_files:
        ext = FileValidator.get_file_extension(filename)
        print(f"   {filename} -> {ext}")


def test_document_processor():
    """Test document processor initialization"""
    print("\n=== Testing Document Processor ===")
    
    try:
        # Check if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            print("   Set it in .env file to test document processing")
            return
        
        # Initialize processor
        processor = DocumentProcessor()
        print("✅ DocumentProcessor initialized successfully")
        print(f"   API Key: {api_key[:10]}...{api_key[-4:]}")
        print(f"   Confidence Threshold: {processor.CONFIDENCE_THRESHOLD}")
        
        # Test date parsing
        print("\n Testing date parsing:")
        test_dates = [
            "2023-01-15",
            "01/15/2023",
            "January 2023",
            "2023",
            "Present",
            None
        ]
        
        for date_str in test_dates:
            parsed = processor._parse_date(date_str)
            if parsed:
                print(f"   '{date_str}' -> {parsed.date()}")
            else:
                print(f"   '{date_str}' -> None")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_data_models():
    """Test data model creation and serialization"""
    print("\n=== Testing Data Models ===")
    
    from src.core.document_models import (
        CVData, EmploymentHistory, EducationEntry,
        EmploymentEvidence, EducationCredential
    )
    from datetime import date
    
    # Test EmploymentHistory
    print("\n1. Testing EmploymentHistory:")
    emp = EmploymentHistory(
        company_name="Tech Corp",
        job_title="Senior Developer",
        start_date=date(2020, 1, 1),
        end_date=date(2023, 12, 31),
        description="Developed awesome software",
        location="San Francisco, CA",
        confidence_score=0.95
    )
    print(f"   Created: {emp.company_name} - {emp.job_title}")
    print(f"   Serialized: {emp.to_dict()}")
    
    # Test CVData
    print("\n2. Testing CVData:")
    cv = CVData(
        candidate_name="John Doe",
        email="john@example.com",
        phone="+1-555-0123",
        employment_history=[emp],
        skills=["Python", "JavaScript", "React"],
        confidence_score=0.92
    )
    print(f"   Created: {cv.candidate_name}")
    print(f"   Employment entries: {len(cv.employment_history)}")
    print(f"   Skills: {len(cv.skills)}")
    
    # Test EmploymentEvidence
    print("\n3. Testing EmploymentEvidence:")
    evidence = EmploymentEvidence(
        company_name="Tech Corp",
        employee_name="John Doe",
        job_title="Senior Developer",
        pay_period_start=date(2023, 1, 1),
        pay_period_end=date(2023, 1, 15),
        confidence_score=0.88
    )
    print(f"   Created: {evidence.company_name} - {evidence.job_title}")
    print(f"   Pay period: {evidence.pay_period_start} to {evidence.pay_period_end}")
    
    # Test EducationCredential
    print("\n4. Testing EducationCredential:")
    credential = EducationCredential(
        institution_name="Stanford University",
        degree_type="Bachelor's",
        major="Computer Science",
        graduation_date=date(2019, 6, 15),
        gpa=3.8,
        confidence_score=0.93
    )
    print(f"   Created: {credential.degree_type} in {credential.major}")
    print(f"   Institution: {credential.institution_name}")
    print(f"   GPA: {credential.gpa}")
    
    print("\n✅ All data models working correctly")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Document Processing System Tests")
    print("=" * 60)
    
    test_file_validator()
    test_data_models()
    test_document_processor()
    
    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
