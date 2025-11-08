# TruthHire MVP - 3-Wave Build Strategy
**24-Hour Hackathon | Safe Parallel Execution**

---

## Strategy Overview

**Approach:** 3 sequential waves, each with 2-3 parallel agents  
**Total Build Time:** ~16 hours (8h buffer for polish/demo)  
**Key Principle:** Validate each layer before building the next  

---

## Wave Structure

```
Hour 0-1:   YOU - Supabase Setup
            ↓
Hour 1-4:   WAVE 1 - Foundation (3 agents parallel)
            ↓ Review & Test (30 mins)
            ↓
Hour 4-10:  WAVE 2 - Core Services (3 agents parallel)
            ↓ Integration & Testing (2 hours)
            ↓
Hour 10-16: WAVE 3 - Orchestration (2 agents parallel)
            ↓ E2E Testing (3 hours)
            ↓
Hour 16-20: Demo Prep & Polish
Hour 20-24: Buffer & Sleep
```

---

## Hour 0-1: Manual Setup (YOU)

### Tasks:
1. **Create Supabase Project**
   - Go to supabase.com
   - Create new project: "truthhire-mvp"
   - Wait for provisioning (~2 mins)
   - Copy credentials:
     - Project URL
     - Anon/Public Key
     - Service Role Key

2. **Run Database Migration**
   ```sql
   -- Execute in Supabase SQL Editor
   
   -- verifications table
   CREATE TABLE verifications (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     candidate_name TEXT NOT NULL,
     candidate_email TEXT,
     github_username TEXT,
     status TEXT NOT NULL DEFAULT 'processing',
     risk_score TEXT,
     resume_url TEXT,
     parsed_data JSONB,
     result JSONB,
     created_at TIMESTAMPTZ DEFAULT NOW(),
     completed_at TIMESTAMPTZ
   );

   -- verification_steps table
   CREATE TABLE verification_steps (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     verification_id UUID REFERENCES verifications(id) ON DELETE CASCADE,
     agent_name TEXT NOT NULL,
     status TEXT NOT NULL,
     message TEXT,
     data JSONB,
     created_at TIMESTAMPTZ DEFAULT NOW()
   );

   CREATE INDEX idx_steps_vid_created ON verification_steps(verification_id, created_at DESC);

   -- Enable Realtime
   ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;
   ```

3. **Create Storage Bucket**
   - Go to Storage section
   - Create bucket: `resumes`
   - Set to private
   - Set max file size: 5MB

4. **Prepare Environment Files**
   
   Create `backend/.env`:
   ```bash
   OPENAI_API_KEY=sk-...  # Your OpenAI key
   SUPABASE_URL=https://xxx.supabase.co
   SUPABASE_ANON_KEY=eyJ...
   SUPABASE_SERVICE_KEY=eyJ...
   GITHUB_TOKEN=  # Optional, add if you have one
   
   USE_MOCK_DATA=true
   FRAUD_DETECTION_STRICT_MODE=true
   LLM_MODEL=gpt-4o-mini
   LLM_TEMPERATURE=0.1
   LLM_MAX_TOKENS=4000
   ```

   Create `frontend/.env.local`:
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

5. **Create Project Directories**
   ```bash
   mkdir -p truthhire/frontend truthhire/backend truthhire/demo
   cd truthhire
   git init
   ```

**Completion Criteria:**
- [ ] Supabase project created
- [ ] Database tables created
- [ ] Storage bucket configured
- [ ] .env files ready
- [ ] Project folders created

---

## WAVE 1: Foundation Layer (Hour 1-4)

### Agent A: Backend Foundation

**Directory:** `backend/`

**Tasks:**
1. Create FastAPI project structure
2. Install dependencies (requirements.txt)
3. Configuration management system
4. Supabase client helper

**Deliverables:**

**`requirements.txt`**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
supabase==2.0.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
pdfplumber==0.10.3
openai==1.3.0
langchain==0.0.340
langgraph==0.0.25
PyGithub==2.1.1
python-multipart==0.0.6
faker==20.1.0
```

**`config.py`**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    github_token: str = ""
    
    # Feature Flags
    use_mock_data: bool = True
    fraud_detection_strict: bool = True
    
    # LLM Config
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**`services/supabase_client.py`**
```python
from supabase import create_client, Client
from config import get_settings

settings = get_settings()
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_key
)

async def update_agent_progress(
    verification_id: str,
    agent_name: str,
    status: str,
    message: str,
    data: dict = None
):
    """Write progress update to verification_steps table"""
    supabase.table("verification_steps").insert({
        "verification_id": verification_id,
        "agent_name": agent_name,
        "status": status,
        "message": message,
        "data": data
    }).execute()

def get_verification(verification_id: str):
    """Get verification record"""
    result = supabase.table("verifications").select("*").eq("id", verification_id).single().execute()
    return result.data

def update_verification_status(verification_id: str, status: str, result: dict = None):
    """Update verification status and result"""
    update_data = {"status": status}
    if result:
        update_data["result"] = result
    if status == "complete":
        from datetime import datetime
        update_data["completed_at"] = datetime.now().isoformat()
    
    supabase.table("verifications").update(update_data).eq("id", verification_id).execute()
```

**`main.py` (skeleton)**
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Agent A Command:**
```
Create FastAPI backend foundation following the exact structure above:
- requirements.txt with all dependencies
- config.py with pydantic-settings
- services/supabase_client.py with helper functions
- main.py with health endpoint and CORS
- Create folders: agents/, services/, mocks/

Test that health endpoint returns 200 and loads config from .env
```

---

### Agent B: Frontend Foundation

**Directory:** `frontend/`

**Tasks:**
1. Initialize Next.js 14 project with TypeScript
2. Set up Tailwind CSS + shadcn/ui
3. Create page skeletons
4. Supabase client setup

**Deliverables:**

**Initialize Project:**
```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
npx shadcn-ui@latest init
```

**Install Dependencies:**
```bash
npm install @supabase/supabase-js
npm install lucide-react
npm install react-pdf
```

**`lib/supabase.ts`**
```typescript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type VerificationStep = {
  id: string
  verification_id: string
  agent_name: string
  status: 'running' | 'complete' | 'failed'
  message: string
  data?: any
  created_at: string
}

