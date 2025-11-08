#!/usr/bin/env python3
"""Test if backend server can run"""

print("Testing backend server initialization...")
print("=" * 60)

try:
    from main import app
    print("[OK] FastAPI app imported successfully")
    
    # Check routes
    print("\nAvailable endpoints:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            print(f"  {methods:10} {route.path}")
    
    print("\n" + "=" * 60)
    print("[OK] Backend server can be run")
    print("\nTo start the server, run:")
    print("  cd backend")
    print("  uvicorn main:app --reload --port 8000")
    
except Exception as e:
    print(f"[FAIL] Server initialization failed: {e}")
    import traceback
    traceback.print_exc()
