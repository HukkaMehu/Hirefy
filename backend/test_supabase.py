#!/usr/bin/env python3
"""Test Supabase integration"""

print("=" * 70)
print("SUPABASE INTEGRATION TEST")
print("=" * 70)

# Test 1: Module loading
print("\n1. Testing Supabase client import...")
try:
    from services.supabase_client import (
        supabase, 
        update_agent_progress,
        get_verification,
        update_verification_status
    )
    print("[OK] Supabase client module loaded successfully")
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 2: Check connection
print("\n2. Testing Supabase connection...")
print("-" * 70)
try:
    from config import get_settings
    settings = get_settings()
    
    print(f"[INFO] Supabase URL: {settings.supabase_url}")
    print(f"[INFO] Using service key: {'*' * 20}...{settings.supabase_service_key[-10:]}")
    
    # Try to query tables (this will fail if tables don't exist yet)
    result = supabase.table("verifications").select("count", count="exact").limit(0).execute()
    print(f"[OK] Successfully connected to Supabase")
    print(f"[INFO] 'verifications' table exists")
    
except Exception as e:
    error_msg = str(e)
    if "relation" in error_msg and "does not exist" in error_msg:
        print(f"[WARNING] Tables not created yet in Supabase")
        print(f"[INFO] Connection works, but database migration needed")
        print(f"[INFO] Run the SQL migration from workstream-3-wave-plan.md")
    elif "service_key" in error_msg.lower() or "invalid" in error_msg.lower():
        print(f"[FAIL] Invalid Supabase credentials")
        print(f"[INFO] Check SUPABASE_SERVICE_KEY in .env file")
    else:
        print(f"[WARNING] Connection issue: {error_msg[:100]}")

# Test 3: Test table structure check
print("\n3. Checking expected table structure...")
print("-" * 70)
try:
    # Try to check verification_steps table
    result = supabase.table("verification_steps").select("count", count="exact").limit(0).execute()
    print(f"[OK] 'verification_steps' table exists")
    
    print("\n[INFO] Database schema ready for Wave 2!")
    
except Exception as e:
    error_msg = str(e)
    if "relation" in error_msg and "does not exist" in error_msg:
        print(f"[WARNING] 'verification_steps' table not created yet")
    else:
        print(f"[WARNING] {error_msg[:100]}")

# Test 4: Configuration check
print("\n4. Verifying configuration...")
print("-" * 70)
try:
    from config import get_settings
    settings = get_settings()
    
    checks = {
        "Supabase URL set": bool(settings.supabase_url and settings.supabase_url != "https://xxx.supabase.co"),
        "Service key set": bool(settings.supabase_service_key and settings.supabase_service_key != "eyJ..."),
        "Anon key set": bool(settings.supabase_anon_key and settings.supabase_anon_key != "eyJ..."),
    }
    
    for check, passed in checks.items():
        status = "[OK]" if passed else "[WARN]"
        print(f"{status} {check}")
    
    all_passed = all(checks.values())
    if all_passed:
        print("\n[OK] All Supabase configuration valid!")
    else:
        print("\n[WARNING] Some configuration placeholders detected")
        print("[INFO] Update .env with real Supabase credentials")
    
except Exception as e:
    print(f"[FAIL] Configuration check failed: {e}")

# Test 5: Function signatures
print("\n5. Verifying function signatures...")
print("-" * 70)
try:
    import inspect
    
    # Check update_agent_progress signature
    sig = inspect.signature(update_agent_progress)
    params = list(sig.parameters.keys())
    expected = ['verification_id', 'agent_name', 'status', 'message', 'data']
    
    if params == expected:
        print("[OK] update_agent_progress() signature correct")
    else:
        print(f"[WARNING] Expected params: {expected}")
        print(f"[WARNING] Got params: {params}")
    
    # Check get_verification signature
    sig = inspect.signature(get_verification)
    params = list(sig.parameters.keys())
    if 'verification_id' in params:
        print("[OK] get_verification() signature correct")
    
    # Check update_verification_status signature
    sig = inspect.signature(update_verification_status)
    params = list(sig.parameters.keys())
    expected = ['verification_id', 'status', 'result']
    if params == expected:
        print("[OK] update_verification_status() signature correct")
    
except Exception as e:
    print(f"[FAIL] {e}")

print("\n" + "=" * 70)
print("SUPABASE INTEGRATION TEST COMPLETE")
print("=" * 70)
print("\nNote: Full database operations require Supabase tables to be created.")
print("Run the SQL migration from Hour 0-1 in workstream-3-wave-plan.md")