export type Verification = {
  id: string
  candidate_name: string
  status: 'processing' | 'complete' | 'failed'
  risk_score?: 'green' | 'yellow' | 'red'
  result?: any
  created_at: string
}
```

**`app/page.tsx` (skeleton)**
```typescript
export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-4xl font-bold mb-4">TruthHire</h1>
        <p className="text-gray-600 mb-8">AI-Powered Candidate Verification</p>
        
        {/* File upload form - to be completed in Wave 2 */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
          <p className="text-gray-500">Resume upload form coming soon...</p>
        </div>
      </div>
    </div>
  )
}
```

**`app/verify/[id]/page.tsx` (skeleton)**
```typescript
export default function VerifyPage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Verification in Progress</h1>
        
        {/* Agent progress cards - to be completed in Wave 2 */}
        <div className="bg-white rounded-lg shadow p-8">
          <p className="text-gray-500">Real-time agent progress coming soon...</p>
          <p className="text-sm text-gray-400 mt-2">Verification ID: {params.id}</p>
        </div>
      </div>
    </div>
  )
}
```

**`app/report/[id]/page.tsx` (skeleton)**
```typescript
export default function ReportPage({ params }: { params: { id: string } }) {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Verification Report</h1>
        
        {/* Report display - to be completed in Wave 2 */}
        <div className="bg-white rounded-lg shadow p-8">
          <p className="text-gray-500">Report display coming soon...</p>
          <p className="text-sm text-gray-400 mt-2">Verification ID: {params.id}</p>
        </div>
      </div>
    </div>
  )
}
```

**Agent B Command:**
```
Create Next.js 14 frontend foundation:
- Initialize with TypeScript, Tailwind, App Router
- Install @supabase/supabase-js, lucide-react, react-pdf
- Create lib/supabase.ts with client and TypeScript types
- Create 3 page skeletons:
  - app/page.tsx (upload page skeleton)
  - app/verify/[id]/page.tsx (progress page skeleton)
  - app/report/[id]/page.tsx (report page skeleton)
- Basic styling with Tailwind
- Test that dev server runs: npm run dev

Use exact code above. Pages should render but show "coming soon" placeholders.
```

---

### Agent C: Data Layer (GitHub API + Mock Data)

**Directory:** `backend/`

**Tasks:**
1. Real GitHub API client
2. Mock data JSON files
3. Mock data loader service

**Deliverables:**

**`services/github_api.py`**
```python
import requests
from typing import Optional
from datetime import datetime
from collections import defaultdict
from config import get_settings

settings = get_settings()

def analyze_github_profile(username: str) -> dict:
    """
    Analyze GitHub profile using REST API
    Returns profile, repos, languages, commits, activity timeline
    """
    headers = {}
    if settings.github_token:
        headers['Authorization'] = f'token {settings.github_token}'
    
    try:
        # Get user profile
        user_response = requests.get(
            f'https://api.github.com/users/{username}',
            headers=headers,
            timeout=10
        )
        
        if user_response.status_code == 404:
            return {'error': 'GitHub user not found'}
        
        user = user_response.json()
        
        # Get repositories
        repos_response = requests.get(
            f'https://api.github.com/users/{username}/repos?per_page=100&sort=updated',
            headers=headers,
            timeout=10
        )
        repos = repos_response.json()
        
        # Analyze repositories
        languages = defaultdict(int)
        total_stars = 0
        original_repos = 0
        forked_repos = 0
        
        for repo in repos[:30]:  # Limit to 30 most recent
            if repo.get('fork'):
                forked_repos += 1
            else:
                original_repos += 1
            
            if repo.get('language'):
                languages[repo['language']] += 1
            
            total_stars += repo.get('stargazers_count', 0)
        
        # Get recent activity (commits in last year)
        # Note: This is expensive, simplified version
        total_commits = 0
        for repo in repos[:10]:  # Only check top 10 repos
            try:
                commits_response = requests.get(
                    f"https://api.github.com/repos/{username}/{repo['name']}/commits?per_page=100",
                    headers=headers,
                    timeout=5
                )
                if commits_response.status_code == 200:
                    commits = commits_response.json()
                    # Count commits by this user
                    user_commits = [c for c in commits if c.get('author') and c['author'].get('login') == username]
                    total_commits += len(user_commits)
            except:
                continue
        
        return {
            'profile': {
                'username': username,
                'name': user.get('name'),
                'public_repos': user.get('public_repos', 0),
                'followers': user.get('followers', 0),
                'created_at': user.get('created_at'),
                'bio': user.get('bio')
            },
            'repositories': {
                'total': len(repos),
                'original': original_repos,
                'forked': forked_repos,
                'languages': dict(languages),
                'stars_received': total_stars
            },
            'activity': {
                'total_commits': total_commits,
                'account_created_year': datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).year if user.get('created_at') else None
            }
        }
    
    except Exception as e:
        return {'error': str(e)}
```

**`mocks/reference_templates.json`**
```json
{
  "templates": [
    {
      "id": "strong_performer",
      "performance_rating": 8,
      "strengths": ["Strong technical skills", "Excellent collaborator", "Takes initiative"],
      "weaknesses": ["Sometimes misses deadlines under pressure"],
      "would_rehire": true,
      "examples": [
        "Led the payment infrastructure rebuild, delivered 3 weeks early",
        "Mentored 3 junior developers, all promoted within a year",
        "Architected our microservices migration, reduced costs by 40%"
      ],
      "weight": 0.6
    },
    {
      "id": "solid_contributor",
      "performance_rating": 7,
      "strengths": ["Reliable", "Good code quality", "Team player"],
      "weaknesses": ["Needs direction on ambiguous tasks"],
      "would_rehire": true,
      "examples": [
        "Rebuilt API gateway, reduced latency by 40%",
        "Fixed critical security vulnerability in auth system",
        "Consistently delivered features on time"
      ],
      "weight": 0.3
    },
    {
      "id": "performance_concerns",
      "performance_rating": 5,
      "strengths": ["Technically competent"],
      "weaknesses": ["Communication issues", "Missed multiple deadlines", "Needed close supervision"],
      "would_rehire": false,
      "examples": [
        "Worked on frontend features but required extensive code review",
        "Delivered features but often late and over budget",
        "Struggled with complex problem-solving"
      ],
      "weight": 0.1
    }
  ]
}
```

**`mocks/fraud_scenarios.json`**
```json
{
  "scenarios": [
    {
      "id": "fake_github_activity",
      "resume_claim": "Prolific open source contributor, 1000+ commits",
      "github_reality": "Only 47 total commits, last activity 2 years ago",
      "severity": "red"
    },
    {
      "id": "title_inflation",
      "resume_claim": "Senior Engineering Manager",
      "verification_reality": "Junior Developer",
      "severity": "red"
    },
    {
      "id": "fake_education",
      "resume_claim": "BS Computer Science, Stanford, 2018",
      "nsc_reality": "No record found",
      "severity": "red"
    },
    {
      "id": "skill_exaggeration",
      "resume_claim": "Expert Python developer",
      "github_reality": "0 Python repositories, only JavaScript",
      "severity": "yellow"
    },
    {
      "id": "employment_gap",
      "resume_claim": "Continuous employment 2018-2024",
      "reality": "8-month unexplained gap in 2021",
      "severity": "yellow"
    }
  ]
}
```

**`services/mock_loader.py`**
```python
import json
import random
from pathlib import Path
from functools import lru_cache
from faker import Faker

