#!/usr/bin/env python3
"""
Employment Verification Agent - Main Entry Point

This script provides a CLI interface for initiating automated employment
verification and reference calls using ElevenLabs conversational AI.
"""

import argparse
import sys
import os
from datetime import datetime
from dotenv import load_dotenv


def main():
    """Main entry point for the Employment Verification Agent CLI."""
    # Load environment variables
    load_dotenv()
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Employment Verification Agent - Automated verification calls and emails using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # HR Verification Call
  python main.py hr --candidate "John Doe" --job-title "Software Engineer" \\
    --start-date "2020-01-15" --end-date "2023-06-30" --phone "+1-555-0100"
  
  # Reference Call
  python main.py reference --candidate "Jane Smith" --reference-name "Bob Johnson" \\
    --phone "+1-555-0200" --relationship "manager"
  
  # HR Verification Email
  python main.py email-hr --candidate "John Doe" --job-title "Software Engineer" \\
    --start-date "2020-01-15" --end-date "2023-06-30" --email "hr@company.com"
  
  # Reference Email
  python main.py email-reference --candidate "Jane Smith" --reference-name "Bob Johnson" \\
    --email "bob.johnson@company.com" --relationship "manager"
        """
    )
    
    # Add subcommands for call and email types
    subparsers = parser.add_subparsers(dest='command_type', help='Type of verification action', required=True)
    
    # HR Verification Call subcommand
    hr_parser = subparsers.add_parser('hr', help='Initiate HR verification call')
    hr_parser.add_argument('--candidate', required=True, help='Candidate full name')
    hr_parser.add_argument('--job-title', required=True, help='Job title to verify')
    hr_parser.add_argument('--start-date', required=True, help='Employment start date (YYYY-MM-DD)')
    hr_parser.add_argument('--end-date', required=True, help='Employment end date (YYYY-MM-DD)')
    hr_parser.add_argument('--phone', required=True, help='HR contact phone number (E.164 format)')
    
    # Reference Call subcommand
    ref_parser = subparsers.add_parser('reference', help='Initiate reference call')
    ref_parser.add_argument('--candidate', required=True, help='Candidate full name')
    ref_parser.add_argument('--reference-name', required=True, help='Reference contact name')
    ref_parser.add_argument('--phone', required=True, help='Reference phone number (E.164 format)')
    ref_parser.add_argument('--relationship', required=True, 
                           choices=['manager', 'coworker', 'supervisor'],
                           help='Relationship to candidate')
    
    # HR Verification Email subcommand
    email_hr_parser = subparsers.add_parser('email-hr', help='Send HR verification email')
    email_hr_parser.add_argument('--candidate', required=True, help='Candidate full name')
    email_hr_parser.add_argument('--job-title', required=True, help='Job title to verify')
    email_hr_parser.add_argument('--start-date', required=True, help='Employment start date (YYYY-MM-DD)')
    email_hr_parser.add_argument('--end-date', required=True, help='Employment end date (YYYY-MM-DD)')
    email_hr_parser.add_argument('--email', required=True, help='HR contact email address')
    
    # Reference Email subcommand
    email_ref_parser = subparsers.add_parser('email-reference', help='Send reference check email')
    email_ref_parser.add_argument('--candidate', required=True, help='Candidate full name')
    email_ref_parser.add_argument('--reference-name', required=True, help='Reference contact name')
    email_ref_parser.add_argument('--email', required=True, help='Reference email address')
    email_ref_parser.add_argument('--relationship', required=True, 
                                  choices=['manager', 'coworker', 'supervisor'],
                                  help='Relationship to candidate')
    
    # Live HR Email Conversation subcommand
    live_hr_parser = subparsers.add_parser('live-email-hr', help='Start live HR verification email conversation')
    live_hr_parser.add_argument('--candidate', required=True, help='Candidate full name')
    live_hr_parser.add_argument('--job-title', required=True, help='Job title to verify')
    live_hr_parser.add_argument('--start-date', required=True, help='Employment start date (YYYY-MM-DD)')
    live_hr_parser.add_argument('--end-date', required=True, help='Employment end date (YYYY-MM-DD)')
    live_hr_parser.add_argument('--email', required=True, help='HR contact email address')
    live_hr_parser.add_argument('--timeout', type=int, default=15, help='Conversation timeout in minutes (default: 15)')
    
    # Live Reference Email Conversation subcommand
    live_ref_parser = subparsers.add_parser('live-email-reference', help='Start live reference check email conversation')
    live_ref_parser.add_argument('--candidate', required=True, help='Candidate full name')
    live_ref_parser.add_argument('--reference-name', required=True, help='Reference contact name')
    live_ref_parser.add_argument('--email', required=True, help='Reference email address')
    live_ref_parser.add_argument('--relationship', required=True, 
                                  choices=['manager', 'coworker', 'supervisor'],
                                  help='Relationship to candidate')
    live_ref_parser.add_argument('--timeout', type=int, default=15, help='Conversation timeout in minutes (default: 15)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Route to appropriate handler based on command type
    if args.command_type in ['hr', 'reference']:
        return handle_call_command(args)
    elif args.command_type in ['email-hr', 'email-reference']:
        return handle_email_command(args)
    elif args.command_type in ['live-email-hr', 'live-email-reference']:
        return handle_live_email_command(args)
    else:
        print(f"❌ Unknown command type: {args.command_type}", file=sys.stderr)
        return 1


def handle_call_command(args):
    """Handle phone call commands (hr, reference).
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Import here to avoid loading ElevenLabs when not needed
    from src.core.call_orchestrator import CallOrchestrator
    
    # Initialize call orchestrator
    try:
        orchestrator = CallOrchestrator()
    except Exception as e:
        print(f"❌ Error initializing call orchestrator: {e}", file=sys.stderr)
        return 1
    
    # Display call initiation message
    print("=" * 60)
    print("EMPLOYMENT VERIFICATION AGENT")
    print("=" * 60)
    print(f"\nCandidate: {args.candidate}")
    print(f"Call Type: {args.command_type.upper()}")
    print(f"Contact Phone: {args.phone}")
    
    # Execute appropriate call type
    try:
        if args.command_type == 'hr':
            print(f"Job Title: {args.job_title}")
            print(f"Employment Period: {args.start_date} to {args.end_date}")
            print("\n🔄 Initiating HR verification call...")
            
            result = orchestrator.initiate_hr_verification(
                candidate_name=args.candidate,
                job_title=args.job_title,
                start_date=args.start_date,
                end_date=args.end_date,
                hr_phone=args.phone
            )
            
        elif args.command_type == 'reference':
            print(f"Reference: {args.reference_name}")
            print(f"Relationship: {args.relationship.title()}")
            print("\n🔄 Initiating reference call...")
            
            result = orchestrator.initiate_reference_call(
                candidate_name=args.candidate,
                reference_name=args.reference_name,
                reference_phone=args.phone,
                relationship=args.relationship
            )
        
        # Display call results
        print("\n" + "=" * 60)
        if result.success:
            print("✅ CALL COMPLETED SUCCESSFULLY")
            print("=" * 60)
            print(f"\nCall ID: {result.call_id}")
            print(f"Duration: {result.duration_seconds} seconds")
            print(f"Transcript saved to: {result.transcript_path}")
            print("\n✨ You can now review the transcript for verification details.")
            return 0
        else:
            print("❌ CALL FAILED")
            print("=" * 60)
            print(f"\nError: {result.error_message}")
            print("\n💡 Please check your configuration and try again.")
            return 1
            
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1


