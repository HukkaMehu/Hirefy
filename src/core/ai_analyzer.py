"""
AI Analyzer - Uses OpenAI to analyze verification data in real-time
"""
import os
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from src.core.ai_data_compiler import AIDataCompiler

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyzes verification data using OpenAI's API"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("AI Analyzer initialized with OpenAI")
        
        self.compiler = AIDataCompiler()
    
    def analyze_verification(self, verification_id: str, model: str = "gpt-4o") -> Dict[str, Any]:
        """
        Analyze a verification using AI
        
        Args:
            verification_id: The verification session ID
            model: OpenAI model to use (default: gpt-4o for deep thinking)
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"🤖 AI Analyzer called for verification {verification_id} with model {model}")
        print(f"🤖 AI Analyzer called for verification {verification_id}")
        
        if not self.client:
            error_msg = "OpenAI API key not configured"
            logger.error(f"❌ {error_msg}")
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        
        try:
            # Compile all verification data
            logger.info(f"📊 Compiling data for verification {verification_id}")
            print(f"📊 Compiling verification data...")
            compiled_data = self.compiler.compile_verification_data(verification_id)
            
            # Create the analysis prompt
            prompt = self.compiler._create_ai_analysis_prompt(compiled_data)
            
            # Call OpenAI API
            logger.info(f"🚀 Sending data to OpenAI ({model}) for analysis")
            print(f"🚀 Calling OpenAI {model}... (this may take 10-30 seconds)")
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert employment verification analyst. Analyze the provided verification data thoroughly and provide a comprehensive assessment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=4000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse the analysis into structured sections
            structured_analysis = self._parse_analysis(analysis_text)
            
            logger.info(f"✅ AI analysis completed for verification {verification_id}")
            print(f"✅ AI analysis completed successfully!")
            
            return {
                "success": True,
                "verification_id": verification_id,
                "model": model,
                "analysis": structured_analysis,
                "raw_analysis": analysis_text,
                "compiled_data": compiled_data,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing verification {verification_id}: {e}", exc_info=True)
            print(f"❌ AI analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse AI analysis text into structured sections"""
        sections = {
            "verification_assessment": "",
            "risk_analysis": "",
            "cross_reference_validation": "",
            "fraud_detection": "",
            "technical_competency": "",
            "recommendations": "",
            "follow_up_actions": "",
            "summary": ""
        }
        
        # Try to extract sections based on common headers
        current_section = "summary"
        lines = analysis_text.split('\n')
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect section headers
            if "verification assessment" in line_lower or "overall assessment" in line_lower:
                current_section = "verification_assessment"
            elif "risk analysis" in line_lower or "risk assessment" in line_lower:
                current_section = "risk_analysis"
            elif "cross-reference" in line_lower or "consistency" in line_lower:
                current_section = "cross_reference_validation"
            elif "fraud detection" in line_lower or "fraud assessment" in line_lower:
                current_section = "fraud_detection"
            elif "technical competency" in line_lower or "technical skills" in line_lower:
                current_section = "technical_competency"
            elif "recommendation" in line_lower and "hiring" in line_lower:
                current_section = "recommendations"
            elif "follow-up" in line_lower or "next steps" in line_lower:
                current_section = "follow_up_actions"
            else:
                # Add line to current section
                if line.strip():
                    sections[current_section] += line + "\n"
        
        # Clean up sections
        for key in sections:
            sections[key] = sections[key].strip()
        
        # If no structured sections found, put everything in summary
        if not any(sections.values()):
            sections["summary"] = analysis_text
        
        return sections
    
    def quick_summary(self, verification_id: str) -> Dict[str, Any]:
        """
        Generate a quick summary using a faster model
        
        Args:
            verification_id: The verification session ID
        
        Returns:
            Dictionary with quick summary
        """
        return self.analyze_verification(verification_id, model="gpt-4o-mini")
