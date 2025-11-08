import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, Clock, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TimelineItem {
  activity: string
  status: 'completed' | 'in_progress' | 'pending'
  timestamp: string
  description: string
}

interface StatusTimelineProps {
  items: TimelineItem[]
  maxItems?: number
}

export default function StatusTimeline({ items, maxItems = 10 }: StatusTimelineProps) {
  const displayItems = items.slice(0, maxItems)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'in_progress':
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
      case 'pending':
        return <Clock className="h-5 w-5 text-gray-400" />
      default:
        return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-300 bg-green-50'
      case 'in_progress':
        return 'border-blue-300 bg-blue-50'
      case 'pending':
        return 'border-gray-300 bg-gray-50'
      default:
        return 'border-gray-300 bg-gray-50'
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    }).format(date)
  }

  if (displayItems.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p>No activities yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <AnimatePresence mode="popLayout">
        {displayItems.map((item, index) => (
          <motion.div
            key={`${item.activity}-${item.timestamp}`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className={cn(
              'flex gap-4 p-4 rounded-lg border-2',
              getStatusColor(item.status)
            )}
          >
            <div className="flex-shrink-0 mt-0.5">{getStatusIcon(item.status)}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2 mb-1">
                <h4 className="font-semibold text-foreground text-sm">{item.activity}</h4>
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                  {formatTimestamp(item.timestamp)}
                </span>
              </div>
              <p className="text-sm text-muted-foreground">{item.description}</p>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
