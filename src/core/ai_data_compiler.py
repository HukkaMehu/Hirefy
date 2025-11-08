"""
AI Data Compiler - Aggregates all verification data for AI thinking model analysis
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class AIDataCompiler:
    """Compiles all verification data including transcripts, documents, and database records"""
    
    def __init__(self):
        """Initialize compiler - imports done here to avoid circular dependencies"""
        pass
    
    def compile_verification_data(self, verification_id: int) -> Dict[str, Any]:
        """
        Compile all data for a specific verification into a structured format
        suitable for AI thinking model analysis
        """
        from src.database import db, VerificationSession
        
        verification = db.session.query(VerificationSession).filter(
            VerificationSession.id == verification_id
        ).first()
        
        if not verification:
            raise ValueError(f"Verification {verification_id} not found")
        
        compiled_data = {
            "verification_id": verification_id,
            "candidate_name": verification.candidate.full_name if verification.candidate else "Unknown",
            "candidate_email": verification.candidate.email if verification.candidate else "Unknown",
            "status": verification.status.value if hasattr(verification.status, 'value') else str(verification.status),
            "created_at": verification.created_at.isoformat() if verification.created_at else None,
            "completed_at": verification.completed_at.isoformat() if verification.completed_at else None,
            
            # Compile all data sources
            "transcripts": self._compile_transcripts(verification.candidate.full_name if verification.candidate else ""),
            "employments": self._compile_employments(verification),
            "education": self._compile_education(verification),
            "fraud_flags": self._compile_fraud_flags(verification),
            "contact_records": self._compile_contact_records(verification),
            "github_analysis": self._compile_github_analysis(verification),
            "verification_report": self._compile_report(verification),
        }
        
        return compiled_data
    
    def _compile_transcripts(self, candidate_name: str) -> List[Dict[str, Any]]:
        """Compile all phone conversation transcripts"""
        transcripts = []
        
        # Look for transcripts in the transcripts directory
        transcript_base = Path("transcripts")
        if not transcript_base.exists():
            return transcripts
        
        # Search for candidate-specific transcripts
        if not candidate_name:
            return transcripts
        candidate_folder = candidate_name.lower().replace(" ", "_")
        candidate_path = transcript_base / candidate_folder
        
        if candidate_path.exists():
            for transcript_file in candidate_path.glob("*.txt"):
                try:
                    with open(transcript_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    transcripts.append({
                        "filename": transcript_file.name,
                        "path": str(transcript_file),
                        "content": content,
                        "parsed_data": self._parse_transcript(content)
                    })
                except Exception as e:
                    transcripts.append({
                        "filename": transcript_file.name,
                        "error": str(e)
                    })
        
        return transcripts
    
    def _parse_transcript(self, content: str) -> Dict[str, Any]:
        """Parse transcript content to extract structured information"""
        lines = content.split('\n')
        parsed = {
            "call_type": None,
            "date": None,
            "duration": None,
            "contact": None,
            "conversation": [],
            "metadata": {}
        }
        
        # Extract metadata from header
        for line in lines:
            if "Call Type:" in line:
                parsed["call_type"] = line.split("Call Type:")[1].strip()
            elif "Date:" in line:
                parsed["date"] = line.split("Date:")[1].strip()
            elif "Duration:" in line:
                parsed["duration"] = line.split("Duration:")[1].strip()
            elif "Contact:" in line:
                parsed["contact"] = line.split("Contact:")[1].strip()
            elif "Reference Name:" in line:
                parsed["metadata"]["reference_name"] = line.split("Reference Name:")[1].strip()
            elif "Relationship:" in line:
                parsed["metadata"]["relationship"] = line.split("Relationship:")[1].strip()
            elif line.startswith("AGENT:") or line.startswith("USER:"):
                speaker = "agent" if line.startswith("AGENT:") else "user"
                message = line.split(":", 1)[1].strip()
                parsed["conversation"].append({
                    "speaker": speaker,
                    "message": message
                })
        
        return parsed
    
    def _compile_employments(self, verification) -> List[Dict[str, Any]]:
        """Compile employment history"""
        return [{
            "company_name": emp.company_name,
            "job_title": emp.job_title,
            "start_date": emp.start_date.isoformat() if emp.start_date else None,
            "end_date": emp.end_date.isoformat() if emp.end_date else None,
            "verification_status": emp.verification_status.value if hasattr(emp.verification_status, 'value') else str(emp.verification_status),
            "verified_by": emp.verified_by,
            "notes": emp.notes
        } for emp in verification.employments]
    
    def _compile_education(self, verification) -> List[Dict[str, Any]]:
        """Compile education credentials"""
        return [{
            "institution_name": edu.institution_name,
            "degree_type": edu.degree_type,
            "field_of_study": edu.field_of_study,
            "graduation_year": edu.graduation_year,
            "verification_status": edu.verification_status.value if hasattr(edu.verification_status, 'value') else str(edu.verification_status),
            "verified_by": edu.verified_by
        } for edu in verification.education_credentials]
    
    def _compile_fraud_flags(self, verification) -> List[Dict[str, Any]]:
        """Compile fraud detection flags"""
        return [{
            "flag_type": flag.flag_type.value if hasattr(flag.flag_type, 'value') else str(flag.flag_type),
            "severity": flag.severity.value if hasattr(flag.severity, 'value') else str(flag.severity),
            "description": flag.description,
            "detected_at": flag.detected_at.isoformat() if flag.detected_at else None
        } for flag in verification.fraud_flags]
    
    def _compile_contact_records(self, verification) -> List[Dict[str, Any]]:
        """Compile contact records"""
        return [{
            "contact_type": record.contact_type,
            "contact_method": record.contact_method,
            "contact_name": record.contact_name,
            "contact_info": record.contact_info,
            "attempted_at": record.attempted_at.isoformat() if record.attempted_at else None,
            "successful": record.successful,
            "notes": record.notes,
            "transcript": record.transcript
        } for record in verification.contact_records]
    
    def _compile_github_analysis(self, verification) -> Dict[str, Any]:
        """Compile GitHub analysis if available"""
        if hasattr(verification, 'github_analysis') and verification.github_analysis:
            gh = verification.github_analysis
            return {
                "username": gh.username,
                "profile_found": gh.profile_found,
                "public_repos": gh.public_repos,
                "followers": gh.followers,
                "following": gh.following,
                "account_created": gh.account_created.isoformat() if gh.account_created else None,
                "last_activity": gh.last_activity.isoformat() if gh.last_activity else None,
                "top_languages": gh.top_languages,
                "contribution_score": gh.contribution_score,
                "verified_projects": gh.verified_projects,
                "analysis_notes": gh.analysis_notes
            }
        return {}
    
    def _compile_report(self, verification) -> Dict[str, Any]:
        """Compile verification report if available"""
        if verification.verification_report:
            report = verification.verification_report
            return {
                "risk_score": report.risk_score.value if hasattr(report.risk_score, 'value') else str(report.risk_score),
                "summary_narrative": report.summary_narrative,
                "employment_narratives": report.employment_narratives,
                "education_summary": report.education_summary,
                "technical_validation": report.technical_validation,
                "interview_questions": report.interview_questions,
                "generated_at": report.generated_at.isoformat() if report.generated_at else None
            }
        return {}
    
    def export_for_ai_analysis(self, verification_id: int, output_path: Optional[str] = None) -> str:
        """
        Export compiled data in a format optimized for AI thinking model analysis
        """
        compiled_data = self.compile_verification_data(verification_id)
        
        # Create a comprehensive prompt for AI analysis
        ai_prompt = self._create_ai_analysis_prompt(compiled_data)
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "compiled_data": compiled_data,
                    "ai_prompt": ai_prompt
                }, f, indent=2, ensure_ascii=False)
        
        return ai_prompt
    
    def _create_ai_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for AI thinking model"""
        prompt = f"""# Comprehensive Verification Analysis Request

## Candidate Information
- Name: {data['candidate_name']}
- Email: {data['candidate_email']}
- Verification ID: {data['verification_id']}
- Status: {data['status']}

## Available Data Sources

### 1. Phone Conversation Transcripts ({len(data['transcripts'])} calls)
"""
        
        for transcript in data['transcripts']:
            if 'parsed_data' in transcript:
                parsed = transcript['parsed_data']
                prompt += f"\n#### {transcript['filename']}\n"
                prompt += f"- Type: {parsed.get('call_type')}\n"
                prompt += f"- Date: {parsed.get('date')}\n"
                prompt += f"- Duration: {parsed.get('duration')}\n"
                if parsed.get('metadata'):
                    prompt += f"- Reference: {parsed['metadata'].get('reference_name')} ({parsed['metadata'].get('relationship')})\n"
                prompt += f"\nConversation:\n"
                for turn in parsed.get('conversation', []):
                    prompt += f"  {turn['speaker'].upper()}: {turn['message']}\n"
                prompt += "\n"
        
        prompt += f"\n### 2. Employment History ({len(data['employments'])} positions)\n"
        for emp in data['employments']:
            prompt += f"\n- {emp['job_title']} at {emp['company_name']}\n"
            prompt += f"  Period: {emp['start_date']} to {emp['end_date']}\n"
            prompt += f"  Status: {emp['verification_status']}\n"
            if emp['notes']:
                prompt += f"  Notes: {emp['notes']}\n"
        
        prompt += f"\n### 3. Education ({len(data['education'])} credentials)\n"
        for edu in data['education']:
            prompt += f"\n- {edu['degree_type']} in {edu['field_of_study']}\n"
            prompt += f"  Institution: {edu['institution_name']}\n"
            prompt += f"  Year: {edu['graduation_year']}\n"
            prompt += f"  Status: {edu['verification_status']}\n"
        
        prompt += f"\n### 4. Fraud Flags ({len(data['fraud_flags'])} detected)\n"
        for flag in data['fraud_flags']:
            prompt += f"\n- [{flag['severity']}] {flag['flag_type']}\n"
            prompt += f"  {flag['description']}\n"
        
        prompt += f"\n### 5. Contact Records ({len(data['contact_records'])} attempts)\n"
        for record in data['contact_records']:
            prompt += f"\n- {record['contact_type']} via {record['contact_method']}\n"
            prompt += f"  Contact: {record['contact_name']}\n"
            prompt += f"  Success: {record['successful']}\n"
            if record['notes']:
                prompt += f"  Notes: {record['notes']}\n"
        
        if data['github_analysis']:
            prompt += f"\n### 6. GitHub Technical Profile\n"
            gh = data['github_analysis']
            prompt += f"- Username: {gh.get('username')}\n"
            prompt += f"- Profile Found: {gh.get('profile_found')}\n"
            prompt += f"- Public Repos: {gh.get('public_repos')}\n"
            prompt += f"- Contribution Score: {gh.get('contribution_score')}\n"
            prompt += f"- Top Languages: {gh.get('top_languages')}\n"
        
        if data['verification_report']:
            prompt += f"\n### 7. Verification Report\n"
            report = data['verification_report']
            prompt += f"- Risk Score: {report.get('risk_score')}\n"
            prompt += f"- Recommendation: {report.get('recommendation')}\n"
            prompt += f"\nSummary: {report.get('summary_narrative')}\n"
        
        prompt += """

## Analysis Request

Please analyze all the provided data and provide:

1. **Verification Assessment**: Overall credibility and reliability of the candidate
2. **Risk Analysis**: Identify any red flags, inconsistencies, or concerns
3. **Cross-Reference Validation**: Check consistency across transcripts, employment history, and claims
4. **Fraud Detection**: Assess likelihood of fraudulent information
5. **Technical Competency**: Evaluate technical skills and experience claims (if applicable)
6. **Recommendations**: Hiring recommendation with confidence level
7. **Follow-up Actions**: Any additional verification steps needed

Please think through this systematically and provide a comprehensive analysis.
"""
        
        return prompt
    
    def compile_all_verifications(self) -> List[Dict[str, Any]]:
        """Compile data for all verifications in the system"""
        from src.database import db, VerificationSession
        
        verifications = db.session.query(VerificationSession).all()
        
        return [
            self.compile_verification_data(v.id)
            for v in verifications
        ]
