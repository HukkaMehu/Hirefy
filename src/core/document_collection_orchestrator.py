"""Document collection orchestrator - manages conversational document collection flow"""

import os
import uuid
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from src.core.conversational_agent import ConversationalAgent
from src.core.consistency_validator import ConsistencyValidator
from src.core.collection_session import CollectionSession, CollectionStage
from src.core.document_processor import DocumentProcessor
from src.core.document_models import CVData, EmploymentEvidence, EducationCredential


class DocumentCollectionOrchestrator:
    """Orchestrates conversational document collection process"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize orchestrator.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
        """
        self.agent = ConversationalAgent(api_key)
        self.validator = ConsistencyValidator()
        self.processor = DocumentProcessor(api_key)
        
        # In-memory session storage (for MVP - would use database in production)
        self.sessions: Dict[str, CollectionSession] = {}
    
    def start_session(
        self,
        verification_session_id: str,
        candidate_name: Optional[str] = None
    ) -> Tuple[str, str]:
        """Start a new document collection session.
        
        Args:
            verification_session_id: ID of the verification session
            candidate_name: Optional candidate name
            
        Returns:
            Tuple of (session_id, initial_message)
        """
        # Create new session
        session_id = str(uuid.uuid4())
        session = CollectionSession(
            session_id=session_id,
            verification_session_id=verification_session_id,
            candidate_name=candidate_name,
            stage=CollectionStage.AWAITING_CV
        )
        
        # Store session
        self.sessions[session_id] = session
        
        # Generate initial greeting
        initial_message = self.agent.generate_initial_greeting(candidate_name)
        session.add_message('assistant', initial_message)
        
        return session_id, initial_message
    
    def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, Any]:
        """Process a user message in the conversation.
        
        Args:
            session_id: Collection session ID
            user_message: User's message
            
        Returns:
            Response dictionary with assistant message and session state
        """
        # Get session
        session = self.sessions.get(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        # Add user message to history
        session.add_message('user', user_message)
        
        # Generate response based on current stage and context
        context = session.get_context_for_ai()
        conversation_history = session.get_conversation_for_ai()
        
        response = self.agent.generate_response(conversation_history, context)
        
        # Add assistant response to history
        session.add_message('assistant', response)
        
        return {
            'success': True,
            'message': response,
            'session': session.to_dict()
        }
    
    def upload_document(
        self,
        session_id: str,
        file_data: bytes,
        filename: str,
        file_extension: str,
        document_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process an uploaded document.
        
        Args:
            session_id: Collection session ID
            file_data: Raw file bytes
            filename: Original filename
            file_extension: File extension
            document_type: Optional document type hint (cv, paystub, diploma)
            
        Returns:
            Response dictionary with processing result
        """
        # Get session
        session = self.sessions.get(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        try:
            # Determine document type if not provided
            if not document_type:
                document_type = self._infer_document_type(session)
            
            # Process document based on type
            if document_type == 'cv':
                result = self._process_cv(session, file_data, filename, file_extension)
            elif document_type == 'paystub':
                result = self._process_paystub(session, file_data, filename, file_extension)
            elif document_type == 'diploma':
                result = self._process_diploma(session, file_data, filename, file_extension)
            else:
                return {
                    'success': False,
                    'error': f'Unknown document type: {document_type}'
                }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing document: {str(e)}'
            }
    
    def finalize_collection(self, session_id: str) -> Dict[str, Any]:
        """Finalize document collection and prepare for verification.
        
        Args:
            session_id: Collection session ID
            
        Returns:
            Summary of collected data
        """
        # Get session
        session = self.sessions.get(session_id)
        if not session:
            return {
                'success': False,
                'error': 'Session not found'
            }
        
        # Mark as completed
        session.stage = CollectionStage.COMPLETED
        session.final_confirmation = True
        
        # Generate summary
        summary = {
            'success': True,
            'session_id': session_id,
            'verification_session_id': session.verification_session_id,
            'documents_collected': len(session.documents),
            'cv_data': session.cv_data.to_dict() if session.cv_data else None,
            'paystubs': [p.to_dict() for p in session.paystubs],
            'diplomas': [d.to_dict() for d in session.diplomas],
            'inconsistencies': [i.to_dict() for i in session.inconsistencies],
            'employment_gaps': [g.to_dict() for g in session.employment_gaps],
            'conflicts_resolved': len(session.resolved_conflicts),
            'gaps_explained': len(session.explained_gaps)
        }
        
        return summary
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session state.
        
        Args:
            session_id: Collection session ID
            
        Returns:
            Session dictionary or None
        """
        session = self.sessions.get(session_id)
        return session.to_dict() if session else None
    
    def get_or_create_session_for_verification(self, verification_session_id: str) -> str:
        """Get existing or create new chat session for a verification session.
        
        Args:
            verification_session_id: Verification session ID
            
        Returns:
            Chat session ID
        """
        # Look for existing session with this verification_session_id
        for session_id, session in self.sessions.items():
            if session.verification_session_id == verification_session_id:
                return session_id
        
        # Create new session if none exists
        session_id, _ = self.start_session(verification_session_id)
        return session_id
    
    def _infer_document_type(self, session: CollectionSession) -> str:
        """Infer document type based on session state.
        
        Args:
            session: Collection session
            
        Returns:
            Inferred document type
        """
        if not session.cv_uploaded:
            return 'cv'
        elif session.stage == CollectionStage.COLLECTING_EMPLOYMENT_DOCS:
            return 'paystub'
        elif session.stage == CollectionStage.COLLECTING_EDUCATION_DOCS:
            return 'diploma'
        else:
            return 'cv'  # Default
    
    def _process_cv(
        self,
        session: CollectionSession,
        file_data: bytes,
        filename: str,
        file_extension: str
    ) -> Dict[str, Any]:
        """Process CV upload.
        
        Args:
            session: Collection session
            file_data: File bytes
            filename: Filename
            file_extension: File extension
            
        Returns:
            Processing result
        """
        # Extract CV data
        print(f"[Orchestrator] Processing CV: {filename} ({file_extension})")
        result = self.processor.extract_from_cv(file_data, file_extension)
        
        if not result.success:
            error_msg = result.error_message or "Failed to extract CV data"
            print(f"[Orchestrator] CV extraction failed: {error_msg}")
            
            # Generate helpful error message
            response_message = f"I'm sorry, I had trouble reading your CV. {error_msg}. Could you try uploading it again, or try a different format (PDF works best)?"
            session.add_message('assistant', response_message)
            
            return {
                'success': False,
                'error': error_msg,
                'message': response_message,
                'warnings': result.warnings
            }
        
        # Check if we got meaningful data
        if not result.data.employment_history and not result.data.education:
            print(f"[Orchestrator] Warning: No employment or education data extracted")
            print(f"[Orchestrator] CV data: {result.data.to_dict()}")
            
            # Still store the data but warn the user
            response_message = "I've processed your CV, but I couldn't find any employment history or education information. This might be because:\n\n"
            response_message += "• The document format is not clear\n"
            response_message += "• The text is not readable (scanned image)\n"
            response_message += "• The CV structure is unusual\n\n"
            response_message += "You can either:\n"
            response_message += "1. Upload a different version of your CV\n"
            response_message += "2. Continue and manually provide the information\n\n"
            response_message += "What would you like to do?"
            
            session.add_message('assistant', response_message)
            
            return {
                'success': True,
                'message': response_message,
                'extracted_data': result.data.to_dict(),
                'confidence_score': result.confidence_score,
                'warnings': result.warnings + ['No employment or education data found'],
                'session': session.to_dict()
            }
        
        # Store CV data
        session.cv_data = result.data
        session.cv_uploaded = True
        session.stage = CollectionStage.CV_PROCESSED
        
        # Add document record
        doc_id = str(uuid.uuid4())
        session.add_document(
            document_id=doc_id,
            document_type='cv',
            filename=filename,
            extracted_data=result.data,
            confidence_score=result.confidence_score
        )
        
        # Update candidate name if available
        if result.data.candidate_name and not session.candidate_name:
            session.candidate_name = result.data.candidate_name
        
        print(f"[Orchestrator] CV processed successfully: {len(result.data.employment_history)} jobs, {len(result.data.education)} education entries")
        
        # Detect employment gaps
        if result.data.employment_history:
            gaps = self.validator.detect_gaps(result.data.employment_history)
            session.employment_gaps = gaps
        
        # Prepare pending document requests
        for emp in result.data.employment_history:
            session.pending_employment_docs.append({
                'company_name': emp.company_name,
                'job_title': emp.job_title,
                'start_date': emp.start_date.isoformat() if emp.start_date else None,
                'end_date': emp.end_date.isoformat() if emp.end_date else None
            })
        
        for edu in result.data.education:
            session.pending_education_docs.append({
                'institution_name': edu.institution_name,
                'degree_type': edu.degree_type
            })
        
        # Move to next stage
        if session.pending_employment_docs:
            session.stage = CollectionStage.COLLECTING_EMPLOYMENT_DOCS
        elif session.pending_education_docs:
            session.stage = CollectionStage.COLLECTING_EDUCATION_DOCS
        else:
            session.stage = CollectionStage.FINAL_CONFIRMATION
        
        # Generate response message
        response_message = self.agent.generate_cv_processed_message(result.data.to_dict())
        
        # If we have employment docs to request, add that
        if session.pending_employment_docs:
            first_emp = session.pending_employment_docs[0]
            doc_request = self.agent.generate_document_request(
                'paystub',
                company_name=first_emp['company_name'],
                start_date=first_emp.get('start_date'),
                end_date=first_emp.get('end_date')
            )
            response_message += f"\n\n{doc_request}"
        
        session.add_message('assistant', response_message)
        
        return {
            'success': True,
            'message': response_message,
            'extracted_data': result.data.to_dict(),
            'confidence_score': result.confidence_score,
            'warnings': result.warnings,
            'session': session.to_dict()
        }
    
    def _process_paystub(
        self,
        session: CollectionSession,
        file_data: bytes,
        filename: str,
        file_extension: str
    ) -> Dict[str, Any]:
        """Process paystub upload.
        
        Args:
            session: Collection session
            file_data: File bytes
            filename: Filename
            file_extension: File extension
            
        Returns:
            Processing result
        """
        # Extract paystub data
        result = self.processor.extract_from_paystub(file_data, file_extension)
        
        if not result.success:
            return {
                'success': False,
                'error': result.error_message,
                'warnings': result.warnings
            }
        
        # Store paystub data
        session.paystubs.append(result.data)
        
        # Add document record
        doc_id = str(uuid.uuid4())
        session.add_document(
            document_id=doc_id,
            document_type='paystub',
            filename=filename,
            extracted_data=result.data,
            confidence_score=result.confidence_score
        )
        
        # Validate against CV if available
        if session.cv_data:
            conflicts = self.validator.validate_employment_dates(session.cv_data, session.paystubs)
            
            # Add new conflicts
            for conflict in conflicts:
                if conflict not in session.inconsistencies:
                    session.inconsistencies.append(conflict)
        
        # Generate response
        response_message = f"Thanks for uploading the document from {result.data.company_name}! "
        
        # Check if we have conflicts to resolve
        if session.inconsistencies and not session.conflicts_resolved:
            session.stage = CollectionStage.RESOLVING_CONFLICTS
            # Ask about first unresolved conflict
            unresolved = [c for c in session.inconsistencies if str(c) not in session.resolved_conflicts]
            if unresolved:
                conflict_question = self.agent.generate_conflict_question(unresolved[0].to_dict())
                response_message += f"\n\n{conflict_question}"
        else:
            # Continue with next document request
            if session.pending_employment_docs:
                next_emp = session.pending_employment_docs[0]
                doc_request = self.agent.generate_document_request(
                    'paystub',
                    company_name=next_emp['company_name'],
                    start_date=next_emp.get('start_date'),
                    end_date=next_emp.get('end_date')
                )
                response_message += f"\n\n{doc_request}"
            elif session.pending_education_docs:
                session.stage = CollectionStage.COLLECTING_EDUCATION_DOCS
                next_edu = session.pending_education_docs[0]
                doc_request = self.agent.generate_document_request(
                    'diploma',
                    institution_name=next_edu['institution_name']
                )
                response_message += f"\n\n{doc_request}"
            elif session.employment_gaps and not session.gaps_explained:
                session.stage = CollectionStage.EXPLAINING_GAPS
                gap_question = self.agent.generate_gap_question(session.employment_gaps[0].to_dict())
                response_message += f"\n\n{gap_question}"
            else:
                session.stage = CollectionStage.FINAL_CONFIRMATION
                summary = self.agent.generate_completion_summary(
                    [doc.document_type for doc in session.documents],
                    len(session.resolved_conflicts),
                    len(session.explained_gaps)
                )
                response_message = summary
        
        session.add_message('assistant', response_message)
        
        return {
            'success': True,
            'message': response_message,
            'extracted_data': result.data.to_dict(),
            'confidence_score': result.confidence_score,
            'warnings': result.warnings,
            'conflicts_detected': len(session.inconsistencies),
            'session': session.to_dict()
        }
    
    def _process_diploma(
        self,
        session: CollectionSession,
        file_data: bytes,
        filename: str,
        file_extension: str
    ) -> Dict[str, Any]:
        """Process diploma upload.
        
        Args:
            session: Collection session
            file_data: File bytes
            filename: Filename
            file_extension: File extension
            
        Returns:
            Processing result
        """
        # Extract diploma data
        result = self.processor.extract_from_diploma(file_data, file_extension)
        
        if not result.success:
            return {
                'success': False,
                'error': result.error_message,
                'warnings': result.warnings
            }
        
        # Store diploma data
        session.diplomas.append(result.data)
        
        # Add document record
        doc_id = str(uuid.uuid4())
        session.add_document(
            document_id=doc_id,
            document_type='diploma',
            filename=filename,
            extracted_data=result.data,
            confidence_score=result.confidence_score
        )
        
        # Validate against CV if available
        if session.cv_data:
            conflicts = self.validator.validate_education(session.cv_data, session.diplomas)
            
            # Add new conflicts
            for conflict in conflicts:
                if conflict not in session.inconsistencies:
                    session.inconsistencies.append(conflict)
        
        # Generate response
        response_message = f"Thanks for uploading your diploma from {result.data.institution_name}! "
        
        # Check if we have conflicts to resolve
        if session.inconsistencies and not session.conflicts_resolved:
            session.stage = CollectionStage.RESOLVING_CONFLICTS
            unresolved = [c for c in session.inconsistencies if str(c) not in session.resolved_conflicts]
            if unresolved:
                conflict_question = self.agent.generate_conflict_question(unresolved[0].to_dict())
                response_message += f"\n\n{conflict_question}"
        else:
            # Continue with next document or move to gaps/completion
            if session.pending_education_docs:
                next_edu = session.pending_education_docs[0]
                doc_request = self.agent.generate_document_request(
                    'diploma',
                    institution_name=next_edu['institution_name']
                )
                response_message += f"\n\n{doc_request}"
            elif session.employment_gaps and not session.gaps_explained:
                session.stage = CollectionStage.EXPLAINING_GAPS
                gap_question = self.agent.generate_gap_question(session.employment_gaps[0].to_dict())
                response_message += f"\n\n{gap_question}"
            else:
                session.stage = CollectionStage.FINAL_CONFIRMATION
                summary = self.agent.generate_completion_summary(
                    [doc.document_type for doc in session.documents],
                    len(session.resolved_conflicts),
                    len(session.explained_gaps)
                )
                response_message = summary
        
        session.add_message('assistant', response_message)
        
        return {
            'success': True,
            'message': response_message,
            'extracted_data': result.data.to_dict(),
            'confidence_score': result.confidence_score,
            'warnings': result.warnings,
            'conflicts_detected': len(session.inconsistencies),
            'session': session.to_dict()
        }
