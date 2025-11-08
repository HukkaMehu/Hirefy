"use client";

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  Users, 
  AlertTriangle, 
  CheckCircle,
  FileSearch,
  Bot,
  Phone,
  Clock,
  ArrowRight,
  Plus
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { StatCard } from '@/src/components/dashboard/StatCard';
import { AgentCard } from '@/src/components/dashboard/AgentCard';
import { RiskBadge, getRiskLevel } from '@/src/components/dashboard/RiskBadge';
import { SkeletonStatCard, SkeletonTableRow } from '@/src/components/dashboard/SkeletonCard';
import { Button } from '@/src/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/card';
import { staggerChildren, fadeIn } from '@/lib/animations';
import { getVerifications, calculateStats, type Verification } from '@/lib/supabase';
import { toast } from 'sonner';

// Mock data for agents (will be replaced with real agent status)
const mockAgents = [
  {
    name: 'HR Verification',
    icon: Phone,
    status: 'active' as const,
    activeCount: 3,
    completedToday: 12,
    lastActivity: '2 min ago',
  },
  {
    name: 'Reference Check',
    icon: Users,
    status: 'processing' as const,
    activeCount: 2,
    completedToday: 8,
    lastActivity: '5 min ago',
  },
  {
    name: 'Analysis Agent',
    icon: Bot,
    status: 'idle' as const,
    activeCount: 0,
    completedToday: 15,
    lastActivity: '15 min ago',
  },
];

function getRelativeTime(timestamp: string): string {
  const now = Date.now();
  const then = new Date(timestamp).getTime();
  const diffMs = now - then;
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min ago`;
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}

export default function DashboardPage() {
  const router = useRouter();
  const [verifications, setVerifications] = useState<Verification[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    inProgress: 0,
    completed: 0,
    flagged: 0,
    verified: 0,
    verifiedPercentage: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        
        // Fetch all verifications
        const data = await getVerifications({ limit: 100 });
        
        setVerifications(data);
        
        // Calculate stats
        const calculatedStats = calculateStats(data);
        setStats(calculatedStats);
      } catch (err) {
        toast.error('Failed to load verifications');
        console.error('Error:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  // Get recent activity (last 5 verifications)
  const recentActivity = verifications.slice(0, 5);

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={staggerChildren}
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={fadeIn}>
        <h1 className="text-4xl font-bold mb-2 gradient-text">Dashboard</h1>
        <p className="text-[#9ca3af]">
          Welcome back! Here&apos;s what&apos;s happening with your verifications today.
        </p>
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={fadeIn} className="flex gap-3">
        <Button 
          onClick={() => router.push('/dashboard/new')}
          className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Verification
        </Button>
        <Button 
          variant="outline"
          onClick={() => router.push('/dashboard/verifications')}
          className="border-white/10 hover:bg-white/5"
        >
          <FileSearch className="w-4 h-4 mr-2" />
          View All
        </Button>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        variants={staggerChildren}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
      >
        {loading ? (
          <>
            <SkeletonStatCard />
            <SkeletonStatCard />
            <SkeletonStatCard />
            <SkeletonStatCard />
          </>
        ) : (
          <>
            <StatCard
              title="Total Verifications"
              value={stats.total}
              icon={Users}
              trend={{ value: 12, direction: 'up' }}
            />
            <StatCard
              title="In Progress"
              value={stats.inProgress}
              icon={Clock}
              trend={{ value: 2, direction: 'up' }}
            />
            <StatCard
              title="Completed"
              value={stats.completed}
              icon={CheckCircle}
              trend={{ value: 10, direction: 'up' }}
            />
            <StatCard
              title="Flagged"
              value={stats.flagged}
              icon={AlertTriangle}
              trend={{ value: 8, direction: 'down' }}
            />
          </>
        )}
      </motion.div>

      {/* Agents Section */}
      <motion.div variants={fadeIn}>
        <h2 className="text-2xl font-semibold mb-4 text-white">AI Agents</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {mockAgents.map((agent) => (
            <AgentCard key={agent.name} {...agent} />
          ))}
        </div>
      </motion.div>

      {/* Recent Activity */}
      <motion.div variants={fadeIn}>
        <Card className="glass border-white/10">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl text-white">Recent Activity</CardTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push('/dashboard/verifications')}
                className="text-blue-400 hover:text-blue-300 hover:bg-white/5"
              >
                View All
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {loading ? (
                <>
                  <SkeletonTableRow />
                  <SkeletonTableRow />
                  <SkeletonTableRow />
                  <SkeletonTableRow />
                  <SkeletonTableRow />
                </>
              ) : recentActivity.length === 0 ? (
                <div className="empty-state py-12">
                  <FileSearch className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-[#6b7280] mb-4">No verifications yet</p>
                  <Button
                    onClick={() => router.push('/dashboard/new')}
                    className="bg-gradient-to-r from-purple-600 to-blue-600"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Start First Verification
                  </Button>
                </div>
              ) : (
                recentActivity.map((verification) => {
                  const riskLevel = verification.result?.risk_level 
                    ? getRiskLevel(verification.result.risk_score || 0)
                    : 'low';
                  
                  return (
                    <button
                      key={verification.id}
                      onClick={() => router.push(`/dashboard/report/${verification.id}`)}
                      className="w-full glass-hover rounded-lg p-4 flex items-center justify-between group transition-all"
                    >
                      <div className="flex items-center gap-4">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            verification.status === 'completed'
                              ? 'bg-green-400'
                              : verification.status === 'failed'
                              ? 'bg-red-400'
                              : 'bg-yellow-400 animate-pulse'
                          }`}
                        />
                        <div className="text-left">
                          <div className="font-medium text-white mb-1">
                            {verification.candidate_name}
                          </div>
                          <div className="text-sm text-[#6b7280]">
                            {verification.position} • {getRelativeTime(verification.created_at)}
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <RiskBadge level={riskLevel} score={verification.result?.risk_score || 0} />
                        <ArrowRight className="w-4 h-4 text-[#6b7280] group-hover:text-purple-400 transition-colors" />
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
