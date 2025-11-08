from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, File
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from schemas import VerificationResponseV1
from services.resume_parser import extract_text_from_pdf, parse_with_llm
from services.supabase_client import supabase
from datetime import datetime
import uuid

settings = get_settings()

app = FastAPI(title="TruthHire API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "config": {
            "use_mock_data": settings.use_mock_data,
            "llm_model": settings.llm_model
        }
    }

@app.post("/api/v1/verify", response_model=VerificationResponseV1)
async def create_verification(
    resume: UploadFile = File(...),
    github_username: str = None,
    background_tasks: BackgroundTasks = None
):
    """Upload resume and start verification"""
    
    verification_id = str(uuid.uuid4())
    
    try:
        # 1. Upload to Supabase Storage
        print(f"[DEBUG] Starting verification {verification_id}")
        resume_bytes = await resume.read()
        print(f"[DEBUG] Read {len(resume_bytes)} bytes from {resume.filename}")
        
        storage_path = f"{verification_id}/{resume.filename}"
        
        print(f"[DEBUG] Uploading to Supabase storage: {storage_path}")
        
        # Try to upload, fallback to mock if bucket doesn't exist
        try:
            supabase.storage.from_("resumes").upload(
                storage_path,
                resume_bytes,
                {"content-type": "application/pdf"}
            )
            resume_url = supabase.storage.from_("resumes").get_public_url(storage_path)
            print(f"[DEBUG] Upload successful: {resume_url}")
        except Exception as storage_error:
            print(f"[WARNING] Storage upload failed: {storage_error}")
            print(f"[WARNING] Using mock storage URL (create 'resumes' bucket in Supabase)")
            resume_url = f"mock://storage/{storage_path}"
        
        # 2. Parse resume
        print(f"[DEBUG] Extracting text from PDF...")
        resume_text = extract_text_from_pdf(resume_bytes)
        print(f"[DEBUG] Extracted {len(resume_text)} characters")
        
        print(f"[DEBUG] Parsing with LLM...")
        try:
            parsed = await parse_with_llm(resume_text)
            print(f"[DEBUG] Parsed candidate: {parsed.name}")
        except Exception as parse_error:
            print(f"[WARNING] LLM parsing failed: {parse_error}")
            print(f"[WARNING] Using mock resume data (add OpenAI credits or use mock mode)")
            
            # Fallback to mock data
            from schemas import ParsedResume, Employment, Education
            parsed = ParsedResume(
                name="Mock Candidate",
                email="mock@example.com",
                employment_history=[
                    Employment(
                        company="TechCorp",
                        title="Senior Engineer",
                        start_date="2020-01",
                        end_date="2023-06",
                        description="Backend development"
                    )
                ],
                education=[
                    Education(
                        school="University",
                        degree="BS",
                        field="Computer Science",
                        graduation_year=2019
                    )
                ],
                skills=["Python", "JavaScript", "React"],
                github_username=github_username
            )
            print(f"[DEBUG] Using mock candidate: {parsed.name}")
        
        # 3. Create verification record
        print(f"[DEBUG] Creating verification record in Supabase...")
        supabase.table("verifications").insert({
            "id": verification_id,
            "candidate_name": parsed.name,
            "candidate_email": parsed.email,
            "github_username": github_username or parsed.github_username,
            "status": "processing",
            "resume_url": resume_url,
            "parsed_data": parsed.model_dump()
        }).execute()
        
        print(f"[DEBUG] Verification {verification_id} created successfully")
        
        return VerificationResponseV1(
            verification_id=verification_id,
            status="processing",
            message="Verification started",
            created_at=datetime.now()
        )
    
    except Exception as e:
        print(f"[ERROR] Verification failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        from services.supabase_client import update_verification_status
        try:
            update_verification_status(verification_id, "failed", {"error": str(e)})
        except:
            pass
        
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/verify/{verification_id}")
async def get_verification(verification_id: str):
    """Get verification status and result"""
    from services.supabase_client import supabase
    result = supabase.table("verifications").select("*").eq("id", verification_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return result.data

@app.get("/api/v1/verify/{verification_id}/steps")
async def get_steps(verification_id: str):
    """Get all agent progress steps"""
    from services.supabase_client import supabase
    steps = supabase.table("verification_steps").select("*").eq("verification_id", verification_id).order("created_at").execute()
    return {"steps": steps.data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
