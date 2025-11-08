import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  Download,
  ChevronDown,
  ChevronUp,
  Shield,
  Briefcase,
  Code,
  AlertTriangle,
  MessageSquare,
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  Github,
  Calendar,
  Building,
  GraduationCap,
  Activity,
  Play,
  AlertCircle,
} from 'lucide-react'
import { apiClient, verificationApi } from '@/lib/api'
import { cn } from '@/lib/utils'
import ProgressBar from '@/components/ProgressBar'
import StatusTimeline from '@/components/StatusTimeline'
import ActivityNotification from '@/components/ActivityNotification'
import { AIAnalysis } from '@/components/AIAnalysis'
import { TranscriptViewer } from '@/components/TranscriptViewer'

interface FraudFlag {
  type: string
  severity: 'CRITICAL' | 'MODERATE' | 'MINOR'
  description: string
}

interface EmploymentNarrative {
  company: string
  title: string
  start_date: string
  end_date: string | null
  verification_status: string
  narrative: string
  reference_quotes?: string[]
}

interface TechnicalValidation {
  github_analysis?: {
    username: string
    profile_url: string
    total_repos: number
    total_commits: number
    commit_frequency: number
    languages: Record<string, number>
    code_quality_score: number
    skills_match: Record<string, boolean>
  }
  skills_match_percentage?: number
  narrative?: string
}

interface VerificationReport {
  risk_score: 'GREEN' | 'YELLOW' | 'RED'
  summary: string
  employment_narratives: EmploymentNarrative[]
  education_summary: string
  technical_validation: TechnicalValidation | null
  interview_questions: string[]
  fraud_flags: FraudFlag[]
  generated_at: string
}

interface VerificationDetail {
  session_id: string
  candidate_name: string
  candidate_email: string
  status: string
  created_at: string
  completed_at: string | null
  risk_score: 'GREEN' | 'YELLOW' | 'RED' | null
  report: VerificationReport | null
}

interface VerificationProgress {
  percentage: number
  documents_collected: boolean
  employment_verifications: number
  total_employments: number
  reference_checks: number
  total_references: number
  education_verifications: number
  total_education: number
  technical_analysis_complete: boolean
  fraud_flags: number
  report_generated: boolean
}

interface TimelineItem {
  activity: string
  status: 'completed' | 'in_progress' | 'pending'
  timestamp: string
  description: string
}

interface ActivityItem {
  type: string
  message: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
}

interface AIAnalysisData {
  verification_assessment?: string
  risk_analysis?: string
  cross_reference_validation?: string
  fraud_detection?: string
  technical_competency?: string
  recommendations?: string
  follow_up_actions?: string
  summary?: string
}

interface VerificationStatus {
  session_id: string
  status: string
  progress: VerificationProgress
  timeline: TimelineItem[]
  activities: ActivityItem[]
  estimated_completion: string | null
  last_updated: string
  ai_analysis?: AIAnalysisData
}

const riskScoreConfig = {
  GREEN: {
    label: 'Low Risk',
    description: 'All verifications passed with no significant concerns',
    color: 'text-green-700',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-300',
    iconBg: 'bg-green-100',
  },
  YELLOW: {
    label: 'Medium Risk',
    description: 'Some concerns identified that warrant further investigation',
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-50',
    borderColor: 'border-yellow-300',
    iconBg: 'bg-yellow-100',
  },
  RED: {
    label: 'High Risk',
    description: 'Critical issues found that require immediate attention',
    color: 'text-red-700',
    bgColor: 'bg-red-50',
    borderColor: 'border-red-300',
    iconBg: 'bg-red-100',
  },
}

const severityConfig = {
  CRITICAL: {
    label: 'Critical',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-300',
  },
  MODERATE: {
    label: 'Moderate',
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100',
    borderColor: 'border-yellow-300',
  },
  MINOR: {
    label: 'Minor',
    color: 'text-blue-700',
    bgColor: 'bg-blue-100',
    borderColor: 'border-blue-300',
  },
}

