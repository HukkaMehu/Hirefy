"""
Test script for starting verification manually via API endpoint.

This demonstrates how to trigger the verification process which will:
- Make REAL phone calls via ElevenLabs
- Send REAL emails via SMTP
- Analyze GitHub profiles
- Detect fraud
- Generate reports

Usage:
    python test_start_verification.py <session_id>
"""

import sys
import requests
import time
import json

API_BASE_URL = "http://localhost:5000/api"


def start_verification(session_id):
    """Start verification for a session"""
    print(f"\n{'='*80}")
    print(f"Starting Verification for Session: {session_id}")
    print(f"{'='*80}\n")
    
    print("⚠️  WARNING: This will make REAL phone calls and send REAL emails!")
    print("⚠️  Make sure you have:")
    print("   - ELEVENLABS_API_KEY set in .env")
    print("   - SMTP credentials configured in .env")
    print("   - Valid phone numbers and email addresses in the session data")
    print()
    
    response = input("Are you sure you want to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
    
    print("\nStarting verification...")
    
    try:
        # Call the start-verification endpoint
        response = requests.post(
            f"{API_BASE_URL}/verifications/{session_id}/start-verification",
            timeout=10
        )
        
        if response.status_code == 202:
            data = response.json()
            print("\n✅ Verification started successfully!")
            print(f"   Status: {data['status']}")
            print(f"   Estimated completion: {data['estimated_completion']}")
            print(f"   Note: {data['note']}")
            
            # Poll for status updates
            print("\n" + "="*80)
            print("Monitoring Progress (press Ctrl+C to stop monitoring)")
            print("="*80 + "\n")
            
            monitor_progress(session_id)
            
        elif response.status_code == 400:
            error = response.json()
            print(f"\n❌ Cannot start verification: {error['message']}")
            print(f"   Current status: {error.get('current_status', 'unknown')}")
            
        elif response.status_code == 404:
            print(f"\n❌ Session not found: {session_id}")
            
        else:
            print(f"\n❌ Unexpected error: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to API server.")
        print("   Make sure the Flask app is running: python app.py")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def monitor_progress(session_id):
    """Monitor verification progress"""
    last_percentage = -1
    last_activities = []
    
    try:
        while True:
            time.sleep(3)  # Poll every 3 seconds
            
            try:
                response = requests.get(
                    f"{API_BASE_URL}/verifications/{session_id}/status",
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data['status']
                    progress = data['progress']
                    activities = data['activities']
                    
                    # Show progress if changed
                    if progress['percentage'] != last_percentage:
                        print(f"\n📊 Progress: {progress['percentage']}%")
                        print(f"   Employment verifications: {progress['employment_verifications']}/{progress['total_employments']}")
                        print(f"   Reference checks: {progress['reference_checks']}/{progress['total_references']}")
                        print(f"   Technical analysis: {'✓' if progress['technical_analysis_complete'] else '...'}")
                        print(f"   Fraud flags: {progress['fraud_flags']}")
                        last_percentage = progress['percentage']
                    
                    # Show new activities
                    for activity in activities:
                        activity_key = f"{activity['type']}_{activity['message']}"
                        if activity_key not in last_activities:
                            status_icon = {
                                'pending': '⏳',
                                'in_progress': '🔄',
                                'completed': '✅'
                            }.get(activity['status'], '•')
                            print(f"{status_icon} {activity['message']}")
                            last_activities.append(activity_key)
                    
                    # Check if completed
                    if status == 'COMPLETED':
                        print("\n" + "="*80)
                        print("✅ VERIFICATION COMPLETED!")
                        print("="*80)
                        
                        # Get final report
                        get_report(session_id)
                        break
                        
            except requests.exceptions.Timeout:
                print("⚠️  Status check timed out, retrying...")
                continue
                
    except KeyboardInterrupt:
        print("\n\n⏸️  Monitoring stopped (verification continues in background)")
        print(f"   Check status: GET {API_BASE_URL}/verifications/{session_id}/status")


def get_report(session_id):
    """Get and display the final report"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/verifications/{session_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if 'report' in data:
                report = data['report']
                
                print(f"\n📋 VERIFICATION REPORT")
                print(f"   Candidate: {data['candidate_name']}")
                print(f"   Risk Score: {report['risk_score']}")
                print(f"\n   Summary:")
                print(f"   {report['summary'][:200]}...")
                
                if report['fraud_flags']:
                    print(f"\n   ⚠️  Fraud Flags: {len(report['fraud_flags'])}")
                    for flag in report['fraud_flags'][:3]:  # Show first 3
                        print(f"      [{flag['severity']}] {flag['type']}: {flag['description'][:80]}...")
                else:
                    print(f"\n   ✅ No fraud flags detected")
                
                print(f"\n   Full report available at: GET {API_BASE_URL}/verifications/{session_id}")
            else:
                print("\n⚠️  Report not yet generated")
                
    except Exception as e:
        print(f"\n❌ Failed to get report: {str(e)}")


def list_sessions():
    """List all verification sessions"""
    try:
        response = requests.get(f"{API_BASE_URL}/verifications", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            sessions = data['verifications']
            
            if not sessions:
                print("\nNo verification sessions found.")
                print("Create one first using the UI or API.")
                return
            
            print(f"\n{'='*80}")
            print(f"Available Verification Sessions ({len(sessions)} total)")
            print(f"{'='*80}\n")
            
            for session in sessions[:10]:  # Show first 10
                print(f"Session ID: {session['session_id']}")
                print(f"  Candidate: {session['candidate_name']}")
                print(f"  Status: {session['status']}")
                print(f"  Risk Score: {session.get('risk_score', 'N/A')}")
                print(f"  Created: {session['created_at']}")
                print()
                
    except Exception as e:
        print(f"❌ Failed to list sessions: {str(e)}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python test_start_verification.py <session_id>")
        print("   or: python test_start_verification.py --list")
        print()
        print("This script will start the verification process which includes:")
        print("  - Phone calls to HR departments (via ElevenLabs)")
        print("  - Phone calls or emails to references")
        print("  - GitHub profile analysis")
        print("  - Fraud detection")
        print("  - Report generation")
        print()
        
        # Try to list available sessions
        list_sessions()
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        list_sessions()
        sys.exit(0)
    
    session_id = sys.argv[1]
    start_verification(session_id)


if __name__ == '__main__':
    main()
