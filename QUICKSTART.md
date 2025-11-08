# 🚀 TruthHire - Quick Start Guide

## ✅ Setup Status

### Completed:
- ✅ Supabase MCP connected
- ✅ Database tables created (`verifications`, `verification_steps`)
- ✅ Realtime enabled
- ✅ `.env` file created with credentials
- ✅ `.vscode/mcp.json` configured

### To Do:
- ⚠️ Add OpenAI API key to `.env`
- ⚠️ Add Supabase Service Role Key to `.env`
- ⚠️ Create `resumes` storage bucket in Supabase dashboard
- ⏳ Create project directories (backend/, frontend/)

---

## 🔑 Get Missing API Keys

### 1. Supabase Service Role Key
Visit: https://supabase.com/dashboard/project/hkmhumkvzgfsucysjamc/settings/api

Look for `service_role` key and add to `.env`:
```
SUPABASE_SERVICE_KEY=eyJhbG...your-service-role-key
```

### 2. OpenAI API Key
Visit: https://platform.openai.com/api-keys

Create new key and add to `.env`:
```
OPENAI_API_KEY=sk-...your-openai-key
```

### 3. GitHub Token (Optional)
Visit: https://github.com/settings/tokens

Create personal access token for higher rate limits (optional):
```
GITHUB_TOKEN=ghp_...your-github-token
```

---

## 📦 Create Storage Bucket

1. Go to: https://supabase.com/dashboard/project/hkmhumkvzgfsucysjamc/storage/buckets
2. Click "New bucket"
3. Settings:
   - Name: `resumes`
   - Public: **No** (private)
   - File size limit: `5242880` (5MB)
4. Click "Create bucket"

---

## 🏗️ Project Structure

According to Wave 1 plan, create these directories:

```
agenticAI/
├── backend/              # FastAPI backend
│   ├── agents/          # AI agent implementations
│   ├── services/        # GitHub API, Supabase, parsers
│   ├── mocks/           # Mock data JSON files
│   ├── config.py        # Settings management
│   ├── main.py          # FastAPI app
│   ├── schemas.py       # Pydantic models
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js 14 frontend
│   ├── app/            # App router pages
│   ├── components/     # React components
│   ├── lib/            # Supabase client
│   └── package.json    # npm dependencies
├── demo/               # Demo materials
│   └── sample PDFs
└── .env                # Environment variables
```

---

## 🧪 Test MCP Connection

I can now autonomously execute database operations. Try asking me to:

- "Show me all tables in the database"
- "Insert a test verification record"
- "Query the verification_steps table"
- "Check security advisories"
- "Generate TypeScript types for Supabase"

Example test:
```sql
-- I can run this for you automatically
SELECT COUNT(*) FROM verifications;
```

---

## 🚦 Next: Wave 1 Development

Once API keys are added, you're ready for Wave 1 (Hour 1-4):

### Agent A: Backend Foundation
- FastAPI project structure
- Requirements.txt
- Config management
- Supabase client helpers

### Agent B: Frontend Foundation
- Next.js 14 with TypeScript
- Tailwind CSS + shadcn/ui
- Page skeletons
- Supabase client setup

### Agent C: Data Layer
- GitHub API client
- Mock data templates
- Mock data loader

---

## 🔧 Useful Commands

```bash
# Create directories
New-Item -ItemType Directory -Path "backend", "frontend", "demo"

# Test Supabase connection
curl https://hkmhumkvzgfsucysjamc.supabase.co

# Install VS Code Supabase extension (optional)
code --install-extension supabase.supabase
```

---

## 🛡️ Security Note

⚠️ **RLS is currently disabled** on both tables. This is fine for hackathon MVP, but before production:

```sql
-- Enable RLS (run when ready for production)
ALTER TABLE verifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE verification_steps ENABLE ROW LEVEL SECURITY;
```

---

## 📊 Database Schema Reference

### verifications
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| candidate_name | text | Full name |
| candidate_email | text | Email (nullable) |
| github_username | text | GitHub handle (nullable) |
| status | text | 'processing' \| 'complete' \| 'failed' |
| risk_score | text | 'green' \| 'yellow' \| 'red' |
| resume_url | text | Supabase Storage URL |
| parsed_data | jsonb | Structured resume data |
| result | jsonb | Final verification report |
| created_at | timestamptz | Record creation time |
| completed_at | timestamptz | Completion time (nullable) |

### verification_steps
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| verification_id | uuid | Foreign key → verifications |
| agent_name | text | Which agent (e.g., "Resume Parser") |
| status | text | 'running' \| 'complete' \| 'failed' |
| message | text | Progress message |
| data | jsonb | Additional agent data |
| created_at | timestamptz | Step creation time |

---

**Ready to start building!** 🎉

Ask me to create any of the Wave 1 components when you're ready.
