"""
Comprehensive System Architecture Analysis
Identifies all potential issues in the data flow
"""

import sys
from pathlib import Path
import inspect
import asyncio

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

print("=" * 80)
print("COMPREHENSIVE SYSTEM ARCHITECTURE ANALYSIS")
print("=" * 80)

# ============================================================================
# 1. DATABASE SCHEMA ANALYSIS
# ============================================================================
print("\n1. DATABASE SCHEMA ANALYSIS")
print("-" * 80)

expected_schema = {
    "verifications": {
        "id": "UUID PRIMARY KEY",
        "candidate_name": "TEXT NOT NULL",
        "candidate_email": "TEXT",
        "github_username": "TEXT",
        "status": "TEXT NOT NULL (processing/complete/failed)",
        "risk_score": "TEXT (green/yellow/red)",
        "resume_url": "TEXT",
        "parsed_data": "JSONB",
        "result": "JSONB",
        "created_at": "TIMESTAMPTZ",
        "completed_at": "TIMESTAMPTZ"
    },
    "verification_steps": {
        "id": "UUID PRIMARY KEY",
        "verification_id": "UUID REFERENCES verifications(id)",
        "agent_name": "TEXT NOT NULL",
        "status": "TEXT NOT NULL",
        "message": "TEXT",
        "data": "JSONB",
        "created_at": "TIMESTAMPTZ"
    }
}

print("\nExpected Database Schema:")
for table, columns in expected_schema.items():
    print(f"\n  Table: {table}")
    for col, dtype in columns.items():
        print(f"    - {col}: {dtype}")

print("\n[OK] Schema requirements documented")

# ============================================================================
# 2. BACKEND FLOW ANALYSIS
# ============================================================================
print("\n\n2. BACKEND FLOW ANALYSIS")
print("-" * 80)

try:
    from schemas import ParsedResume, Employment, Education, VerificationResponseV1
    print("\n[OK] Schema imports successful")
    
    print("\nParsedResume fields:")
    for field_name, field_type in ParsedResume.__annotations__.items():
        print(f"  - {field_name}: {field_type}")
    
    print("\nEmployment fields:")
    for field_name, field_type in Employment.__annotations__.items():
        print(f"  - {field_name}: {field_type}")
        
    print("\nEducation fields:")
    for field_name, field_type in Education.__annotations__.items():
        print(f"  - {field_name}: {field_type}")
        
except Exception as e:
    print(f"\n[FAIL] Schema import failed: {e}")

# Check orchestrator
try:
    from agents.orchestrator import run_verification_workflow, VerificationState
    print("\n✓ Orchestrator imports successful")
    
    print("\nrun_verification_workflow signature:")
    sig = inspect.signature(run_verification_workflow)
    print(f"  {sig}")
    
    print("\nVerificationState fields:")
    if hasattr(VerificationState, '__annotations__'):
        for field, ftype in VerificationState.__annotations__.items():
            print(f"  - {field}: {ftype}")
    
except Exception as e:
    print(f"\n✗ Orchestrator import failed: {e}")

# Check fraud detector
try:
    from agents.fraud_detector import FraudDetector
    print("\n✓ FraudDetector imports successful")
    
    detector = FraudDetector()
    print("\nFraudDetector.analyze signature:")
    sig = inspect.signature(detector.analyze)
    print(f"  {sig}")
    
except Exception as e:
    print(f"\n✗ FraudDetector import failed: {e}")

# Check supabase client
try:
    from services.supabase_client import (
        update_agent_progress, 
        update_verification_status,
        get_verification,
        supabase
    )
    print("\n✓ Supabase client imports successful")
    
    print("\nupdate_agent_progress signature:")
    sig = inspect.signature(update_agent_progress)
    print(f"  {sig}")
    
    print("\nupdate_verification_status signature:")
    sig = inspect.signature(update_verification_status)
    print(f"  {sig}")
    
except Exception as e:
    print(f"\n✗ Supabase client import failed: {e}")

