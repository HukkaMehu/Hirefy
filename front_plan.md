# TruthHire Frontend Migration Plan

## 📋 Overview
**Goal:** Migrate from Figma-generated frontend to production-ready Next.js + Supabase integration  
**Current State:** Standalone React + Vite with mock data  
**Target State:** Next.js App Router + Supabase realtime + Backend API integration

---

## 🎯 Migration TODO Plan

### **Phase 1: Setup & Infrastructure** (2-3 hours)

#### 1.1 Environment Setup
- [ ] Copy UI components from `Build TruthHire MVP Frontend/src/components/ui/` to `frontend/src/components/ui/`
- [ ] Copy global styles from globals.css and merge with existing globals.css
- [ ] Install missing dependencies: `motion/react` (Framer Motion v12), `sonner`, `lucide-react`
- [ ] Update `tailwind.config.ts` to include glassmorphism utilities and color tokens
- [ ] Create `lib/animations.ts` for reusable motion variants
- [ ] Set up CSS variables for dark theme matching Figma design

#### 1.2 Type Definitions
- [ ] Create `types/verification.ts` with interfaces:
  - `Verification` (matches Supabase schema)
  - `VerificationStep` (agent progress)
  - `VerificationReport` (final report structure)
  - `Agent` (agent status types)
- [ ] Update existing `lib/supabase.ts` with new types
- [ ] Remove mock data types from copied files

---

### **Phase 2: Core Layout Components** (3-4 hours)

#### 2.1 Dashboard Layout
- [ ] Create `app/(dashboard)/layout.tsx` with sidebar navigation
  - [ ] Implement sidebar from DashboardLayout.tsx
  - [ ] Add navigation items: Overview, Verifications, New Verification, Settings
  - [ ] Add TruthHire logo and branding
  - [ ] Add user profile dropdown (placeholder for now)
  - [ ] Make responsive (collapsible on mobile)

#### 2.2 Shared Components
- [ ] Create `components/StatCard.tsx` for metric cards
  - [ ] Props: label, value, change, trend, icon, color
  - [ ] Add hover animations (scale + translate-y)
  - [ ] Use glassmorphism styling
- [ ] Create `components/RiskBadge.tsx` for risk level indicators
  - [ ] Green (Verified), Yellow (Caution), Red (Fraud)
  - [ ] Animated pulse for processing state
  - [ ] Match Figma color palette
- [ ] Create `components/AgentCard.tsx` for agent progress display
  - [ ] Status icons: pending, running, complete, failed
  - [ ] Progress animations (spinner for running)
  - [ ] Collapsible details section

---

### **Phase 3: Dashboard Overview Page** (4-5 hours)

#### 3.1 Overview Page Structure
- [ ] Create page.tsx (replaces current landing)
- [ ] Implement layout from DashboardOverview.tsx:
  - [ ] Header section with title and description
  - [ ] 4-column stats grid (Total, Verified Clean, Fraud Detected, Avg Time)
  - [ ] Recent verifications table
  - [ ] Quick action button (+ New Verification)

#### 3.2 Stats Calculation
- [ ] Create `lib/statsCalculator.ts`:
  - [ ] `calculateTotalVerifications(verifications)`
  - [ ] `calculateVerifiedCleanPercentage(verifications)`
  - [ ] `calculateFraudCount(verifications)`
  - [ ] `calculateAverageTime(verifications)` (placeholder for now)
- [ ] Fetch real data from Supabase `verifications` table
- [ ] Add loading skeletons for stats cards
- [ ] Add error handling with toast notifications

#### 3.3 Recent Activity Table
- [ ] Display last 5 verifications from Supabase
- [ ] Show: Candidate name, timestamp, risk level badge, view button
- [ ] Add hover effects (glass-hover utility)
- [ ] Make rows clickable → navigate to `/report/[id]`
- [ ] Real-time updates via Supabase subscription

---

### **Phase 4: Verifications List Page** (4-5 hours)

#### 4.1 List Page Structure
- [ ] Create page.tsx
- [ ] Implement layout from VerificationsList.tsx:
  - [ ] Header with search bar
  - [ ] Filter pills (All, Verified, Caution, Fraud)
  - [ ] Data table with columns: Name, Status, Risk, GitHub, Refs, Date, Actions
  - [ ] Pagination controls

