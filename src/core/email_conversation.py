"""
Live Email Conversation Handler

Monitors inbox for replies and uses AI to conduct real-time email conversations
for employment verification.
"""

import os
import time
import imaplib
import email
from email.header import decode_header
from datetime import datetime
from typing import Optional, List, Dict
import logging
from openai import OpenAI

from src.core.email_client import EmailClient

logger = logging.getLogger(__name__)


class EmailConversationHandler:
    """Handles live email conversations with AI-powered responses."""
    
    def __init__(self, openai_api_key: str):
        """Initialize the email conversation handler.
        
        Args:
            openai_api_key: OpenAI API key for AI responses
        """
        self.email_client = EmailClient()
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Get SMTP config from environment for IMAP
        smtp_host = os.getenv('SMTP_HOST')
        self.imap_host = smtp_host.replace('smtp', 'imap')
        self.imap_username = os.getenv('SMTP_USERNAME')
        self.imap_password = os.getenv('SMTP_PASSWORD')
        self.conversation_history: List[Dict[str, str]] = []
        
    def start_conversation(
        self,
        recipient_email: str,
        initial_subject: str,
        initial_message: str,
        system_prompt: str,
        timeout_minutes: int = 15,
        poll_interval_seconds: int = 10
    ) -> Dict[str, any]:
        """Start a live email conversation.
        
        Args:
            recipient_email: Email address to converse with
            initial_subject: Subject line for initial email
            initial_message: Initial message to send
            system_prompt: System prompt for AI behavior
            timeout_minutes: Maximum conversation duration
            poll_interval_seconds: How often to check for replies
            
        Returns:
            Dictionary with conversation results
        """
        print(f"\n📧 Starting live email conversation with {recipient_email}")
        print(f"⏱️  Timeout: {timeout_minutes} minutes")
        print(f"🔄 Checking for replies every {poll_interval_seconds} seconds\n")
        
        # Send initial email
        print(f"[{self._timestamp()}] Sending initial email...")
        success = self.email_client.send_email(
            to_address=recipient_email,
            subject=initial_subject,
            body=initial_message
        )
        
        if not success:
            return {
                'success': False,
                'error': 'Failed to send initial email',
                'conversation': []
            }
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'assistant',
            'content': initial_message,
            'timestamp': self._timestamp()
        })
        
        print(f"[{self._timestamp()}] ✅ Initial email sent")
        print(f"[{self._timestamp()}] 👀 Monitoring inbox for replies...\n")
        
        # Monitor for replies
        start_time = time.time()
        timeout_seconds = timeout_minutes * 60
        last_check_time = 0
        conversation_complete = False
        
        while time.time() - start_time < timeout_seconds:
            current_time = time.time()
            
            # Check for new emails at specified interval
            if current_time - last_check_time >= poll_interval_seconds:
                last_check_time = current_time
                
                reply = self._check_for_reply(recipient_email, initial_subject)
                
                if reply:
                    print(f"[{self._timestamp()}] 📨 Received reply from {recipient_email}")
                    print(f"[{self._timestamp()}] Reply: {reply[:100]}...")
                    
                    # Add to conversation history
                    self.conversation_history.append({
                        'role': 'user',
                        'content': reply,
                        'timestamp': self._timestamp()
                    })
                    
                    # Generate AI response
                    print(f"[{self._timestamp()}] 🤖 Generating AI response...")
                    ai_response, is_complete = self._generate_response(
                        system_prompt,
                        reply
                    )
                    
                    if is_complete:
                        print(f"[{self._timestamp()}] ✅ Verification complete!")
                        conversation_complete = True
                        
                        # Send final response
                        self.email_client.send_email(
                            to_address=recipient_email,
                            subject=f"Re: {initial_subject}",
                            body=ai_response
                        )
                        
                        self.conversation_history.append({
                            'role': 'assistant',
                            'content': ai_response,
                            'timestamp': self._timestamp()
                        })
                        
                        print(f"[{self._timestamp()}] 📧 Final response sent")
                        break
                    else:
                        # Send follow-up question
                        print(f"[{self._timestamp()}] 📧 Sending follow-up...")
                        self.email_client.send_email(
                            to_address=recipient_email,
                            subject=f"Re: {initial_subject}",
                            body=ai_response
                        )
                        
                        self.conversation_history.append({
                            'role': 'assistant',
                            'content': ai_response,
                            'timestamp': self._timestamp()
                        })
                        
                        print(f"[{self._timestamp()}] ✅ Follow-up sent")
                        print(f"[{self._timestamp()}] 👀 Waiting for next reply...\n")
            
            time.sleep(1)  # Small sleep to prevent busy waiting
        
        # Conversation ended
        elapsed_time = time.time() - start_time
        
        if conversation_complete:
            print(f"\n✅ Conversation completed successfully!")
        else:
            print(f"\n⏱️  Conversation timed out after {elapsed_time:.0f} seconds")
        
        return {
            'success': conversation_complete or len(self.conversation_history) > 1,
            'conversation': self.conversation_history,
            'duration_seconds': int(elapsed_time),
            'complete': conversation_complete
        }
    
    def _check_for_reply(self, from_email: str, subject: str) -> Optional[str]:
        """Check inbox for new replies from specific sender.
        
        Args:
            from_email: Email address to check for
            subject: Subject line to match
            
        Returns:
            Reply text if found, None otherwise
        """
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_host)
            mail.login(self.imap_username, self.imap_password)
            mail.select('inbox')
            
            # Search for UNSEEN emails from sender with subject
            # UNSEEN ensures we only get new emails we haven't processed
            _, message_numbers = mail.search(None, f'(UNSEEN FROM "{from_email}" SUBJECT "{subject}")')
            
            if not message_numbers[0]:
                mail.close()
                mail.logout()
                return None
            
            # Get the most recent unread email
            latest_email_id = message_numbers[0].split()[-1]
            _, msg_data = mail.fetch(latest_email_id, '(RFC822)')
            
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Check if this email was sent by us (avoid processing our own emails)
            sender = email_message.get('From', '')
            if self.imap_username.lower() in sender.lower():
                # This is an email we sent, not a reply - mark as seen and skip
                mail.store(latest_email_id, '+FLAGS', '\\Seen')
                mail.close()
                mail.logout()
                return None
            
            # Extract text content
            reply_text = self._extract_email_text(email_message)
            
            # Mark as read to avoid re-processing
            mail.store(latest_email_id, '+FLAGS', '\\Seen')
            
            mail.close()
            mail.logout()
            
            return reply_text
            
        except Exception as e:
            logger.error(f"Error checking for reply: {e}")
            return None
    
    def _extract_email_text(self, email_message) -> str:
        """Extract plain text from email message.
        
        Args:
            email_message: Email message object
            
        Returns:
            Plain text content
        """
        text_content = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        text_content = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                text_content = email_message.get_payload(decode=True).decode()
            except:
                pass
        
        return text_content.strip()
    
    def _generate_response(self, system_prompt: str, user_message: str) -> tuple[str, bool]:
        """Generate AI response using OpenAI.
        
        Args:
            system_prompt: System prompt defining AI behavior
            user_message: User's message to respond to
            
        Returns:
            Tuple of (response_text, is_conversation_complete)
        """
        try:
            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            for msg in self.conversation_history:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Check if conversation is complete
            # Simple heuristic: if AI says "thank you" or "complete" or similar
            completion_keywords = ['thank you for', 'verification complete', 'all set', 'that\'s all', 'have everything']
            is_complete = any(keyword in ai_response.lower() for keyword in completion_keywords)
            
            return ai_response, is_complete
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I apologize, but I'm having trouble processing your response. Could you please try again?", False
    
    def _timestamp(self) -> str:
        """Get current timestamp string."""
        return datetime.now().strftime("%H:%M:%S")
