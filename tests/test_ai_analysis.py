"""
Test AI Analysis Integration
"""
import os
from src.api.app import create_app
from src.core.ai_analyzer import AIAnalyzer


def test_ai_analysis():
    """Test AI analysis on a verification"""
    print("=" * 80)
    print("AI ANALYSIS INTEGRATION TEST")
    print("=" * 80)
    
    # Check if OpenAI API key is configured
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  OPENAI_API_KEY not found in environment")
        print("Please add it to your .env file to enable AI analysis")
        print("\nExample:")
        print("OPENAI_API_KEY=sk-...")
        return
    
    app = create_app()
    
    with app.app_context():
        from src.database import db, VerificationSession
        
        # Get a verification
        verifications = db.session.query(VerificationSession).all()
        
        if not verifications:
            print("\n❌ No verifications found")
            return
        
        verification = verifications[0]
        candidate_name = verification.candidate.full_name if verification.candidate else "Unknown"
        
        print(f"\n📊 Testing AI analysis for: {candidate_name}")
        print(f"   Verification ID: {verification.id}")
        
        # Run AI analysis
        analyzer = AIAnalyzer()
        print("\n🤖 Running AI analysis...")
        print("   This may take 10-30 seconds...")
        
        result = analyzer.analyze_verification(verification.id)
        
        if result['success']:
            print("\n✅ AI Analysis completed successfully!")
            print(f"\n📈 Token usage:")
            print(f"   Prompt tokens: {result['usage']['prompt_tokens']}")
            print(f"   Completion tokens: {result['usage']['completion_tokens']}")
            print(f"   Total tokens: {result['usage']['total_tokens']}")
            
            print("\n" + "=" * 80)
            print("ANALYSIS SECTIONS:")
            print("=" * 80)
            
            analysis = result['analysis']
            for section, content in analysis.items():
                if content:
                    print(f"\n### {section.replace('_', ' ').title()}")
                    print("-" * 80)
                    print(content[:200] + "..." if len(content) > 200 else content)
            
            print("\n" + "=" * 80)
            print("✅ AI analysis is working!")
            print("=" * 80)
            print("\n📋 The analysis will now appear automatically in the UI after verification completes")
            
        else:
            print(f"\n❌ AI analysis failed: {result.get('error')}")


if __name__ == "__main__":
    test_ai_analysis()
