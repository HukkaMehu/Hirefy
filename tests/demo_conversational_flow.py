"""Demo script showing conversational document collection flow"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.core.document_collection_orchestrator import DocumentCollectionOrchestrator


def print_separator():
    """Print a visual separator"""
    print("\n" + "=" * 70 + "\n")


def demo_conversational_flow():
    """Demonstrate the conversational document collection flow"""
    
    print_separator()
    print("🎯 CONVERSATIONAL DOCUMENT COLLECTION DEMO")
    print_separator()
    
    # Initialize orchestrator
    orchestrator = DocumentCollectionOrchestrator()
    print("✅ Orchestrator initialized")
    
    # Step 1: Start a new session
    print("\n📝 Step 1: Starting new collection session...")
    session_id, greeting = orchestrator.start_session(
        verification_session_id="demo-verify-001",
        candidate_name="Alice Johnson"
    )
    print(f"   Session ID: {session_id}")
    print(f"   🤖 Assistant: {greeting}")
    
    # Step 2: Candidate responds
    print("\n💬 Step 2: Candidate responds...")
    print("   👤 Candidate: I'm ready to start! Let me upload my CV.")
    result = orchestrator.process_message(
        session_id,
        "I'm ready to start! Let me upload my CV."
    )
    print(f"   🤖 Assistant: {result['message']}")
    
    # Step 3: Check session state
    print("\n📊 Step 3: Checking session state...")
    session = orchestrator.get_session(session_id)
    print(f"   Current Stage: {session['stage']}")
    print(f"   Messages Exchanged: {len(session['conversation_history'])}")
    print(f"   Documents Uploaded: {len(session['documents'])}")
    
    # Step 4: Simulate CV upload (without actual file)
    print("\n📄 Step 4: Simulating CV upload...")
    print("   (In real usage, candidate would upload actual CV file)")
    print("   Expected flow:")
    print("   - CV is processed with OCR")
    print("   - Employment history extracted")
    print("   - Education credentials extracted")
    print("   - System requests supporting documents")
    
    # Step 5: Show what happens after CV processing
    print("\n🔍 Step 5: After CV processing...")
    print("   System would:")
    print("   ✓ Extract candidate name, email, phone")
    print("   ✓ Parse employment history (companies, titles, dates)")
    print("   ✓ Parse education (institutions, degrees, dates)")
    print("   ✓ Detect employment gaps (>3 months)")
    print("   ✓ Request paystubs for each employment")
    print("   ✓ Request diplomas for each education entry")
    
    # Step 6: Show conflict detection
    print("\n⚠️  Step 6: Conflict detection example...")
    print("   If CV says: 'Senior Developer at Tech Corp (2020-2022)'")
    print("   But paystub shows: 'Developer at Tech Corp (2020-2022)'")
    print("   🤖 System asks: 'I noticed your CV says you worked as")
    print("      'Senior Developer' but the document shows 'Developer'.")
    print("      Which is correct?'")
    
    # Step 7: Show gap explanation
    print("\n📅 Step 7: Gap explanation example...")
    print("   If gap detected: Jan 2019 - Jun 2019 (5 months)")
    print("   🤖 System asks: 'I notice a gap in your employment from")
    print("      Jan 2019 to Jun 2019 (about 5 months). Could you tell")
    print("      me what you were doing during this time?'")
    
    # Step 8: Final confirmation
    print("\n✅ Step 8: Final confirmation...")
    print("   After all documents collected and conflicts resolved:")
    print("   🤖 System: 'Great! I've collected 5 documents: CV, 2 paystubs,")
    print("      2 diplomas. We've clarified 1 inconsistency. Does everything")
    print("      look correct before we begin contacting your references and")
    print("      employers?'")
    
    # Step 9: Finalization
    print("\n🎉 Step 9: Finalizing collection...")
    print("   When candidate confirms, system:")
    print("   ✓ Marks session as COMPLETED")
    print("   ✓ Returns summary with all extracted data")
    print("   ✓ Passes data to verification orchestrator")
    print("   ✓ Begins employment/reference verification")
    
    print_separator()
    print("✨ DEMO COMPLETE")
    print_separator()
    
    # Show session summary
    print("\n📋 Session Summary:")
    print(f"   Session ID: {session_id}")
    print(f"   Verification ID: demo-verify-001")
    print(f"   Candidate: Alice Johnson")
    print(f"   Stage: {session['stage']}")
    print(f"   Messages: {len(session['conversation_history'])}")
    print(f"   Documents: {len(session['documents'])}")
    
    print("\n💡 Key Features Demonstrated:")
    print("   ✓ Natural language conversation")
    print("   ✓ Step-by-step document collection")
    print("   ✓ Automatic conflict detection")
    print("   ✓ Employment gap identification")
    print("   ✓ Conversational clarification")
    print("   ✓ Session state management")
    print("   ✓ Final confirmation before verification")
    
    print("\n🔗 API Endpoints Available:")
    print("   POST   /api/chat/sessions")
    print("   POST   /api/chat/sessions/{id}/messages")
    print("   POST   /api/chat/sessions/{id}/documents")
    print("   GET    /api/chat/sessions/{id}")
    print("   POST   /api/chat/sessions/{id}/finalize")
    
    print_separator()


if __name__ == '__main__':
    demo_conversational_flow()