#### 4.2 Search & Filter
- [ ] Implement client-side search by candidate name
- [ ] Add filter state for risk level
- [ ] Add filter state for status (processing, completed, failed)
- [ ] Show result count: "Showing 1-10 of 127 candidates"
- [ ] Debounce search input (300ms)

#### 4.3 Data Table
- [ ] Use shadcn `Table` component as base
- [ ] Fetch all verifications from Supabase with pagination
- [ ] Display risk badges with correct colors
- [ ] Show GitHub status (✅ Yes / ❌ No)
- [ ] Show reference stats (e.g., "8/41")
- [ ] Add "View Report" button per row
- [ ] Add sorting by date, name, risk level
- [ ] Add loading state with skeleton rows

#### 4.4 Real-time Updates
- [ ] Subscribe to Supabase `verifications` table changes
- [ ] Update list when new verification completes
- [ ] Show processing indicator for in-progress verifications
- [ ] Auto-refresh stats when data changes

---

### **Phase 5: New Verification Page** (3-4 hours)

#### 5.1 Upload Form
- [ ] Create page.tsx
- [ ] Implement drag-and-drop file upload
- [ ] Add GitHub username input (optional)
- [ ] Add file validation (PDF only, max 5MB)
- [ ] Show file preview after selection
- [ ] Add "Start Verification" button

#### 5.2 Upload Flow
- [ ] Call backend `/api/v1/verify` endpoint
- [ ] Upload resume to Supabase Storage
- [ ] Create verification record in database
- [ ] Redirect to `/verify/[id]` on success
- [ ] Show error toast on failure
- [ ] Add loading state during upload

---

### **Phase 6: Progress Page** (5-6 hours)

#### 6.1 Live Progress View
- [ ] Create page.tsx
- [ ] Implement layout from `ProgressPage.tsx`:
  - [ ] Full-screen view (no sidebar)
  - [ ] Candidate name header
  - [ ] 5 agent cards in vertical list
  - [ ] Auto-redirect to report on completion

#### 6.2 Agent Cards
- [ ] Display 5 agents:
  1. Resume Parser
  2. Reference Discovery
  3. GitHub Analyzer
  4. Fraud Detector
  5. Report Synthesizer
- [ ] Show status icons (pending, running, complete, failed, skipped)
- [ ] Show real-time messages from backend
- [ ] Animate agent transitions (pending → running → complete)
- [ ] Show timestamps for each step

#### 6.3 Real-time Updates
- [ ] Subscribe to Supabase `verification_steps` table
- [ ] Filter by `verification_id=eq.[id]`
- [ ] Update agent status on new INSERT events
- [ ] Check for "Report Synthesizer" + "completed" status
- [ ] Auto-redirect to `/report/[id]` after 2 seconds
- [ ] Handle failed state with error message

#### 6.4 Progress Animations
- [ ] Use Framer Motion for agent card entrance
- [ ] Add spinner animation for running agents
- [ ] Add checkmark animation for completed agents
- [ ] Add pulse effect for current running agent
- [ ] Match animations from Figma design

---

### **Phase 7: Report Page** (6-8 hours)

#### 7.1 Report Layout
- [ ] Create page.tsx
- [ ] Implement layout from ReportPage.tsx:
  - [ ] Header with candidate name and risk badge (large, animated)
  - [ ] Summary section with narrative
  - [ ] GitHub analysis section (collapsible)
  - [ ] Reference verification section (collapsible)
  - [ ] Fraud flags section (collapsible if any)
  - [ ] Interview questions section
  - [ ] Action buttons (Download, Share, New Verification)

#### 7.2 Risk Badge Header
- [ ] Large animated risk badge at top
- [ ] Colors:
  - 🟢 GREEN: `bg-green-400/10 text-green-400 border-green-400`
  - 🟡 YELLOW: `bg-yellow-400/10 text-yellow-400 border-yellow-400`
  - 🔴 RED: `bg-red-400/10 text-red-400 border-red-400`
- [ ] Add pulse animation from Figma
- [ ] Show candidate name below badge

