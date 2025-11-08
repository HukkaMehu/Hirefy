"""
Test AI Data Compiler - Demonstrates compiling all verification data for AI analysis
"""
import sys
import json
from src.core.ai_data_compiler import AIDataCompiler


def test_compile_verification():
    """Test compiling data for a specific verification"""
    print("=" * 80)
    print("AI DATA COMPILER TEST")
    print("=" * 80)
    
    # Create Flask app context
    from src.api.app import create_app
    app = create_app()
    
    with app.app_context():
        compiler = AIDataCompiler()
        
        # Get all verifications
        from src.database import db, VerificationSession
        verifications = db.session.query(VerificationSession).all()
        
        if not verifications:
            print("\n❌ No verifications found in database")
            print("Please create a verification first using the API or demo scripts")
            return
        
        print(f"\n✅ Found {len(verifications)} verification(s)")
        
        # Compile data for the first verification
        verification = verifications[0]
        candidate_name = verification.candidate.full_name if verification.candidate else "Unknown"
        print(f"\n📊 Compiling data for: {candidate_name}")
        print(f"   Verification ID: {verification.id}")
        print(f"   Status: {verification.status.value if hasattr(verification.status, 'value') else verification.status}")
        
        try:
            compiled_data = compiler.compile_verification_data(verification.id)
            
            print("\n" + "=" * 80)
            print("COMPILED DATA SUMMARY")
            print("=" * 80)
            
            print(f"\n📞 Transcripts: {len(compiled_data['transcripts'])}")
            for transcript in compiled_data['transcripts']:
                print(f"   - {transcript['filename']}")
                if 'parsed_data' in transcript:
                    parsed = transcript['parsed_data']
                    print(f"     Type: {parsed.get('call_type')}")
                    print(f"     Date: {parsed.get('date')}")
                    print(f"     Conversation turns: {len(parsed.get('conversation', []))}")
            
            print(f"\n💼 Employment Records: {len(compiled_data['employments'])}")
            for emp in compiled_data['employments']:
                print(f"   - {emp['job_title']} at {emp['company_name']}")
            
            print(f"\n🎓 Education Records: {len(compiled_data['education'])}")
            for edu in compiled_data['education']:
                print(f"   - {edu['degree_type']} from {edu['institution_name']}")
            
            print(f"\n🚩 Fraud Flags: {len(compiled_data['fraud_flags'])}")
            for flag in compiled_data['fraud_flags']:
                print(f"   - [{flag['severity']}] {flag['flag_type']}")
            
            print(f"\n📋 Contact Records: {len(compiled_data['contact_records'])}")
            for record in compiled_data['contact_records']:
                print(f"   - {record['contact_type']} with {record['contact_name']}")
            
            print("\n" + "=" * 80)
            print("AI ANALYSIS PROMPT")
            print("=" * 80)
            
            ai_prompt = compiler.export_for_ai_analysis(verification.id)
            print(ai_prompt)
            
            # Save to file
            output_file = f"ai_analysis_verification_{verification.id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "compiled_data": compiled_data,
                    "ai_prompt": ai_prompt
                }, f, indent=2, ensure_ascii=False)
            
            print("\n" + "=" * 80)
            print(f"✅ Data exported to: {output_file}")
            print("=" * 80)
            
            print("\n📋 You can now:")
            print("   1. Copy the AI prompt above and paste it into an AI thinking model")
            print("   2. Use the exported JSON file for programmatic analysis")
            print("   3. Access via API: GET /api/ai/verifications/{id}/ai-prompt")
            
        except Exception as e:
            print(f"\n❌ Error compiling data: {e}")
            import traceback
            traceback.print_exc()


def test_api_endpoints():
    """Show available API endpoints for AI data compilation"""
    print("\n" + "=" * 80)
    print("AVAILABLE API ENDPOINTS")
    print("=" * 80)
    
    endpoints = [
        {
            "method": "GET",
            "path": "/api/ai/verifications/<id>/compile",
            "description": "Get compiled data for a verification"
        },
        {
            "method": "GET",
            "path": "/api/ai/verifications/<id>/ai-prompt",
            "description": "Get AI analysis prompt with all data"
        },
        {
            "method": "GET",
            "path": "/api/ai/verifications/<id>/export",
            "description": "Download compiled data as JSON file"
        },
        {
            "method": "GET",
            "path": "/api/ai/verifications/compile-all",
            "description": "Compile data for all verifications"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n{endpoint['method']} {endpoint['path']}")
        print(f"   {endpoint['description']}")


if __name__ == "__main__":
    test_compile_verification()
    test_api_endpoints()
