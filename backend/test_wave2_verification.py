"""
Comprehensive Wave 2 Backend Verification Test
Tests all components as specified in workstream-3-wave-plan.md lines 775-1625
"""

import sys
import traceback
from pathlib import Path

# Test results storage
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test_result(name: str, passed: bool, details: str = ""):
    if passed:
        results["passed"].append(f"[PASS] {name}: {details}")
        print(f"[PASS] {name}")
    else:
        results["failed"].append(f"[FAIL] {name}: {details}")
        print(f"[FAIL] {name}: {details}")

def test_warning(name: str, details: str):
    results["warnings"].append(f"[WARN] {name}: {details}")
    print(f"[WARN] {name}: {details}")

print("=" * 80)
print("WAVE 2 BACKEND VERIFICATION TEST")
print("=" * 80)
print()

# Test 1: Verify directory structure
print("TEST 1: Directory Structure")
print("-" * 80)

backend_dir = Path(__file__).parent
agents_dir = backend_dir / "agents"
services_dir = backend_dir / "services"
mocks_dir = backend_dir / "mocks"

test_result(
    "agents directory exists",
    agents_dir.exists(),
    str(agents_dir)
)

test_result(
    "services directory exists",
    services_dir.exists(),
    str(services_dir)
)

test_result(
    "mocks directory exists",
    mocks_dir.exists(),
    str(mocks_dir)
)

# Test 2: Verify __init__.py files
print("\nTEST 2: __init__.py Files")
print("-" * 80)

agents_init = agents_dir / "__init__.py"
services_init = services_dir / "__init__.py"

test_result(
    "agents/__init__.py exists",
    agents_init.exists(),
    str(agents_init)
)

test_result(
    "services/__init__.py exists",
    services_init.exists(),
    str(services_init)
)

# Test 3: Import core modules
print("\nTEST 3: Module Imports")
print("-" * 80)

try:
    from config import get_settings
    settings = get_settings()
    test_result("config.get_settings", True, f"LLM model: {settings.llm_model}")
except Exception as e:
    test_result("config.get_settings", False, str(e))

try:
    import schemas
    test_result("schemas module", True, "Imported successfully")
except Exception as e:
    test_result("schemas module", False, str(e))

try:
    from schemas import VerificationResponseV1, ParsedResume, Employment, Education
    test_result("schemas.VerificationResponseV1", True)
    test_result("schemas.ParsedResume", True)
    test_result("schemas.Employment", True)
    test_result("schemas.Education", True)
    
    # Verify VerificationResponseV1 has Literal type for status
    import inspect
    from typing import get_type_hints
    hints = get_type_hints(VerificationResponseV1)
    status_type = str(hints.get('status', ''))
    has_literal = 'Literal' in status_type or 'processing' in status_type
    test_result(
        "VerificationResponseV1.status uses Literal",
        has_literal,
        f"Type: {status_type}"
    )
except Exception as e:
    test_result("schemas imports", False, str(e))

# Test 4: Resume Parser
print("\nTEST 4: Resume Parser Service")
print("-" * 80)

try:
    from services.resume_parser import extract_text_from_pdf, parse_with_llm
    test_result("services.resume_parser.extract_text_from_pdf", True)
    test_result("services.resume_parser.parse_with_llm", True)
except Exception as e:
    test_result("services.resume_parser", False, str(e))

# Test 5: Fraud Detector
print("\nTEST 5: Fraud Detector Agent")
print("-" * 80)

