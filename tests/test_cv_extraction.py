"""Test CV extraction to debug the issue"""

import os
from dotenv import load_dotenv
from src.core.document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

def test_cv_extraction():
    """Test CV extraction with a sample file"""
    
    # Initialize processor
    processor = DocumentProcessor()
    
    # Check if we have a test CV file
    test_file = "Touko Ursin CV BCG 2025.pdf"
    
    if not os.path.exists(test_file):
        print(f"Test file '{test_file}' not found in current directory")
        print("Please place a CV file in the current directory and update the filename")
        return
    
    print(f"Testing CV extraction with: {test_file}")
    print("-" * 60)
    
    # Read file
    with open(test_file, 'rb') as f:
        file_data = f.read()
    
    print(f"File size: {len(file_data)} bytes")
    
    # Extract data
    result = processor.extract_from_cv(file_data, 'pdf')
    
    print("\n" + "=" * 60)
    print("EXTRACTION RESULT")
    print("=" * 60)
    
    if result.success:
        print(f"✓ Success!")
        print(f"Confidence Score: {result.confidence_score}")
        print(f"\nCandidate Name: {result.data.candidate_name}")
        print(f"Email: {result.data.email}")
        print(f"Phone: {result.data.phone}")
        
        print(f"\nEmployment History ({len(result.data.employment_history)} entries):")
        for i, emp in enumerate(result.data.employment_history, 1):
            print(f"  {i}. {emp.job_title} at {emp.company_name}")
            print(f"     {emp.start_date} - {emp.end_date or 'Present'}")
        
        print(f"\nEducation ({len(result.data.education)} entries):")
        for i, edu in enumerate(result.data.education, 1):
            print(f"  {i}. {edu.degree_type} in {edu.major or 'N/A'}")
            print(f"     {edu.institution_name}")
            print(f"     Graduated: {edu.graduation_date or 'N/A'}")
        
        skills = result.data.skills or []
        print(f"\nSkills ({len(skills)}):")
        if skills:
            print(f"  {', '.join(skills[:10])}")
            if len(skills) > 10:
                print(f"  ... and {len(skills) - 10} more")
        
        if result.warnings:
            print(f"\nWarnings:")
            for warning in result.warnings:
                print(f"  ⚠ {warning}")
    else:
        print(f"✗ Failed!")
        print(f"Error: {result.error_message}")
        if result.warnings:
            print(f"\nWarnings:")
            for warning in result.warnings:
                print(f"  ⚠ {warning}")

if __name__ == '__main__':
    test_cv_extraction()
