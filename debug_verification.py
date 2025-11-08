"""
Debug script to check verification workflow
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.supabase_client import supabase

def check_verifications():
    """Check recent verifications"""
    print("\n=== Checking Verifications Table ===")
    try:
        result = supabase.table("verifications").select("*").order("created_at", desc=True).limit(5).execute()
        if result.data:
            for v in result.data:
                print(f"\nID: {v['id']}")
                print(f"  Name: {v['candidate_name']}")
                print(f"  Status: {v['status']}")
                print(f"  Created: {v['created_at']}")
                
                # Check steps for this verification
                steps = supabase.table("verification_steps").select("*").eq("verification_id", v['id']).execute()
                print(f"  Steps: {len(steps.data) if steps.data else 0}")
                if steps.data:
                    for step in steps.data:
                        print(f"    - {step['agent_name']}: {step['status']} - {step['message']}")
        else:
            print("No verifications found")
    except Exception as e:
        print(f"Error: {e}")

def check_realtime_config():
    """Check if realtime is enabled"""
    print("\n=== Checking Realtime Configuration ===")
    print("To enable realtime, run this SQL in Supabase:")
    print("ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;")

if __name__ == "__main__":
    check_verifications()
    check_realtime_config()