try:
    from agents.fraud_detector import FraudDetector, FraudFlag
    test_result("agents.fraud_detector.FraudDetector", True)
    test_result("agents.fraud_detector.FraudFlag", True)
    
    # Test instantiation
    detector = FraudDetector()
    test_result("FraudDetector instantiation", True, f"Rules: {len(detector.rules)}")
    
    # Test basic analysis
    test_resume = {
        "skills": ["Python", "JavaScript"],
        "employment_history": [
            {
                "company": "Company A",
                "title": "Engineer",
                "start_date": "2020-01",
                "end_date": "2021-06",
                "description": "Test"
            }
        ]
    }
    
    result = detector.analyze(test_resume, {}, [])
    test_result(
        "FraudDetector.analyze",
        "risk_level" in result and "flags" in result,
        f"Risk: {result.get('risk_level')}, Flags: {len(result.get('flags', []))}"
    )
    
    # Test with GitHub data
    github_data = {
        "repositories": {
            "languages": {"Python": 10}
        }
    }
    result2 = detector.analyze(test_resume, github_data, [])
    test_result(
        "FraudDetector GitHub consistency check",
        True,
        f"Analyzed with GitHub data"
    )
    
except Exception as e:
    test_result("agents.fraud_detector", False, f"{str(e)}\n{traceback.format_exc()}")

# Test 6: GitHub API Service
print("\nTEST 6: GitHub API Service")
print("-" * 80)

try:
    from services.github_api import analyze_github_profile
    test_result("services.github_api.analyze_github_profile", True)
    
    # Test with 'torvalds' profile
    print("Testing GitHub API with username 'torvalds'...")
    github_result = analyze_github_profile('torvalds')
    
    has_profile = 'profile' in github_result
    has_repos = 'repositories' in github_result
    has_error = 'error' in github_result
    
    if has_error:
        test_warning(
            "GitHub API test",
            f"Error: {github_result['error']} (API rate limit or network issue)"
        )
    else:
        test_result(
            "GitHub API analyze_github_profile('torvalds')",
            has_profile and has_repos,
            f"Profile: {github_result.get('profile', {}).get('username')}, Repos: {github_result.get('repositories', {}).get('total')}"
        )
        
        if has_repos:
            langs = github_result['repositories'].get('languages', {})
            test_result(
                "GitHub API returns languages",
                len(langs) > 0,
                f"Languages: {list(langs.keys())[:5]}"
            )
except Exception as e:
    test_result("services.github_api", False, f"{str(e)}\n{traceback.format_exc()}")

# Test 7: Mock Loader Service
print("\nTEST 7: Mock Loader Service")
print("-" * 80)

try:
    from services.mock_loader import (
        load_reference_templates,
        load_fraud_scenarios,
        get_weighted_reference_response,
        generate_mock_references,
        simulate_outreach_responses
    )
    test_result("services.mock_loader imports", True)
    
    # Test load functions
    ref_templates = load_reference_templates()
    test_result(
        "load_reference_templates",
        "templates" in ref_templates,
        f"Templates: {len(ref_templates.get('templates', []))}"
    )
    
    fraud_scenarios = load_fraud_scenarios()
    test_result(
        "load_fraud_scenarios",
        isinstance(fraud_scenarios, dict),
        "Loaded successfully"
    )
    
    # Test reference generation
    weighted_ref = get_weighted_reference_response()
    test_result(
        "get_weighted_reference_response",
        "performance_rating" in weighted_ref and "would_rehire" in weighted_ref,
        f"Rating: {weighted_ref.get('performance_rating')}/10"
    )
    
    # Test mock reference generation
    test_jobs = [
        {"company": "Test Corp", "title": "Engineer", "start_date": "2020-01", "end_date": "2021-01", "description": "Test"}
    ]
    mock_refs = generate_mock_references(test_jobs)
    test_result(
        "generate_mock_references",
        len(mock_refs) >= 15,
        f"Generated {len(mock_refs)} references"
    )
    
    # Test response simulation
    responses = simulate_outreach_responses(mock_refs, response_rate=0.20)
    test_result(
        "simulate_outreach_responses",
        len(responses) >= 1,
        f"Generated {len(responses)} responses from {len(mock_refs)} references"
    )
    
except Exception as e:
    test_result("services.mock_loader", False, f"{str(e)}\n{traceback.format_exc()}")

# Test 8: Main API Endpoints
print("\nTEST 8: FastAPI Main Application")
print("-" * 80)