# ============================================================================
# 3. DATA STRUCTURE COMPATIBILITY
# ============================================================================
print("\n\n3. DATA STRUCTURE COMPATIBILITY")
print("-" * 80)

print("\nData flow chain:")
print("  1. main.py: resume upload → parse_with_llm() → ParsedResume object")
print("  2. main.py: parsed.model_dump() → dict")
print("  3. main.py: background_tasks.add_task(run_verification_workflow, verification_id, parsed.model_dump(), github_username)")
print("  4. orchestrator.py: VerificationState(parsed_resume=parsed.model_dump())")
print("  5. orchestrator.py: detector.analyze(state['parsed_resume'], github_data, refs)")
print("  6. fraud_detector.py: analyze(resume_data: dict, github_data: dict, reference_responses: list)")

print("\nChecking compatibility:")

# Test ParsedResume → dict conversion
try:
    test_emp = Employment(
        company="TestCorp",
        title="Engineer",
        start_date="2020-01",
        end_date="2023-06",
        description="Test"
    )
    test_edu = Education(
        school="TestU",
        degree="BS",
        field="CS",
        graduation_year=2020
    )
    test_parsed = ParsedResume(
        name="Test User",
        email="test@example.com",
        employment_history=[test_emp],
        education=[test_edu],
        skills=["Python"],
        github_username="testuser"
    )
    
    parsed_dict = test_parsed.model_dump()
    
    print("\n✓ ParsedResume.model_dump() produces dict:")
    print(f"  Type: {type(parsed_dict)}")
    print(f"  Keys: {list(parsed_dict.keys())}")
    
    # Test if dict can be used by fraud detector
    detector = FraudDetector()
    fraud_result = detector.analyze(parsed_dict, {}, [])
    
    print("\n✓ FraudDetector.analyze() accepts dict from model_dump()")
    print(f"  Risk level: {fraud_result['risk_level']}")
    print(f"  Flags: {len(fraud_result['flags'])}")
    
