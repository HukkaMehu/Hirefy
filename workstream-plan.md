# TruthHire MVP - Parallel Workstream Plan
**24-Hour Hackathon Build Strategy**

---

## Team Structure (Recommended)

### Option A: 3-Person Team
- **Person 1:** Frontend + UI/UX
- **Person 2:** Backend + Agent Orchestration
- **Person 3:** Data Layer + Integration

### Option B: 2-Person Team
- **Person 1:** Full Frontend + Supabase Setup
- **Person 2:** Full Backend + Agents + Integration

### Option C: Solo (You + AI Agents)
- **You:** Orchestration + Critical Path + Demo
- **AI Agents:** Parallel implementation tasks

---

## Dependency Analysis

### Critical Path (Must be Sequential)
1. **Hour 0-1:** Supabase setup (blocks everything)
2. **Hour 1-3:** Database schema + basic API (blocks frontend)
3. **Hour 18-22:** Integration + End-to-End testing
4. **Hour 22-24:** Demo polish + pitch prep

### Parallel Workstreams (Can Run Simultaneously After Hour 1)

```
Hour 0-1: SETUP PHASE (Sequential)
    └─ Supabase project + DB schema

Hour 1-18: PARALLEL BUILD PHASE
    ├─ Stream A: Frontend Components
    ├─ Stream B: Backend Agents
    ├─ Stream C: Mock Data + GitHub API
    └─ Stream D: Fraud Detection Logic

Hour 18-22: INTEGRATION PHASE
    └─ Wire everything together

Hour 22-24: DEMO PHASE
    └─ Polish + practice pitch
```

---

## Workstream Breakdown (AI Agent Tasks)

### 🟦 Stream A: Frontend Development
**Dependencies:** Supabase credentials, API schema  
**Parallelizable:** Yes (independent components)  
**Estimated Time:** 6 hours

**Subtasks:**
1. **A1: Next.js Project Setup** (30 mins)
   - Initialize Next.js 14 with TypeScript
   - Install dependencies: Tailwind, shadcn/ui, Supabase client
   - Set up environment variables

2. **A2: Supabase Client Setup** (20 mins)
   - Create `lib/supabase.ts` with client initialization
   - Test connection to database

3. **A3: Resume Upload Page** (1.5 hours)
   - File upload component
   - Form validation
   - API integration (POST `/api/v1/verify`)
   - Loading states

4. **A4: Real-Time Progress Page** (2 hours)
   - Supabase Realtime subscription
   - Agent step cards with status icons
   - Progress visualization
   - Auto-redirect when complete

5. **A5: Report Display Page** (1.5 hours)
   - Risk badge component
   - Fraud flags display
   - Narrative summary
   - Interview questions section

6. **A6: PDF Export** (30 mins)
   - PDF generation from report data
   - Download button

**AI Agent Command:**
```
Create Next.js frontend with:
- Resume upload page (app/page.tsx)
- Real-time verification progress (app/verify/[id]/page.tsx)
- Report display (app/report/[id]/page.tsx)
- Supabase Realtime integration
- Tailwind + shadcn/ui styling
Use environment variables from .env.local
```

---

### 🟩 Stream B: Backend API + Orchestration
**Dependencies:** Supabase credentials, database schema  
**Parallelizable:** Yes (after API structure defined)  
**Estimated Time:** 8 hours

**Subtasks:**
1. **B1: FastAPI Project Setup** (30 mins)
   - Initialize FastAPI project structure
   - Install dependencies: FastAPI, supabase-py, pydantic-settings
   - Create config.py with environment loading

2. **B2: Supabase Client + Database Helpers** (45 mins)
   - Create `services/supabase_client.py`
   - Helper functions for DB writes
   - Test connection

3. **B3: API Routes (Skeleton)** (1 hour)
   - `POST /api/v1/verify` (resume upload endpoint)
   - `GET /api/v1/verify/{id}` (get report)
   - `GET /api/v1/verify/{id}/steps` (get progress)
   - `GET /health` (health check)
   - Pydantic schemas in `schemas.py`

4. **B4: Resume Parser Service** (1.5 hours)
   - PDF text extraction (pdfplumber)
   - GPT-4 structured extraction
   - Test with sample resumes

