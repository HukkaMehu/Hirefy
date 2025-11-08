"use client";

import { motion } from 'framer-motion';
import { LucideIcon, Activity, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/card';
import { Badge } from '@/src/components/ui/badge';
import { scaleIn } from '@/lib/animations';
import { cn } from '@/lib/utils';

export type AgentStatus = 'active' | 'idle' | 'processing' | 'error';

export interface AgentCardProps {
  name: string;
  icon: LucideIcon;
  status: AgentStatus;
  activeCount?: number;
  completedToday?: number;
  lastActivity?: string;
  className?: string;
}

const statusConfig = {
  active: {
    label: 'Active',
    color: 'bg-green-500/10 text-green-400 border-green-500/30',
    dotColor: 'bg-green-400',
  },
  idle: {
    label: 'Idle',
    color: 'bg-gray-500/10 text-gray-400 border-gray-500/30',
    dotColor: 'bg-gray-400',
  },
  processing: {
    label: 'Processing',
    color: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
    dotColor: 'bg-blue-400',
  },
  error: {
    label: 'Error',
    color: 'bg-red-500/10 text-red-400 border-red-500/30',
    dotColor: 'bg-red-400',
  },
};

export function AgentCard({ 
  name,
  icon: Icon,
  status,
  activeCount,
  completedToday,
  lastActivity,
  className = ''
}: AgentCardProps) {
  const config = statusConfig[status];
  const isPulsing = status === 'active' || status === 'processing';

  return (
    <motion.div
      variants={scaleIn}
      whileHover={{ scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className={className}
    >
      <Card className="glass border-white/10 hover:border-purple-500/50 transition-all">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-lg border border-purple-500/30">
                <Icon className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <CardTitle className="text-base text-white">{name}</CardTitle>
              </div>
            </div>
            
            <Badge 
              variant="outline" 
              className={cn(
                'flex items-center gap-1.5 px-2 py-0.5',
                config.color
              )}
            >
              <span 
                className={cn(
                  'w-2 h-2 rounded-full',
                  config.dotColor,
                  isPulsing && 'animate-pulse'
                )}
              />
              <span className="text-xs">{config.label}</span>
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-3">
          {/* Stats */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2 text-[#9ca3af]">
              <Activity className="w-4 h-4" />
              <span>Active</span>
            </div>
            <span className="font-semibold text-white">
              {activeCount !== undefined ? activeCount : '—'}
            </span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2 text-[#9ca3af]">
              <span>Completed Today</span>
            </div>
            <span className="font-semibold text-white">
              {completedToday !== undefined ? completedToday : '—'}
            </span>
          </div>

          {/* Last Activity */}
          {lastActivity && (
            <div className="pt-2 border-t border-white/10">
              <div className="flex items-center gap-2 text-xs text-[#6b7280]">
                <Clock className="w-3.5 h-3.5" />
                <span>Last activity: {lastActivity}</span>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
