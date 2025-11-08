"use client";

import { motion } from 'framer-motion';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { Card, CardContent } from '@/src/components/ui/card';
import { scaleIn, hoverLift } from '@/lib/animations';

export interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
  description?: string;
  className?: string;
}

export function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  description,
  className = '' 
}: StatCardProps) {
  const trendColor = trend?.direction === 'up' ? 'text-green-400' : 'text-red-400';
  const TrendIcon = trend?.direction === 'up' ? TrendingUp : TrendingDown;

  return (
    <motion.div
      variants={scaleIn}
      whileHover="hover"
      className={className}
    >
      <Card className="glass border-white/10 hover:border-purple-500/50 transition-all">
        <CardContent className="p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm text-[#9ca3af] mb-1">{title}</p>
              <h3 className="text-3xl font-bold text-white mb-2">{value}</h3>
              
              {trend && (
                <div className={`flex items-center gap-1 text-sm ${trendColor}`}>
                  <TrendIcon className="w-4 h-4" />
                  <span>{Math.abs(trend.value)}%</span>
                  <span className="text-[#6b7280] ml-1">vs last month</span>
                </div>
              )}
              
              {description && !trend && (
                <p className="text-sm text-[#6b7280]">{description}</p>
              )}
            </div>
            
            <div className="p-3 bg-gradient-to-br from-purple-600/20 to-blue-600/20 rounded-lg border border-purple-500/30">
              <Icon className="w-6 h-6 text-purple-400" />
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