5. **B5: LangGraph Orchestrator** (2 hours)
   - Define VerificationState TypedDict
   - Create state machine graph
   - Wire agent nodes
   - Add edge transitions

6. **B6: Agent Progress Logging** (45 mins)
   - `update_agent_progress()` function
   - Write to `verification_steps` table
   - Test Realtime updates

7. **B7: Background Task Execution** (30 mins)
   - FastAPI BackgroundTasks integration
   - Error handling + status updates

**AI Agent Command:**
```
Create FastAPI backend with:
- main.py with API routes
- config.py for environment management
- LangGraph orchestrator in agents/orchestrator.py
- Resume parser using pdfplumber + GPT-4
- Supabase client integration
- Background task execution
Follow schemas in technical-requirements-mvp.md
```

---

### 🟨 Stream C: GitHub API + Mock Data
**Dependencies:** None (fully independent)  
**Parallelizable:** Yes  
**Estimated Time:** 4 hours

**Subtasks:**
1. **C1: GitHub API Client** (2 hours)
   - Create `services/github_api.py`
   - Implement profile fetching
   - Repository analysis (languages, commits)
   - Activity timeline extraction
   - Error handling for rate limits

2. **C2: Mock Data Files** (1 hour)
   - `mocks/reference_templates.json`
   - `mocks/fraud_scenarios.json`
   - `mocks/education_verifications.json`
   - `mocks/employment_verifications.json`

3. **C3: Mock Data Loader** (45 mins)
   - `services/mock_loader.py`
   - `get_weighted_reference_response()`
   - `inject_fraud_scenario()`
   - Test weighted distribution

4. **C4: Reference Discovery Generator** (15 mins)
   - Generate 50-100 realistic fake coworkers
   - Use Faker library for names, titles

**AI Agent Command:**
```
Create two services:
1. GitHub API client (services/github_api.py):
   - Fetch user profile
   - Analyze repositories (languages, commits, stars)
   - Extract activity timeline
   - Handle rate limits

2. Mock data system (mocks/*.json + services/mock_loader.py):
   - JSON templates for references, fraud scenarios
   - Weighted random selection
   - Loader functions with caching

Follow schemas in technical-requirements-mvp.md
```

---

### 🟥 Stream D: Fraud Detection Engine
**Dependencies:** None (can mock inputs)  
**Parallelizable:** Yes  
**Estimated Time:** 4 hours

**Subtasks:**
1. **D1: Fraud Detector Class** (2 hours)
   - Create `agents/fraud_detector.py`
   - FraudFlag dataclass
   - Pluggable rule architecture
   - Risk level calculation logic

2. **D2: Detection Rules** (1.5 hours)
   - `_check_github_consistency()` (skill mismatch)
   - `_check_employment_timeline()` (gaps)
   - `_check_title_consistency()` (inflation)
   - `_check_education_verification()` (fake degrees)
   - `_check_reference_sentiment()` (negative patterns)

3. **D3: Unit Tests** (30 mins)
   - Test each rule with mock data
   - Verify risk level calculation
   - Edge case handling

**AI Agent Command:**
```
Create fraud detection engine (agents/fraud_detector.py):
- FraudDetector class with pluggable rules
- Implement 5 detection rules:
  1. GitHub consistency (skills match languages)
  2. Employment timeline (detect gaps)
  3. Title consistency (detect inflation)
  4. Education verification (fake credentials)
  5. Reference sentiment (negative patterns)
- Risk level calculation (green/yellow/red)
- Return structured FraudFlag objects

Follow exact specifications in technical-requirements-mvp.md
```

---

### 🟪 Stream E: Agent Implementations
**Dependencies:** Orchestrator structure (B5)  
**Parallelizable:** Yes (after orchestrator skeleton)  
**Estimated Time:** 5 hours

**Subtasks:**
1. **E1: Agent 1 - Resume Parser** (30 mins)
   - Already done in B4, wrap in agent function
   - Add progress logging

2. **E2: Agent 2 - Reference Discovery** (1 hour)
   - Generate mock coworkers
   - Simulate outreach (20% response rate)
   - Generate mock responses using templates

