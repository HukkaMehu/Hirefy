# TruthHire MVP - Technical Requirements (Agile Version)
**Multi-Agent AI Verification Platform**

**Build Target:** 24-hour hackathon  
**Demo Duration:** 90 seconds  
**Architecture:** Designed for rapid iteration and post-MVP scaling  

---

## Executive Summary

An AI agent system that verifies job candidates by cross-referencing resume claims against GitHub profiles, mock reference checks, and credential verification. Built on a **modular, database-backed architecture** that enables easy feature additions without rewrites.

**Core Innovation:** Multi-source fraud detection through coordinated AI agents + real-time verification visibility.

---

## Product Scope

### IN SCOPE (MVP) ✅

1. **Resume upload & parsing** (PDF/DOCX → structured JSON)
2. **Multi-source reference discovery** (generate 50-100 realistic mock former coworkers)
3. **GitHub analysis** (REAL - commits, languages, activity timeline via GitHub API)
4. **Fraud detection engine** (cross-reference resume vs GitHub vs verifications)
5. **5-Agent LangGraph orchestration** (state machine with visible workflow)
6. **Real-time progress UI** (Supabase Realtime WebSocket updates)
7. **Risk scoring** (Green/Yellow/Red with specific flags)
8. **Interview question generation** (GPT-4 based on discovered red flags)
9. **Professional web report** (+ downloadable PDF)
10. **Verification history** (last 10 runs persisted in database)

### OUT OF SCOPE (Post-MVP) ❌

- ❌ Real NSC/Work Number API (use JSON mock data)
- ❌ Actual email sending (simulate outreach flow)
- ❌ LinkedIn scraping (REMOVED - use mock data generator)
- ❌ User authentication (Supabase Auth ready but not wired)
- ❌ Payment processing
- ❌ ATS integrations
- ❌ SMS/Voice agents (stubs present, partner integration later)

**Why this scope:** Impressive demo with real GitHub analysis + agent coordination, while keeping infrastructure simple and extensible.

---

## System Architecture

### High-Level Flow

```
┌──────────────────────────────────────────────┐
│         Next.js Frontend (TypeScript)        │
│  - Resume upload (Supabase Storage)          │
│  - Real-time agent progress (Supabase WS)    │
│  - Report display + PDF export               │
└────────┬─────────────────────────────────┬──┘
         │                                  │
         │ REST API                         │ WebSocket
         ↓                                  ↓
┌─────────────────┐              ┌──────────────────────┐
│  FastAPI Backend│◄────────────►│  Supabase Cloud      │
│  - API routes   │              │  - Postgres DB       │
│  - Agent orch.  │              │  - Realtime channels │
│  - Config mgmt  │              │  - File storage      │
└────────┬────────┘              │  - Auth (future)     │
         │                        └──────────────────────┘
         ↓                                  ▲
┌─────────────────────────────────────────┐│
│    5-Agent System (LangGraph)           ││
├─────────────────────────────────────────┤│
│  Agent 1: Resume Parser                 ││ MCP
│  Agent 2: Reference Discovery           ││ (Agents write
│  Agent 3: GitHub Analyzer (REAL)        ││  progress via
│  Agent 4: Fraud Detector                ││  Supabase MCP)
│  Agent 5: Report Synthesizer            ││
└─────────────────────────────────────────┘│
         │                                  │
         ↓                                  │
┌─────────────────────────────────────────┴┘
│       External Services                   
├──────────────────────────────────────────
│  - OpenAI GPT-4o-mini (LLM)              
│  - GitHub REST API (real data)           
│  - Mock data (backend/mocks/*.json)      
└──────────────────────────────────────────
```

### Key Architectural Decisions (for Agility)

| Decision | Rationale | Post-MVP Benefit |
|----------|-----------|------------------|
| **Supabase DB** | Persistent storage + realtime + auth ready | Easy to add user accounts, history, caching |
| **LangGraph state machine** | Agents as modular nodes | Add/remove agents without rewriting orchestration |
| **JSON mock configs** | Externalized test data | Non-technical team can edit scenarios |
| **Environment-based config** | `.env` for all keys/flags | Swap mock → real APIs via one flag |
| **Versioned API schemas** | Pydantic models with versions | Breaking changes won't break frontend |
| **MCP for DB writes** | Agents write directly to Supabase | Less backend boilerplate, cleaner logs |

