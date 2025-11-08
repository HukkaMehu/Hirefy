import { motion } from 'framer-motion'

interface LoadingSkeletonProps {
  className?: string
  variant?: 'text' | 'card' | 'circle' | 'button'
  count?: number
}

export default function LoadingSkeleton({ 
  className = '', 
  variant = 'text',
  count = 1 
}: LoadingSkeletonProps) {
  const baseClasses = 'bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded animate-pulse'
  
  const variantClasses = {
    text: 'h-4 w-full',
    card: 'h-32 w-full',
    circle: 'h-12 w-12 rounded-full',
    button: 'h-10 w-24'
  }

  const skeletons = Array.from({ length: count }, (_, i) => (
    <motion.div
      key={i}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: i * 0.1 }}
    />
  ))

  return count > 1 ? <div className="space-y-3">{skeletons}</div> : skeletons[0]
}

export function VerificationListSkeleton() {
  return (
    <div className="space-y-4">
      {Array.from({ length: 5 }).map((_, i) => (
        <motion.div
          key={i}
          className="bg-white rounded-lg border border-gray-200 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex-1 space-y-3">
              <LoadingSkeleton variant="text" className="w-1/3" />
              <LoadingSkeleton variant="text" className="w-1/4" />
            </div>
            <LoadingSkeleton variant="circle" />
          </div>
        </motion.div>
      ))}
    </div>
  )
}

export function VerificationDetailSkeleton() {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <LoadingSkeleton variant="text" className="w-1/2 h-8 mb-4" />
        <LoadingSkeleton variant="text" className="w-1/3" />
      </div>
      
      {Array.from({ length: 3 }).map((_, i) => (
        <motion.div
          key={i}
          className="bg-white rounded-lg border border-gray-200 p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.15 }}
        >
          <LoadingSkeleton variant="text" className="w-1/4 h-6 mb-4" />
          <div className="space-y-2">
            <LoadingSkeleton variant="text" />
            <LoadingSkeleton variant="text" className="w-5/6" />
            <LoadingSkeleton variant="text" className="w-4/6" />
          </div>
        </motion.div>
      ))}
    </div>
  )
}