3. **E3: Agent 3 - GitHub Analyzer** (30 mins)
   - Call GitHub API service
   - Add progress logging
   - Handle missing usernames gracefully

4. **E4: Agent 4 - Fraud Detector** (30 mins)
   - Call FraudDetector class
   - Pass all verification data
   - Add progress logging

5. **E5: Agent 5 - Report Synthesizer** (2 hours)
   - Generate narrative summary with GPT-4
   - Generate interview questions from flags
   - Compile final report JSON
   - Update database with result

**AI Agent Command:**
```
Create 5 agent functions for LangGraph (agents/):
1. parser_agent.py - Resume parsing (uses B4 service)
2. discovery_agent.py - Generate mock references + responses
3. github_agent.py - Real GitHub API analysis (uses C1)
4. fraud_detector_agent.py - Run fraud detection (uses D1)
5. report_agent.py - GPT-4 narrative + interview questions

Each agent:
- Takes VerificationState as input
- Updates state with results
- Logs progress to verification_steps table
- Returns updated state

Follow LangGraph patterns from technical-requirements-mvp.md
```

---

### 🟧 Stream F: Demo Data + Testing
**Dependencies:** Complete system  
**Parallelizable:** Partially  
**Estimated Time:** 2 hours

**Subtasks:**
1. **F1: Demo Resume PDFs** (1 hour)
   - Create 3 realistic resumes:
     - `candidate_green.pdf` (clean, no issues)
     - `candidate_yellow.pdf` (minor concerns)
     - `candidate_red.pdf` (major fraud flags)
   - Include different GitHub usernames

2. **F2: End-to-End Test** (30 mins)
   - Upload each resume
   - Verify real-time updates work
   - Check final reports

3. **F3: Demo Script** (30 mins)
   - 90-second pitch outline
   - Key talking points
   - Backup screenshots/video

**Manual Task (You):**
Create 3 demo resumes with varying fraud scenarios

---

## Hour-by-Hour Schedule

### Hour 0-1: Foundation (You + Agent)
**You:**
- [ ] Create Supabase project
- [ ] Copy credentials to `.env` files
- [ ] Run database migrations

**AI Agent:**
- [ ] Initialize Next.js project (A1)
- [ ] Initialize FastAPI project (B1)

### Hour 1-6: Parallel Build Sprint 1
**AI Agent 1 (Frontend):**
- [ ] A2: Supabase client setup
- [ ] A3: Resume upload page
- [ ] A4: Real-time progress page

**AI Agent 2 (Backend Core):**
- [ ] B2: Supabase client + helpers
- [ ] B3: API routes skeleton
- [ ] B4: Resume parser service

**AI Agent 3 (Data Layer):**
- [ ] C1: GitHub API client
- [ ] C2: Mock data JSON files
- [ ] C3: Mock data loader

**AI Agent 4 (Fraud Detection):**
- [ ] D1: Fraud detector class
- [ ] D2: All 5 detection rules

### Hour 6-12: Parallel Build Sprint 2
**AI Agent 1 (Frontend):**
- [ ] A5: Report display page
- [ ] A6: PDF export

**AI Agent 2 (Backend Orchestration):**
- [ ] B5: LangGraph orchestrator
- [ ] B6: Agent progress logging
- [ ] B7: Background tasks

**AI Agent 5 (Agents):**
- [ ] E1-E5: Implement all 5 agent functions

**You:**
- [ ] Review AI agent outputs
- [ ] Fix integration issues
- [ ] Test individual components

### Hour 12-18: Integration + Polish
**You + AI Agents:**
- [ ] Wire frontend ↔ backend
- [ ] Test Realtime updates
- [ ] Debug API calls
- [ ] Fix CORS issues
- [ ] Style improvements

### Hour 18-20: End-to-End Testing
**You:**
- [ ] Create demo resumes (F1)
- [ ] Run full verification flow 3x
- [ ] Fix critical bugs
- [ ] Verify all features work

### Hour 20-22: Demo Prep
**You:**
- [ ] Record backup demo video
- [ ] Practice 90-second pitch
- [ ] Prepare judge Q&A answers
- [ ] Screenshot key features