#### 7.3 Summary Section
- [ ] Fetch verification from Supabase by ID
- [ ] Display AI-generated narrative (2 paragraphs)
- [ ] Show timestamp
- [ ] Add glassmorphism card styling

#### 7.4 GitHub Analysis Section
- [ ] Check if `github_summary` exists in report
- [ ] Show:
  - [ ] Username with link to GitHub profile
  - [ ] Repository count
  - [ ] Languages used (if available in data)
  - [ ] Account age (if available)
- [ ] Make section collapsible
- [ ] Show "No GitHub profile analyzed" if missing

#### 7.5 Reference Verification Section
- [ ] Parse `reference_summary` string
  - Extract: responded count, avg rating, would rehire count
- [ ] Display metrics in grid:
  - [ ] Responded: X/Y
  - [ ] Avg Rating: X.X/5.0
  - [ ] Would Rehire: X/Y
- [ ] Make section collapsible

#### 7.6 Fraud Flags Section
- [ ] Only show if `fraud_flags` array is not empty
- [ ] Display each flag with:
  - [ ] Severity indicator (critical/high/medium/low)
  - [ ] Message/description
  - [ ] Color-coded by severity
- [ ] Make section collapsible
- [ ] Show "No fraud flags detected" if empty

#### 7.7 Interview Questions
- [ ] Display `interview_questions` array
- [ ] Show as numbered list
- [ ] Add "Copy" button per question
- [ ] Show toast on copy: "Question copied to clipboard"
- [ ] Add checkmark icon after copy (temporary, 2s)

#### 7.8 Action Buttons
- [ ] "Download PDF" → Generate PDF report (Phase 8)
- [ ] "Share Report" → Copy link to clipboard
- [ ] "Start New Verification" → Navigate to `/new`
- [ ] Style with glassmorphism and hover effects

---

### **Phase 8: Polish & Animations** (4-5 hours)

#### 8.1 Page Transitions
- [ ] Add Framer Motion `AnimatePresence` to layout
- [ ] Implement page transition variants:
  - [ ] Fade + slide up on enter
  - [ ] Fade + slide down on exit
- [ ] Stagger children animations on list pages
- [ ] Match timing from Figma prototype

#### 8.2 Hover Effects
- [ ] Add `glass-hover` utility class
  - Scale: 1.02
  - Translate Y: -4px
  - Increase shadow
- [ ] Apply to all cards and buttons
- [ ] Add transition: `transition-all duration-200`

#### 8.3 Loading States
- [ ] Create skeleton components:
  - [ ] `SkeletonStatCard`
  - [ ] `SkeletonTableRow`
  - [ ] `SkeletonReportSection`
- [ ] Add pulse animation (gray gradient)
- [ ] Show during data fetching

#### 8.4 Empty States
- [ ] Dashboard with no verifications:
  - Icon + message + "Upload Resume" CTA
- [ ] Verifications list with no results:
  - "No verifications found" + adjust filters
- [ ] Report sections with no data:
  - "No GitHub analysis", "No flags detected"

#### 8.5 Error States
- [ ] Failed verification page
  - Show error message from backend
  - "Retry" button to start new verification
- [ ] API error handling
  - Toast notifications for errors
  - Graceful fallbacks

---

### **Phase 9: Responsive Design** (3-4 hours)

#### 9.1 Mobile Breakpoints
- [ ] Sidebar → Hamburger menu on mobile (<768px)
- [ ] Stats grid → 2 columns on tablet, 1 on mobile
- [ ] Table → Card list on mobile
- [ ] Hide secondary info on small screens
- [ ] Adjust font sizes for mobile

#### 9.2 Touch Interactions
- [ ] Increase button tap targets to 44px minimum
- [ ] Add touch feedback (scale down on tap)
- [ ] Optimize scroll performance
- [ ] Test swipe gestures for navigation

---

### **Phase 10: Integration & Testing** (4-5 hours)

#### 10.1 API Integration
- [ ] Replace all mock data with Supabase queries
- [ ] Test `/api/v1/verify` endpoint
- [ ] Test `/api/v1/verify/{id}` endpoint
- [ ] Verify realtime subscriptions work
- [ ] Handle API errors gracefully

