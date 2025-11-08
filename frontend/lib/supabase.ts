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
