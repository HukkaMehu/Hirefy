# Comprehensive System Architecture and Data Flow Analysis

## Executive Summary

This document provides a detailed analysis of the TruthHire verification system architecture, identifying potential issues in data flow, compatibility, and integration across backend, database, and frontend components.

---

## 1. Database Schema Analysis

### Expected Schema (from documentation)

#### `verifications` table
```sql
CREATE TABLE verifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_name TEXT NOT NULL,
  candidate_email TEXT,
  github_username TEXT,
  status TEXT NOT NULL DEFAULT 'processing',  -- 'processing' | 'complete' | 'failed'
  risk_score TEXT,  -- 'green' | 'yellow' | 'red'
  resume_url TEXT,
  parsed_data JSONB,
  result JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);
```

#### `verification_steps` table
```sql
CREATE TABLE verification_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  verification_id UUID REFERENCES verifications(id) ON DELETE CASCADE,
  agent_name TEXT NOT NULL,
  status TEXT NOT NULL,  -- 'running' | 'complete' | 'failed'
  message TEXT,
  data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_steps_vid_created ON verification_steps(verification_id, created_at DESC);
ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;
```

### Findings
- ✅ Schema is well-designed with proper foreign keys and indexing
- ✅ JSONB columns provide flexibility for structured data
- ⚠️ Realtime publication must be manually enabled
- ⚠️ 'resumes' storage bucket must be created separately

---

## 2. Backend Flow Analysis

### Data Flow Chain

```
1. POST /api/v1/verify (main.py)
   ├─> Upload file → Supabase Storage
   ├─> extract_text_from_pdf(bytes) → text
   ├─> parse_with_llm(text) → ParsedResume object
   ├─> parsed.model_dump() → dict
   ├─> Insert to verifications table
   └─> background_tasks.add_task(
         run_verification_workflow,
         verification_id,
         parsed.model_dump(),  ← dict passed here
         github_username
       )

2. Orchestrator (orchestrator.py)
   ├─> VerificationState(
   │     parsed_resume=parsed.model_dump()  ← dict stored in state
   │   )
   ├─> log_parsing → update_agent_progress()
   ├─> discover_references → update_agent_progress()
   ├─> analyze_github → update_agent_progress()
   ├─> detect_fraud
   │   └─> detector.analyze(
   │         state["parsed_resume"],  ← dict from state
   │         github_analysis,
   │         reference_responses
   │       )
   └─> synthesize_report
       ├─> update_verification_status()
       └─> update_agent_progress()

3. Fraud Detector (fraud_detector.py)
   └─> analyze(resume_data: dict, ...)  ← Expects dict
```

### Key Observations

**Schema Definitions** (`backend/schemas.py`):
- `ParsedResume` has fields: name, email, employment_history, education, skills, github_username
- `Employment` has: company, title, start_date, end_date, description
- `Education` has: school, degree, field, graduation_year
- All use Pydantic BaseModel with proper typing

**Data Conversion**:
- ✅ `ParsedResume.model_dump()` correctly converts object → dict
- ✅ `FraudDetector.analyze()` signature accepts dict as first parameter
- ✅ Dict keys from `model_dump()` match what fraud_detector expects

**Function Compatibility**:
- ✅ `parse_with_llm()` returns `ParsedResume` object (line 60 in resume_parser.py)
- ✅ Orchestrator correctly calls `parsed.model_dump()` before passing to workflow
- ✅ `FraudDetector.analyze()` correctly accesses dict keys like `resume_data.get("skills", [])`

---

## 3. Async/Sync Compatibility Analysis

### Function Signatures

#### Supabase Client Functions (`services/supabase_client.py`)
```python
async def update_agent_progress(...)  # ← ASYNC
def update_verification_status(...)   # ← SYNC
def get_verification(...)              # ← SYNC
```

