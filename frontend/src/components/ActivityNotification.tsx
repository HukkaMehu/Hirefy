import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, Loader2, AlertCircle, X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface Activity {
  type: string
  message: string
  status: 'pending' | 'in_progress' | 'completed' | 'error'
}

interface ActivityNotificationProps {
  activities: Activity[]
  onDismiss?: (index: number) => void
}

export default function ActivityNotification({
  activities,
  onDismiss,
}: ActivityNotificationProps) {
  const getActivityIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'in_progress':
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-600" />
      case 'pending':
        return <Loader2 className="h-5 w-5 text-gray-400" />
      default:
        return <Loader2 className="h-5 w-5 text-gray-400" />
    }
  }

  const getActivityColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-300 bg-green-50'
      case 'in_progress':
        return 'border-blue-300 bg-blue-50'
      case 'error':
        return 'border-red-300 bg-red-50'
      case 'pending':
        return 'border-gray-300 bg-gray-50'
      default:
        return 'border-gray-300 bg-gray-50'
    }
  }

  if (activities.length === 0) {
    return null
  }

  return (
    <div className="space-y-2">
      <AnimatePresence mode="popLayout">
        {activities.map((activity, index) => (
          <motion.div
            key={`${activity.type}-${index}`}
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className={cn(
              'flex items-center gap-3 p-3 rounded-lg border-2 shadow-sm',
              getActivityColor(activity.status)
            )}
          >
            <div className="flex-shrink-0">{getActivityIcon(activity.status)}</div>
            <p className="flex-1 text-sm font-medium text-foreground">{activity.message}</p>
            {onDismiss && activity.status === 'completed' && (
              <button
                onClick={() => onDismiss(index)}
                className="flex-shrink-0 p-1 hover:bg-black/5 rounded transition-colors"
                aria-label="Dismiss notification"
              >
                <X className="h-4 w-4 text-muted-foreground" />
              </button>
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  )
}
