import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Search, 
  Filter, 
  CheckCircle, 
  Clock, 
  AlertTriangle,
  FileText,
  ChevronRight,
  UserPlus
} from 'lucide-react'
import { apiClient } from '@/lib/api'
import { cn } from '@/lib/utils'
import { VerificationListSkeleton } from './LoadingSkeleton'
import EmptyState from './EmptyState'
import ErrorState from './ErrorState'

interface Verification {
  session_id: string
  candidate_name: string
  status: string
  risk_score: 'GREEN' | 'YELLOW' | 'RED' | null
  created_at: string
  completed_at: string | null
}

interface VerificationListResponse {
  verifications: Verification[]
  total: number
  limit: number
  offset: number
}

const statusConfig = {
  PENDING_DOCUMENTS: {
    label: 'Pending Documents',
    icon: FileText,
    color: 'text-gray-500',
    bgColor: 'bg-gray-100',
  },
  DOCUMENTS_COLLECTED: {
    label: 'Documents Collected',
    icon: CheckCircle,
    color: 'text-blue-500',
    bgColor: 'bg-blue-100',
  },
  VERIFICATION_IN_PROGRESS: {
    label: 'In Progress',
    icon: Clock,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-100',
  },
  COMPLETED: {
    label: 'Completed',
    icon: CheckCircle,
    color: 'text-green-500',
    bgColor: 'bg-green-100',
  },
  FAILED: {
    label: 'Failed',
    icon: AlertTriangle,
    color: 'text-red-500',
    bgColor: 'bg-red-100',
  },
}

const riskScoreConfig = {
  GREEN: {
    label: 'Low Risk',
    color: 'text-green-700',
    bgColor: 'bg-green-100',
    borderColor: 'border-green-300',
  },
  YELLOW: {
    label: 'Medium Risk',
    color: 'text-yellow-700',
    bgColor: 'bg-yellow-100',
    borderColor: 'border-yellow-300',
  },
  RED: {
    label: 'High Risk',
    color: 'text-red-700',
    bgColor: 'bg-red-100',
    borderColor: 'border-red-300',
  },
}