---

## Technical Stack

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Components:** shadcn/ui
- **Database Client:** @supabase/supabase-js
- **PDF Export:** react-pdf or jsPDF
- **State:** React hooks (minimal state, rely on DB)

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Agent Framework:** LangChain + LangGraph
- **LLM:** OpenAI GPT-4o-mini
- **Database Client:** supabase-py
- **Resume Parsing:** pdfplumber
- **GitHub API:** PyGithub
- **Config:** pydantic-settings
- **Mock Data:** JSON files + Faker library

### Database & Storage
- **Platform:** Supabase (managed Postgres + Realtime + Storage + Auth)
- **Tables:** `verifications`, `verification_steps`, `mock_references`
- **Storage:** `resumes` bucket (S3-compatible)
- **MCP:** Supabase MCP server for agent-DB communication

### Infrastructure
- **Local Dev:** FastAPI (localhost:8000) + Next.js (localhost:3000) + Supabase Cloud
- **Deployment:** Vercel (frontend) + Railway (backend) + Supabase (database)
- **Environment Config:** `.env` files for all secrets and feature flags

---

## Database Schema

### Supabase Postgres Tables

```sql
-- verifications: Main verification records
CREATE TABLE verifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  candidate_name TEXT NOT NULL,
  candidate_email TEXT,
  github_username TEXT,
  status TEXT NOT NULL DEFAULT 'processing', -- 'processing' | 'complete' | 'failed'
  risk_score TEXT, -- 'green' | 'yellow' | 'red'
  resume_url TEXT, -- Supabase Storage URL
  parsed_data JSONB, -- Structured resume output
  result JSONB, -- Full verification result
  created_at TIMESTAMPTZ DEFAULT NOW(),
  completed_at TIMESTAMPTZ
);

-- verification_steps: Real-time agent progress
CREATE TABLE verification_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  verification_id UUID REFERENCES verifications(id) ON DELETE CASCADE,
  agent_name TEXT NOT NULL, -- 'Resume Parser' | 'GitHub Analyzer' | etc.
  status TEXT NOT NULL, -- 'running' | 'complete' | 'failed'
  message TEXT, -- "Analyzed 23 repositories, found 547 commits"
  data JSONB, -- Agent-specific structured output
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_steps_vid_created ON verification_steps(verification_id, created_at DESC);

-- Supabase Realtime: Enable live updates
ALTER PUBLICATION supabase_realtime ADD TABLE verification_steps;
```

### Supabase Storage Buckets

```sql
-- Resume uploads (private)
CREATE BUCKET resumes (
  public = false,
  file_size_limit = 5242880, -- 5MB
  allowed_mime_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
);
```

---

## Configuration Management

### Environment Variables

**Backend `.env`:**
```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...  # Public key (safe for frontend)
SUPABASE_SERVICE_KEY=eyJ...  # Service role key (backend only)

# GitHub
GITHUB_TOKEN=ghp_...  # Optional, increases rate limit 60/hr → 5000/hr

# Feature Flags
USE_MOCK_DATA=true
FRAUD_DETECTION_STRICT_MODE=true

# LLM Config
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=4000

# Future: SMS/Voice Agents (partner integration)
COMM_AGENTS_ENABLED=false
COMM_AGENT_API_KEY=
COMM_AGENT_URL=http://localhost:9000
```

**Frontend `.env.local`:**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Config Module (backend/config.py)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    supabase_url: str
    supabase_anon_key: str
    supabase_service_key: str
    github_token: str | None = None
    
    # Feature Flags
    use_mock_data: bool = True
    fraud_detection_strict: bool = True
    comm_agents_enabled: bool = False
    
    # LLM Config (easy to swap models)
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4000
    
    # External Services
    comm_agent_api_key: str | None = None
    comm_agent_url: str = "http://localhost:9000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**Usage:**
```python
from config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

# Easy to change LLM model via env var
llm = ChatOpenAI(model=settings.llm_model, temperature=settings.llm_temperature)
```

---