#### 10.2 E2E Testing Flow
- [ ] Upload a resume → See progress → View report
- [ ] Test with GitHub username → Verify analysis appears
- [ ] Test without GitHub → Verify "No profile" message
- [ ] Test with red/yellow/green risk levels
- [ ] Test search and filters on list page

#### 10.3 Performance
- [ ] Lazy load report page components
- [ ] Optimize Supabase queries (select only needed columns)
- [ ] Add React Query for caching (optional)
- [ ] Minimize bundle size (code splitting)

#### 10.4 Bug Fixes
- [ ] Fix auto-redirect timing on progress page
- [ ] Fix realtime subscription cleanup
- [ ] Fix status value mismatch (`completed` vs `complete`)
- [ ] Test on different browsers (Chrome, Firefox, Safari)

---

### **Phase 11: Production Readiness** (2-3 hours)

#### 11.1 Environment Variables
- [ ] Create .env.example with all required vars
- [ ] Document Supabase setup in README
- [ ] Add environment validation on app load

#### 11.2 SEO & Meta Tags
- [ ] Add meta titles per page
- [ ] Add meta descriptions
- [ ] Add Open Graph tags for sharing
- [ ] Add favicon

#### 11.3 Deployment
- [ ] Test build: `npm run build`
- [ ] Fix any build errors
- [ ] Deploy to Vercel
- [ ] Test production deployment
- [ ] Set up custom domain (optional)

---

## 📦 Files to Create/Update

### New Files (29 files)
```
frontend/src/
├── app/(dashboard)/
│   ├── layout.tsx                 # Sidebar layout
│   ├── page.tsx                   # Dashboard overview
│   ├── new/
│   │   └── page.tsx              # Upload form
│   └── verifications/
│       └── page.tsx              # Full list + filters
├── components/
│   ├── AgentCard.tsx             # Agent progress card
│   ├── RiskBadge.tsx             # Risk level badge
│   ├── StatCard.tsx              # Metric card
│   ├── SkeletonStatCard.tsx      # Loading state
│   ├── SkeletonTableRow.tsx      # Loading state
│   └── SkeletonReportSection.tsx # Loading state
├── lib/
│   ├── animations.ts             # Framer Motion variants
│   └── statsCalculator.ts        # Stats functions
└── types/
    └── verification.ts           # Type definitions
```

### Files to Update (8 files)
```
frontend/
├── src/styles/globals.css        # Add glassmorphism + colors
├── tailwind.config.ts            # Add custom utilities
├── src/app/verify/[id]/page.tsx  # Replace with live progress
├── src/app/report/[id]/page.tsx  # Replace with full report
├── src/lib/supabase.ts           # Add new types
└── package.json                  # Add motion, sonner deps
```

### Files to Copy (40+ UI components)
```
All files from: Build TruthHire MVP Frontend/src/components/ui/
→ frontend/src/components/ui/
```

---

## ⏱️ Time Estimates

| Phase | Task | Hours |
|-------|------|-------|
| 1 | Setup & Infrastructure | 2-3 |
| 2 | Core Layout | 3-4 |
| 3 | Dashboard Overview | 4-5 |
| 4 | Verifications List | 4-5 |
| 5 | New Verification | 3-4 |
| 6 | Progress Page | 5-6 |
| 7 | Report Page | 6-8 |
| 8 | Polish & Animations | 4-5 |
| 9 | Responsive Design | 3-4 |
| 10 | Integration & Testing | 4-5 |
| 11 | Production | 2-3 |
| **TOTAL** | **40-52 hours** |

---

## 🚀 Quick Start Command

```bash
# 1. Copy UI components
cp -r "c:\Users\henri\Downloads\Build TruthHire MVP Frontend\src\components\ui" "c:\Users\henri\Documents\hackathon\agenticAI\frontend\src\components\"

# 2. Install dependencies
cd frontend
npm install framer-motion sonner lucide-react

# 3. Start both servers
cd ../backend && python main.py &
cd ../frontend && npm run dev
```

---

## 🎯 Success Criteria

✅ All 5 pages working with real Supabase data  
✅ Realtime updates on progress page  
✅ Animations match Figma design  
✅ Mobile responsive (375px+)  
✅ No TypeScript errors  
✅ Build passes without warnings  
✅ E2E flow works: Upload → Progress → Report  
✅ Glassmorphism styling consistent throughout