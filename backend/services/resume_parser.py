import pdfplumber
from io import BytesIO
from openai import OpenAI
import json
from config import get_settings
from schemas import ParsedResume

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes"""
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

async def parse_with_llm(resume_text: str) -> ParsedResume:
    """Parse resume text into structured data using GPT-4"""
    
    prompt = f"""Extract structured data from this resume. Return valid JSON only.

Resume text:
{resume_text}

Return JSON with this exact structure:
{{
  "name": "Full Name",
  "email": "email@example.com or null",
  "employment_history": [
    {{
      "company": "Company Name",
      "title": "Job Title",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM",
      "description": "Brief description of role"
    }}
  ],
  "education": [
    {{
      "school": "University Name",
      "degree": "BS/MS/PhD",
      "field": "Field of Study",
      "graduation_year": 2020
    }}
  ],
  "skills": ["Python", "JavaScript", "etc"],
  "github_username": "username or null"
}}"""

    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.llm_temperature,
        response_format={"type": "json_object"}
    )
    
    parsed_json = json.loads(response.choices[0].message.content)
    return ParsedResume(**parsed_json)