## Mock Data Strategy (Externalized)

### File Structure

```
backend/
  mocks/
    reference_templates.json     # Realistic reference response patterns
    fraud_scenarios.json          # Pre-defined fraud cases
    education_verifications.json  # Mock NSC responses
    employment_verifications.json # Mock Work Number responses
```

### reference_templates.json

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
        "Architected our microservices migration"
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
        "Fixed critical security vulnerability in auth system"
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
        "Delivered features but often late and over budget"
      ],
      "weight": 0.1
    }
  ]
}
```

### fraud_scenarios.json

```json
{
  "scenarios": [
    {
      "id": "fake_github_activity",
      "resume_claim": "Prolific open source contributor, 1000+ commits across multiple projects",
      "github_reality": "Account exists but only 47 total commits, last activity 2 years ago",
      "detection_rule": "github_commit_mismatch",
      "severity": "red"
    },
    {
      "id": "title_inflation",
      "resume_claim": "Senior Engineering Manager",
      "verification_reality": "Employment verified as: Junior Developer",
      "detection_rule": "title_mismatch",
      "severity": "red"
    },
    {
      "id": "fake_education",
      "resume_claim": "BS Computer Science, Stanford University, 2018",
      "nsc_reality": "No record found",
      "detection_rule": "education_unverified",
      "severity": "red"
    },
    {
      "id": "skill_exaggeration",
      "resume_claim": "Expert Python developer with 5 years experience",
      "github_reality": "GitHub shows 0 Python repositories, only JavaScript",
      "detection_rule": "skill_language_mismatch",
      "severity": "yellow"
    },
    {
      "id": "employment_gap",
      "resume_claim": "Continuous employment 2018-2024",
      "reality": "8-month unexplained gap in 2021",
      "detection_rule": "timeline_gap",
      "severity": "yellow"
    }
  ]
}
```

### Mock Data Loader (backend/services/mock_loader.py)

```python
import json
from pathlib import Path
from functools import lru_cache
import random

MOCKS_DIR = Path(__file__).parent.parent / "mocks"

@lru_cache()
def load_reference_templates() -> dict:
    with open(MOCKS_DIR / "reference_templates.json") as f:
        return json.load(f)

@lru_cache()
def load_fraud_scenarios() -> dict:
    with open(MOCKS_DIR / "fraud_scenarios.json") as f:
        return json.load(f)

def get_weighted_reference_response() -> dict:
    """Returns realistic reference response based on weighted distribution"""
    templates = load_reference_templates()["templates"]
    
    # Weight distribution: 60% strong, 30% solid, 10% concerns
    weights = [t["weight"] for t in templates]
    selected = random.choices(templates, weights=weights)[0]
    
    return {
        "performance_rating": selected["performance_rating"],
        "strengths": selected["strengths"],
        "weaknesses": selected["weaknesses"],
        "would_rehire": selected["would_rehire"],
        "specific_example": random.choice(selected["examples"])
    }

def inject_fraud_scenario(verification_data: dict, scenario_id: str) -> dict:
    """Inject a specific fraud scenario for demo purposes"""
    scenarios = load_fraud_scenarios()["scenarios"]
    scenario = next(s for s in scenarios if s["id"] == scenario_id)
    
    # Modify verification data to trigger fraud detection
    # Implementation depends on scenario type
    return modified_data
```

**Why externalize mocks:**
- Non-developers can edit scenarios for testing
- Easy to A/B test fraud detection rules
- Demo team can add new edge cases without touching code
- JSON files can be version-controlled separately

---

## Agent Orchestration (LangGraph State Machine)

### Why LangGraph Over Procedural

**Before (Procedural - Brittle):**
```python
# Hard to modify, hard to test individual agents
async def run_verification(parsed, github_username):
    refs = await agent1_discover_references(parsed)
    outreach = await agent2_simulate_outreach(refs)
    github = await agent3_analyze_github(github_username)
    fraud = await agent4_detect_fraud(parsed, github, outreach)
    report = await agent5_synthesize_report(fraud)
    return report
```

**After (LangGraph - Modular):**
```python
# Easy to add/remove agents, easy to test, clear state transitions
from langgraph.graph import StateGraph, END