def handle_email_command(args):
    """Handle email commands (email-hr, email-reference).
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Import here to avoid loading ElevenLabs when not needed
    from src.core.email_orchestrator import EmailOrchestrator
    
    # Initialize email orchestrator
    try:
        orchestrator = EmailOrchestrator()
    except ValueError as e:
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        print("\n💡 Please check your SMTP settings in the .env file.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error initializing email orchestrator: {e}", file=sys.stderr)
        return 1
    
    # Display email initiation message
    print("=" * 60)
    print("EMPLOYMENT VERIFICATION AGENT - EMAIL")
    print("=" * 60)
    print(f"\nCandidate: {args.candidate}")
    print(f"Email Type: {args.command_type.upper()}")
    print(f"Recipient: {args.email}")
    
    # Execute appropriate email type
    try:
        if args.command_type == 'email-hr':
            print(f"Job Title: {args.job_title}")
            print(f"Employment Period: {args.start_date} to {args.end_date}")
            print("\n📧 Sending HR verification email...")
            
            result = orchestrator.send_hr_verification_email(
                candidate_name=args.candidate,
                job_title=args.job_title,
                start_date=args.start_date,
                end_date=args.end_date,
                hr_email=args.email
            )
            
        elif args.command_type == 'email-reference':
            print(f"Reference: {args.reference_name}")
            print(f"Relationship: {args.relationship.title()}")
            print("\n📧 Sending reference check email...")
            
            result = orchestrator.send_reference_email(
                candidate_name=args.candidate,
                reference_name=args.reference_name,
                reference_email=args.email,
                relationship=args.relationship
            )
        
        # Display email results
        print("\n" + "=" * 60)
        if result.success:
            print("✅ EMAIL SENT SUCCESSFULLY")
            print("=" * 60)
            print(f"\nEmail ID: {result.email_id}")
            print(f"Recipient: {result.recipient}")
            print(f"Log saved to: {result.log_path}")
            print("\n✨ The verification request has been sent. You can check the log for details.")
            return 0
        else:
            print("❌ EMAIL FAILED")
            print("=" * 60)
            print(f"\nError: {result.error_message}")
            print(f"\nLog saved to: {result.log_path}")
            print("\n💡 Please check your SMTP configuration and try again.")
            return 1
            
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}", file=sys.stderr)
        print("\n💡 Please check your input parameters and try again.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1


def handle_live_email_command(args):
    """Handle live email conversation commands.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Import here to avoid loading dependencies when not needed
    from src.core.email_conversation import EmailConversationHandler
    
    # Get OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if not openai_api_key:
        print("❌ Missing OPENAI_API_KEY in .env file", file=sys.stderr)
        return 1
    
    # Initialize conversation handler
    try:
        handler = EmailConversationHandler(openai_api_key)
    except Exception as e:
        print(f"❌ Error initializing conversation handler: {e}", file=sys.stderr)
        return 1
    
    # Display conversation initiation message
    print("=" * 60)
    print("LIVE EMAIL CONVERSATION")
    print("=" * 60)
    print(f"\nCandidate: {args.candidate}")
    print(f"Type: {args.command_type.upper()}")
    print(f"Recipient: {args.email}")
    
    try:
        if args.command_type == 'live-email-hr':
            print(f"Job Title: {args.job_title}")
            print(f"Employment Period: {args.start_date} to {args.end_date}")
            
            # Create initial message
            initial_subject = f"Employment Verification Request for {args.candidate}"
            initial_message = f"""Hello,

I am conducting an employment verification for {args.candidate}, who has listed your organization as a previous employer.

Could you please confirm the following information:
- Employee Name: {args.candidate}
- Job Title: {args.job_title}
- Employment Start Date: {args.start_date}
- Employment End Date: {args.end_date}

Please reply to this email with confirmation or any corrections needed.

Thank you for your assistance.

Best regards,
{os.getenv('SMTP_FROM_NAME')}
{os.getenv('SMTP_FROM_EMAIL')}"""
            
            system_prompt = f"""You are an HR verification assistant conducting employment verification via email. 
Your goal is to verify employment details for {args.candidate} (Job Title: {args.job_title}, Dates: {args.start_date} to {args.end_date}).

Be professional, concise, and polite. Ask follow-up questions if information is unclear or incomplete.
When you have confirmed all the required information (name, job title, start date, end date), thank them and end the conversation.
Always end your final message with "Thank you for your assistance with this verification."
"""
            
            result = handler.start_conversation(
                recipient_email=args.email,
                initial_subject=initial_subject,
                initial_message=initial_message,
                system_prompt=system_prompt,
                timeout_minutes=args.timeout
            )
            
        elif args.command_type == 'live-email-reference':
            print(f"Reference: {args.reference_name}")
            print(f"Relationship: {args.relationship.title()}")
            
            # Create initial message
            initial_subject = f"Reference Request for {args.candidate}"
            initial_message = f"""Hello {args.reference_name},

I am conducting a reference check for {args.candidate}, who has listed you as a {args.relationship}.

I would appreciate your feedback on the following:
- How would you describe {args.candidate}'s work performance?
- What were their key strengths?
- How well did they work with the team?

Please reply to this email with your feedback.

Thank you for your time.

Best regards,
{os.getenv('SMTP_FROM_NAME')}
{os.getenv('SMTP_FROM_EMAIL')}"""
            
            system_prompt = f"""You are a reference check assistant conducting a reference check via email for {args.candidate}.
The reference contact is {args.reference_name}, who was their {args.relationship}.

Be professional, friendly, and conversational. Ask follow-up questions to get detailed feedback about:
- Work performance and quality
- Strengths and areas for improvement
- Teamwork and collaboration
- Overall recommendation

When you have gathered sufficient qualitative feedback, thank them warmly and end the conversation.
Always end your final message with "Thank you for taking the time to provide this reference."
"""
            
            result = handler.start_conversation(
                recipient_email=args.email,
                initial_subject=initial_subject,
                initial_message=initial_message,
                system_prompt=system_prompt,
                timeout_minutes=args.timeout
            )
        
        # Display results
        print("\n" + "=" * 60)
        if result['success']:
            print("✅ CONVERSATION COMPLETED")
            print("=" * 60)
            print(f"\nDuration: {result['duration_seconds']} seconds")
            print(f"Messages exchanged: {len(result['conversation'])}")
            print(f"Status: {'Complete' if result['complete'] else 'Timed out'}")
            
            # Save conversation transcript
            candidate_dir = os.path.join(
                os.getenv('TRANSCRIPT_OUTPUT_DIR', './transcripts'),
                args.candidate.lower().replace(' ', '_')
            )
            os.makedirs(candidate_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            transcript_path = os.path.join(
                candidate_dir,
                f"email_conversation_{args.command_type.replace('live-email-', '')}_{timestamp}.txt"
            )
            
            with open(transcript_path, 'w', encoding='utf-8') as f:
                f.write(f"=== EMAIL CONVERSATION ===\n")
                f.write(f"Candidate: {args.candidate}\n")
                f.write(f"Type: {args.command_type}\n")
                f.write(f"Recipient: {args.email}\n")
                f.write(f"Duration: {result['duration_seconds']} seconds\n")
                f.write(f"Status: {'Complete' if result['complete'] else 'Timed out'}\n\n")
                f.write(f"--- CONVERSATION ---\n\n")
                
                for msg in result['conversation']:
                    role = "Agent" if msg['role'] == 'assistant' else "Recipient"
                    f.write(f"[{msg['timestamp']}] {role}:\n")
                    f.write(f"{msg['content']}\n\n")
                
                f.write(f"--- END CONVERSATION ---\n")
            
            print(f"Transcript saved to: {transcript_path}")
            print("\n✨ You can review the full conversation in the transcript file.")
            return 0
        else:
            print("❌ CONVERSATION FAILED")
            print("=" * 60)
            print(f"\nError: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1



if __name__ == '__main__':
    sys.exit(main())
