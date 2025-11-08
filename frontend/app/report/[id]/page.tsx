'use client'

import { useEffect, useState } from 'react'
import { AlertCircle, CheckCircle, XCircle, Loader2 } from 'lucide-react'

type Report = {
  candidate_name?: string
  risk_level: 'green' | 'yellow' | 'red'
  fraud_flags?: any[]
  flags?: any[]
  narrative?: string
  interview_questions?: string[]
  github_summary?: string
  reference_summary?: string
}

export default function ReportPage({ params }: { params: { id: string } }) {
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/verify/${params.id}`)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        
        if (data.status === 'completed' && data.result) {
          setReport(data.result)
        } else if (data.status === 'failed') {
          setError(data.result?.error || 'Verification failed')
        } else {
          setError('Report not ready yet. Please wait for verification to complete.')
        }
      } catch (err) {
        console.error('Failed to fetch report:', err)
        setError(err instanceof Error ? err.message : 'Failed to load report')
      } finally {
        setLoading(false)
      }
    }

    fetchReport()
    
    const interval = setInterval(() => {
      if (loading || error) {
        fetchReport()
      }
    }, 5000)

    return () => clearInterval(interval)
  }, [params.id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center animate-fade-in">
          <Loader2 className="animate-spin h-16 w-16 text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600 text-lg">Loading report...</p>
          <p className="text-gray-400 text-sm mt-2">This may take a few moments</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
        <div className="text-center max-w-md animate-fade-in">
          <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center animate-fade-in">
          <AlertCircle className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
          <p className="text-gray-600">Report not found or still processing</p>
        </div>
      </div>
    )
  }

  const riskColors = {
    green: 'bg-green-100 text-green-800 border-green-300',
    yellow: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    red: 'bg-red-100 text-red-800 border-red-300'
  }

  const riskIcons = {
    green: <CheckCircle className="h-8 w-8" />,
    yellow: <AlertCircle className="h-8 w-8" />,
    red: <XCircle className="h-8 w-8" />
  }

  const flags = report.fraud_flags || report.flags || []

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto animate-fade-in">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Verification Report</h1>
        {report.candidate_name && (
          <p className="text-xl text-gray-600 mb-8">{report.candidate_name}</p>
        )}

        <div className={`rounded-xl border-2 p-6 mb-8 ${riskColors[report.risk_level]} transition-all hover:shadow-lg`}>
          <div className="flex items-center gap-4">
            {riskIcons[report.risk_level]}
            <div>
              <h2 className="text-2xl font-bold uppercase">{report.risk_level} Risk</h2>
              {report.narrative && <p className="mt-2 leading-relaxed">{report.narrative}</p>}
            </div>
          </div>
        </div>

        {report.github_summary && (
          <div className="bg-white rounded-xl shadow-md p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-3">GitHub Analysis</h3>
            <p className="text-gray-700">{report.github_summary}</p>
          </div>
        )}

        {report.reference_summary && (
          <div className="bg-white rounded-xl shadow-md p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-3">Reference Check</h3>
            <p className="text-gray-700">{report.reference_summary}</p>
          </div>
        )}

        {flags.length > 0 && (
          <div className="bg-white rounded-xl shadow-md p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Detected Issues</h3>
            <div className="space-y-4">
              {flags.map((flag, idx) => (
                <div 
                  key={idx} 
                  className="border-l-4 border-red-500 pl-4 py-2 hover:bg-gray-50 transition"
                  style={{ animationDelay: `${idx * 100}ms` }}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="font-semibold text-gray-900">{flag.category || flag.type}</span>
                      <p className="text-gray-700 mt-1">{flag.message}</p>
                      <span className="text-sm text-gray-500 uppercase mt-1 inline-block">
                        Severity: {flag.severity}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {report.interview_questions && report.interview_questions.length > 0 && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Recommended Interview Questions</h3>
            <ol className="list-decimal list-inside space-y-3">
              {report.interview_questions.map((q, idx) => (
                <li 
                  key={idx} 
                  className="text-gray-700 leading-relaxed hover:bg-gray-50 p-2 rounded transition"
                  style={{ animationDelay: `${idx * 100}ms` }}
                >
                  {q}
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  )
}