class VerificationState(TypedDict):
    verification_id: str
    parsed_resume: dict
    github_username: Optional[str]
    references: list
    outreach_results: dict
    github_analysis: dict
    fraud_results: dict
    final_report: dict
    current_step: str

# Define agent functions
async def parse_resume(state: VerificationState) -> VerificationState:
    # Agent 1 logic
    state["current_step"] = "parsing_complete"
    return state

async def discover_references(state: VerificationState) -> VerificationState:
    # Agent 2 logic
    state["references"] = generate_mock_references(state["parsed_resume"])
    state["current_step"] = "references_discovered"
    return state

async def analyze_github(state: VerificationState) -> VerificationState:
    if state["github_username"]:
        state["github_analysis"] = await real_github_api_call(state["github_username"])
    state["current_step"] = "github_analyzed"
    return state

async def detect_fraud(state: VerificationState) -> VerificationState:
    detector = FraudDetector()
    state["fraud_results"] = detector.analyze(
        state["parsed_resume"],
        state["github_analysis"],
        state["outreach_results"]
    )
    state["current_step"] = "fraud_detected"
    return state

async def synthesize_report(state: VerificationState) -> VerificationState:
    state["final_report"] = await generate_report_with_llm(state)
    state["current_step"] = "complete"
    return state

# Build state machine
workflow = StateGraph(VerificationState)

# Add nodes (agents)
workflow.add_node("parse", parse_resume)
workflow.add_node("discover", discover_references)
workflow.add_node("github", analyze_github)
workflow.add_node("fraud", detect_fraud)
workflow.add_node("report", synthesize_report)

# Define edges (flow)
workflow.set_entry_point("parse")
workflow.add_edge("parse", "discover")
workflow.add_edge("discover", "github")
workflow.add_edge("github", "fraud")
workflow.add_edge("fraud", "report")
workflow.add_edge("report", END)

# Compile
app = workflow.compile()

# Execute with state persistence
async def run_verification(verification_id: str, parsed: dict, github_username: str):
    initial_state = {
        "verification_id": verification_id,
        "parsed_resume": parsed,
        "github_username": github_username,
        "current_step": "started"
    }
    
    # LangGraph handles state transitions
    final_state = await app.ainvoke(initial_state)
    return final_state["final_report"]
```

**Benefits:**
- Add new agent = add one node + one edge
- Test agents in isolation
- Conditional branching (e.g., skip GitHub if no username)
- Built-in checkpointing for debugging
- Visualize workflow as graph

---

## Real-Time Progress Updates (Supabase Realtime)

### Backend: Agents Write Progress via MCP

```python
from supabase import create_client, Client
from config import get_settings

settings = get_settings()
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_key  # Service key for backend writes
)

async def update_agent_progress(
    verification_id: str,
    agent_name: str,
    status: str,
    message: str,
    data: dict = None
):
    """Write progress update that frontend will receive via WebSocket"""
    supabase.table("verification_steps").insert({
        "verification_id": verification_id,
        "agent_name": agent_name,
        "status": status,
        "message": message,
        "data": data
    }).execute()

# Usage in agents
async def analyze_github(state: VerificationState) -> VerificationState:
    await update_agent_progress(
        state["verification_id"],
        "GitHub Analyzer",
        "running",
        "Fetching profile and repositories..."
    )
    
    github_data = await fetch_github_profile(state["github_username"])
    
    await update_agent_progress(
        state["verification_id"],
        "GitHub Analyzer",
        "running",
        f"Analyzed {github_data['repositories']['total']} repositories, {github_data['activity']['total_commits']} commits"
    )
    
    state["github_analysis"] = github_data
    
    await update_agent_progress(
        state["verification_id"],
        "GitHub Analyzer",
        "complete",
        "GitHub analysis complete",
        data={"summary": github_data}
    )
    
    return state
