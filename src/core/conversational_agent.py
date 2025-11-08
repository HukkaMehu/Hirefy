"""Conversational AI agent for guiding document collection"""

import os
from typing import List, Dict, Any, Optional
from openai import OpenAI


class ConversationalAgent:
    """Wraps OpenAI GPT-4 for natural language chat interactions during document collection"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize conversational agent.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # System prompt for document collection
        self.system_prompt = """You are a friendly and professional document collection assistant for a recruitment verification platform. Your role is to:

1. Guide candidates through uploading their CV, diplomas, and employment evidence (paystubs/offer letters)
2. Ask clarifying questions when you detect inconsistencies between documents
3. Request explanations for employment gaps (>3 months)
4. Be conversational, warm, and supportive while maintaining professionalism
5. Keep responses concise and focused on one request at a time
6. Use natural language, not robotic or overly formal

Guidelines:
- Start by requesting the CV
- After CV is processed, request supporting documents for each employment period
- If you detect conflicts (e.g., different job titles, dates), ask for clarification
- For employment gaps, ask what the candidate was doing during that time
- For education, request diplomas or transcripts
- Always acknowledge document uploads and thank the candidate
- At the end, summarize what was collected and ask for confirmation

Handling skipped documents:
- If a candidate says they don't have a document, acknowledge it and move to the next one
- If they say "I'm done" or "continue", summarize what was collected and move to finalization
- Be understanding - not everyone has all documents readily available
- Make a note of skipped documents for the verification report