#### Orchestrator Node Functions (`agents/orchestrator.py`)
```python
async def log_parsing(state)           # ← ASYNC
async def discover_references(state)   # ← ASYNC
async def analyze_github(state)        # ← ASYNC
async def detect_fraud(state)          # ← ASYNC
async def synthesize_report(state)     # ← ASYNC
```

#### Fraud Detector (`agents/fraud_detector.py`)
```python
def analyze(resume_data, github_data, ...)  # ← SYNC
```

### Issues Identified

**CRITICAL: Async/Sync Mismatch**

Location: `orchestrator.py` lines 207 and 394
```python
# Line 207 in synthesize_report()
await update_verification_status(  # ← AWAIT on SYNC function
    verification_id=state["verification_id"],
    status="completed",
    result=final_report
)

# Line 394 in run_verification_workflow()
await update_verification_status(  # ← AWAIT on SYNC function
    verification_id=verification_id,
    status="failed",
    result={"error": str(e)}
)
```

**Issue**: `update_verification_status` is defined as a synchronous function but is called with `await`.

**Impact**: This will cause runtime errors when the function is called.

**Fix Options**:
1. Make `update_verification_status` async (recommended)
2. Remove `await` and call it synchronously
3. Wrap calls in `asyncio.to_thread()` like done for `analyze_github_profile`

### Correctly Handled Async/Sync Calls

**Good Example 1**: FraudDetector (line 160-165 in orchestrator.py)
```python
fraud_results = await asyncio.to_thread(
    detector.analyze,
    state["parsed_resume"],
    state.get("github_analysis"),
    state.get("reference_responses")
)
```
✅ Sync function properly wrapped in `asyncio.to_thread()`

**Good Example 2**: GitHub Analysis (line 117 in orchestrator.py)
```python
github_data = await asyncio.to_thread(analyze_github_profile, github_username)
```
✅ Sync function properly wrapped

**Good Example 3**: Agent Progress (lines 29-35, 80-89, etc.)
```python
await update_agent_progress(  # ← Correctly awaits async function
    verification_id=state["verification_id"],
    agent_name="Resume Parser",
    status="completed",
    message="Resume parsed successfully",
    data={"parsed": state["parsed_resume"]}
)
```
✅ Async function properly awaited

---

## 4. Status Value Inconsistencies

### Backend Status Values

**In orchestrator.py** (used when calling `update_agent_progress`):
- `"in_progress"` (lines 43, 110, 153, 185)
- `"completed"` (lines 31, 82, 130, 172, 217)
- `"failed"` (lines 142, 401)
- `"skipped"` (lines 102)

**In supabase_client.py**:
- Line 36: Checks for `status == "complete"` (no 'd')
```python
if status == "complete":  # ← No 'd', but orchestrator passes "completed"
    from datetime import datetime
    update_data["completed_at"] = datetime.now().isoformat()
```

### Frontend Status Values

**In frontend/lib/supabase.ts** (line 12):
```typescript
status: 'running' | 'complete' | 'failed'
```

**In frontend/app/verify/[id]/page.tsx** (lines 73-77):
```typescript
const statusIcons = {
  in_progress: <Loader2 className="animate-spin h-6 w-6 text-blue-500" />,
  completed: <CheckCircle2 className="h-6 w-6 text-green-600" />,
  failed: <XCircle className="h-6 w-6 text-red-600" />,
  skipped: <AlertTriangle className="h-6 w-6 text-gray-400" />
}
```

### Issues Identified

**MEDIUM: Status Value Mismatch**

1. **Backend vs Frontend TypeScript definition**:
   - TypeScript definition expects: `'running' | 'complete' | 'failed'`
   - Backend uses: `'in_progress' | 'completed' | 'failed' | 'skipped'`
   - Frontend JSX actually handles: `in_progress`, `completed`, `failed`, `skipped`

2. **Backend internal inconsistency**:
   - `supabase_client.py` checks for `"complete"` (line 36)
   - `orchestrator.py` passes `"completed"` (line 207)
   - Result: `completed_at` timestamp never gets set!