```

### Frontend: Subscribe to Real-Time Updates

```typescript
// app/verify/[id]/page.tsx
import { createClient } from '@supabase/supabase-js'
import { useEffect, useState } from 'react'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export default function VerificationPage({ params }: { params: { id: string } }) {
  const [steps, setSteps] = useState<any[]>([])
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
          console.log('New step:', payload.new)
          setSteps(prev => [...prev, payload.new])
          
          // Check if all agents complete
          if (payload.new.agent_name === 'Report Synthesizer' && payload.new.status === 'complete') {
            setStatus('complete')
          }
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [params.id])

  return (
    <div className="max-w-4xl mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Verification in Progress</h1>
      
      <div className="space-y-4">
        {steps.map((step, idx) => (
          <AgentStepCard key={idx} step={step} />
        ))}
      </div>
      
      {status === 'complete' && (
        <Button onClick={() => router.push(`/report/${params.id}`)}>
          View Report
        </Button>
      )}
    </div>
  )
}

function AgentStepCard({ step }) {
  const statusIcons = {
    running: <Loader2 className="animate-spin" />,
    complete: <CheckCircle2 className="text-green-600" />,
    failed: <XCircle className="text-red-600" />
  }

  return (
    <div className="border rounded-lg p-4 flex items-start gap-4">
      {statusIcons[step.status]}
      <div className="flex-1">
        <h3 className="font-semibold">{step.agent_name}</h3>
        <p className="text-sm text-gray-600">{step.message}</p>
        <span className="text-xs text-gray-400">
          {new Date(step.created_at).toLocaleTimeString()}
        </span>
      </div>
    </div>
  )
}
```

**Demo Impact:**
- Judges see agents working in real-time
- Professional UI (not fake progress bars)
- Easy to debug (all steps logged in DB)

---

## Fraud Detection Engine

### Modular Detection Rules (backend/agents/fraud_detector.py)

```python
from typing import Literal
from dataclasses import dataclass

FraudLevel = Literal["green", "yellow", "red"]

@dataclass
class FraudFlag:
    type: str
    severity: str  # "low" | "medium" | "high" | "critical"
    message: str
    category: str
    evidence: dict

class FraudDetector:
    """
    Pluggable fraud detection rules
    Easy to add new rules without touching orchestration
    """
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.rules = [
            self._check_github_consistency,
            self._check_employment_timeline,
            self._check_title_consistency,
            self._check_education_verification,
            self._check_reference_sentiment,
            self._check_skill_verification
        ]
    
    def analyze(
        self,
        resume_data: dict,
        github_data: dict | None,
        reference_responses: list,
        education_verification: dict = None,
        employment_verification: dict = None
    ) -> dict:
        """Run all fraud detection rules"""
        
        all_flags = []
        
        # Run each rule
        for rule in self.rules:
            flags = rule(
                resume_data,
                github_data,
                reference_responses,
                education_verification,
                employment_verification
            )
            all_flags.extend(flags)
        
        # Calculate risk score
        risk_level = self._calculate_risk_level(all_flags)
        
        return {
            "risk_level": risk_level,
            "flags": all_flags,
            "flag_count": {
                "critical": len([f for f in all_flags if f.severity == "critical"]),
                "high": len([f for f in all_flags if f.severity == "high"]),
                "medium": len([f for f in all_flags if f.severity == "medium"]),
                "low": len([f for f in all_flags if f.severity == "low"])
            },
            "summary": self._generate_summary(risk_level, all_flags)
        }
    
    def _check_github_consistency(self, resume, github, *args) -> list[FraudFlag]:
        """Rule: Resume skills must match GitHub languages"""
        flags = []
        
        if not github or "error" in github:
            return flags
        
        resume_skills = [s.lower() for s in resume.get("skills", [])]
        github_langs = [lang.lower() for lang in github.get("repositories", {}).get("languages", {}).keys()]
        
        # Map framework → language
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
                        evidence={
                            "claimed_skill": skill,
                            "github_languages": github_langs
                        }
                    ))
        
        return flags
    
    def _check_employment_timeline(self, resume, *args) -> list[FraudFlag]:
        """Rule: Detect unexplained employment gaps > 6 months"""
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
    
    def _check_reference_sentiment(self, resume, github, references, *args) -> list[FraudFlag]:
        """Rule: Flag negative reference patterns"""
        flags = []
        
        if not references:
            return flags
        
        avg_rating = sum(r.get("performance_rating", 7) for r in references) / len(references)
        would_not_rehire = [r for r in references if not r.get("would_rehire", True)]
        
        if avg_rating < 6.5:
            flags.append(FraudFlag(
                type="low_performance_ratings",
                severity="high",
                message=f"Average reference rating {avg_rating:.1f}/10 (below threshold)",
                category="References",
                evidence={"avg_rating": avg_rating, "total_references": len(references)}
            ))
        
        if len(would_not_rehire) >= 2:
            flags.append(FraudFlag(
                type="rehire_concerns",
                severity="high",
                message=f"{len(would_not_rehire)} of {len(references)} references would NOT rehire",
                category="References",
                evidence={"would_not_rehire_count": len(would_not_rehire)}
            ))
        
        return flags
    
    def _calculate_risk_level(self, flags: list[FraudFlag]) -> FraudLevel:
        """Determine overall risk level"""
        
        # Any critical flag = RED
        if any(f.severity == "critical" for f in flags):
            return "red"
        
        # 2+ high severity = RED
        high_count = len([f for f in flags if f.severity == "high"])
        if high_count >= 2:
            return "red"
        
        # 1 high OR 3+ medium = YELLOW
        medium_count = len([f for f in flags if f.severity == "medium"])
        if high_count >= 1 or medium_count >= 3:
            return "yellow"
        
        # Otherwise GREEN
        return "green"
    
    def _generate_summary(self, risk_level: FraudLevel, flags: list[FraudFlag]) -> str:
        if risk_level == "green":
            return "Verification successful. All claims verified with no major concerns."
        
        critical_msgs = [f.message for f in flags if f.severity in ["critical", "high"]]
        
        if risk_level == "red":
            return f"CRITICAL ISSUES DETECTED: {'; '.join(critical_msgs[:2])}"
        else:
            return f"Verification complete with concerns: {'; '.join(critical_msgs[:2])}"
    
    def _calculate_gap_months(self, end_date: str, start_date: str) -> int:
        """Helper: calculate months between dates"""
        from datetime import datetime
        end = datetime.strptime(end_date, "%Y-%m")
        start = datetime.strptime(start_date, "%Y-%m")
        return (start.year - end.year) * 12 + (start.month - end.month)
