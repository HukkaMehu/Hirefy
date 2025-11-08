# Wave 2 Testing Guide

## Quick Start - Run Wave 2

### Prerequisites
1. ✅ Supabase project created with tables
2. ✅ Environment variables configured in `.env`
3. ✅ Python dependencies installed: `pip install -r backend/requirements.txt`
4. ✅ Frontend dependencies installed: `cd frontend && npm install`

---

## Step-by-Step Testing

### 1. Test Backend Components (5 minutes)

#### A. Quick Component Test
```bash
# From project root
python backend\quick_test.py
```

**Expected Output:**
```
1. Testing schemas... OK
2. Testing resume parser... OK
3. Testing fraud detector... OK
4. Testing GitHub API... OK
5. Testing mock loader... OK (16 refs)
6. Testing main API... OK
7. Testing full integration... OK
   Risk: red/yellow/green
   Flags: X
   References: X

ALL TESTS PASSED!
```

#### B. Test Fraud Detector
```bash
python backend\test_fraud_detector.py
```

**Expected Output:**
```
[Test 1: Green Scenario] Risk Level: green, Flags: 0
[Test 3: Employment Gap] Risk Level: green, Flags: 1
  - [MEDIUM] 9-month gap between Company A and Company B
```

#### C. Test Mock Data System
```bash
python backend\test_mock_quick.py
```

**Expected Output:**
```
Created 36 references across 2 companies
Got 7 responses from 36 contacts (19.4% response rate)
```

---

### 2. Start Backend Server

#### Terminal 1 - Backend
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### Test Health Endpoint
Open browser or use curl:
```bash
# Browser: http://localhost:8000/health
# Or curl:
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "config": {
    "use_mock_data": true,
    "llm_model": "gpt-4o-mini"
  }
}
```

---

### 3. Start Frontend Server

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

**Expected Output:**
```
- ready started server on 0.0.0.0:3000
- Local: http://localhost:3000
```

#### Open in Browser
Navigate to: **http://localhost:3000**

You should see:
- ✅ TruthHire heading
- ✅ "AI-Powered Candidate Verification" subtitle
- ✅ Resume upload area (drag-drop)
- ✅ GitHub Username input field
- ✅ "Start Verification" button

---

## What to Test - Manual Testing Checklist

### Test 1: Upload Form Validation ✅

**Steps:**
1. Open http://localhost:3000
2. Click "Start Verification" WITHOUT selecting a file
3. **Expected:** Red error message "Please select a resume file"

**Result:** □ PASS / □ FAIL

---

### Test 2: File Upload UI ✅

**Steps:**
1. Click the file upload area
2. Select a PDF file (create a dummy PDF if needed)
3. **Expected:** 
   - File name appears below upload area
   - "Start Verification" button becomes enabled

**Result:** □ PASS / □ FAIL

---

### Test 3: API Connection Test ✅

**Backend must be running on port 8000**

**Steps:**
1. Select a PDF file
2. (Optional) Enter a GitHub username like "torvalds"
3. Click "Start Verification"
4. **Expected:**
   - Button shows spinner and "Starting Verification..."
   - After 1-3 seconds, redirects to `/verify/[id]` page

**Result:** □ PASS / □ FAIL

---

### Test 4: Verification Progress Page ✅

**After upload, you should be on `/verify/[id]` page**

**Expected to See:**
- ✅ "Verification in Progress" heading
- ✅ "Our AI agents are analyzing the candidate..." subtitle
- ✅ If no workflow yet: "Initializing verification..." message

**Note:** In Wave 2, agent steps won't appear yet because Wave 3 (orchestration) isn't implemented. This is expected!

**Result:** □ PASS / □ FAIL

---

### Test 5: Report Page (Manual Access) ✅

**Steps:**
1. Get verification ID from URL (e.g., `/verify/abc-123`)
2. Manually navigate to: `http://localhost:3000/report/abc-123`
3. **Expected:**
   - Shows "Loading report..." OR
   - Shows "Report not found or still processing"

**Why?** No verification results yet because Wave 3 workflow isn't running.

**Result:** □ PASS / □ FAIL

---

## Backend API Testing (curl/Postman)

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

**Expected:** `{"status":"healthy", ...}`

---