**Impact**:
- Frontend JSX will work because it matches backend values
- TypeScript types are incorrect but won't cause runtime errors
- `completed_at` field never gets populated due to spelling mismatch

**Recommended Fix**:
- Use `"completed"` everywhere (backend standard)
- Fix `supabase_client.py` line 36: `if status == "completed":`
- Update frontend TypeScript to match: `'in_progress' | 'completed' | 'failed' | 'skipped'`

---

## 5. Frontend Integration Analysis

### Real-time Subscription

**Frontend setup** (`frontend/app/verify/[id]/page.tsx` lines 15-40):
```typescript
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
      
      if (newStep.status === 'failed') {
        setError(`Agent ${newStep.agent_name} failed: ${newStep.message}`)
      }
      
      if (newStep.agent_name === 'Report Synthesizer' && newStep.status === 'completed') {
        setTimeout(() => {
          router.push(`/report/${params.id}`)
        }, 2000)
      }
    }
  )
  .subscribe()
```

### Requirements for Real-time to Work

1. **Database publication** (must be run in Supabase SQL editor):
   ```sql
   ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;
   ```

2. **Row Level Security**: If enabled, anon key must have SELECT permission on `verification_steps`

3. **Table structure must match**: All columns referenced must exist

### API Integration

**Upload endpoint** (`frontend/app/page.tsx`):
```typescript
POST ${process.env.NEXT_PUBLIC_API_URL}/api/v1/verify
```

**Report endpoint** (`frontend/app/report/[id]/page.tsx`):
```typescript
GET ${process.env.NEXT_PUBLIC_API_URL}/api/v1/verify/${id}
```

### Findings

✅ API endpoints are correctly implemented in backend (`main.py` lines 35-168)
✅ Frontend correctly subscribes to real-time updates
✅ Frontend correctly handles navigation flow: upload → verify → report
⚠️ Requires `NEXT_PUBLIC_API_URL` environment variable (likely `http://localhost:8000`)
⚠️ Realtime publication must be manually enabled in Supabase

---

## 6. Configuration Analysis

### Backend Configuration

**Required environment variables** (`backend/config.py`):
```python
openai_api_key: str
supabase_url: str
supabase_anon_key: str
supabase_service_key: str
github_token: str = ""  # optional

# Feature flags
use_mock_data: bool = True
fraud_detection_strict_mode: bool = True

# LLM config
llm_model: str = "gpt-4o-mini"
llm_temperature: float = 0.1
llm_max_tokens: int = 4000
```

**Environment file location**: `backend/.env` or root `.env`

### Frontend Configuration

**Required environment variables** (`frontend/lib/supabase.ts`):
```typescript
NEXT_PUBLIC_SUPABASE_URL
NEXT_PUBLIC_SUPABASE_ANON_KEY
NEXT_PUBLIC_API_URL  // e.g., http://localhost:8000
```

### Findings

✅ Backend has proper fallback behavior when services fail:
   - LLM parsing failure → uses mock resume data (line 78-107 in main.py)
   - Storage upload failure → uses mock URL (line 64-67 in main.py)

⚠️ Root `.env.example` file is empty - should contain template

---

## 7. Identified Issues Summary

### Critical Issues (Must Fix)

#### 1. Async/Sync Mismatch
**Severity**: CRITICAL  
**Location**: `backend/services/supabase_client.py`, `backend/agents/orchestrator.py:207, 394`  
**Description**: `update_verification_status` is sync but called with `await`  
**Impact**: Runtime error when called  
**Fix**:
```python
# Option 1: Make function async (recommended)
async def update_verification_status(verification_id: str, status: str, result: dict = None):
    """Update verification status and result"""
    update_data = {"status": status}
    if result:
        update_data["result"] = result
    if status == "completed":  # Also fix this spelling
        from datetime import datetime
        update_data["completed_at"] = datetime.now().isoformat()
    
    supabase.table("verifications").update(update_data).eq("id", verification_id).execute()
```

