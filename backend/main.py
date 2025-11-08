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
        resume_bytes = await resume.read()
        storage_path = f"{verification_id}/{resume.filename}"
        
        supabase.storage.from_("resumes").upload(
            storage_path,
            resume_bytes,
            {"content-type": "application/pdf"}
        )
        
        resume_url = supabase.storage.from_("resumes").get_public_url(storage_path)
        
        # 2. Parse resume
        resume_text = extract_text_from_pdf(resume_bytes)
        parsed = await parse_with_llm(resume_text)
        
        # 3. Create verification record
        supabase.table("verifications").insert({
            "id": verification_id,
            "candidate_name": parsed.name,
            "candidate_email": parsed.email,
            "github_username": github_username or parsed.github_username,
            "status": "processing",
            "resume_url": resume_url,
            "parsed_data": parsed.model_dump()
        }).execute()
        
        return VerificationResponseV1(
            verification_id=verification_id,
            status="processing",
            message="Verification started",
            created_at=datetime.now()
        )
    
    except Exception as e:
        from services.supabase_client import update_verification_status
        update_verification_status(verification_id, "failed", {"error": str(e)})
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
