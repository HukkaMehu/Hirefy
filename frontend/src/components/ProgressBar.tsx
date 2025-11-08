import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface ProgressBarProps {
  percentage: number
  label?: string
  showPercentage?: boolean
  size?: 'sm' | 'md' | 'lg'
  color?: 'primary' | 'green' | 'yellow' | 'red'
}

const sizeConfig = {
  sm: 'h-1',
  md: 'h-2',
  lg: 'h-3',
}

const colorConfig = {
  primary: 'bg-primary',
  green: 'bg-green-500',
  yellow: 'bg-yellow-500',
  red: 'bg-red-500',
}

export default function ProgressBar({
  percentage,
  label,
  showPercentage = true,
  size = 'md',
  color = 'primary',
}: ProgressBarProps) {
  const clampedPercentage = Math.min(Math.max(percentage, 0), 100)

  return (
    <div className="w-full">
      {(label || showPercentage) && (
        <div className="flex items-center justify-between mb-2">
          {label && <span className="text-sm font-medium text-foreground">{label}</span>}
          {showPercentage && (
            <span className="text-sm font-medium text-muted-foreground">
              {clampedPercentage}%
            </span>
          )}
        </div>
      )}
      <div className={cn('w-full bg-muted rounded-full overflow-hidden', sizeConfig[size])}>
        <motion.div
          className={cn('h-full rounded-full', colorConfig[color])}
          initial={{ width: 0 }}
          animate={{ width: `${clampedPercentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}