MOCKS_DIR = Path(__file__).parent.parent / "mocks"
fake = Faker()

@lru_cache()
def load_reference_templates() -> dict:
    with open(MOCKS_DIR / "reference_templates.json") as f:
        return json.load(f)

@lru_cache()
def load_fraud_scenarios() -> dict:
    with open(MOCKS_DIR / "fraud_scenarios.json") as f:
        return json.load(f)

def get_weighted_reference_response() -> dict:
    """Get random reference response using weighted distribution"""
    templates = load_reference_templates()["templates"]
    weights = [t["weight"] for t in templates]
    selected = random.choices(templates, weights=weights)[0]
    
    return {
        "performance_rating": selected["performance_rating"],
        "strengths": selected["strengths"].copy(),
        "weaknesses": selected["weaknesses"].copy(),
        "would_rehire": selected["would_rehire"],
        "specific_example": random.choice(selected["examples"])
    }

def generate_mock_references(employment_history: list) -> list:
    """Generate 50-100 realistic mock former coworkers"""
    all_references = []
    
    for job in employment_history:
        company = job["company"]
        num_coworkers = random.randint(15, 25)
        
        for _ in range(num_coworkers):
            ref = {
                "id": fake.uuid4(),
                "name": fake.name(),
                "company": company,
                "title": random.choice([
                    "Engineering Manager",
                    "Senior Developer",
                    "Tech Lead",
                    "Product Manager",
                    "Software Engineer"
                ]),
                "relationship": random.choice(["Manager", "Peer", "Peer", "Direct Report"])
            }
            all_references.append(ref)
    
    return all_references

def simulate_outreach_responses(references: list, response_rate: float = 0.20) -> list:
    """Simulate 20% response rate with mock answers"""
    num_responses = int(len(references) * response_rate)
    responding_refs = random.sample(references, min(num_responses, len(references)))
    
    responses = []
    for ref in responding_refs:
        response = get_weighted_reference_response()
        response.update({
            "reference_id": ref["id"],
            "reference_name": ref["name"],
            "reference_title": ref["title"],
            "company": ref["company"],
            "relationship": ref["relationship"]
        })
        responses.append(response)
    
    return responses
```

**Agent C Command:**
```
Create data layer services in backend/:

1. services/github_api.py:
   - analyze_github_profile(username) function
   - Use requests library to call GitHub REST API
   - Return profile, repos, languages, commits
   - Handle rate limits and errors gracefully
   - Use exact code structure above

2. mocks/reference_templates.json:
   - 3 templates: strong_performer, solid_contributor, performance_concerns
   - Include weights (0.6, 0.3, 0.1)
   - Use exact JSON structure above

3. mocks/fraud_scenarios.json:
   - 5 scenarios covering different fraud types
   - Use exact JSON structure above

4. services/mock_loader.py:
   - load_reference_templates() with caching
   - get_weighted_reference_response()
   - generate_mock_references(employment_history)
   - simulate_outreach_responses(references, 0.20)
   - Use Faker for realistic names

Test GitHub API with real username (e.g., 'torvalds') and verify it returns data.
```

---

### Wave 1 Review Checklist (Hour 4 - 30 mins)

**You Test:**

1. **Backend Health Check**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   # Open http://localhost:8000/health
   # Should return {"status": "healthy", ...}
   ```

2. **Frontend Dev Server**
   ```bash
   cd frontend
   npm install
   npm run dev
   # Open http://localhost:3000
   # Should see "TruthHire" page with placeholder
   ```

3. **GitHub API Test**
   ```bash
   cd backend
   python -c "from services.github_api import analyze_github_profile; print(analyze_github_profile('torvalds'))"
   # Should return Linus Torvalds' GitHub data
   ```

4. **Mock Data Test**
   ```bash
   python -c "from services.mock_loader import get_weighted_reference_response; print(get_weighted_reference_response())"
   # Should return weighted random reference
   ```

5. **Supabase Connection**
   ```bash
   python -c "from services.supabase_client import supabase; print(supabase.table('verifications').select('*').limit(1).execute())"
   # Should connect (empty result is fine)
   ```

**Pass Criteria:**
- [ ] Backend runs without errors
- [ ] Frontend renders 3 pages
- [ ] GitHub API returns real data
- [ ] Mock data loads from JSON
- [ ] Supabase client connects
- [ ] Config loaded from .env

**If failing:** Fix blockers before Wave 2. Don't proceed with broken foundation.

---

## WAVE 2: Core Services (Hour 4-10)

### Agent D: Backend API + Resume Parser

**Tasks:**
1. Complete API routes
2. Pydantic schemas
3. Resume parser service
4. File upload handling

**Deliverables:**

**`schemas.py`**
```python
from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class VerificationRequestV1(BaseModel):
    github_username: Optional[str] = None

class VerificationResponseV1(BaseModel):
    verification_id: str
    status: Literal["processing", "complete", "failed"]
    message: str
    created_at: datetime

class Employment(BaseModel):
    company: str
    title: str
    start_date: str  # YYYY-MM format
    end_date: str
    description: str

class Education(BaseModel):
    school: str
    degree: str
    field: str
    graduation_year: int

class ParsedResume(BaseModel):
    name: str
    email: Optional[str] = None
    employment_history: list[Employment]
    education: list[Education]
    skills: list[str]
    github_username: Optional[str] = None
```

**`services/resume_parser.py`**
```python
import pdfplumber
from io import BytesIO
import openai
import json
from config import get_settings
from schemas import ParsedResume

settings = get_settings()
openai.api_key = settings.openai_api_key

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

    response = openai.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=settings.llm_temperature,
        response_format={"type": "json_object"}
    )
    
    parsed_json = json.loads(response.choices[0].message.content)
    return ParsedResume(**parsed_json)
```

**Update `main.py` with routes:**
```python
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks, File
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from schemas import VerificationResponseV1
from services.supabase_client import supabase, update_verification_status
from services.resume_parser import extract_text_from_pdf, parse_with_llm
from datetime import datetime
import uuid

settings = get_settings()
app = FastAPI(title="TruthHire API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
        # 4. TODO: Start workflow in background (Wave 3)
        # background_tasks.add_task(run_verification_workflow, verification_id, parsed, github_username)
        
        return VerificationResponseV1(
            verification_id=verification_id,
            status="processing",
            message="Verification started",
            created_at=datetime.now()
        )
    
    except Exception as e:
        update_verification_status(verification_id, "failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/verify/{verification_id}")
async def get_verification(verification_id: str):
    """Get verification status and result"""
    result = supabase.table("verifications").select("*").eq("id", verification_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    return result.data

@app.get("/api/v1/verify/{verification_id}/steps")
async def get_steps(verification_id: str):
    """Get all agent progress steps"""
    steps = supabase.table("verification_steps").select("*").eq("verification_id", verification_id).order("created_at").execute()
    return {"steps": steps.data}

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
```