```

**Adding New Rules:**
```python
# Just add a new method - no orchestration changes needed
def _check_social_media_consistency(self, resume, github, *args) -> list[FraudFlag]:
    """New rule: Check LinkedIn vs resume consistency"""
    flags = []
    # Implementation
    return flags

# Add to rules list
self.rules.append(self._check_social_media_consistency)
```

---

## API Specification (Versioned)

### Pydantic Schemas (backend/schemas.py)

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

# API Version 1
class VerificationRequestV1(BaseModel):
    github_username: Optional[str] = None
    demo_scenario: Optional[str] = None  # For injecting fraud scenarios

class VerificationResponseV1(BaseModel):
    verification_id: str
    status: Literal["processing", "complete", "failed"]
    message: str
    created_at: datetime

class ReportV1(BaseModel):
    verification_id: str
    candidate_name: str
    risk_level: Literal["green", "yellow", "red"]
    risk_score: dict
    narrative_summary: str
    verification_details: dict
    interview_questions: list[str]
    generated_at: datetime

# Future API Version 2 (easy to add without breaking V1)
class VerificationRequestV2(VerificationRequestV1):
    include_social_media: bool = False  # New feature
    priority: Literal["standard", "express"] = "standard"
```

### FastAPI Routes (backend/main.py)