### Hour 22-24: Buffer + Sleep
- [ ] Final bug fixes
- [ ] Deploy to Vercel/Railway (optional)
- [ ] Sleep before presentation

---

## AI Agent Coordination Strategy

### Sequential Dependencies
```
1. Supabase setup (YOU) 
   └─> All agents can start

2. API schema defined (B3)
   └─> Frontend can call APIs (A3, A4, A5)

3. Orchestrator structure (B5)
   └─> Agent implementations (E1-E5)

4. All components done
   └─> Integration testing (You)
```

### Independent Work (Can Run in Parallel)
- Frontend UI components (A1-A6)
- GitHub API client (C1)
- Mock data system (C2-C4)
- Fraud detection engine (D1-D3)
- Individual agent logic (E1-E5) [after B5]

---

## AI Agent Invocation Commands

### Round 1: Foundation (Hour 0-1)
```bash
# Agent 1: Initialize frontend
spawn_subagent("Frontend project setup", """
Create Next.js 14 project with TypeScript, Tailwind, shadcn/ui.
Install: @supabase/supabase-js, react-pdf
Create lib/supabase.ts with client setup
Create .env.local template
""", "general")

# Agent 2: Initialize backend
spawn_subagent("Backend project setup", """
Create FastAPI project structure:
- main.py with FastAPI app
- config.py with pydantic-settings
- requirements.txt with: fastapi, uvicorn, supabase, langchain, langgraph, pdfplumber, openai
- .env template
Create folder structure: agents/, services/, mocks/
""", "general")
```

### Round 2: Core Services (Hour 1-6)
```bash
# Agent 3: GitHub API + Mock Data
spawn_subagent("GitHub API and Mock Data", """
Create services/github_api.py:
- analyze_github_profile(username) function
- Return profile, repos, languages, commits, activity
- Use PyGithub or requests
- Handle rate limits gracefully

Create mocks/ JSON files:
- reference_templates.json (3 templates: strong/solid/concerns)
- fraud_scenarios.json (5 scenarios from tech requirements)

Create services/mock_loader.py:
- load_reference_templates() cached loader
- get_weighted_reference_response() with 60/30/10 distribution
""", "general")

# Agent 4: Fraud Detection Engine
spawn_subagent("Fraud Detection Engine", """
Create agents/fraud_detector.py following EXACT spec from technical-requirements-mvp.md:
- FraudFlag dataclass
- FraudDetector class with 5 rules:
  1. _check_github_consistency (skill/language mismatch)
  2. _check_employment_timeline (gaps >6mo)
  3. _check_title_consistency (inflation detection)
  4. _check_education_verification (fake credentials)
  5. _check_reference_sentiment (negative patterns)
- _calculate_risk_level (green/yellow/red logic)
- _generate_summary
Include all helper functions (_calculate_gap_months, etc.)
""", "general")

# Agent 5: Frontend Pages
spawn_subagent("Frontend UI Pages", """
Create 3 Next.js pages using Tailwind + shadcn/ui:

1. app/page.tsx (Resume Upload):
   - File upload component (PDF only)
   - GitHub username input (optional)
   - Submit → POST /api/v1/verify
   - Redirect to /verify/[id] on success

2. app/verify/[id]/page.tsx (Real-time Progress):
   - Supabase Realtime subscription to verification_steps table
   - Display agent step cards (agent name, status icon, message, timestamp)
   - Auto-redirect to /report/[id] when status=complete

3. app/report/[id]/page.tsx (Report Display):
   - Fetch from GET /api/v1/verify/{id}
   - Risk badge (green/yellow/red)
   - Fraud flags list
   - Narrative summary
   - Interview questions
   - Download PDF button

Use TypeScript, proper error handling, loading states.
""", "general")

# Agent 6: Backend API + Resume Parser
spawn_subagent("Backend API and Resume Parser", """
Create FastAPI backend following technical-requirements-mvp.md:

1. main.py:
   - POST /api/v1/verify (upload resume → Supabase Storage → parse → start workflow)
   - GET /api/v1/verify/{id} (return report)
   - GET /api/v1/verify/{id}/steps (return progress)
   - GET /health
   - Use Pydantic schemas from schemas.py

2. services/resume_parser.py:
   - extract_text_from_pdf(bytes) using pdfplumber
   - parse_with_llm(text) using GPT-4o-mini
   - Return structured JSON: {name, email, employment_history, education, skills, github_username}

3. services/supabase_client.py:
   - Helper function: update_agent_progress(vid, agent, status, msg, data)

Include proper error handling, type hints.
""", "general")
```