**Agent D Command:**
```
Complete backend API in backend/:

1. Create schemas.py with Pydantic models:
   - VerificationRequestV1, VerificationResponseV1
   - ParsedResume with nested Employment, Education models
   - Use exact structure above

2. Create services/resume_parser.py:
   - extract_text_from_pdf(bytes) using pdfplumber
   - parse_with_llm(text) using OpenAI GPT-4o-mini
   - Return ParsedResume object
   - Use exact code above

3. Update main.py with full API routes:
   - POST /api/v1/verify (upload resume, parse, store in Supabase)
   - GET /api/v1/verify/{id} (get verification)
   - GET /api/v1/verify/{id}/steps (get progress)
   - Handle file upload to Supabase Storage
   - Use exact code above

Test with curl:
curl -X POST http://localhost:8000/api/v1/verify -F "resume=@sample.pdf"
```

---

### Agent E: Fraud Detection Engine

**Tasks:**
1. Complete fraud detector class
2. Implement all detection rules
3. Risk level calculation

**Deliverables:**

**`agents/fraud_detector.py`**
```python
from typing import Literal
from dataclasses import dataclass, asdict

FraudLevel = Literal["green", "yellow", "red"]

@dataclass
class FraudFlag:
    type: str
    severity: str  # "low" | "medium" | "high" | "critical"
    message: str
    category: str
    evidence: dict

class FraudDetector:
    """Modular fraud detection engine"""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.rules = [
            self._check_github_consistency,
            self._check_employment_timeline,
            self._check_reference_sentiment,
        ]
    
    def analyze(
        self,
        resume_data: dict,
        github_data: dict = None,
        reference_responses: list = None,
    ) -> dict:
        """Run all fraud detection rules"""
        
        all_flags = []
        
        # Run each rule
        for rule in self.rules:
            try:
                flags = rule(resume_data, github_data or {}, reference_responses or [])
                all_flags.extend(flags)
            except Exception as e:
                print(f"Rule error: {e}")
                continue
        
        # Calculate risk
        risk_level = self._calculate_risk_level(all_flags)
        
        return {
            "risk_level": risk_level,
            "flags": [asdict(f) for f in all_flags],
            "flag_count": {
                "critical": len([f for f in all_flags if f.severity == "critical"]),
                "high": len([f for f in all_flags if f.severity == "high"]),
                "medium": len([f for f in all_flags if f.severity == "medium"]),
                "low": len([f for f in all_flags if f.severity == "low"])
            },
            "summary": self._generate_summary(risk_level, all_flags)
        }
    
    def _check_github_consistency(self, resume, github, refs) -> list:
        """Check if resume skills match GitHub languages"""
        flags = []
        
        if not github or "error" in github:
            return flags
        
        resume_skills = [s.lower() for s in resume.get("skills", [])]
        github_langs = [lang.lower() for lang in github.get("repositories", {}).get("languages", {}).keys()]
        
        # Map frameworks to languages
        skill_map = {
            "react": "javascript",
            "node.js": "javascript",
            "django": "python",
            "flask": "python"
        }
        
        for skill in ["python", "javascript", "typescript", "java", "go", "rust"]:
            if skill in resume_skills:
                mapped = skill_map.get(skill, skill)
                
                if mapped not in github_langs and skill not in github_langs:
                    flags.append(FraudFlag(
                        type="skill_mismatch",
                        severity="high",
                        message=f"Resume claims {skill.title()} expertise, but GitHub shows 0 {skill.title()} code",
                        category="Technical Skills",
                        evidence={"claimed": skill, "github_languages": github_langs}
                    ))
        
        return flags
    
    def _check_employment_timeline(self, resume, github, refs) -> list:
        """Detect employment gaps > 6 months"""
        flags = []
        
        jobs = sorted(resume.get("employment_history", []), key=lambda j: j["start_date"])
        
        for i in range(len(jobs) - 1):
            gap_months = self._calculate_gap_months(jobs[i]["end_date"], jobs[i+1]["start_date"])
            
            if gap_months > 6:
                flags.append(FraudFlag(
                    type="employment_gap",
                    severity="medium",
                    message=f"{gap_months}-month gap between {jobs[i]['company']} and {jobs[i+1]['company']}",
                    category="Employment History",
                    evidence={
                        "gap_start": jobs[i]["end_date"],
                        "gap_end": jobs[i+1]["start_date"],
                        "gap_months": gap_months
                    }
                ))
        
        return flags
    
    def _check_reference_sentiment(self, resume, github, refs) -> list:
        """Flag negative reference patterns"""
        flags = []
        
        if not refs:
            return flags
        
        avg_rating = sum(r.get("performance_rating", 7) for r in refs) / len(refs)
        would_not_rehire = [r for r in refs if not r.get("would_rehire", True)]
        
        if avg_rating < 6.5:
            flags.append(FraudFlag(
                type="low_performance_ratings",
                severity="high",
                message=f"Average reference rating {avg_rating:.1f}/10 (below threshold)",
                category="References",
                evidence={"avg_rating": avg_rating, "total_references": len(refs)}
            ))
        
        if len(would_not_rehire) >= 2:
            flags.append(FraudFlag(
                type="rehire_concerns",
                severity="high",
                message=f"{len(would_not_rehire)} of {len(refs)} references would NOT rehire",
                category="References",
                evidence={"would_not_rehire_count": len(would_not_rehire)}
            ))
        
        return flags
    
    def _calculate_risk_level(self, flags: list) -> FraudLevel:
        """Determine overall risk"""
        if any(f.severity == "critical" for f in flags):
            return "red"
        
        high_count = len([f for f in flags if f.severity == "high"])
        if high_count >= 2:
            return "red"
        
        medium_count = len([f for f in flags if f.severity == "medium"])
        if high_count >= 1 or medium_count >= 3:
            return "yellow"
        
        return "green"
    
    def _generate_summary(self, risk_level: FraudLevel, flags: list) -> str:
        if risk_level == "green":
            return "Verification successful. All claims verified with no major concerns."
        
        critical_msgs = [f.message for f in flags if f.severity in ["critical", "high"]]
        
        if risk_level == "red":
            return f"CRITICAL ISSUES: {'; '.join(critical_msgs[:2])}"
        else:
            return f"Minor concerns detected: {'; '.join(critical_msgs[:2])}"
    
    def _calculate_gap_months(self, end_date: str, start_date: str) -> int:
        """Calculate months between YYYY-MM dates"""
        from datetime import datetime
        end = datetime.strptime(end_date, "%Y-%m")
        start = datetime.strptime(start_date, "%Y-%m")
        return (start.year - end.year) * 12 + (start.month - end.month)
```