```python
from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from supabase import create_client
from config import get_settings
from schemas import VerificationRequestV1, VerificationResponseV1, ReportV1
import uuid

app = FastAPI(title="TruthHire API", version="1.0.0")
settings = get_settings()
supabase = create_client(settings.supabase_url, settings.supabase_service_key)

@app.post("/api/v1/verify", response_model=VerificationResponseV1)
async def create_verification(
    resume: UploadFile,
    github_username: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Start new verification
    Returns verification_id for tracking progress
    """
    
    verification_id = str(uuid.uuid4())
    
    try:
        # 1. Upload resume to Supabase Storage
        resume_bytes = await resume.read()
        storage_path = f"{verification_id}/{resume.filename}"
        
        supabase.storage.from_("resumes").upload(
            storage_path,
            resume_bytes,
            {"content-type": resume.content_type}
        )
        
        resume_url = supabase.storage.from_("resumes").get_public_url(storage_path)
        
        # 2. Parse resume
        from services.resume_parser import extract_text_from_pdf, parse_with_llm
        resume_text = extract_text_from_pdf(resume_bytes)
        parsed_data = await parse_with_llm(resume_text)
        
        # 3. Create DB record
        supabase.table("verifications").insert({
            "id": verification_id,
            "candidate_name": parsed_data["name"],
            "candidate_email": parsed_data.get("email"),
            "github_username": github_username or parsed_data.get("github_username"),
            "status": "processing",
            "resume_url": resume_url,
            "parsed_data": parsed_data
        }).execute()
        
        # 4. Run verification workflow in background
        background_tasks.add_task(
            run_verification_workflow,
            verification_id,
            parsed_data,
            github_username
        )
        
        return VerificationResponseV1(
            verification_id=verification_id,
            status="processing",
            message="Verification started. Subscribe to real-time updates via Supabase.",
            created_at=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/verify/{verification_id}", response_model=ReportV1)
async def get_verification_report(verification_id: str):
    """Get verification report (once complete)"""
    
    result = supabase.table("verifications").select("*").eq("id", verification_id).single().execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    if result.data["status"] != "complete":
        raise HTTPException(status_code=400, detail="Verification still processing")
    
    return ReportV1(**result.data["result"])

@app.get("/api/v1/verify/{verification_id}/steps")
async def get_verification_steps(verification_id: str):
    """Get all agent progress steps (for debugging)"""
    
    steps = supabase.table("verification_steps").select("*").eq("verification_id", verification_id).order("created_at").execute()
    
    return {"steps": steps.data}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "config": {
            "use_mock_data": settings.use_mock_data,
            "llm_model": settings.llm_model
        }
    }
```

---

## File Structure (Modular)

```
truthhire/
├── frontend/                      # Next.js app
│   ├── app/
│   │   ├── page.tsx              # Resume upload
│   │   ├── verify/[id]/page.tsx  # Real-time progress
│   │   └── report/[id]/page.tsx  # Final report
│   ├── components/
│   │   ├── AgentStepCard.tsx
│   │   ├── RiskBadge.tsx
│   │   ├── FileUpload.tsx
│   │   └── ReportPDF.tsx
│   ├── lib/
│   │   ├── supabase.ts           # Supabase client
│   │   └── api.ts                # API wrapper
│   └── .env.local
│
├── backend/                       # FastAPI server
│   ├── main.py                   # API routes
│   ├── config.py                 # Pydantic settings
│   ├── schemas.py                # API models (versioned)
│   │
│   ├── agents/
│   │   ├── orchestrator.py       # LangGraph workflow
│   │   ├── fraud_detector.py     # Modular fraud rules
│   │   ├── parser_agent.py
│   │   ├── discovery_agent.py
│   │   ├── github_agent.py
│   │   └── report_agent.py
│   │
│   ├── services/
│   │   ├── resume_parser.py      # PDF → text → LLM
│   │   ├── github_api.py         # Real GitHub API client
│   │   ├── mock_loader.py        # JSON mock data loader
│   │   └── supabase_client.py    # DB helper functions
│   │
│   ├── mocks/                     # Externalized test data
│   │   ├── reference_templates.json
│   │   ├── fraud_scenarios.json
│   │   ├── education_verifications.json
│   │   └── employment_verifications.json
│   │
│   └── .env
│
├── supabase/
│   ├── migrations/
│   │   └── 001_initial_schema.sql
│   └── config.toml
│
└── demo/
    ├── resumes/
    │   ├── candidate_green.pdf   # Clean verification
    │   ├── candidate_yellow.pdf  # Minor concerns
    │   └── candidate_red.pdf     # Major fraud flags
    └── demo_script.md
```

---

## Deployment Checklist

### Local Development (Day 1)

```bash
# 1. Set up Supabase project
# Go to supabase.com, create project, copy credentials to .env

# 2. Run database migrations
cd supabase
npx supabase db push

# 3. Start backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 4. Start frontend
cd frontend
npm install
npm run dev
```