export default function VerificationList() {
  const navigate = useNavigate()
  const [verifications, setVerifications] = useState<Verification[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [riskFilter, setRiskFilter] = useState<string>('all')

  useEffect(() => {
    fetchVerifications()
  }, [])

  const fetchVerifications = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiClient.get<VerificationListResponse>('/api/verifications')
      setVerifications(response.verifications)
    } catch (error) {
      console.error('Failed to fetch verifications:', error)
      setError('Failed to load verifications. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const filteredVerifications = verifications.filter((verification) => {
    const matchesSearch = verification.candidate_name
      .toLowerCase()
      .includes(searchQuery.toLowerCase())
    
    const matchesStatus = 
      statusFilter === 'all' || verification.status === statusFilter
    
    const matchesRisk = 
      riskFilter === 'all' || 
      (riskFilter === 'none' && !verification.risk_score) ||
      verification.risk_score === riskFilter

    return matchesSearch && matchesStatus && matchesRisk
  })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  if (loading) {
    return <VerificationListSkeleton />
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchVerifications} />
  }

  if (verifications.length === 0 && !searchQuery && statusFilter === 'all' && riskFilter === 'all') {
    return (
      <EmptyState
        icon={FileText}
        title="No verifications yet"
        description="Get started by creating your first candidate verification. It only takes a few seconds."
        action={{
          label: 'Create Verification',
          onClick: () => navigate('/verifications/create')
        }}
      />
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
        >
          <h1 className="text-3xl font-bold text-foreground">Verifications</h1>
          <p className="text-muted-foreground mt-1">
            {filteredVerifications.length} of {verifications.length} verifications
          </p>
        </motion.div>
        <motion.button
          onClick={() => navigate('/verifications/create')}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-all shadow-sm hover:shadow-md"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4 }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <UserPlus className="h-5 w-5" />
          Create Verification
        </motion.button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by candidate name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {/* Status Filter */}
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="pl-10 pr-8 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary appearance-none cursor-pointer"
          >
            <option value="all">All Statuses</option>
            <option value="PENDING_DOCUMENTS">Pending Documents</option>
            <option value="DOCUMENTS_COLLECTED">Documents Collected</option>
            <option value="VERIFICATION_IN_PROGRESS">In Progress</option>
            <option value="COMPLETED">Completed</option>
            <option value="FAILED">Failed</option>
          </select>
        </div>

        {/* Risk Filter */}
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="pl-10 pr-8 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary appearance-none cursor-pointer"
          >
            <option value="all">All Risk Levels</option>
            <option value="GREEN">Low Risk</option>
            <option value="YELLOW">Medium Risk</option>
            <option value="RED">High Risk</option>
            <option value="none">Not Assessed</option>
          </select>
        </div>
      </div>

      {/* Desktop Table View */}
      <div className="hidden lg:block bg-card border border-border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted/50 border-b border-border">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Candidate
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Risk Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Completed
              </th>
              <th className="px-6 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            <AnimatePresence mode="popLayout">
              {filteredVerifications.map((verification, index) => {
                const statusInfo = statusConfig[verification.status as keyof typeof statusConfig]
                const StatusIcon = statusInfo.icon
                const riskInfo = verification.risk_score 
                  ? riskScoreConfig[verification.risk_score]
                  : null

                return (
                  <motion.tr
                    key={verification.session_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.2, delay: index * 0.05 }}
                    className="hover:bg-muted/50 transition-colors cursor-pointer group"
                    onClick={() => navigate(`/verifications/${verification.session_id}`)}
                    whileHover={{ scale: 1.005 }}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-foreground">
                        {verification.candidate_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <div className={cn('p-1 rounded', statusInfo.bgColor)}>
                          <StatusIcon className={cn('h-4 w-4', statusInfo.color)} />
                        </div>
                        <span className="text-sm text-foreground">
                          {statusInfo.label}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {riskInfo ? (
                        <div className={cn(
                          'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border',
                          riskInfo.bgColor,
                          riskInfo.color,
                          riskInfo.borderColor
                        )}>
                          {riskInfo.label}
                        </div>
                      ) : (
                        <span className="text-sm text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                      {formatDate(verification.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                      {verification.completed_at ? formatDate(verification.completed_at) : '—'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:translate-x-1 transition-transform" />
                    </td>
                  </motion.tr>
                )
              })}
            </AnimatePresence>
          </tbody>
        </table>

        {filteredVerifications.length === 0 && (
          <motion.div 
            className="text-center py-12"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No verifications match your filters</p>
            <p className="text-sm text-muted-foreground mt-2">Try adjusting your search or filters</p>
          </motion.div>
        )}
      </div>

      {/* Mobile Card View */}
      <div className="lg:hidden space-y-4">
        <AnimatePresence mode="popLayout">
          {filteredVerifications.map((verification, index) => {
            const statusInfo = statusConfig[verification.status as keyof typeof statusConfig]
            const StatusIcon = statusInfo.icon
            const riskInfo = verification.risk_score 
              ? riskScoreConfig[verification.risk_score]
              : null

            return (
              <motion.div
                key={verification.session_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2, delay: index * 0.05 }}
                className="bg-card border border-border rounded-lg p-4 hover:shadow-lg hover:border-primary/20 transition-all cursor-pointer group"
                onClick={() => navigate(`/verifications/${verification.session_id}`)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-semibold text-foreground">
                      {verification.candidate_name}
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      {formatDate(verification.created_at)}
                    </p>
                  </div>
                  <ChevronRight className="h-5 w-5 text-muted-foreground flex-shrink-0 group-hover:translate-x-1 transition-transform" />
                </div>

                <div className="flex items-center gap-2 mb-3">
                  <div className={cn('p-1 rounded', statusInfo.bgColor)}>
                    <StatusIcon className={cn('h-4 w-4', statusInfo.color)} />
                  </div>
                  <span className="text-sm text-foreground">
                    {statusInfo.label}
                  </span>
                </div>

                {riskInfo && (
                  <div className={cn(
                    'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border',
                    riskInfo.bgColor,
                    riskInfo.color,
                    riskInfo.borderColor
                  )}>
                    {riskInfo.label}
                  </div>
                )}

                {verification.completed_at && (
                  <div className="mt-3 pt-3 border-t border-border">
                    <p className="text-xs text-muted-foreground">
                      Completed: {formatDate(verification.completed_at)}
                    </p>
                  </div>
                )}
              </motion.div>
            )
          })}
        </AnimatePresence>

        {filteredVerifications.length === 0 && (
          <motion.div 
            className="text-center py-12 bg-card border border-border rounded-lg"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4 }}
          >
            <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No verifications match your filters</p>
            <p className="text-sm text-muted-foreground mt-2">Try adjusting your search or filters</p>
          </motion.div>
        )}
      </div>
    </div>
  )
}