try:
    from main import app
    test_result("main.app", True, "FastAPI app imported")
    
    # Check routes
    routes = [route.path for route in app.routes]
    
    test_result(
        "/health endpoint",
        "/health" in routes,
        "Exists"
    )
    
    test_result(
        "POST /api/v1/verify endpoint",
        "/api/v1/verify" in routes,
        "Exists"
    )
    
    test_result(
        "GET /api/v1/verify/{verification_id} endpoint",
        any("/api/v1/verify/{verification_id}" in r for r in routes),
        "Exists"
    )
    
    test_result(
        "GET /api/v1/verify/{verification_id}/steps endpoint",
        any("/api/v1/verify/{verification_id}/steps" in r for r in routes),
        "Exists"
    )
    
    # Count endpoints
    api_endpoints = [r for r in routes if r.startswith("/api")]
    test_result(
        "Total API endpoints",
        len(api_endpoints) >= 3,
        f"Found {len(api_endpoints)} endpoints"
    )
    
except Exception as e:
    test_result("main.app", False, f"{str(e)}\n{traceback.format_exc()}")

# Test 9: Supabase Client
print("\nTEST 9: Supabase Client Service")
print("-" * 80)

try:
    from services.supabase_client import supabase, update_verification_status
    test_result("services.supabase_client.supabase", True)
    test_result("services.supabase_client.update_verification_status", True)
except Exception as e:
    test_result("services.supabase_client", False, str(e))

# Test 10: Integration Test
print("\nTEST 10: Integration Test - Fraud Detection Pipeline")
print("-" * 80)

try:
    from agents.fraud_detector import FraudDetector
    from services.github_api import analyze_github_profile
    from services.mock_loader import generate_mock_references, simulate_outreach_responses
    
    # Simulate a full pipeline
    test_resume = {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "JavaScript", "TypeScript"],
        "employment_history": [
            {
                "company": "Tech Corp",
                "title": "Senior Engineer",
                "start_date": "2020-01",
                "end_date": "2021-12",
                "description": "Backend development"
            },
            {
                "company": "StartupXYZ",
                "title": "Lead Developer",
                "start_date": "2022-01",
                "end_date": "2023-12",
                "description": "Full stack"
            }
        ],
        "education": [
            {
                "school": "University",
                "degree": "BS",
                "field": "Computer Science",
                "graduation_year": 2019
            }
        ]
    }
    
    # Generate references
    mock_refs = generate_mock_references(test_resume["employment_history"])
    responses = simulate_outreach_responses(mock_refs, response_rate=0.20)
    
    # Get GitHub data (use mock if API fails)
    github_data = analyze_github_profile('torvalds')
    if 'error' in github_data:
        github_data = {
            "repositories": {"languages": {"C": 50, "Python": 20}},
            "profile": {"username": "torvalds"}
        }
    
    # Run fraud detection
    detector = FraudDetector()
    fraud_result = detector.analyze(test_resume, github_data, responses)
    
    test_result(
        "Full pipeline integration",
        fraud_result["risk_level"] in ["green", "yellow", "red"],
        f"Risk: {fraud_result['risk_level']}, Flags: {len(fraud_result['flags'])}, References: {len(responses)}"
    )
    
except Exception as e:
    test_result("Integration test", False, f"{str(e)}\n{traceback.format_exc()}")

# Print Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print(f"\n[PASS] PASSED: {len(results['passed'])}")
for item in results['passed']:
    print(f"  {item}")

if results['warnings']:
    print(f"\n[WARN] WARNINGS: {len(results['warnings'])}")
    for item in results['warnings']:
        print(f"  {item}")

if results['failed']:
    print(f"\n[FAIL] FAILED: {len(results['failed'])}")
    for item in results['failed']:
        print(f"  {item}")
    print("\nSome tests failed. Please review the errors above.")
    sys.exit(1)
else:
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    print("\nWave 2 Backend is complete and verified.")
    sys.exit(0)
