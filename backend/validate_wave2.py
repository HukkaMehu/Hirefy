"""
Quick validation script for Wave 2 Backend API
Checks that all components are working without requiring a running server
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test all imports work"""
    print("\n=== Testing Imports ===")
    try:
        from schemas import ParsedResume, VerificationResponseV1, Employment, Education
        print("OK: schemas imported")
        
        from services.resume_parser import extract_text_from_pdf, parse_with_llm
        print("OK: resume_parser imported")
        
        from main import app
        print("OK: FastAPI app imported")
        
        return True
    except Exception as e:
        print(f"ERROR: Import failed - {e}")
        return False

def test_schemas():
    """Test Pydantic schemas"""
    print("\n=== Testing Schemas ===")
    try:
        from schemas import Employment, Education, ParsedResume
        from datetime import datetime
        
        # Test Employment
        emp = Employment(
            company="Test Corp",
            title="Software Engineer",
            start_date="2020-01",
            end_date="2022-12",
            description="Built things"
        )
        print(f"OK: Employment schema works")
        
        # Test Education
        edu = Education(
            school="Test University",
            degree="BS",
            field="Computer Science",
            graduation_year=2020
        )
        print(f"OK: Education schema works")
        
        # Test ParsedResume
        resume = ParsedResume(
            name="Test User",
            email="test@example.com",
            employment_history=[emp],
            education=[edu],
            skills=["Python", "JavaScript"],
            github_username="testuser"
        )
        print(f"OK: ParsedResume schema works")
        print(f"   - Name: {resume.name}")
        print(f"   - Skills: {len(resume.skills)} skills")
        print(f"   - Employment: {len(resume.employment_history)} entries")
        
        return True
    except Exception as e:
        print(f"ERROR: Schema test failed - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_extraction():
    """Test PDF text extraction"""
    print("\n=== Testing PDF Extraction ===")
    try:
        from services.resume_parser import extract_text_from_pdf
        
        # Find test resume
        resume_path = backend_path.parent / "resume_examples" / "resume1.pdf"
        
        if not resume_path.exists():
            print(f"SKIP: No test resume found at {resume_path}")
            return True
        
        with open(resume_path, "rb") as f:
            pdf_bytes = f.read()
        
        text = extract_text_from_pdf(pdf_bytes)
        
        if len(text) > 0:
            print(f"OK: Extracted {len(text)} characters from PDF")
            print(f"   First 100 chars: {text[:100].strip()}...")
            return True
        else:
            print("ERROR: No text extracted from PDF")
            return False
            
    except Exception as e:
        print(f"ERROR: PDF extraction failed - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fastapi_routes():
    """Test FastAPI routes are registered"""
    print("\n=== Testing FastAPI Routes ===")
    try:
        from main import app
        
        routes = [r.path for r in app.routes if hasattr(r, 'path')]
        
        required_routes = [
            '/health',
            '/api/v1/verify',
            '/api/v1/verify/{verification_id}',
            '/api/v1/verify/{verification_id}/steps'
        ]
        
        for route in required_routes:
            if route in routes:
                print(f"OK: {route}")
            else:
                print(f"ERROR: Missing route {route}")
                return False
        
        return True
        
    except Exception as e:
        print(f"ERROR: Route test failed - {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration"""
    print("\n=== Testing Configuration ===")
    try:
        from config import get_settings
        
        settings = get_settings()
        
        print(f"OK: OpenAI API key: {settings.openai_api_key[:20]}...")
        print(f"OK: Supabase URL: {settings.supabase_url}")
        print(f"OK: LLM Model: {settings.llm_model}")
        print(f"OK: Use Mock Data: {settings.use_mock_data}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Config test failed - {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("WAVE 2 Backend API Validation")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Schemas", test_schemas()))
    results.append(("PDF Extraction", test_pdf_extraction()))
    results.append(("FastAPI Routes", test_fastapi_routes()))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nTo start the server:")
        print("  cd backend")
        print("  ..\\venv\\Scripts\\python.exe -m uvicorn main:app --reload")
        print("\nTo test with actual API calls:")
        print("  ..\\venv\\Scripts\\python.exe test_upload.py")
    else:
        print("\nSome tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