Keep your tone friendly and encouraging. Remember, candidates may be nervous about the verification process."""
    
    def generate_response(
        self,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a conversational response based on history and context.
        
        Args:
            conversation_history: List of messages [{"role": "user/assistant", "content": "..."}]
            context: Additional context about the verification session (extracted data, conflicts, etc.)
            
        Returns:
            Assistant's response text
        """
        try:
            # Build messages with system prompt
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Add context as a system message if provided
            if context:
                context_message = self._format_context(context)
                if context_message:
                    messages.append({"role": "system", "content": context_message})
            
            # Add conversation history
            messages.extend(conversation_history)
            
            # Generate response
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
                temperature=0.7  # Slightly higher for more natural conversation
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Error generating conversational response: {str(e)}")
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information for the AI.
        
        Args:
            context: Context dictionary with session state
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Current stage
        if 'stage' in context:
            context_parts.append(f"Current stage: {context['stage']}")
        
        # Documents collected
        if 'documents_collected' in context:
            docs = context['documents_collected']
            context_parts.append(f"Documents collected: {', '.join(docs)}")
        
        # Extracted CV data
        if 'cv_data' in context:
            cv = context['cv_data']
            context_parts.append(f"Candidate name: {cv.get('candidate_name', 'Unknown')}")
            
            if 'employment_history' in cv:
                emp_count = len(cv['employment_history'])
                context_parts.append(f"Employment history: {emp_count} positions found")
            
            if 'education' in cv:
                edu_count = len(cv['education'])
                context_parts.append(f"Education: {edu_count} entries found")
        
        # Pending requests
        if 'pending_requests' in context:
            pending = context['pending_requests']
            if pending:
                context_parts.append(f"Pending document requests: {', '.join(pending)}")
        
        # Conflicts detected
        if 'conflicts' in context:
            conflicts = context['conflicts']
            if conflicts:
                context_parts.append(f"Conflicts detected: {len(conflicts)} inconsistencies need clarification")
                for conflict in conflicts[:3]:  # Show first 3
                    context_parts.append(f"  - {conflict.get('description', '')}")
        
        # Employment gaps
        if 'gaps' in context:
            gaps = context['gaps']
            if gaps:
                context_parts.append(f"Employment gaps: {len(gaps)} gaps need explanation")
        
        # Next action
        if 'next_action' in context:
            context_parts.append(f"Next action: {context['next_action']}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def generate_initial_greeting(self, candidate_name: Optional[str] = None) -> str:
        """Generate initial greeting message.
        
        Args:
            candidate_name: Candidate's name if known
            
        Returns:
            Greeting message
        """
        if candidate_name:
            return f"Hi {candidate_name}! 👋 I'm here to help you through the verification process. To get started, could you please upload your CV or resume? This will help me understand your background and guide you through the rest of the process."
        else:
            return "Hi there! 👋 I'm here to help you through the verification process. To get started, could you please upload your CV or resume? This will help me understand your background and guide you through the rest of the process."
    
    def generate_cv_processed_message(self, cv_data: Dict[str, Any]) -> str:
        """Generate message after CV is processed.
        
        Args:
            cv_data: Extracted CV data
            
        Returns:
            Response message
        """
        candidate_name = cv_data.get('candidate_name') or 'there'
        # Handle case where candidate_name is the string "None"
        if candidate_name == 'None' or not candidate_name.strip():
            candidate_name = 'there'
        
        employment_count = len(cv_data.get('employment_history', []))
        education_count = len(cv_data.get('education', []))
        
        return f"Thanks {candidate_name}! I've reviewed your CV and found {employment_count} employment position(s) and {education_count} education entry(ies). Now, let's verify these with supporting documents. I'll guide you through each one."
    
    def generate_document_request(
        self,
        document_type: str,
        company_name: Optional[str] = None,
        institution_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """Generate a request for a specific document.
        
        Args:
            document_type: Type of document (paystub, diploma, etc.)
            company_name: Company name for employment docs
            institution_name: Institution name for education docs
            start_date: Start date for employment
            end_date: End date for employment
            
        Returns:
            Document request message
        """
        if document_type == 'paystub':
            date_range = f"from {start_date} to {end_date}" if start_date and end_date else ""
            return f"Could you please upload a pay stub or offer letter from {company_name} {date_range}? This will help verify your employment there."
        
        elif document_type == 'diploma':
            return f"Could you please upload your diploma or transcript from {institution_name}? This will help verify your education credentials."
        
        return f"Could you please upload the requested document?"
    
    def generate_conflict_question(self, conflict: Dict[str, Any]) -> str:
        """Generate a question about a detected conflict.
        
        Args:
            conflict: Conflict information
            
        Returns:
            Clarification question
        """
        conflict_type = conflict.get('type', 'unknown')
        
        if conflict_type == 'job_title_mismatch':
            cv_title = conflict.get('cv_value')
            doc_title = conflict.get('document_value')
            return f"I noticed your CV says you worked as '{cv_title}' but the document shows '{doc_title}'. Which is correct, or were there multiple titles during your time there?"
        
        elif conflict_type == 'date_mismatch':
            cv_date = conflict.get('cv_value')
            doc_date = conflict.get('document_value')
            field = conflict.get('field', 'date')
            return f"Your CV shows {field} as {cv_date}, but the document shows {doc_date}. Could you clarify which is accurate?"
        
        elif conflict_type == 'company_name_mismatch':
            cv_company = conflict.get('cv_value')
            doc_company = conflict.get('document_value')
            return f"Your CV mentions '{cv_company}' but the document shows '{doc_company}'. Are these the same company, or is there a discrepancy?"
        
        return f"I noticed an inconsistency: {conflict.get('description', 'Please clarify this information.')}"
    
    def generate_gap_question(self, gap: Dict[str, Any]) -> str:
        """Generate a question about an employment gap.
        
        Args:
            gap: Gap information
            
        Returns:
            Gap explanation question
        """
        start_date = gap.get('start_date', '')
        end_date = gap.get('end_date', '')
        duration_months = gap.get('duration_months', 0)
        
        return f"I notice a gap in your employment from {start_date} to {end_date} (about {duration_months} months). Could you tell me what you were doing during this time?"
    
    def generate_completion_summary(
        self,
        documents_collected: List[str],
        conflicts_resolved: int,
        gaps_explained: int
    ) -> str:
        """Generate summary message before finalizing.
        
        Args:
            documents_collected: List of document types collected
            conflicts_resolved: Number of conflicts resolved
            gaps_explained: Number of gaps explained
            
        Returns:
            Summary message
        """
        summary = f"Great! I've collected {len(documents_collected)} document(s): {', '.join(documents_collected)}."
        
        if conflicts_resolved > 0:
            summary += f" We've clarified {conflicts_resolved} inconsistency(ies)."
        
        if gaps_explained > 0:
            summary += f" You've explained {gaps_explained} employment gap(s)."
        
        summary += " Does everything look correct before we begin contacting your references and employers?"
        
        return summary