### High Priority Issues

#### 2. Status Spelling Mismatch
**Severity**: HIGH  
**Location**: `backend/services/supabase_client.py:36`  
**Description**: Checks for `"complete"` but receives `"completed"`  
**Impact**: `completed_at` timestamp never gets set  
**Fix**: Change line 36 to:
```python
if status == "completed":  # Add the 'd'
```

#### 3. Frontend TypeScript Type Mismatch
**Severity**: MEDIUM  
**Location**: `frontend/lib/supabase.ts:12`  
**Description**: Type definition doesn't match backend status values  
**Impact**: TypeScript errors, confusion  
**Fix**: Update to:
```typescript
status: 'in_progress' | 'completed' | 'failed' | 'skipped'
```

### Medium Priority Issues

#### 4. Missing Realtime Publication
**Severity**: MEDIUM  
**Location**: Supabase database configuration  
**Description**: `verification_steps` table not added to realtime publication  
**Impact**: Frontend won't receive live updates  
**Fix**: Run in Supabase SQL editor:
```sql
ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;
```

#### 5. Missing Storage Bucket
**Severity**: LOW  
**Location**: Supabase storage configuration  
**Description**: 'resumes' bucket may not exist  
**Impact**: Resume uploads fail, falls back to mock URL  
**Fix**: Create 'resumes' bucket in Supabase Storage dashboard (public=false, max 5MB)

### Low Priority Issues

#### 6. Empty .env.example
**Severity**: LOW  
**Location**: Root `.env.example`  
**Description**: File is empty, should contain template  
**Impact**: Makes setup harder for new developers  
**Fix**: Add template with all required variables

---

## 8. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Next.js)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Upload Page (app/page.tsx)                                          │
│     User selects PDF + optional GitHub username                         │
│     │                                                                    │
│     └──> POST /api/v1/verify                                            │
│          ├─ multipart/form-data: resume file                            │
│          └─ query param: github_username                                │
│                                                                          │
│  2. Verification Progress Page (app/verify/[id]/page.tsx)               │
│     Real-time agent progress display                                    │
│     │                                                                    │
│     ├──> Supabase Realtime subscription:                                │
│     │    table='verification_steps'                                     │
│     │    filter='verification_id=eq.{id}'                               │
│     │                                                                    │
│     └──> On 'Report Synthesizer' completed:                             │
│          Navigate to /report/{id}                                       │
│                                                                          │
│  3. Report Page (app/report/[id]/page.tsx)                              │
│     Final verification results                                          │
│     │                                                                    │
│     └──> GET /api/v1/verify/{id}                                        │
│          Returns: verification record with result JSONB                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          BACKEND (FastAPI)                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  main.py                                                                 │
│  POST /api/v1/verify (line 35)                                          │
│     │                                                                    │
│     ├─> 1. Upload to Supabase Storage                                   │
│     │   supabase.storage.from_("resumes").upload(...)                   │
│     │   [Fallback to mock URL on failure]                               │
│     │                                                                    │
│     ├─> 2. Extract text from PDF                                        │
│     │   extract_text_from_pdf(resume_bytes) → text                      │
│     │                                                                    │
│     ├─> 3. Parse with LLM                                               │
│     │   parse_with_llm(text) → ParsedResume object                      │
│     │   [Fallback to mock data on failure]                              │
│     │                                                                    │
│     ├─> 4. Save to database                                             │
│     │   supabase.table("verifications").insert({                        │
│     │     id: verification_id,                                          │
│     │     candidate_name: parsed.name,                                  │
│     │     parsed_data: parsed.model_dump(),  ← Pydantic → dict          │
│     │     status: "processing"                                          │
│     │   })                                                               │
│     │                                                                    │
│     └─> 5. Start background workflow                                    │
│         background_tasks.add_task(                                      │
│           run_verification_workflow,                                    │
│           verification_id,                                              │
│           parsed.model_dump(),  ← Pass as dict                          │
│           github_username                                               │
│         )                                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              │ Background Task
                              ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (LangGraph)                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  agents/orchestrator.py                                                  │
