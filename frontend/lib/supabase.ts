import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Types
export type VerificationStep = {
  id: string
  verification_id: string
  agent_name: string
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
  message: string
  data?: any
  started_at?: string
  completed_at?: string
  created_at: string
}

export type Verification = {
  id: string
  candidate_name: string
  candidate_email?: string
  candidate_phone?: string
  linkedin_url?: string
  github_username?: string
  company?: string
  position?: string
  employment_start?: string
  employment_end?: string
  verification_options?: any
  status: 'pending' | 'processing' | 'completed' | 'failed'
  result?: VerificationResult
  created_at: string
  updated_at?: string
}

export type VerificationResult = {
  candidate_name?: string
  risk_level: 'green' | 'yellow' | 'red'
  risk_score?: number
  fraud_flags?: FraudFlag[]
  narrative?: string
  interview_questions?: string[]
  github_summary?: string
  reference_summary?: string
}

export type FraudFlag = {
  severity: 'low' | 'medium' | 'high' | 'critical'
  type: string
  description: string
  resolved?: boolean
}

// Utility Functions

/**
 * Fetch all verifications with optional filtering
 */
export async function getVerifications(options?: {
  status?: Verification['status'];
  limit?: number;
  offset?: number;
}) {
  let query = supabase
    .from('verifications')
    .select('*')
    .order('created_at', { ascending: false });

  if (options?.status) {
    query = query.eq('status', options.status);
  }

  if (options?.limit) {
    query = query.limit(options.limit);
  }

  if (options?.offset) {
    query = query.range(options.offset, options.offset + (options.limit || 10) - 1);
  }

  const { data, error } = await query;
  
  if (error) {
    console.error('Error fetching verifications:', error);
    throw error;
  }

  return data as Verification[];
}

/**
 * Fetch a single verification by ID
 */
export async function getVerification(id: string) {
  const { data, error } = await supabase
    .from('verifications')
    .select('*')
    .eq('id', id)
    .single();

  if (error) {
    console.error('Error fetching verification:', error);
    throw error;
  }

  return data as Verification;
}

/**
 * Fetch verification steps for a specific verification
 */
export async function getVerificationSteps(verificationId: string) {
  const { data, error } = await supabase
    .from('verification_steps')
    .select('*')
    .eq('verification_id', verificationId)
    .order('created_at', { ascending: true });

  if (error) {
    console.error('Error fetching verification steps:', error);
    throw error;
  }

  return data as VerificationStep[];
}

/**
 * Subscribe to verification status changes
 */
export function subscribeToVerification(
  verificationId: string,
  callback: (verification: Verification) => void
) {
  const channel = supabase
    .channel(`verification:${verificationId}`)
    .on(
      'postgres_changes',
      {
        event: 'UPDATE',
        schema: 'public',
        table: 'verifications',
        filter: `id=eq.${verificationId}`,
      },
      (payload) => {
        callback(payload.new as Verification);
      }
    )
    .subscribe();

  return channel;
}

/**
 * Subscribe to verification steps for real-time progress
 */
export function subscribeToVerificationSteps(
  verificationId: string,
  callback: (step: VerificationStep) => void
) {
  const channel = supabase
    .channel(`verification_steps:${verificationId}`)
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'verification_steps',
        filter: `verification_id=eq.${verificationId}`,
      },
      (payload) => {
        callback(payload.new as VerificationStep);
      }
    )
    .subscribe();

  return channel;
}

/**
 * Calculate statistics from verifications
 */
export function calculateStats(verifications: Verification[]) {
  const total = verifications.length;
  const completed = verifications.filter(v => v.status === 'completed').length;
  const inProgress = verifications.filter(v => v.status === 'processing').length;
  
  const completedVerifications = verifications.filter(
    v => v.status === 'completed' && v.result
  );
  
  const flagged = completedVerifications.filter(
    v => v.result?.risk_level === 'red' || (v.result?.fraud_flags && v.result.fraud_flags.length > 0)
  ).length;

  const verified = completedVerifications.filter(
    v => v.result?.risk_level === 'green'
  ).length;

  return {
    total,
    completed,
    inProgress,
    flagged,
    verified,
    verifiedPercentage: total > 0 ? Math.round((verified / total) * 100) : 0,
  };
}
