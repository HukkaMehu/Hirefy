"use client";

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter, useParams } from 'next/navigation';
import { 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Github,
  Phone,
  Users,
  FileText,
  Shield,
  ArrowRight,
  Loader2
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/card';
import { Progress } from '@/src/components/ui/progress';
import { Button } from '@/src/components/ui/button';
import { Badge } from '@/src/components/ui/badge';
import { staggerChildren, fadeIn } from '@/lib/animations';
import { 
  getVerification, 
  getVerificationSteps, 
  subscribeToVerificationSteps,
  subscribeToVerification,
  type Verification,
  type VerificationStep 
} from '@/lib/supabase';
import { toast } from 'sonner';

interface AgentStatus {
  name: string;
  icon: typeof Github;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'skipped';
  message: string;
  startedAt?: string;
  completedAt?: string;
}

export default function ProgressPage() {
  const router = useRouter();
  const params = useParams();
  const verificationId = params.id as string;

  const [verification, setVerification] = useState<Verification | null>(null);
  const [steps, setSteps] = useState<VerificationStep[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);

        // Fetch verification details
        const verificationData = await getVerification(verificationId);
        setVerification(verificationData);

        // Fetch verification steps
        const stepsData = await getVerificationSteps(verificationId);
        setSteps(stepsData);

        // Subscribe to realtime updates for steps
        const stepsChannel = subscribeToVerificationSteps(verificationId, (newStep) => {
          setSteps((prevSteps) => {
            const existingIndex = prevSteps.findIndex(s => s.agent_name === newStep.agent_name);
            if (existingIndex >= 0) {
              // Update existing step
              const updated = [...prevSteps];
              updated[existingIndex] = newStep;
              return updated;
            } else {
              // Add new step
              return [...prevSteps, newStep];
            }
          });
        });

        // Subscribe to verification status updates
        const verificationChannel = subscribeToVerification(verificationId, (updatedVerification) => {
          setVerification(updatedVerification);
          
          // Check if verification is complete
          if (updatedVerification.status === 'completed' || updatedVerification.status === 'failed') {
            // Redirect to report after 2 seconds
            setTimeout(() => {
              router.push(`/dashboard/report/${verificationId}`);
            }, 2000);
          }
        });

        return () => {
          stepsChannel.unsubscribe();
          verificationChannel.unsubscribe();
        };
      } catch (err) {
        console.error('Error fetching progress:', err);
        toast.error('Failed to load verification progress');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, [verificationId, router]);

  // Map steps to agents
  const agents: AgentStatus[] = [
    {
      name: 'GitHub Analysis',
      icon: Github,
      status: steps.find(s => s.agent_name === 'github_analyzer')?.status || 'pending',
      message: steps.find(s => s.agent_name === 'github_analyzer')?.message || 'Waiting to start...',
      startedAt: steps.find(s => s.agent_name === 'github_analyzer')?.started_at,
      completedAt: steps.find(s => s.agent_name === 'github_analyzer')?.completed_at,
    },
    {
      name: 'HR Verification',
      icon: Phone,
      status: steps.find(s => s.agent_name === 'hr_verifier')?.status || 'pending',
      message: steps.find(s => s.agent_name === 'hr_verifier')?.message || 'Waiting to start...',
      startedAt: steps.find(s => s.agent_name === 'hr_verifier')?.started_at,
      completedAt: steps.find(s => s.agent_name === 'hr_verifier')?.completed_at,
    },
    {
      name: 'Reference Checks',
      icon: Users,
      status: steps.find(s => s.agent_name === 'reference_checker')?.status || 'pending',
      message: steps.find(s => s.agent_name === 'reference_checker')?.message || 'Waiting to start...',
      startedAt: steps.find(s => s.agent_name === 'reference_checker')?.started_at,
      completedAt: steps.find(s => s.agent_name === 'reference_checker')?.completed_at,
    },
    {
      name: 'Resume Analysis',
      icon: FileText,
      status: steps.find(s => s.agent_name === 'resume_analyzer')?.status || 'pending',
      message: steps.find(s => s.agent_name === 'resume_analyzer')?.message || 'Waiting to start...',
      startedAt: steps.find(s => s.agent_name === 'resume_analyzer')?.started_at,
      completedAt: steps.find(s => s.agent_name === 'resume_analyzer')?.completed_at,
    },
    {
      name: 'Fraud Detection',
      icon: Shield,
      status: steps.find(s => s.agent_name === 'fraud_detector')?.status || 'pending',
      message: steps.find(s => s.agent_name === 'fraud_detector')?.message || 'Waiting to start...',
      startedAt: steps.find(s => s.agent_name === 'fraud_detector')?.started_at,
      completedAt: steps.find(s => s.agent_name === 'fraud_detector')?.completed_at,
    },
  ];

  // Calculate overall progress
  const completedSteps = agents.filter(a => a.status === 'completed').length;
  const totalSteps = agents.length;
  const progressPercentage = (completedSteps / totalSteps) * 100;

  const getStatusIcon = (status: AgentStatus['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'running':
        return <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />;
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      case 'skipped':
        return <AlertCircle className="w-5 h-5 text-yellow-400" />;
      default:
        return <Clock className="w-5 h-5 text-[#6b7280]" />;
    }
  };

  const getStatusColor = (status: AgentStatus['status']) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/10 border-green-500/30';
      case 'running':
        return 'bg-blue-500/10 border-blue-500/30';
      case 'failed':
        return 'bg-red-500/10 border-red-500/30';
      case 'skipped':
        return 'bg-yellow-500/10 border-yellow-500/30';
      default:
        return 'bg-white/5 border-white/10';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-purple-400 animate-spin mx-auto mb-4" />
          <p className="text-[#9ca3af]">Loading verification progress...</p>
        </div>
      </div>
    );
  }

  if (!verification) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-white text-xl mb-2">Verification not found</p>
          <Button
            variant="outline"
            onClick={() => router.push('/dashboard')}
            className="border-white/10 hover:bg-white/5"
          >
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={staggerChildren}
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={fadeIn}>
        <h1 className="text-4xl font-bold mb-2 gradient-text">Verification in Progress</h1>
        <p className="text-[#9ca3af]">
          Verifying {verification.candidate_name} • {verification.position || 'N/A'}
        </p>
      </motion.div>

      {/* Overall Progress */}
      <motion.div variants={fadeIn}>
        <Card className="glass border-white/10">
          <CardHeader>
            <CardTitle className="text-white">Overall Progress</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-[#9ca3af]">
                {completedSteps} of {totalSteps} checks completed
              </span>
              <span className="text-white font-medium">{Math.round(progressPercentage)}%</span>
            </div>
            <Progress value={progressPercentage} className="h-2" />
            
            {verification.status === 'completed' && (
              <div className="flex items-center gap-2 text-green-400 text-sm">
                <CheckCircle className="w-4 h-4" />
                <span>Verification complete! Redirecting to report...</span>
              </div>
            )}
            {verification.status === 'failed' && (
              <div className="flex items-center gap-2 text-red-400 text-sm">
                <AlertCircle className="w-4 h-4" />
                <span>Verification failed. Redirecting to report...</span>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Agent Cards */}
      <motion.div variants={staggerChildren} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => {
          const Icon = agent.icon;
          
          return (
            <motion.div key={agent.name} variants={fadeIn}>
              <Card className={`glass border ${getStatusColor(agent.status)} transition-all`}>
                <CardContent className="p-6">
                  <div className="flex items-start gap-4">
                    <div className={`p-3 rounded-lg ${getStatusColor(agent.status)}`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-white">{agent.name}</h3>
                        {getStatusIcon(agent.status)}
                      </div>
                      <p className="text-sm text-[#9ca3af] mb-2">
                        {agent.message}
                      </p>
                      <Badge
                        variant="outline"
                        className={`text-xs ${getStatusColor(agent.status)}`}
                      >
                        {agent.status}
                      </Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Actions */}
      {verification.status === 'completed' && (
        <motion.div variants={fadeIn} className="flex justify-end">
          <Button
            onClick={() => router.push(`/dashboard/report/${verificationId}`)}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
          >
            View Full Report
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        </motion.div>
      )}
    </motion.div>
  );
}