│  run_verification_workflow(verification_id, parsed_resume_dict,         │
│                            github_username)                              │
│                                                                          │
│  Initial State:                                                          │
│    VerificationState(                                                    │
│      verification_id: str,                                               │
│      parsed_resume: dict  ← from ParsedResume.model_dump()              │
│      github_username: Optional[str],                                     │
│      references: [],                                                     │
│      reference_responses: [],                                            │
│      github_analysis: {},                                                │
│      fraud_results: {},                                                  │
│      final_report: {}                                                    │
│    )                                                                     │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ Workflow: StateGraph with 5 nodes                            │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
│  1. log_parsing (async)                                                  │
│     └─> await update_agent_progress(                                    │
│           agent_name="Resume Parser",                                   │
│           status="completed",                                           │
│           data={"parsed": state["parsed_resume"]}                       │
│         )                                                                │
│     [Writes to verification_steps table]                                │
│                                                                          │
│  2. discover_references (async)                                          │
│     ├─> Parse employment_history from state["parsed_resume"]           │
│     ├─> Generate mock references (3 per job)                            │
│     ├─> Simulate reference responses (20% chance)                       │
│     └─> await update_agent_progress(                                    │
│           agent_name="Reference Discovery",                             │
│           status="completed",                                           │
│           data={references, responses}                                  │
│         )                                                                │
│                                                                          │
│  3. analyze_github (async)                                               │
│     ├─> if github_username exists:                                      │
│     │   └─> github_data = await asyncio.to_thread(                     │
│     │         analyze_github_profile, github_username                   │
│     │       )                                                            │
│     └─> await update_agent_progress(                                    │
│           agent_name="GitHub Analyzer",                                 │
│           status="completed"/"skipped",                                 │
│           data=github_data                                              │
│         )                                                                │
│                                                                          │
│  4. detect_fraud (async)                                                 │
│     ├─> detector = FraudDetector()                                      │
│     ├─> fraud_results = await asyncio.to_thread(                        │
│     │     detector.analyze,                                             │
│     │     state["parsed_resume"],  ← dict passed here                   │
│     │     state["github_analysis"],                                     │
│     │     state["reference_responses"]                                  │
│     │   )                                                                │
│     └─> await update_agent_progress(                                    │
│           agent_name="Fraud Detector",                                  │
│           status="completed",                                           │
│           data=fraud_results                                            │
│         )                                                                │
│                                                                          │
│  5. synthesize_report (async)                                            │
│     ├─> narrative = await generate_narrative(state)  [Calls OpenAI]    │
│     ├─> interview_questions = generate_interview_questions(...)         │
│     ├─> final_report = {                                                │
│     │     candidate_name, risk_level, fraud_flags,                      │
│     │     narrative, interview_questions, ...                           │
│     │   }                                                                │
│     ├─> [ISSUE] await update_verification_status(  ← Awaiting sync fn! │
│     │     verification_id, "completed", final_report                    │
│     │   )                                                                │
│     └─> await update_agent_progress(                                    │
│           agent_name="Report Synthesizer",                              │
│           status="completed",                                           │
│           data=final_report                                             │
│         )                                                                │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
       │                                    │
       │ Writes to DB                       │ Writes to DB
       ↓                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                          SUPABASE                                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  PostgreSQL Tables:                                                      │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ verifications                                                │       │
