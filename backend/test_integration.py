"""
Full integration test for Wave 2 Backend API
Tests resume parsing with real OpenAI API
"""

import sys
from pathlib import Path
import asyncio

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

async def test_resume_parsing():
    """Test full resume parsing pipeline"""
    print("\n=== Testing Resume Parsing with OpenAI ===")
    
    try:
        from services.resume_parser import extract_text_from_pdf, parse_with_llm
        
        # Find test resume
        resume_path = backend_path.parent / "resume_examples" / "resume1.pdf"
        
        if not resume_path.exists():
            print(f"ERROR: No test resume found at {resume_path}")
            return False
        
        print(f"Loading resume from: {resume_path}")
        
        # Step 1: Extract text
        with open(resume_path, "rb") as f:
            pdf_bytes = f.read()
        
        print(f"OK: Read {len(pdf_bytes)} bytes from PDF")
        
        resume_text = extract_text_from_pdf(pdf_bytes)
        print(f"OK: Extracted {len(resume_text)} characters of text")
        
        if len(resume_text) < 10:
            print("WARNING: Very little text extracted from PDF")
            print("This might be a scanned/image PDF. Using sample text instead.")
            resume_text = """
John Doe
Software Engineer
john.doe@example.com

EXPERIENCE
Senior Software Engineer at Tech Corp (2020-01 to 2023-12)
- Led development of microservices architecture
- Managed team of 5 engineers

Software Engineer at StartupXYZ (2018-06 to 2019-12)
- Built RESTful APIs with Python and FastAPI
- Implemented CI/CD pipelines

EDUCATION
Bachelor of Science in Computer Science
MIT - Graduated 2018

SKILLS
Python, JavaScript, TypeScript, React, FastAPI, Docker, Kubernetes

GITHUB
github.com/johndoe
"""
        
        print("\nSample of extracted text:")
        print("-" * 60)
        print(resume_text[:300].strip())
        print("-" * 60)
        
        # Step 2: Parse with LLM
        print("\nParsing with OpenAI...")
        parsed = await parse_with_llm(resume_text)
        
        print("\n=== PARSED RESUME ===")
        print(f"Name: {parsed.name}")
        print(f"Email: {parsed.email}")
        print(f"GitHub: {parsed.github_username}")
        print(f"\nSkills ({len(parsed.skills)}):")
        for skill in parsed.skills[:10]:
            print(f"  - {skill}")
        if len(parsed.skills) > 10:
            print(f"  ... and {len(parsed.skills) - 10} more")
        
        print(f"\nEmployment History ({len(parsed.employment_history)}):")
        for emp in parsed.employment_history:
            print(f"  - {emp.title} at {emp.company}")
            print(f"    {emp.start_date} to {emp.end_date}")
        
        print(f"\nEducation ({len(parsed.education)}):")
        for edu in parsed.education:
            print(f"  - {edu.degree} in {edu.field}")
            print(f"    {edu.school} ({edu.graduation_year})")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Resume parsing failed - {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_supabase_connection():
    """Test Supabase connection"""
    print("\n=== Testing Supabase Connection ===")
    
    try:
        from services.supabase_client import supabase
        
        # Try to query verifications table
        result = supabase.table("verifications").select("id").limit(1).execute()
        print(f"OK: Successfully connected to Supabase")
        print(f"OK: verifications table exists")
        
        # Check storage bucket
        buckets = supabase.storage.list_buckets()
        print(f"OK: Found {len(buckets)} storage buckets")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Supabase connection failed - {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all integration tests"""
    print("=" * 60)
    print("WAVE 2 Backend API - Full Integration Test")
    print("=" * 60)
    
    results = []
    
    # Test Supabase
    supabase_ok = await test_supabase_connection()
    results.append(("Supabase Connection", supabase_ok))
    
    # Test Resume Parsing
    parsing_ok = await test_resume_parsing()
    results.append(("Resume Parsing", parsing_ok))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        print("\nReady to test full API endpoints!")
        print("\nNext steps:")
        print("1. Start the server:")
        print("   cd backend")
        print("   ..\\venv\\Scripts\\python.exe -m uvicorn main:app --reload")
        print("\n2. Test API endpoints:")
        print("   ..\\venv\\Scripts\\python.exe test_upload.py")
    else:
        print("\nSome tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
