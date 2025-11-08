"use client";

import { Badge } from '@/src/components/ui/badge';
import { cn } from '@/lib/utils';
import { 
  Shield, 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle 
} from 'lucide-react';

export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  showIcon?: boolean;
  className?: string;
}

const riskConfig = {
  low: {
    label: 'Low Risk',
    color: 'bg-green-500/10 text-green-400 border-green-500/30 hover:bg-green-500/20',
    icon: ShieldCheck,
  },
  medium: {
    label: 'Medium Risk',
    color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30 hover:bg-yellow-500/20',
    icon: Shield,
  },
  high: {
    label: 'High Risk',
    color: 'bg-orange-500/10 text-orange-400 border-orange-500/30 hover:bg-orange-500/20',
    icon: ShieldAlert,
  },
  critical: {
    label: 'Critical Risk',
    color: 'bg-red-500/10 text-red-400 border-red-500/30 hover:bg-red-500/20',
    icon: AlertTriangle,
  },
};

export function RiskBadge({ 
  level, 
  score, 
  showIcon = true,
  className = '' 
}: RiskBadgeProps) {
  const config = riskConfig[level];
  const Icon = config.icon;

  return (
    <Badge 
      variant="outline" 
      className={cn(
        'flex items-center gap-1.5 px-3 py-1 transition-all',
        config.color,
        className
      )}
    >
      {showIcon && <Icon className="w-3.5 h-3.5" />}
      <span className="font-medium">{config.label}</span>
      {score !== undefined && (
        <span className="ml-1 opacity-70">({score}%)</span>
      )}
    </Badge>
  );
}

/**
 * Utility function to determine risk level from a score (0-100)
 */
export function getRiskLevel(score: number): RiskLevel {
  if (score >= 75) return 'critical';
  if (score >= 50) return 'high';
  if (score >= 25) return 'medium';
  return 'low';
}