│  ├─────────────────────────────────────────────────────────────┤       │
│  │ id (UUID), candidate_name, candidate_email,                 │       │
│  │ github_username, status, risk_score, resume_url,            │       │
│  │ parsed_data (JSONB), result (JSONB),                        │       │
│  │ created_at, completed_at                                     │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ verification_steps (REALTIME ENABLED)                        │       │
│  ├─────────────────────────────────────────────────────────────┤       │
│  │ id (UUID), verification_id (FK), agent_name,                │       │
│  │ status, message, data (JSONB), created_at                   │       │
│  │                                                              │       │
│  │ [Real-time publication broadcasts INSERTs to frontend]      │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
│  Storage Buckets:                                                        │
│  ┌─────────────────────────────────────────────────────────────┐       │
│  │ resumes (private, max 5MB, PDF only)                        │       │
│  └─────────────────────────────────────────────────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Recommendations and Fixes

### Immediate Actions Required

1. **Fix async/sync mismatch in `update_verification_status`**
   ```python
   # In backend/services/supabase_client.py
   async def update_verification_status(verification_id: str, status: str, result: dict = None):
       """Update verification status and result"""
       update_data = {"status": status}
       if result:
           update_data["result"] = result
       if status == "completed":  # Fix spelling here too
           from datetime import datetime
           update_data["completed_at"] = datetime.now().isoformat()
       
       supabase.table("verifications").update(update_data).eq("id", verification_id).execute()
   ```

2. **Fix status spelling mismatch**
   - Change line 36 in `supabase_client.py` from `"complete"` to `"completed"`

3. **Update frontend TypeScript types**
   ```typescript
   // In frontend/lib/supabase.ts
   export type VerificationStep = {
     id: string
     verification_id: string
     agent_name: string
     status: 'in_progress' | 'completed' | 'failed' | 'skipped'  // Updated
     message: string
     data?: any
     created_at: string
   }
   ```

4. **Enable Supabase realtime** (run in SQL editor):
   ```sql
   ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;
   ```

5. **Create storage bucket** (in Supabase dashboard):
   - Name: `resumes`
   - Public: No
   - File size limit: 5MB
   - Allowed MIME types: `application/pdf`

### Data Structure Validation

✅ All data structures are compatible:
- `ParsedResume.model_dump()` produces dict with correct keys
- `FraudDetector.analyze()` correctly accesses dict keys
- JSONB columns can store any structured data
- No schema mismatches detected

### Testing Checklist

- [ ] Test `update_verification_status` after making it async
- [ ] Verify `completed_at` gets populated correctly
- [ ] Test frontend real-time updates after enabling publication
- [ ] Test resume upload to storage bucket
- [ ] Test full workflow end-to-end with real resume
- [ ] Verify status icons display correctly in frontend
- [ ] Test error handling when services fail

---

## 10. Configuration Checklist

### Backend Setup
- [ ] Create `backend/.env` with all required keys
- [ ] Set `OPENAI_API_KEY` with valid key
- [ ] Set `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`
- [ ] Set `GITHUB_TOKEN` (optional, for higher rate limits)
- [ ] Install dependencies: `pip install -r backend/requirements.txt`

### Frontend Setup
- [ ] Create `frontend/.env.local` with:
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `NEXT_PUBLIC_API_URL=http://localhost:8000`
- [ ] Install dependencies: `cd frontend && npm install`

### Database Setup
- [ ] Run schema migration SQL (from `workstream-3-wave-plan.md` lines 51-79)
- [ ] Enable realtime: `ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;`
- [ ] Create `resumes` storage bucket
- [ ] (Optional) Configure Row Level Security if needed

---

## Conclusion

The system architecture is well-designed with clear separation of concerns. The main issues are:

1. **Critical**: Async/sync mismatch in `update_verification_status` - must fix
2. **High**: Status value spelling inconsistency - affects `completed_at` field
3. **Medium**: Frontend TypeScript types don't match backend values
4. **Low**: Missing database configuration (realtime publication, storage bucket)

All data structures are compatible and flow correctly through the system. The ParsedResume → dict conversion works as expected, and the fraud detector correctly processes the dictionary format.

Once the critical and high-priority issues are fixed, the system should work as designed.
