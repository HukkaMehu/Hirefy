# TruthHire Frontend

Next.js 14 frontend with TypeScript and Tailwind CSS for AI-powered candidate verification.

## Setup Complete

All dependencies installed and project structure created.

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx                 # Home page with resume upload
│   ├── layout.tsx               # Root layout with metadata
│   ├── globals.css              # Tailwind CSS imports
│   ├── verify/[id]/
│   │   └── page.tsx            # Real-time verification progress page
│   └── report/[id]/
│       └── page.tsx            # Final verification report page
├── lib/
│   └── supabase.ts             # Supabase client and TypeScript types
├── public/                      # Static assets
├── .env.local                   # Environment variables (template)
├── package.json                 # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.ts          # Tailwind CSS configuration with animations
├── postcss.config.js           # PostCSS configuration
├── next.config.js              # Next.js configuration
└── .eslintrc.json              # ESLint configuration

## Environment Variables

Copy `.env.local` and fill in your values:

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing Instructions

### 1. Start Development Server

```bash
cd frontend
npm run dev
```

Visit http://localhost:3000

### 2. Test Routes

- **Home Page**: http://localhost:3000
  - Should display "TruthHire" heading
  - Placeholder for resume upload form

- **Verification Progress**: http://localhost:3000/verify/test-id
  - Should show "Verification in Progress"
  - Display the verification ID

- **Report Page**: http://localhost:3000/report/test-id
  - Should show "Verification Report"
  - Display the verification ID

### 3. Build Production

```bash
npm run build
npm start
```

## Dependencies Installed

### Core
- next@14.2.21
- react@18.3.1
- react-dom@18.3.1

### Features
- @supabase/supabase-js@2.47.10
- lucide-react@0.462.0

### Development
- typescript@5.6.3
- tailwindcss@3.4.15
- eslint@8.57.1
- eslint-config-next@14.2.21

## Next Steps

1. Configure Supabase credentials in `.env.local`
2. Implement resume upload component in `app/page.tsx`
3. Add real-time subscription logic in `app/verify/[id]/page.tsx`
4. Build report visualization in `app/report/[id]/page.tsx`

## Custom Tailwind Animations

The config includes a `fade-in` animation:

```tsx
<div className="animate-fade-in">
  Content with fade-in effect
</div>
```

## TypeScript Types

Supabase types are defined in `lib/supabase.ts`:

- `Verification`: Main verification record
- `VerificationStep`: Individual agent step progress

## Notes

- App Router (Next.js 13+) is used
- No `src/` directory (direct `app/` structure)
- Import alias `@/*` configured for root-level imports
- ESLint configured with Next.js recommended rules
