#!/usr/bin/env python3
"""Test Wave 1 deliverables"""

print("=" * 60)
print("WAVE 1 VERIFICATION TEST")
print("=" * 60)

# Test 1: Config loading
print("\n1. Testing config.py...")
try:
    from config import get_settings
    settings = get_settings()
    print(f"   [OK] Config loaded successfully")
    print(f"   - LLM Model: {settings.llm_model}")
    print(f"   - Use Mock Data: {settings.use_mock_data}")
    print(f"   - Fraud Detection Strict Mode: {settings.fraud_detection_strict_mode}")
except Exception as e:
    print(f"   [FAIL] Config failed: {e}")

# Test 2: Supabase client
print("\n2. Testing services/supabase_client.py...")
try:
    from services.supabase_client import supabase, update_agent_progress
    print(f"   [OK] Supabase client initialized")
    print(f"   [OK] update_agent_progress function available")
except Exception as e:
    print(f"   [FAIL] Supabase client failed: {e}")

# Test 3: GitHub API
print("\n3. Testing services/github_api.py...")
try:
    from services.github_api import analyze_github_profile
    print(f"   [OK] GitHub API module loaded")
    print(f"   [OK] analyze_github_profile function available")
except Exception as e:
    print(f"   [FAIL] GitHub API failed: {e}")

# Test 4: Mock loader
print("\n4. Testing services/mock_loader.py...")
try:
    from services.mock_loader import load_reference_templates, load_fraud_scenarios
    templates = load_reference_templates()
    scenarios = load_fraud_scenarios()
    print(f"   [OK] Mock loader initialized")
    print(f"   - Reference templates loaded: {len(templates['templates'])}")
    print(f"   - Fraud scenarios loaded: {len(scenarios['scenarios'])}")
except Exception as e:
    print(f"   [FAIL] Mock loader failed: {e}")

# Test 5: Mock data files
print("\n5. Testing mock data files...")
try:
    import json
    from pathlib import Path
    
    mocks_dir = Path(__file__).parent / "mocks"
    ref_file = mocks_dir / "reference_templates.json"
    fraud_file = mocks_dir / "fraud_scenarios.json"
    
    assert ref_file.exists(), f"reference_templates.json missing (looked in {ref_file})"
    assert fraud_file.exists(), f"fraud_scenarios.json missing (looked in {fraud_file})"
    
    print(f"   [OK] reference_templates.json exists")
    print(f"   [OK] fraud_scenarios.json exists")
except Exception as e:
    print(f"   [FAIL] Mock data files failed: {e}")

print("\n" + "=" * 60)
print("WAVE 1 VERIFICATION COMPLETE")
print("=" * 60)