### Round 3: Agent Orchestration (Hour 6-12)
```bash
# Agent 7: LangGraph Orchestrator + All Agents
spawn_subagent("LangGraph Orchestrator and Agent Implementations", """
Create agent orchestration system following technical-requirements-mvp.md:

1. agents/orchestrator.py:
   - VerificationState TypedDict
   - StateGraph with 5 nodes: parse → discover → github → fraud → report
   - run_verification(verification_id, parsed, github_username) function

2. agents/parser_agent.py:
   - parse_resume(state) - calls resume_parser service
   - Logs progress to DB

3. agents/discovery_agent.py:
   - discover_references(state) - generates 50-100 mock coworkers
   - simulate_outreach(state) - 20% response rate
   - Uses mock_loader.get_weighted_reference_response()

4. agents/github_agent.py:
   - analyze_github(state) - calls github_api service
   - Gracefully handles missing username

5. agents/fraud_detector_agent.py:
   - detect_fraud(state) - calls FraudDetector class
   - Passes resume, github, references

6. agents/report_agent.py:
   - synthesize_report(state) - GPT-4 narrative + interview questions
   - Compiles final report JSON
   - Updates verifications table with result

Each agent logs progress via update_agent_progress().
""", "general")
```

---

## Risk Mitigation

### Critical Risks
1. **Supabase Realtime not working**
   - Fallback: Polling every 2 seconds
   - Test early (Hour 2)

2. **GitHub API rate limits**
   - Use GITHUB_TOKEN (5000/hr limit)
   - Cache results in DB
   - Graceful fallback if down

3. **LangGraph complexity**
   - Fallback: Simple sequential execution
   - Test orchestrator early (Hour 8)

4. **GPT-4 latency**
   - Use gpt-4o-mini (faster)
   - Cache common prompts
   - Show "AI is thinking..." loaders

### Time Buffers
- Hour 12-18: 6-hour integration buffer
- Hour 22-24: 2-hour final polish buffer

---

## Success Checklist

### Minimum Viable Demo (Must-Have by Hour 18)
- [ ] Upload resume → stored in Supabase
- [ ] See 5 agents run (fake or real)
- [ ] Display final report with risk score
- [ ] 1 fraud scenario works end-to-end

### Full Feature Set (Goal by Hour 20)
- [ ] Real-time agent progress updates
- [ ] GitHub API pulling real data
- [ ] Fraud detection catching 2+ scenarios
- [ ] Professional UI with Tailwind styling
- [ ] Can demo 3 different outcomes (green/yellow/red)

### Stretch Goals (If time)
- [ ] PDF export
- [ ] Deploy to Vercel/Railway
- [ ] Backup demo video
- [ ] Animated transitions

---

## Decision: How to Execute

### Recommended Approach (Solo with AI Agents)

**You handle:**
1. Supabase project setup (15 mins)
2. Review AI agent outputs (continuous)
3. Integration + debugging (Hour 12-18)
4. Demo prep (Hour 20-22)

**AI Agents handle:**
1. All code generation (parallel)
2. Following exact specs from technical-requirements-mvp.md
3. Individual component testing

**Execution:**
```bash
# Hour 0: Setup
1. Create Supabase project manually
2. Copy credentials to .env

# Hour 0-1: Launch parallel agents
spawn 6 AI agents (commands above)

# Hour 6-8: Review + integrate agent outputs
3. Test each component
4. Fix integration issues

# Hour 8-12: Launch orchestration agents
spawn agent 7 (LangGraph + agents)

# Hour 12-18: Integration sprint
5. Wire everything together
6. End-to-end testing

# Hour 18-22: Demo prep
7. Create demo resumes
8. Practice pitch
```

---

**Ready to start? Confirm workstream strategy and I'll begin spawning agents!**
