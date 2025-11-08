'use client'

import { useEffect, useState } from 'react'
import { AlertCircle, CheckCircle, XCircle } from 'lucide-react'

type Report = {
  risk_level: 'green' | 'yellow' | 'red'
  flags: any[]
  summary: string
  narrative?: string
  interview_questions?: string[]
}

export default function ReportPage({ params }: { params: { id: string } }) {
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchReport = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/verify/${params.id}`)
        const data = await response.json()
        
        if (data.status === 'complete' && data.result) {
          setReport(data.result.fraud_results)
        }
      } catch (err) {
        console.error('Failed to fetch report:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchReport()
  }, [params.id])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading report...</p>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
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

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Verification Report</h1>

        {/* Risk Badge */}
        <div className={`rounded-xl border-2 p-6 mb-8 ${riskColors[report.risk_level]}`}>
          <div className="flex items-center gap-4">
            {riskIcons[report.risk_level]}
            <div>
              <h2 className="text-2xl font-bold uppercase">{report.risk_level} Risk</h2>
              <p className="mt-1">{report.summary}</p>
            </div>
          </div>
        </div>

        {/* Fraud Flags */}
        {report.flags && report.flags.length > 0 && (
          <div className="bg-white rounded-xl shadow-md p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Detected Issues</h3>
            <div className="space-y-4">
              {report.flags.map((flag, idx) => (
                <div key={idx} className="border-l-4 border-red-500 pl-4 py-2">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="font-semibold text-gray-900">{flag.category}</span>
                      <p className="text-gray-700 mt-1">{flag.message}</p>
                      <span className="text-sm text-gray-500">Severity: {flag.severity}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Interview Questions */}
        {report.interview_questions && report.interview_questions.length > 0 && (
          <div className="bg-white rounded-xl shadow-md p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Recommended Interview Questions</h3>
            <ol className="list-decimal list-inside space-y-3">
              {report.interview_questions.map((q, idx) => (
                <li key={idx} className="text-gray-700">{q}</li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  )
}