export default function VerificationDetail() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const [verification, setVerification] = useState<VerificationDetail | null>(null)
  const [verificationStatus, setVerificationStatus] = useState<VerificationStatus | null>(null)
  const [transcripts, setTranscripts] = useState<any[]>([])
  const [aiSummary, setAiSummary] = useState<string | null>(null)
  const [generatingAiSummary, setGeneratingAiSummary] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    summary: true,
    employment: true,
    education: true,
    technical: true,
    redFlags: true,
    questions: true,
    progress: true,
    timeline: true,
  })
  const [dismissedActivities, setDismissedActivities] = useState<Set<number>>(new Set())
  const pollingIntervalRef = useRef<number | null>(null)

  useEffect(() => {
    if (sessionId) {
      fetchVerification()
      fetchVerificationStatus()
      fetchTranscripts()
      
      // Start polling for status updates if verification is in progress
      startPolling()
    }

    return () => {
      stopPolling()
    }
  }, [sessionId])

  useEffect(() => {
    // Adjust polling based on verification status
    if (verification) {
      if (verification.status === 'COMPLETED' || verification.status === 'FAILED') {
        stopPolling()
      } else if (!pollingIntervalRef.current) {
        startPolling()
      }
    }
  }, [verification?.status])

  const startPolling = () => {
    // Poll every 30 seconds for status updates
    if (!pollingIntervalRef.current) {
      pollingIntervalRef.current = setInterval(() => {
        fetchVerificationStatus()
        // Also refresh main verification data less frequently
        if (Math.random() < 0.3) { // 30% chance each poll (roughly every 100 seconds)
          fetchVerification()
        }
      }, 30000)
    }
  }

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
  }

  const fetchVerification = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await apiClient.get<VerificationDetail>(`/api/verifications/${sessionId}`)
      setVerification(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load verification')
    } finally {
      setLoading(false)
    }
  }

  const [startingVerification, setStartingVerification] = useState(false)
  const [startError, setStartError] = useState<string | null>(null)

  const handleStartVerification = async () => {
    if (!sessionId) return

    const confirmed = window.confirm(
      '⚠️ WARNING: This will make REAL phone calls and send REAL emails!\n\n' +
      'This action will:\n' +
      '• Call HR departments for employment verification\n' +
      '• Call or email references\n' +
      '• Analyze GitHub profiles\n' +
      '• Detect fraud\n' +
      '• Generate a verification report\n\n' +
      'Are you sure you want to start verification?'
    )

    if (!confirmed) return

    try {
      setStartingVerification(true)
      setStartError(null)
      
      await verificationApi.startVerification(sessionId)
      
      // Refresh data and start polling
      await fetchVerification()
      await fetchVerificationStatus()
      startPolling()
      
    } catch (err) {
      setStartError(err instanceof Error ? err.message : 'Failed to start verification')
    } finally {
      setStartingVerification(false)
    }
  }

  const fetchVerificationStatus = async () => {
    try {
      const data = await apiClient.get<VerificationStatus>(`/api/verifications/${sessionId}/status`)
      setVerificationStatus(data)
    } catch (err) {
      console.error('Failed to fetch verification status:', err)
    }
  }

  const fetchTranscripts = async () => {
    try {
      const data = await apiClient.get<any>(`/api/verifications/${sessionId}/transcripts`)
      if (data.success) {
        setTranscripts(data.transcripts || [])
        
        // Auto-generate AI summary if we have transcripts
        if (data.transcripts && data.transcripts.length > 0 && !aiSummary) {
          generateAiSummary()
        }
      }
    } catch (err) {
      console.error('Failed to fetch transcripts:', err)
    }
  }

  const generateAiSummary = async () => {
    if (!sessionId) return
    
    setGeneratingAiSummary(true)
    try {
      const data = await apiClient.post<any>(`/api/verifications/${sessionId}/ai-summary`, {})
      if (data.success) {
        setAiSummary(data.summary)
      }
    } catch (err) {
      console.error('Failed to generate AI summary:', err)
    } finally {
      setGeneratingAiSummary(false)
    }
  }

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const handleDownloadPDF = async () => {
    // TODO: Implement PDF download
    alert('PDF download will be implemented')
  }

  const handleDismissActivity = (index: number) => {
    setDismissedActivities((prev) => new Set(prev).add(index))
  }

  const getVisibleActivities = () => {
    if (!verificationStatus?.activities) return []
    return verificationStatus.activities.filter((_, index) => !dismissedActivities.has(index))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (error || !verification) {
    return (
      <div className="flex flex-col items-center justify-center h-screen">
        <AlertTriangle className="h-12 w-12 text-red-500 mb-4" />
        <h2 className="text-xl font-semibold text-foreground mb-2">Error Loading Verification</h2>
        <p className="text-muted-foreground mb-4">{error || 'Verification not found'}</p>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Back to Dashboard
        </button>
      </div>
    )
  }

  const report = verification.report
  const riskInfo = verification.risk_score ? riskScoreConfig[verification.risk_score] : null

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Dashboard
        </button>
        <div className="flex items-center gap-3">
          {/* Start Verification Button */}
          {verification.status === 'DOCUMENTS_COLLECTED' && !report && (
            <button
              onClick={handleStartVerification}
              disabled={startingVerification}
              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {startingVerification ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Starting...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Start Verification
                </>
              )}
            </button>
          )}
          {report && (
            <button
              onClick={handleDownloadPDF}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
            >
              <Download className="h-4 w-4" />
              Download PDF
            </button>
          )}
        </div>
      </div>

      {/* Start Verification Error */}
      {startError && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3"
        >
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-red-900">Failed to Start Verification</h3>
            <p className="text-sm text-red-700 mt-1">{startError}</p>
          </div>
        </motion.div>
      )}

      {/* Candidate Info Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-card border border-border rounded-lg p-6"
      >
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-foreground">{verification.candidate_name}</h1>
            <p className="text-muted-foreground mt-1">{verification.candidate_email}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Created: {new Date(verification.created_at).toLocaleDateString()}
              {verification.completed_at && (
                <> • Completed: {new Date(verification.completed_at).toLocaleDateString()}</>
              )}
            </p>
          </div>
          {riskInfo && (
            <div className={cn('p-6 rounded-lg border-2', riskInfo.bgColor, riskInfo.borderColor)}>
              <div className="flex items-center gap-3">
                <div className={cn('p-3 rounded-full', riskInfo.iconBg)}>
                  <Shield className={cn('h-6 w-6', riskInfo.color)} />
                </div>
                <div>
                  <div className={cn('text-2xl font-bold', riskInfo.color)}>{riskInfo.label}</div>
                  <div className={cn('text-sm', riskInfo.color)}>{riskInfo.description}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Progress and Activities Section */}
      {!report && verificationStatus && (
        <>
          {/* Current Activities */}
          {getVisibleActivities().length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-card border border-border rounded-lg p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Activity className="h-5 w-5 text-primary" />
                </div>
                <h2 className="text-xl font-semibold text-foreground">Current Activities</h2>
              </div>
              <ActivityNotification
                activities={getVisibleActivities()}
                onDismiss={handleDismissActivity}
              />
            </motion.div>
          )}

          {/* Progress Section */}
          <CollapsibleSection
            title="Verification Progress"
            icon={Activity}
            isExpanded={expandedSections.progress}
            onToggle={() => toggleSection('progress')}
          >
            <div className="space-y-6">
              <ProgressBar
                percentage={verificationStatus.progress.percentage}
                label="Overall Progress"
                size="lg"
                color={
                  verificationStatus.progress.percentage === 100
                    ? 'green'
                    : verificationStatus.progress.percentage > 50
                    ? 'primary'
                    : 'yellow'
                }
              />

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <ProgressCard
                  label="Employment Verifications"
                  current={verificationStatus.progress.employment_verifications}
                  total={verificationStatus.progress.total_employments}
                  icon={Briefcase}
                />
                <ProgressCard
                  label="Reference Checks"
                  current={verificationStatus.progress.reference_checks}
                  total={verificationStatus.progress.total_references}
                  icon={MessageSquare}
                />
                <ProgressCard
                  label="Education Verifications"
                  current={verificationStatus.progress.education_verifications}
                  total={verificationStatus.progress.total_education}
                  icon={GraduationCap}
                />
              </div>

              {verificationStatus.estimated_completion && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  <span>
                    Estimated completion:{' '}
                    {new Date(verificationStatus.estimated_completion).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </CollapsibleSection>

          {/* Timeline Section */}
          {verificationStatus.timeline.length > 0 && (
            <CollapsibleSection
              title="Activity Timeline"
              icon={Clock}
              isExpanded={expandedSections.timeline}
              onToggle={() => toggleSection('timeline')}
            >
              <StatusTimeline items={verificationStatus.timeline} />
            </CollapsibleSection>
          )}
        </>
      )}

      {!report && !verificationStatus && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card border border-border rounded-lg p-12 text-center"
        >
          <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-foreground mb-2">Verification In Progress</h2>
          <p className="text-muted-foreground">
            The verification report is being generated. Please check back later.
          </p>
        </motion.div>
      )}

      {report && (
        <>
          {/* Summary Section */}
          <CollapsibleSection
            title="AI Executive Summary"
            icon={MessageSquare}
            isExpanded={expandedSections.summary}
            onToggle={() => toggleSection('summary')}
          >
            <div className="space-y-6">
              {generatingAiSummary ? (
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Generating AI summary from call transcripts...</span>
                </div>
              ) : aiSummary ? (
                <div className="prose max-w-none">
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-600 p-6 rounded-r-lg">
                    <div className="flex items-start gap-3 mb-4">
                      <div className="p-2 rounded-lg bg-blue-600 text-white">
                        <MessageSquare className="h-5 w-5" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 text-lg">AI-Generated Analysis</h3>
                        <p className="text-sm text-gray-600">Based on call transcripts and verification data</p>
                      </div>
                    </div>
                    <div className="text-gray-800 whitespace-pre-wrap leading-relaxed">
                      {aiSummary}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-foreground leading-relaxed">{report.summary}</p>
              )}
            </div>
          </CollapsibleSection>

          {/* Employment History Section */}
          {report.employment_narratives && report.employment_narratives.length > 0 && (
            <CollapsibleSection
              title="Employment History"
              icon={Briefcase}
              isExpanded={expandedSections.employment}
              onToggle={() => toggleSection('employment')}
            >
              <div className="space-y-6">
                {report.employment_narratives.map((employment, index) => (
                  <EmploymentCard key={index} employment={employment} />
                ))}
              </div>
            </CollapsibleSection>
          )}

          {/* Education Section */}
          {report.education_summary && (
            <CollapsibleSection
              title="Education Verification"
              icon={GraduationCap}
              isExpanded={expandedSections.education}
              onToggle={() => toggleSection('education')}
            >
              <p className="text-foreground leading-relaxed">{report.education_summary}</p>
            </CollapsibleSection>
          )}

          {/* Technical Validation Section */}
          {report.technical_validation && (
            <CollapsibleSection
              title="Technical Profile Analysis"
              icon={Code}
              isExpanded={expandedSections.technical}
              onToggle={() => toggleSection('technical')}
            >
              <TechnicalValidationCard validation={report.technical_validation} />
            </CollapsibleSection>
          )}

          {/* Red Flags Section */}
          {report.fraud_flags && report.fraud_flags.length > 0 && (
            <CollapsibleSection
              title={`Red Flags (${report.fraud_flags.length})`}
              icon={AlertTriangle}
              isExpanded={expandedSections.redFlags}
              onToggle={() => toggleSection('redFlags')}
            >
              <div className="space-y-3">
                {report.fraud_flags.map((flag, index) => (
                  <FraudFlagCard key={index} flag={flag} />
                ))}
              </div>
            </CollapsibleSection>
          )}

          {/* Interview Questions Section */}
          {report.interview_questions && report.interview_questions.length > 0 && (
            <CollapsibleSection
              title="Suggested Interview Questions"
              icon={MessageSquare}
              isExpanded={expandedSections.questions}
              onToggle={() => toggleSection('questions')}
            >
              <div className="space-y-3">
                {report.interview_questions.map((question, index) => (
                  <div
                    key={index}
                    className="flex gap-3 p-4 bg-muted/50 rounded-lg border border-border"
                  >
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-medium">
                      {index + 1}
                    </div>
                    <p className="text-foreground flex-1">{question}</p>
                  </div>
                ))}
              </div>
            </CollapsibleSection>
          )}

          {/* Call Transcripts Section - ALWAYS SHOW IF WE HAVE TRANSCRIPTS */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card border border-border rounded-lg p-6"
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 rounded-lg bg-primary/10">
                <MessageSquare className="h-5 w-5 text-primary" />
              </div>
              <h2 className="text-xl font-semibold text-foreground">
                Call Transcripts {transcripts.length > 0 && `(${transcripts.length})`}
              </h2>
            </div>
            <TranscriptViewer transcripts={transcripts} />
          </motion.div>
        </>
      )}

      {/* Show transcripts even if no report yet */}
      {!report && transcripts.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-card border border-border rounded-lg p-6"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 rounded-lg bg-primary/10">
              <MessageSquare className="h-5 w-5 text-primary" />
            </div>
            <h2 className="text-xl font-semibold text-foreground">
              Call Transcripts ({transcripts.length})
            </h2>
          </div>
          <TranscriptViewer transcripts={transcripts} />
        </motion.div>
      )}
    </div>
  )
}

