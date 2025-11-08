"""
Simple test to verify AI analysis works
"""
import os
from src.api.app import create_app
from src.core.ai_analyzer import AIAnalyzer
from src.database.models import VerificationSession

print("=" * 80)
print("SIMPLE AI ANALYSIS TEST")
print("=" * 80)

# Create app context
app = create_app()

with app.app_context():
    # Get the most recent verification
    session = VerificationSession.query.order_by(VerificationSession.created_at.desc()).first()
    
    if not session:
        print("❌ No verification sessions found in database")
        exit(1)
    
    print(f"\n📋 Testing with verification: {session.id}")
    print(f"   Candidate: {session.candidate.full_name}")
    print(f"   Status: {session.status.value}")
    
    # Check OpenAI API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n❌ OPENAI_API_KEY not found in environment!")
        print("   Set it in your .env file")
        exit(1)
    else:
        print(f"\n✅ OpenAI API key found: {api_key[:10]}...")
    
    # Create analyzer
    print("\n🤖 Creating AI Analyzer...")
    analyzer = AIAnalyzer()
    
    if not analyzer.client:
        print("❌ AI Analyzer client not initialized!")
        exit(1)
    
    print("✅ AI Analyzer initialized")
    
    # Run analysis
    print(f"\n🚀 Running AI analysis on verification {session.id}...")
    print("   This may take 10-30 seconds...")
    
    result = analyzer.analyze_verification(session.id)
    
    print("\n" + "=" * 80)
    if result.get('success'):
        print("✅ AI ANALYSIS SUCCEEDED!")
        print("=" * 80)
        print(f"\nModel: {result.get('model')}")
        print(f"Tokens used: {result.get('usage', {}).get('total_tokens', 'N/A')}")
        print("\n📊 Analysis sections:")
        for key in result.get('analysis', {}).keys():
            print(f"   - {key}")
        print("\n📝 Summary:")
        print(result.get('analysis', {}).get('summary', 'No summary')[:200] + "...")
    else:
        print("❌ AI ANALYSIS FAILED!")
        print("=" * 80)
        print(f"\nError: {result.get('error')}")
    
    print("\n" + "=" * 80)