### Production Deployment (Post-Hackathon)

1. **Frontend (Vercel):**
   - Push to GitHub
   - Import to Vercel
   - Set environment variables
   - Auto-deploys on push

2. **Backend (Railway):**
   - Connect GitHub repo
   - Set environment variables
   - Railway auto-detects FastAPI

3. **Database (Supabase):**
   - Already cloud-hosted
   - Upgrade to paid plan when > 500MB

---

## Post-MVP Roadmap (Enabled by Architecture)

### Easy Additions (No Rewrites)

| Feature | How to Add | Time Estimate |
|---------|-----------|---------------|
| **User accounts** | Wire Supabase Auth (already installed) | 2 hours |
| **Verification history** | Already persisted, just add UI | 1 hour |
| **Export reports** | Add PDF generation endpoint | 3 hours |
| **Real NSC API** | Swap mock → real in config | 1 hour |
| **SMS/Voice agents** | Flip `COMM_AGENTS_ENABLED=true` | Partner-dependent |
| **New fraud rule** | Add method to FraudDetector | 30 mins |
| **A/B test fraud logic** | Load different mock configs | 15 mins |
| **Caching GitHub calls** | Add Redis layer | 4 hours |
| **Custom report branding** | Template system + DB field | 2 hours |

### Why This is Agile

1. **Database-backed:** No migration from stateless → stateful
2. **Config-driven:** Feature flags enable gradual rollout
3. **Modular agents:** Add agent = add node to graph
4. **Versioned APIs:** V2 endpoints don't break V1 clients
5. **Externalized mocks:** Product team tests scenarios without dev help

---

## Success Metrics

### Hackathon Demo (Must-Have)

- ✅ Upload resume → see 5 agents work in real-time
- ✅ GitHub analysis pulls REAL data (commit count, languages)
- ✅ Fraud detection catches ≥2 types of discrepancies
- ✅ Report generates in <90 seconds
- ✅ Can demo 3 scenarios (green/yellow/red) back-to-back
- ✅ UI is polished (not hacky)

### Post-MVP Agility Test

- ✅ Add new fraud rule without touching orchestration (< 30 mins)
- ✅ Non-dev can edit mock scenarios in JSON (< 5 mins)
- ✅ Swap LLM model via environment variable (< 2 mins)
- ✅ Enable user accounts without rewriting API (< 2 hours)

---

## Questions & Answers (Prep for Judges)

**Q: "Why Supabase over raw Postgres?"**  
A: "Three reasons: (1) Realtime WebSocket built-in for agent progress, (2) Auth ready when we add user accounts, (3) Storage for resume uploads. Saves us 2 days of infrastructure work."

**Q: "Can you add new fraud detection rules easily?"**  
A: "Yes. [Show FraudDetector class] Each rule is a separate method. Add rule = add 20 lines. Non-technical team can even edit scenarios in JSON files."

**Q: "What if GitHub API goes down?"**  
A: "Graceful degradation. If GitHub fails, we still verify via references + education. GitHub is one data source, not a dependency."

**Q: "How do you prevent false positives?"**  
A: "Three-tier severity (low/medium/high/critical). Green = no issues. Yellow = minor concerns but proceed. Red = critical flags, recommend rejecting. Customers can tune thresholds via config."

---

## Definition of Done

**MVP Complete When:**

1. ✅ Resume upload → Supabase Storage
2. ✅ 5 agents run via LangGraph state machine
3. ✅ Real-time progress visible in UI (Supabase Realtime)
4. ✅ GitHub analysis works for real usernames
5. ✅ Fraud detection flags ≥2 scenario types
6. ✅ Report shows risk score + narrative + questions
7. ✅ Database persists last 10 verifications
8. ✅ Config management via `.env` files
9. ✅ Mock data externalized to JSON
10. ✅ Can add new fraud rule in <30 minutes

**Agility Validated When:**

- Non-dev team member can edit fraud scenarios
- Swap mock → real API via environment variable
- Add new agent without touching existing agents
- Frontend API calls work if backend adds new fields

---

**BUILD TIME. You have 24 hours.** 🚀