### Test 2: Upload Resume
```bash
# Create a dummy PDF first or use existing
curl -X POST http://localhost:8000/api/v1/verify \
  -F "resume=@path/to/resume.pdf" \
  -F "github_username=torvalds"
```

**Expected Response:**
```json
{
  "verification_id": "uuid-here",
  "status": "processing",
  "message": "Verification started",
  "created_at": "2025-11-08T..."
}
```

**Copy the `verification_id` for next tests!**

---

### Test 3: Get Verification Status
```bash
curl http://localhost:8000/api/v1/verify/YOUR_VERIFICATION_ID
```

**Expected Response:**
```json
{
  "id": "uuid",
  "candidate_name": "Name from Resume",
  "status": "processing",
  "parsed_data": { ... },
  ...
}
```

---

### Test 4: Get Agent Steps
```bash
curl http://localhost:8000/api/v1/verify/YOUR_VERIFICATION_ID/steps
```

**Expected Response:**
```json
{
  "steps": []
}
```

**Note:** Empty array is expected in Wave 2 - agents don't run yet!

---

## Known Behavior (Expected in Wave 2)

### ✅ What SHOULD Work:
1. ✅ Frontend renders all 3 pages
2. ✅ File upload form validates input
3. ✅ POST /api/v1/verify creates verification record
4. ✅ Resume gets parsed into structured data
5. ✅ Verification record saved in Supabase
6. ✅ Frontend redirects to progress page
7. ✅ All backend tests pass

### ⚠️ What WON'T Work Yet (Wave 3):
1. ❌ Agent steps don't appear in real-time
2. ❌ Verification status stays "processing" forever
3. ❌ No fraud detection results
4. ❌ Report page shows "not found"
5. ❌ No GitHub analysis runs
6. ❌ No mock reference generation

**This is EXPECTED!** Wave 3 implements the orchestration workflow.

---

## Troubleshooting

### Backend won't start
**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

---

### Frontend won't build
**Error:** `Cannot find module 'lucide-react'`

**Solution:**
```bash
cd frontend
npm install
```

---

### CORS Error in Browser
**Error:** `Access to fetch ... has been blocked by CORS policy`

**Solution:** Check backend is running on port 8000 and allows `localhost:3000`:
```python
# In backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ← Must match frontend URL
    ...
)
```

---

### File Upload Returns 500 Error

**Check:**
1. ✅ OpenAI API key in `.env`
2. ✅ Supabase credentials in `.env`
3. ✅ Supabase Storage bucket "resumes" created
4. ✅ Backend console for error details

**Common Issue:** Missing OpenAI API key
```bash
# In .env file
OPENAI_API_KEY=sk-...  # ← Must be set
```

---

## Success Criteria - Wave 2 Complete ✅

Check all that apply:

### Backend
- [ ] `python backend\quick_test.py` shows ALL TESTS PASSED
- [ ] Backend starts without errors: `uvicorn main:app`
- [ ] Health endpoint returns 200: `curl localhost:8000/health`
- [ ] Can upload resume via curl
- [ ] Fraud detector tests pass

### Frontend
- [ ] Frontend builds: `npm run build` (no errors)
- [ ] Frontend starts: `npm run dev`
- [ ] Upload page renders correctly
- [ ] File validation works
- [ ] Can select and upload file
- [ ] Redirects to `/verify/[id]` after upload

### Integration
- [ ] File upload creates Supabase record
- [ ] Resume gets parsed (check parsed_data in DB)
- [ ] No CORS errors in browser console

---

## Next Steps

Once ALL Wave 2 tests pass:

✅ **You're ready for Wave 3: Orchestration**

Wave 3 will add:
1. LangGraph workflow orchestrator
2. Background task processing
3. Real-time agent progress updates
4. Complete fraud detection flow
5. Report generation

**Estimated Time:** 4-6 hours for Wave 3 implementation

---

## Quick Reference - All Commands

```bash
# Backend Tests
python backend\quick_test.py
python backend\test_fraud_detector.py
python backend\test_github_api.py

# Start Servers
cd backend && python -m uvicorn main:app --reload
cd frontend && npm run dev

# Build Frontend
cd frontend && npm run build

# API Tests
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/verify -F "resume=@resume.pdf"
```

---

**Last Updated:** 2025-11-08  
**Wave Status:** Wave 2 Complete, Ready for Wave 3