// Collapsible Section Component
interface CollapsibleSectionProps {
  title: string
  icon: React.ElementType
  isExpanded: boolean
  onToggle: () => void
  children: React.ReactNode
}

function CollapsibleSection({
  title,
  icon: Icon,
  isExpanded,
  onToggle,
  children,
}: CollapsibleSectionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-border rounded-lg overflow-hidden"
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-6 hover:bg-muted/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-primary/10">
            <Icon className="h-5 w-5 text-primary" />
          </div>
          <h2 className="text-xl font-semibold text-foreground">{title}</h2>
        </div>
        {isExpanded ? (
          <ChevronUp className="h-5 w-5 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-5 w-5 text-muted-foreground" />
        )}
      </button>
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="p-6 pt-0 border-t border-border">{children}</div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

// Employment Card Component
interface EmploymentCardProps {
  employment: EmploymentNarrative
}

function EmploymentCard({ employment }: EmploymentCardProps) {
  const isVerified = employment.verification_status === 'VERIFIED'
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      year: 'numeric',
    }).format(date)
  }
  
  const dateRange = employment.end_date
    ? `${formatDate(employment.start_date)} - ${formatDate(employment.end_date)}`
    : `${formatDate(employment.start_date)} - Present`

  return (
    <div className="border border-border rounded-lg p-5 space-y-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <Building className="h-5 w-5 text-muted-foreground" />
            <h3 className="text-lg font-semibold text-foreground">{employment.company}</h3>
          </div>
          <p className="text-foreground font-medium">{employment.title}</p>
          <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            {dateRange}
          </div>
        </div>
        <div
          className={cn(
            'flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium',
            isVerified
              ? 'bg-green-100 text-green-700 border border-green-300'
              : 'bg-gray-100 text-gray-700 border border-gray-300'
          )}
        >
          {isVerified ? (
            <CheckCircle className="h-4 w-4" />
          ) : (
            <XCircle className="h-4 w-4" />
          )}
          {employment.verification_status}
        </div>
      </div>

      <p className="text-foreground leading-relaxed">{employment.narrative}</p>

      {employment.reference_quotes && employment.reference_quotes.length > 0 && (
        <div className="space-y-3 pt-3 border-t border-border">
          <h4 className="text-sm font-semibold text-foreground">Reference Feedback</h4>
          {employment.reference_quotes.map((quote, index) => (
            <div key={index} className="bg-muted/50 rounded-lg p-4">
              <p className="text-sm text-muted-foreground italic">"{quote}"</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// Technical Validation Card Component
interface TechnicalValidationCardProps {
  validation: TechnicalValidation
}

function TechnicalValidationCard({ validation }: TechnicalValidationCardProps) {
  const github = validation.github_analysis

  return (
    <div className="space-y-6">
      {validation.narrative && (
        <p className="text-foreground leading-relaxed">{validation.narrative}</p>
      )}

      {github && (
        <div className="border border-border rounded-lg p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gray-900">
                <Github className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-foreground">GitHub Profile</h3>
                <a
                  href={github.profile_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-primary hover:underline"
                >
                  @{github.username}
                </a>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-foreground">{github.code_quality_score}/10</div>
              <div className="text-sm text-muted-foreground">Code Quality</div>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Repositories" value={github.total_repos} />
            <StatCard label="Total Commits" value={github.total_commits} />
            <StatCard
              label="Commit Frequency"
              value={`${github.commit_frequency.toFixed(1)}/mo`}
            />
            <StatCard
              label="Skills Match"
              value={`${validation.skills_match_percentage || 0}%`}
            />
          </div>

          {github.languages && Object.keys(github.languages).length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-3">Language Distribution</h4>
              <div className="space-y-2">
                {Object.entries(github.languages)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([lang, percentage]) => (
                    <div key={lang} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span className="text-foreground">{lang}</span>
                        <span className="text-muted-foreground">{percentage.toFixed(1)}%</span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full transition-all"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// Stat Card Component
interface StatCardProps {
  label: string
  value: string | number
}

function StatCard({ label, value }: StatCardProps) {
  return (
    <div className="bg-muted/50 rounded-lg p-4">
      <div className="text-2xl font-bold text-foreground">{value}</div>
      <div className="text-sm text-muted-foreground mt-1">{label}</div>
    </div>
  )
}

// Fraud Flag Card Component
interface FraudFlagCardProps {
  flag: FraudFlag
}

function FraudFlagCard({ flag }: FraudFlagCardProps) {
  const severityInfo = severityConfig[flag.severity]

  return (
    <div className="flex gap-4 p-4 border border-border rounded-lg bg-card">
      <div className="flex-shrink-0">
        <AlertTriangle className={cn('h-5 w-5', severityInfo.color)} />
      </div>
      <div className="flex-1">
        <div className="flex items-center gap-3 mb-2">
          <h4 className="font-semibold text-foreground">{flag.type.replace(/_/g, ' ')}</h4>
          <span
            className={cn(
              'px-2 py-1 rounded-full text-xs font-medium border',
              severityInfo.bgColor,
              severityInfo.color,
              severityInfo.borderColor
            )}
          >
            {severityInfo.label}
          </span>
        </div>
        <p className="text-sm text-muted-foreground">{flag.description}</p>
      </div>
    </div>
  )
}

// Progress Card Component
interface ProgressCardProps {
  label: string
  current: number
  total: number
  icon: React.ElementType
}

function ProgressCard({ label, current, total, icon: Icon }: ProgressCardProps) {
  const percentage = total > 0 ? (current / total) * 100 : 0
  const isComplete = current === total && total > 0

  return (
    <div className="bg-muted/50 rounded-lg p-4 border border-border">
      <div className="flex items-center gap-3 mb-3">
        <div className={cn('p-2 rounded-lg', isComplete ? 'bg-green-100' : 'bg-primary/10')}>
          <Icon className={cn('h-4 w-4', isComplete ? 'text-green-600' : 'text-primary')} />
        </div>
        <div className="flex-1">
          <div className="text-sm font-medium text-foreground">{label}</div>
          <div className="text-xs text-muted-foreground">
            {current} of {total} completed
          </div>
        </div>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <motion.div
          className={cn('h-full rounded-full', isComplete ? 'bg-green-500' : 'bg-primary')}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}
