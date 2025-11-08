'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { supabase, VerificationStep } from '@/lib/supabase'
import { CheckCircle2, Loader2, XCircle, AlertTriangle } from 'lucide-react'

export default function VerifyPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [steps, setSteps] = useState<VerificationStep[]>([])
  const [status, setStatus] = useState<string>('processing')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
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

    const fetchSteps = async () => {
      try {
        const { data, error: fetchError } = await supabase
          .from('verification_steps')
          .select('*')
          .eq('verification_id', params.id)
          .order('created_at', { ascending: true })
        
        if (fetchError) throw fetchError
        
        if (data) {
          setSteps(data)
          const failedStep = data.find(s => s.status === 'failed')
          if (failedStep) {
            setError(`Agent ${failedStep.agent_name} failed: ${failedStep.message}`)
          }
        }
      } catch (err) {
        setError('Failed to load verification progress')
        console.error(err)
      }
    }
    
    fetchSteps()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [params.id, router])

  const statusIcons = {
    in_progress: <Loader2 className="animate-spin h-6 w-6 text-blue-500" />,
    completed: <CheckCircle2 className="h-6 w-6 text-green-600" />,
    failed: <XCircle className="h-6 w-6 text-red-600" />,
    skipped: <AlertTriangle className="h-6 w-6 text-gray-400" />
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Verification in Progress</h1>
          <p className="text-gray-600">Our AI agents are analyzing the candidate...</p>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 animate-fade-in">
            <div className="flex">
              <XCircle className="h-6 w-6 text-red-500 mr-3" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="space-y-4">
          {steps.map((step, idx) => (
            <div
              key={step.id}
              className="bg-white rounded-lg shadow-md p-6 flex items-start gap-4 animate-fade-in transition-all hover:shadow-lg"
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              {statusIcons[step.status] || statusIcons.in_progress}
              <div className="flex-1">
                <h3 className="font-semibold text-lg text-gray-900">{step.agent_name}</h3>
                <p className="text-gray-700 mt-1">{step.message}</p>
                <span className="text-sm text-gray-400 mt-2 block">
                  {new Date(step.created_at).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}

          {steps.length === 0 && !error && (
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
