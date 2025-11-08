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
        .from('verification_steps')
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