**Agent E Command:**
```
Create fraud detection engine in backend/agents/fraud_detector.py:

- FraudFlag dataclass with type, severity, message, category, evidence
- FraudDetector class with pluggable rules list
- Implement 3 core rules:
  1. _check_github_consistency (skill/language mismatch)
  2. _check_employment_timeline (gaps >6 months)
  3. _check_reference_sentiment (low ratings, rehire concerns)
- _calculate_risk_level (green/yellow/red logic)
- _generate_summary
- Helper: _calculate_gap_months

Use exact code structure above.

Test:
python -c "from agents.fraud_detector import FraudDetector; d = FraudDetector(); print(d.analyze({'skills': ['Python'], 'employment_history': []}, {'repositories': {'languages': {}}}, []))"
```

---

### Agent F: Frontend Components (Complete UI)

**Tasks:**
1. Complete upload page with form
2. Real-time progress page with Supabase Realtime
3. Report display page

**Deliverables:**

**`app/page.tsx` (Complete)**
```typescript
'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, Loader2 } from 'lucide-react'

export default function HomePage() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [githubUsername, setGithubUsername] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!file) {
      setError('Please select a resume file')
      return
    }

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('resume', file)
      if (githubUsername) {
        formData.append('github_username', githubUsername)
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/verify`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      router.push(`/verify/${data.verification_id}`)
    } catch (err) {
      setError('Failed to upload resume. Please try again.')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-8">
      <div className="max-w-2xl w-full bg-white rounded-xl shadow-2xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-5xl font-bold text-gray-900 mb-2">TruthHire</h1>
          <p className="text-xl text-gray-600">AI-Powered Candidate Verification</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Resume (PDF)
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-indigo-500 transition-colors">
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-indigo-50 file:text-indigo-700
                  hover:file:bg-indigo-100"
              />
              {file && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: {file.name}
                </p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              GitHub Username (optional)
            </label>
            <input
              type="text"
              value={githubUsername}
              onChange={(e) => setGithubUsername(e.target.value)}
              placeholder="e.g., torvalds"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !file}
            className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
          >
            {loading ? (
              <>
                <Loader2 className="animate-spin h-5 w-5" />
                Starting Verification...
              </>
            ) : (
              'Start Verification'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
```

**`app/verify/[id]/page.tsx` (Complete with Realtime)**
```typescript
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase, VerificationStep } from '@/lib/supabase'
import { CheckCircle2, Loader2, XCircle } from 'lucide-react'

export default function VerifyPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [steps, setSteps] = useState<VerificationStep[]>([])
  const [status, setStatus] = useState<string>('processing')

  useEffect(() => {
    // Subscribe to real-time updates
    const channel = supabase
      .channel('verification_progress')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'verification_steps',
          filter: `verification_id=eq.${params.id}`
        },
        (payload) => {
          const newStep = payload.new as VerificationStep
          setSteps(prev => [...prev, newStep])
          
          // Check if complete
          if (newStep.agent_name === 'Report Synthesizer' && newStep.status === 'complete') {
            setTimeout(() => {
              router.push(`/report/${params.id}`)
            }, 2000)
          }
        }
      )
      .subscribe()

    // Fetch existing steps
    const fetchSteps = async () => {
      const { data } = await supabase
        .table('verification_steps')
        .select('*')
        .eq('verification_id', params.id)
        .order('created_at', { ascending: true })
      
      if (data) {
        setSteps(data)
      }
    }
    
    fetchSteps()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [params.id, router])

  const statusIcons = {
    running: <Loader2 className="animate-spin h-6 w-6 text-blue-500" />,
    complete: <CheckCircle2 className="h-6 w-6 text-green-600" />,
    failed: <XCircle className="h-6 w-6 text-red-600" />
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Verification in Progress</h1>
          <p className="text-gray-600">Our AI agents are analyzing the candidate...</p>
        </div>

        <div className="space-y-4">
          {steps.map((step, idx) => (
            <div
              key={step.id}
              className="bg-white rounded-lg shadow-md p-6 flex items-start gap-4 animate-fade-in"
            >
              {statusIcons[step.status]}
              <div className="flex-1">
                <h3 className="font-semibold text-lg text-gray-900">{step.agent_name}</h3>
                <p className="text-gray-700 mt-1">{step.message}</p>
                <span className="text-sm text-gray-400 mt-2 block">
                  {new Date(step.created_at).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}

          {steps.length === 0 && (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <Loader2 className="animate-spin h-12 w-12 text-indigo-600 mx-auto mb-4" />
              <p className="text-gray-600">Initializing verification...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

**`app/report/[id]/page.tsx` (Complete)**
```typescript
'use client'

import { useEffect, useState } from 'react'
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react'

type Report = {
  risk_level: 'green' | 'yellow' | 'red'
  flags: any[]
  summary: string
  narrative?: string
  interview_questions?: string[]
}

export default function ReportPage({ params }: { params: { id: string } }) {
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/verify/${params.id}`)
        const data = await response.json()
        
        if (data.status === 'complete' && data.result) {
          setReport(data.result.fraud_results)
        }
      } catch (err) {
        console.error('Failed to fetch report:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchReport()
  }, [params.id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading report...</p>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">Report not found or still processing</p>
        </div>
      </div>
    )
  }

  const riskColors = {
    green: 'bg-green-100 text-green-800 border-green-300',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    red: 'bg-red-100 text-red-800 border-red-300'
  }

  const riskIcons = {
    green: <CheckCircle className="h-8 w-8" />,
    yellow: <AlertCircle className="h-8 w-8" />,
    red: <XCircle className="h-8 w-8" />
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Verification Report</h1>

        {/* Risk Badge */}
        <div className={`rounded-xl border-2 p-6 mb-8 ${riskColors[report.risk_level]}`}>
          <div className="flex items-center gap-4">
            {riskIcons[report.risk_level]}
            <div>
              <h2 className="text-2xl font-bold uppercase">{report.risk_level} Risk</h2>
              <p className="mt-1">{report.summary}</p>
            </div>
          </div>
        </div>

        {/* Fraud Flags */}
        {report.flags && report.flags.length > 0 && (
          <div className="bg-white rounded-xl shadow-md p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Detected Issues</h3>
            <div className="space-y-4">
              {report.flags.map((flag, idx) => (
                <div key={idx} className="border-l-4 border-red-500 pl-4 py-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="font-semibold text-gray-900">{flag.category}</span>
                      <p className="text-gray-700 mt-1">{flag.message}</p>
                      <span className="text-sm text-gray-500">Severity: {flag.severity}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Interview Questions */}
        {report.interview_questions && report.interview_questions.length > 0 && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Recommended Interview Questions</h3>
            <ol className="list-decimal list-inside space-y-3">
              {report.interview_questions.map((q, idx) => (
                <li key={idx} className="text-gray-700">{q}</li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  )
}
```

**Agent F Command:**
```
Complete frontend UI in frontend/:

1. Update app/page.tsx:
   - File upload form with drag-drop styling
   - GitHub username input (optional)
   - Form submission to POST /api/v1/verify
   - Loading state with spinner
   - Error handling
   - Redirect to /verify/[id] on success
   - Use exact code above

2. Update app/verify/[id]/page.tsx:
   - Supabase Realtime subscription to verification_steps
   - Display agent step cards (icon, name, message, timestamp)
   - Auto-redirect to /report/[id] when complete
   - Use exact code above

3. Update app/report/[id]/page.tsx:
   - Fetch verification result from API
   - Risk badge (green/yellow/red with colors)
   - Fraud flags list
   - Interview questions
   - Use exact code above

Install lucide-react if not already: npm install lucide-react

Test all pages render and compile.
```

---

### Wave 2 Integration (Hour 10 - 2 hours)

**You Test:**

1. **Upload Resume End-to-End**
   ```bash
   # Create sample resume PDF or use existing
   # Upload via frontend: http://localhost:3000
   # Verify:
   # - File uploads to Supabase Storage
   # - Resume gets parsed
   # - Verification record created in DB
   # - Redirects to /verify/[id]
   ```

2. **API Integration**
   ```bash
   # Test with curl
   curl -X POST http://localhost:8000/api/v1/verify \
     -F "resume=@test.pdf" \
     -F "github_username=torvalds"
   
   # Should return verification_id
   ```

3. **GitHub API Test**
   ```bash
   # Test fraud detector with real GitHub data
   python -c "
   from services.github_api import analyze_github_profile
   from agents.fraud_detector import FraudDetector
   
   github = analyze_github_profile('torvalds')
   detector = FraudDetector()
   result = detector.analyze(
       {'skills': ['C', 'Assembly'], 'employment_history': []},
       github,
       []
   )
   print(result)
   "
   ```

4. **Fix CORS Issues**
   - Frontend should call backend without CORS errors
   - Check browser console
   - Verify backend CORS middleware allows localhost:3000

**Pass Criteria:**
- [ ] File upload works frontend → backend
- [ ] Resume parsing extracts structured data
- [ ] Verification record saved in Supabase
- [ ] GitHub API returns real data
- [ ] Fraud detector runs without errors
- [ ] Frontend pages render without errors

**Common Issues:**
- CORS: Check main.py middleware
- File upload: Ensure Content-Type headers correct
- OpenAI: Verify API key in .env
- Supabase Storage: Check bucket is created and accessible

---

## WAVE 3: Orchestration (Hour 10-16)

### Agent G: LangGraph Orchestrator + All Agents

**Tasks:**
1. LangGraph state machine
2. All 5 agent implementations
3. Background task execution

**Deliverables:**

**`agents/orchestrator.py`**
```python
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from services.supabase_client import update_agent_progress, update_verification_status
from services.resume_parser import ParsedResume
from services.github_api import analyze_github_profile
from services.mock_loader import generate_mock_references, simulate_outreach_responses
from agents.fraud_detector import FraudDetector
import openai
import json
from config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

class VerificationState(TypedDict):
    verification_id: str
    parsed_resume: dict
    github_username: Optional[str]
    references: list
    reference_responses: list
    github_analysis: dict
    fraud_results: dict
    final_report: dict
    current_step: str

# Agent 1: Resume Parser (already done in upload, just log)
async def log_parsing(state: VerificationState) -> VerificationState:
    await update_agent_progress(
        state["verification_id"],
        "Resume Parser",
        "complete",
        f"Extracted data for {state['parsed_resume']['name']}"
    )
    state["current_step"] = "parsing_complete"
    return state

# Agent 2: Reference Discovery
async def discover_references(state: VerificationState) -> VerificationState:
    await update_agent_progress(
        state["verification_id"],
        "Reference Discovery",
        "running",
        "Discovering former coworkers..."
    )
    
    # Generate mock references
    refs = generate_mock_references(state["parsed_resume"]["employment_history"])
    
    await update_agent_progress(
        state["verification_id"],
        "Reference Discovery",
        "running",
        f"Found {len(refs)} former coworkers, simulating outreach..."
    )
    
    # Simulate outreach with 20% response rate
    responses = simulate_outreach_responses(refs, response_rate=0.20)
    
    await update_agent_progress(
        state["verification_id"],
        "Reference Discovery",
        "complete",
        f"Contacted {len(refs)} references, received {len(responses)} responses ({len(responses)/len(refs)*100:.0f}% response rate)"
    )
    
    state["references"] = refs
    state["reference_responses"] = responses
    state["current_step"] = "references_discovered"
    return state

# Agent 3: GitHub Analyzer
async def analyze_github(state: VerificationState) -> VerificationState:
    username = state.get("github_username")
    
    if not username:
        await update_agent_progress(
            state["verification_id"],
            "GitHub Analyzer",
            "complete",
            "No GitHub username provided, skipping analysis"
        )
        state["github_analysis"] = {}
        state["current_step"] = "github_skipped"
        return state
    
    await update_agent_progress(
        state["verification_id"],
        "GitHub Analyzer",
        "running",
        f"Analyzing GitHub profile: {username}"
    )
    
    # Real GitHub API call
    github_data = analyze_github_profile(username)
    
    if "error" in github_data:
        await update_agent_progress(
            state["verification_id"],
            "GitHub Analyzer",
            "failed",
            f"GitHub analysis failed: {github_data['error']}"
        )
        state["github_analysis"] = {}
    else:
        total_repos = github_data.get("repositories", {}).get("total", 0)
        total_commits = github_data.get("activity", {}).get("total_commits", 0)
        languages = list(github_data.get("repositories", {}).get("languages", {}).keys())
        
        await update_agent_progress(
            state["verification_id"],
            "GitHub Analyzer",
            "complete",
            f"Analyzed {total_repos} repositories, {total_commits} commits. Languages: {', '.join(languages[:5])}"
        )
        state["github_analysis"] = github_data
    
    state["current_step"] = "github_analyzed"
    return state

# Agent 4: Fraud Detection
async def detect_fraud(state: VerificationState) -> VerificationState:
    await update_agent_progress(
        state["verification_id"],
        "Fraud Detector",
        "running",
        "Cross-referencing resume claims with verification data..."
    )
    
    detector = FraudDetector(strict_mode=settings.fraud_detection_strict)
    
    fraud_results = detector.analyze(
        state["parsed_resume"],
        state.get("github_analysis", {}),
        state.get("reference_responses", [])
    )
    
    risk_level = fraud_results["risk_level"]
    flag_count = fraud_results["flag_count"]
    
    await update_agent_progress(
        state["verification_id"],
        "Fraud Detector",
        "complete",
        f"Risk assessment: {risk_level.upper()} | Flags: {flag_count['high']} high, {flag_count['medium']} medium"
    )
    
    state["fraud_results"] = fraud_results
    state["current_step"] = "fraud_detected"
    return state

# Agent 5: Report Synthesizer
async def synthesize_report(state: VerificationState) -> VerificationState:
    await update_agent_progress(
        state["verification_id"],
        "Report Synthesizer",
        "running",
        "Generating narrative summary and interview questions..."
    )
    
    # Generate narrative with GPT-4
    narrative = await generate_narrative(state)
    
    # Generate interview questions
    questions = generate_interview_questions(state["fraud_results"])
    
    final_report = {
        "fraud_results": state["fraud_results"],
        "narrative_summary": narrative,
        "interview_questions": questions,
        "verification_details": {
            "references_contacted": len(state.get("references", [])),
            "references_responded": len(state.get("reference_responses", [])),
            "github_analyzed": bool(state.get("github_analysis", {}).get("profile"))
        }
    }
    
    # Update verification record with result
    update_verification_status(
        state["verification_id"],
        "complete",
        final_report
    )
    
    await update_agent_progress(
        state["verification_id"],
        "Report Synthesizer",
        "complete",
        "Verification complete! Report ready."
    )
    
    state["final_report"] = final_report
    state["current_step"] = "complete"
    return state

async def generate_narrative(state: VerificationState) -> str:
    """Generate narrative summary with GPT-4"""
    
    prompt = f"""Write a concise 2-paragraph verification summary for a hiring manager.

Candidate: {state['parsed_resume']['name']}
Employment History: {json.dumps(state['parsed_resume']['employment_history'][:2])}
Reference Responses: {len(state.get('reference_responses', []))} responses received
Risk Level: {state['fraud_results']['risk_level']}
Key Flags: {state['fraud_results']['summary']}

Write professionally. Focus on verification findings, not speculation.
"""
    
    response = openai.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content

def generate_interview_questions(fraud_results: dict) -> list:
    """Generate targeted interview questions from fraud flags"""
    
    questions = []
    
    for flag in fraud_results.get("flags", [])[:5]:  # Top 5 flags
        if flag["type"] == "skill_mismatch":
            questions.append(f"Can you walk us through a recent project where you used {flag['evidence'].get('claimed', 'this skill')}? What was your specific role?")
        
        elif flag["type"] == "employment_gap":
            questions.append(f"I noticed a {flag['evidence']['gap_months']}-month gap in your employment history. Can you tell us what you were doing during that time?")
        
        elif flag["type"] == "low_performance_ratings":
            questions.append("Your references had some concerns about performance consistency. How do you handle feedback and what steps have you taken to improve?")
        
        elif flag["type"] == "rehire_concerns":
            questions.append("If we contacted your former managers, what would they say about working with you? Any areas where you've grown since then?")
    
    # Add generic questions if few flags
    if len(questions) < 3:
        questions.append("Tell us about a time you faced a significant challenge in a previous role. How did you handle it?")
        questions.append("What would your former colleagues say are your greatest strengths and areas for improvement?")
    
    return questions[:5]  # Max 5 questions

# Build LangGraph workflow
workflow = StateGraph(VerificationState)

# Add nodes
workflow.add_node("parse", log_parsing)
workflow.add_node("discover", discover_references)
workflow.add_node("github", analyze_github)
workflow.add_node("fraud", detect_fraud)
workflow.add_node("report", synthesize_report)

# Define edges
workflow.set_entry_point("parse")
workflow.add_edge("parse", "discover")
workflow.add_edge("discover", "github")
workflow.add_edge("github", "fraud")
workflow.add_edge("fraud", "report")
workflow.add_edge("report", END)

# Compile
verification_app = workflow.compile()

# Main execution function
async def run_verification_workflow(
    verification_id: str,
    parsed_resume: ParsedResume,
    github_username: Optional[str]
):
    """Execute full verification workflow"""
    
    initial_state: VerificationState = {
        "verification_id": verification_id,
        "parsed_resume": parsed_resume.model_dump(),
        "github_username": github_username,
        "references": [],
        "reference_responses": [],
        "github_analysis": {},
        "fraud_results": {},
        "final_report": {},
        "current_step": "started"
    }
    
    try:
        final_state = await verification_app.ainvoke(initial_state)
        return final_state["final_report"]
    except Exception as e:
        update_verification_status(verification_id, "failed", {"error": str(e)})
        raise
```

**Update `main.py` to use orchestrator:**
```python
# Add import at top
from agents.orchestrator import run_verification_workflow

# Update create_verification endpoint (replace TODO comment):
@app.post("/api/v1/verify", response_model=VerificationResponseV1)
async def create_verification(
    resume: UploadFile = File(...),
    github_username: str = None,
    background_tasks: BackgroundTasks = None
):
    """Upload resume and start verification"""
    
    verification_id = str(uuid.uuid4())
    
    try:
        # ... existing code for upload and parsing ...
        
        # 4. Start workflow in background
        background_tasks.add_task(
            run_verification_workflow,
            verification_id,
            parsed,
            github_username or parsed.github_username
        )
        
        return VerificationResponseV1(
            verification_id=verification_id,
            status="processing",
            message="Verification started",
            created_at=datetime.now()
        )
    
    except Exception as e:
        update_verification_status(verification_id, "failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))
```

**Agent G Command:**
```
Create LangGraph orchestration system in backend/agents/orchestrator.py:

1. VerificationState TypedDict with all workflow state
2. 5 async agent functions:
   - log_parsing (logs resume parse completion)
   - discover_references (generates mocks + responses)
   - analyze_github (calls real GitHub API)
   - detect_fraud (calls FraudDetector)
   - synthesize_report (GPT-4 narrative + questions)
3. Each agent logs progress via update_agent_progress()
4. LangGraph StateGraph with nodes: parse → discover → github → fraud → report
5. run_verification_workflow(verification_id, parsed_resume, github_username) main function
6. Use exact code above

Update main.py:
- Import run_verification_workflow
- Call in background_tasks.add_task()

Test:
Upload resume via frontend and watch real-time agent progress!
```

---

### Agent H: Polish + Demo Prep

**Tasks:**
1. Error handling throughout
2. Loading states
3. Create demo resume PDFs
4. Test all scenarios

**Deliverables:**

**`demo/create_demo_resumes.py`**
```python
"""
Generate 3 demo resume PDFs for different scenarios
Run: python demo/create_demo_resumes.py
"""

from fpdf import FPDF
import os

def create_green_resume():
    """Clean candidate - no fraud flags"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "SARAH CHEN", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "sarah.chen@email.com | github: torvalds", ln=True, align="C")
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "EXPERIENCE", ln=True)
    pdf.set_font("Arial", "", 10)
    
    pdf.multi_cell(0, 5, """
Senior Software Engineer | TechCorp | 2020-01 to 2024-01
- Led backend infrastructure team of 5 engineers
- Built microservices architecture serving 10M+ users
- Technologies: Python, Django, PostgreSQL, AWS
    
Software Engineer | StartupXYZ | 2018-06 to 2019-12
- Full-stack development on React/Node.js platform
- Contributed to open source projects
    """)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "EDUCATION", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "BS Computer Science | MIT | 2018", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "SKILLS", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "Python, JavaScript, React, PostgreSQL, AWS, Docker", ln=True)
    
    pdf.output("demo/candidate_green.pdf")

def create_yellow_resume():
    """Minor concerns - employment gap"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "MIKE JOHNSON", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "mike.j@email.com | github: your-github-here", ln=True, align="C")
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "EXPERIENCE", ln=True)
    pdf.set_font("Arial", "", 10)
    
    pdf.multi_cell(0, 5, """
Frontend Developer | WebAgency | 2023-01 to 2024-11
- Built responsive web applications with React
- Collaborated with design team on UI/UX
    
Developer | FreelanceCo | 2021-01 to 2021-12
- Various contract projects
- [8-month gap between jobs will trigger yellow flag]
    """)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "EDUCATION", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "BS Computer Science | State University | 2020", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "SKILLS", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "JavaScript, React, TypeScript, Node.js, HTML, CSS", ln=True)
    
    pdf.output("demo/candidate_yellow.pdf")

def create_red_resume():
    """Major fraud - skill mismatch with GitHub"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "JOHN FRAUD", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "john.fraud@email.com | github: your-github-here", ln=True, align="C")
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "EXPERIENCE", ln=True)
    pdf.set_font("Arial", "", 10)
    
    pdf.multi_cell(0, 5, """
Senior Python Engineer | FakeCorp | 2020-01 to 2024-01
- Led Python/Django backend development
- 1000+ commits to open source Python projects
- Expert in Python, Django, Flask, FastAPI
[Will conflict with GitHub showing 0 Python code]
    """)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "EDUCATION", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "MS Computer Science | Stanford | 2019", ln=True)
    pdf.cell(0, 5, "[May trigger education verification flag]", ln=True)
    
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "SKILLS", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, "Python (Expert), Django, Flask, PostgreSQL, Redis", ln=True)
    pdf.cell(0, 5, "[Claims Python expert but GitHub will show different languages]", ln=True)
    
    pdf.output("demo/candidate_red.pdf")

if __name__ == "__main__":
    os.makedirs("demo", exist_ok=True)
    create_green_resume()
    create_yellow_resume()
    create_red_resume()
    print("✅ Created 3 demo resumes in demo/ folder")
```

**Add error boundaries to frontend components**
**Add loading skeletons**
**Polish animations**

**Agent H Command:**
```
Polish and demo prep:

1. Add error handling to all API calls in frontend
2. Add loading skeletons to report page
3. Create demo/create_demo_resumes.py script to generate 3 PDFs (green/yellow/red)
   - Use fpdf2 library
   - Green: Clean candidate (use GitHub username: torvalds)
   - Yellow: Employment gap scenario
   - Red: Skill mismatch (claims Python expert, GitHub shows Java)
4. Add fade-in animations to agent step cards (Tailwind animate-fade-in)
5. Test all 3 scenarios end-to-end

Install fpdf2: pip install fpdf2
Run: python demo/create_demo_resumes.py
```

---

### Wave 3 Testing (Hour 16-19 - 3 hours)

**You Test:**

**End-to-End Test - Green Scenario:**
1. Upload `candidate_green.pdf` with GitHub username
2. Watch agents run in real-time
3. Verify green risk score in report
4. Check narrative makes sense

**End-to-End Test - Yellow Scenario:**
1. Upload `candidate_yellow.pdf`
2. Verify employment gap detected
3. Check yellow risk score

**End-to-End Test - Red Scenario:**
1. Upload `candidate_red.pdf` with GitHub username showing different skills
2. Verify skill mismatch detected
3. Check red risk score
4. Verify interview questions reference the flags

**Pass Criteria:**
- [ ] All 3 scenarios complete without errors
- [ ] Real-time updates work smoothly
- [ ] Fraud detection catches appropriate flags
- [ ] Reports display correctly
- [ ] Can run back-to-back demos

---

## Hour 16-20: Demo Prep

**Your Tasks:**

1. **Practice 90-Second Pitch**
   - Problem: Companies waste time on fraudulent candidates
   - Solution: AI agents verify claims via multi-source analysis
   - Demo: Upload resume, watch agents work, show fraud detection
   - Business: $100-150/verification, targets tech companies

2. **Record Backup Video**
   - Screen record all 3 scenarios
   - Upload to YouTube (unlisted)
   - Have ready if live demo fails

3. **Prepare Q&A Answers**
   - Review questions in technical-requirements-mvp.md
   - Practice answers out loud

4. **Test on Different Machine**
   - Ensure it runs on presentation laptop
   - Test internet connection (GitHub API needs network)

5. **Create Slide Deck (Optional)**
   - 3-5 slides: Problem, Solution, Demo, Business Model
   - Keep minimal, focus on live demo

---

## Hour 20-24: Buffer & Sleep

- [ ] Final bug fixes
- [ ] Deploy to Vercel/Railway (optional)
- [ ] Sleep before presentation

---

## Success Criteria

### Minimum Viable Demo (Must-Have)
- [ ] Upload resume works
- [ ] See 5 agents run (real-time updates)
- [ ] Display report with risk score
- [ ] 1 fraud scenario works

### Full Feature Set (Goal)
- [ ] All 3 demo scenarios work (green/yellow/red)
- [ ] GitHub API pulls real data
- [ ] Fraud detection catches 2+ flag types
- [ ] Professional UI with smooth animations
- [ ] Can run back-to-back without errors

---

## Emergency Rollback Plan

**If Wave 3 fails:**
- Revert to Wave 2 code
- Manually trigger fraud detection (skip orchestration)
- Still have working upload + display

**If Wave 2 fails:**
- Revert to Wave 1 code
- Show static demo with pre-generated data

**If everything fails:**
- Show backup video
- Walk through architecture on slides

---

## Agent Spawn Summary

**Wave 1 (Hour 1-4):** Spawn 3 agents
- Agent A: Backend foundation
- Agent B: Frontend foundation  
- Agent C: Data layer (GitHub + mocks)

**Wave 2 (Hour 4-10):** Spawn 3 agents
- Agent D: Backend API + Resume Parser
- Agent E: Fraud Detection Engine
- Agent F: Frontend Components (complete UI)

**Wave 3 (Hour 10-16):** Spawn 2 agents
- Agent G: LangGraph Orchestrator + All Agents
- Agent H: Polish + Demo Prep

**Total:** 8 agents across 3 waves

---

**Ready to start Wave 1? Confirm Supabase setup is complete!**