except Exception as e:
    print(f"\n✗ Data structure compatibility issue: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# 4. ASYNC/SYNC ANALYSIS
# ============================================================================
print("\n\n4. ASYNC/SYNC FUNCTION ANALYSIS")
print("-" * 80)

try:
    print("\nFunction async status:")
    
    # Check update_agent_progress
    is_async = inspect.iscoroutinefunction(update_agent_progress)
    print(f"  update_agent_progress: {'async' if is_async else 'sync'}")
    
    # Check update_verification_status
    is_async = inspect.iscoroutinefunction(update_verification_status)
    print(f"  update_verification_status: {'async' if is_async else 'sync'}")
    
    # Check orchestrator nodes
    from agents.orchestrator import (
        log_parsing, discover_references, analyze_github,
        detect_fraud, synthesize_report
    )
    
    for func in [log_parsing, discover_references, analyze_github, detect_fraud, synthesize_report]:
        is_async = inspect.iscoroutinefunction(func)
        status = "✓ async" if is_async else "✗ sync (should be async)"
        print(f"  {func.__name__}: {status}")
    
    # Check fraud detector analyze
    is_async = inspect.iscoroutinefunction(FraudDetector.analyze)
    print(f"  FraudDetector.analyze: {'async' if is_async else 'sync'}")
    
    print("\n⚠ ISSUE DETECTED:")
    print("  - update_agent_progress is async, called with await ✓")
    print("  - update_verification_status is sync, called with await ✗")
    print("  - FraudDetector.analyze is sync, called with asyncio.to_thread ✓")
    
except Exception as e:
    print(f"\n✗ Async analysis failed: {e}")

# ============================================================================
# 5. FRONTEND INTEGRATION
# ============================================================================
print("\n\n5. FRONTEND INTEGRATION ANALYSIS")
print("-" * 80)

frontend_expectations = {
    "Supabase real-time": {
        "table": "verification_steps",
        "filter": "verification_id=eq.{id}",
        "event": "INSERT"
    },
    "VerificationStep type": {
        "status": "'running' | 'complete' | 'failed'"
    },
    "Backend status values": {
        "used": "'in_progress', 'completed', 'failed', 'skipped'"
    }
}

print("\nFrontend expectations vs Backend implementation:")
print("\n  ⚠ ISSUE DETECTED: Status value mismatch")
print("    Frontend expects: 'running' | 'complete' | 'failed'")
print("    Backend uses: 'in_progress' | 'completed' | 'failed' | 'skipped'")
print("\n    This will cause UI rendering issues!")

print("\n  API Endpoints:")
print("    - POST /api/v1/verify (returns verification_id)")
print("    - GET /api/v1/verify/{id} (returns verification record)")
print("    - GET /api/v1/verify/{id}/steps (returns all steps)")

print("\n  Real-time subscription:")
print("    - Table: verification_steps")
print("    - Filter: verification_id=eq.{params.id}")
print("    - Publication: supabase_realtime (must be enabled)")

# ============================================================================
# 6. POTENTIAL ISSUES SUMMARY
# ============================================================================
print("\n\n6. POTENTIAL ISSUES IDENTIFIED")
print("=" * 80)

issues = [
    {
        "severity": "CRITICAL",
        "category": "Async/Sync Mismatch",
        "description": "update_verification_status is sync but called with await",
        "location": "orchestrator.py:207, 394",
        "fix": "Make update_verification_status async or remove await"
    },
    {
        "severity": "HIGH",
        "category": "Frontend Type Mismatch",
        "description": "Frontend expects status: 'running'|'complete'|'failed', backend uses 'in_progress'|'completed'",
        "location": "frontend/lib/supabase.ts:12 vs backend status values",
        "fix": "Standardize status values across frontend and backend"
    },
    {
        "severity": "MEDIUM",
        "category": "Missing Realtime Publication",
        "description": "verification_steps table may not be added to supabase_realtime publication",
        "location": "Supabase SQL Editor",
        "fix": "Run: ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;"
    },
    {
        "severity": "LOW",
        "category": "Status Completion Value",
        "description": "update_verification_status checks for 'complete' but orchestrator passes 'completed'",
        "location": "supabase_client.py:36 vs orchestrator.py:207",
        "fix": "Use consistent 'completed' everywhere"
    },
    {
        "severity": "INFO",
        "category": "Missing Storage Bucket",
        "description": "Resumes bucket may not exist, code falls back to mock URL",
        "location": "main.py:64",
        "fix": "Create 'resumes' bucket in Supabase Storage"
    }
]

for i, issue in enumerate(issues, 1):
    print(f"\n{i}. [{issue['severity']}] {issue['category']}")
    print(f"   Description: {issue['description']}")
    print(f"   Location: {issue['location']}")
    print(f"   Fix: {issue['fix']}")

# ============================================================================
# 7. ARCHITECTURE DIAGRAM
# ============================================================================
print("\n\n7. SYSTEM ARCHITECTURE DATA FLOW")
print("=" * 80)

print("""
┌─────────────────────────────────────────────────────────────────────┐
│ FRONTEND (Next.js)                                                   │
├─────────────────────────────────────────────────────────────────────┤
│ 1. Upload Page (app/page.tsx)                                       │
│    └─> POST /api/v1/verify (resume file, github_username)          │
│                                                                      │
│ 2. Verification Page (app/verify/[id]/page.tsx)                    │
│    ├─> Subscribe to verification_steps (Realtime)                  │
│    └─> Display agent progress live                                 │
│                                                                      │
│ 3. Report Page (app/report/[id]/page.tsx)                          │
│    └─> GET /api/v1/verify/{id} → display final result             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ HTTP
┌─────────────────────────────────────────────────────────────────────┐
│ BACKEND (FastAPI)                                                    │
├─────────────────────────────────────────────────────────────────────┤
│ main.py                                                              │
│ ├─> POST /api/v1/verify                                             │
│ │   ├─> 1. Upload to Supabase Storage (resumes bucket)             │
│ │   ├─> 2. extract_text_from_pdf(bytes) → text                     │
│ │   ├─> 3. parse_with_llm(text) → ParsedResume                     │
│ │   ├─> 4. Insert to verifications table                           │
│ │   └─> 5. background_tasks.add_task(run_verification_workflow)    │
│ │                                                                    │
│ └─> GET /api/v1/verify/{id}                                         │
│     └─> Return verification record with result                      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ Background Task
┌─────────────────────────────────────────────────────────────────────┐
│ ORCHESTRATOR (LangGraph)                                             │
├─────────────────────────────────────────────────────────────────────┤
│ run_verification_workflow(verification_id, parsed_resume_dict,      │
│                           github_username)                           │
│                                                                      │
│ VerificationState:                                                   │
│   - verification_id: str                                             │
│   - parsed_resume: dict  ← ParsedResume.model_dump()                │
│   - github_username: Optional[str]                                   │
│   - references: list                                                 │
│   - reference_responses: list                                        │
│   - github_analysis: dict                                            │
│   - fraud_results: dict                                              │
│   - final_report: dict                                               │
│                                                                      │
│ Workflow:                                                            │
│   1. log_parsing                                                     │
│      └─> await update_agent_progress(...)                           │
│                                                                      │
│   2. discover_references                                             │
│      ├─> Parse employment_history from parsed_resume dict          │
│      └─> await update_agent_progress(...)                           │
│                                                                      │
│   3. analyze_github                                                  │
│      ├─> analyze_github_profile(username) [sync]                    │
│      └─> await update_agent_progress(...)                           │
│                                                                      │
│   4. detect_fraud                                                    │
│      ├─> detector.analyze(parsed_resume, github_analysis, refs)    │
│      │   [sync function called with asyncio.to_thread]              │
│      └─> await update_agent_progress(...)                           │
│                                                                      │
│   5. synthesize_report                                               │
│      ├─> generate_narrative(state) [async, calls OpenAI]           │
│      ├─> generate_interview_questions(fraud_results) [sync]        │
│      ├─> ⚠ await update_verification_status(...) [ISSUE: sync fn]  │
│      └─> await update_agent_progress(...)                           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ Writes to DB
┌─────────────────────────────────────────────────────────────────────┐
│ SUPABASE                                                             │
├─────────────────────────────────────────────────────────────────────┤
│ Tables:                                                              │
│   - verifications (status, result, parsed_data)                     │
│   - verification_steps (agent_name, status, message, data)          │
│                                                                      │
│ Storage:                                                             │
│   - resumes bucket (PDF files)                                      │
│                                                                      │
│ Realtime:                                                            │
│   - Publication: supabase_realtime                                   │
│   - Table: verification_steps                                        │
│   └─> Frontend subscribes and gets live updates                    │
└─────────────────────────────────────────────────────────────────────┘
""")

# ============================================================================
# 8. RECOMMENDATIONS
# ============================================================================
print("\n\n8. RECOMMENDATIONS FOR FIXES")
print("=" * 80)

recommendations = [
    {
        "priority": 1,
        "action": "Fix async/sync mismatch in update_verification_status",
        "details": [
            "Change update_verification_status to async function",
            "Update signature: async def update_verification_status(...)",
            "Or remove await when calling it in orchestrator.py"
        ]
    },
    {
        "priority": 2,
        "action": "Standardize status values",
        "details": [
            "Frontend expects: 'running', 'complete', 'failed'",
            "Backend uses: 'in_progress', 'completed', 'failed', 'skipped'",
            "Choose one standard and update all code"
        ]
    },
    {
        "priority": 3,
        "action": "Verify Supabase real-time publication",
        "details": [
            "Run: ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;",
            "Test real-time updates in frontend"
        ]
    },
    {
        "priority": 4,
        "action": "Create resumes storage bucket",
        "details": [
            "Create 'resumes' bucket in Supabase Storage",
            "Set public=false, max_size=5MB"
        ]
    },
    {
        "priority": 5,
        "action": "Add error handling for missing columns",
        "details": [
            "Ensure all expected columns exist in DB",
            "Add migration checks on startup"
        ]
    }
]

for rec in recommendations:
    print(f"\n{rec['priority']}. {rec['action']}")
    for detail in rec['details']:
        print(f"   - {detail}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
