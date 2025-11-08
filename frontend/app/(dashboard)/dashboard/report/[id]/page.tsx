"use client";

import { motion } from 'framer-motion';
import { 
  Github, 
  Users, 
  AlertTriangle, 
  MessageSquare,
  Download,
  Phone,
  Mail,
  Calendar,
  ArrowLeft,
  Copy,
  Check,
  Loader2,
  Share2,
  XCircle,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { RiskBadge, getRiskLevel } from '@/src/components/dashboard/RiskBadge';
import { Button } from '@/src/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/card';
import { Badge } from '@/src/components/ui/badge';
import { Separator } from '@/src/components/ui/separator';
import { staggerChildren, fadeIn, slideUp } from '@/lib/animations';
import { toast } from 'sonner';
import { getVerification, type Verification } from '@/lib/supabase';

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

export default function ReportPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [verification, setVerification] = useState<Verification | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchVerification = async () => {
      try {
        const data = await getVerification(params.id);
        setVerification(data);
      } catch (error) {
        console.error('Error fetching verification:', error);
        toast.error('Failed to load verification report');
      } finally {
        setLoading(false);
      }
    };

    fetchVerification();
  }, [params.id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-purple-400 mx-auto mb-4" />
          <p className="text-gray-400">Loading report...</p>
        </div>
      </div>
    );
  }

  if (!verification) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <XCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <p className="text-gray-400 mb-4">Verification not found</p>
          <Button onClick={() => router.push('/dashboard/verifications')}>
            Back to Verifications
          </Button>
        </div>
      </div>
    );
  }

  if (verification.status !== 'completed' || !verification.result) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
          <p className="text-gray-400 mb-4">Verification is still in progress</p>
          <Button onClick={() => router.push(`/dashboard/progress/${params.id}`)}>
            View Progress
          </Button>
        </div>
      </div>
    );
  }

  const result = verification.result;
  const riskScore = result.risk_score || 0;
  const riskLevel = getRiskLevel(riskScore);

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const downloadReport = () => {
    toast.info('PDF download feature coming soon');
  };

  const shareReport = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    toast.success('Report link copied to clipboard');
  };

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={staggerChildren}
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={fadeIn} className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <Button
            variant="ghost"
            onClick={() => router.back()}
            className="mb-4 -ml-2 hover:bg-white/5"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <h1 className="text-4xl font-bold gradient-text">Verification Report</h1>
          <p className="text-[#9ca3af] mt-2">
            Generated {getRelativeTime(verification.created_at)}
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={shareReport} variant="outline" className="border-white/10">
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
          <Button onClick={downloadReport} className="bg-gradient-to-r from-purple-600 to-blue-600">
            <Download className="w-4 h-4 mr-2" />
            Download PDF
          </Button>
        </div>
      </motion.div>

      {/* Risk Summary Card */}
      <motion.div variants={slideUp}>
        <Card className={`glass border-2 ${
          riskLevel === 'low' ? 'border-green-500/50' :
          riskLevel === 'medium' ? 'border-yellow-500/50' :
          riskLevel === 'high' ? 'border-orange-500/50' :
          'border-red-500/50'
        } pulse-glow`}>
          <CardContent className="p-8">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-4 mb-4">
                  <h2 className="text-2xl font-bold text-white">{verification.candidate_name}</h2>
                  <RiskBadge level={riskLevel} score={riskScore} />
                </div>
                <p className="text-[#9ca3af] mb-4">
                  {result.narrative || 'Verification completed successfully.'}
                </p>
                <div className="flex flex-wrap gap-4 text-sm text-[#9ca3af]">
                  {verification.candidate_email && (
                    <div className="flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      {verification.candidate_email}
                    </div>
                  )}
                  {verification.candidate_phone && (
                    <div className="flex items-center gap-2">
                      <Phone className="w-4 h-4" />
                      {verification.candidate_phone}
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    {new Date(verification.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-bold gradient-text mb-2">{riskScore}</div>
                <div className="text-sm text-[#6b7280]">Risk Score</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <motion.div variants={fadeIn} className="lg:col-span-2 space-y-6">
          {/* GitHub Analysis */}
          {result.github_summary ? (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Github className="w-5 h-5 text-purple-400" />
                  GitHub Analysis
                  {verification.github_username && (
                    <a
                      href={`https://github.com/${verification.github_username}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-purple-400 hover:text-purple-300 ml-2"
                    >
                      @{verification.github_username}
                    </a>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-[#9ca3af] whitespace-pre-wrap">{result.github_summary}</p>
              </CardContent>
            </Card>
          ) : (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Github className="w-5 h-5 text-gray-400" />
                  GitHub Analysis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-[#6b7280]">No GitHub profile analyzed for this verification.</p>
              </CardContent>
            </Card>
          )}

          {/* Reference Verification */}
          {result.reference_summary ? (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Users className="w-5 h-5 text-blue-400" />
                  Reference Verification
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-[#9ca3af] whitespace-pre-wrap">{result.reference_summary}</p>
              </CardContent>
            </Card>
          ) : (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Users className="w-5 h-5 text-gray-400" />
                  Reference Verification
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-[#6b7280]">No reference checks completed for this verification.</p>
              </CardContent>
            </Card>
          )}

          {/* Fraud Flags */}
          {result.fraud_flags && result.fraud_flags.length > 0 && (
            <Card className="glass border-red-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                  Fraud Flags ({result.fraud_flags.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {result.fraud_flags.map((flag, index) => (
                    <div 
                      key={index} 
                      className={`p-4 rounded-lg border ${
                        flag.severity === 'critical' ? 'border-red-500/50 bg-red-500/10' :
                        flag.severity === 'high' ? 'border-orange-500/50 bg-orange-500/10' :
                        flag.severity === 'medium' ? 'border-yellow-500/50 bg-yellow-500/10' :
                        'border-blue-500/50 bg-blue-500/10'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge 
                            variant="outline" 
                            className={`
                              ${flag.severity === 'critical' ? 'border-red-400 text-red-400' :
                                flag.severity === 'high' ? 'border-orange-400 text-orange-400' :
                                flag.severity === 'medium' ? 'border-yellow-400 text-yellow-400' :
                                'border-blue-400 text-blue-400'}
                            `}
                          >
                            {flag.severity.toUpperCase()}
                          </Badge>
                          <span className="font-medium text-white">{flag.type}</span>
                        </div>
                        {flag.resolved && (
                          <Badge variant="outline" className="border-green-400 text-green-400">
                            Resolved
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-[#9ca3af]">{flag.description}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Interview Questions */}
          {result.interview_questions && result.interview_questions.length > 0 && (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <MessageSquare className="w-5 h-5 text-purple-400" />
                  Recommended Interview Questions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {result.interview_questions.map((question, index) => (
                    <div key={index} className="flex items-start gap-3 p-4 glass-hover rounded-lg group">
                      <div className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-sm flex-shrink-0">
                        {index + 1}
                      </div>
                      <p className="flex-1 text-white">{question}</p>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(question, index)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        {copiedIndex === index ? (
                          <Check className="w-4 h-4 text-green-400" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>

        {/* Sidebar */}
        <motion.div variants={fadeIn} className="space-y-6">
          {/* Employment Details */}
          {(verification.company || verification.position) && (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Employment Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                {verification.company && (
                  <div>
                    <div className="text-[#6b7280]">Company</div>
                    <div className="text-white font-medium">{verification.company}</div>
                  </div>
                )}
                {verification.position && (
                  <div>
                    <div className="text-[#6b7280]">Position</div>
                    <div className="text-white font-medium">{verification.position}</div>
                  </div>
                )}
                {verification.employment_start && (
                  <div>
                    <div className="text-[#6b7280]">Start Date</div>
                    <div className="text-white font-medium">
                      {new Date(verification.employment_start).toLocaleDateString()}
                    </div>
                  </div>
                )}
                {verification.employment_end && (
                  <div>
                    <div className="text-[#6b7280]">End Date</div>
                    <div className="text-white font-medium">
                      {new Date(verification.employment_end).toLocaleDateString()}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Quick Actions */}
          <Card className="glass border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button 
                onClick={downloadReport} 
                variant="outline" 
                className="w-full border-white/10"
              >
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </Button>
              <Button 
                onClick={shareReport} 
                variant="outline" 
                className="w-full border-white/10"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share Report
              </Button>
              <Separator className="my-2 bg-white/10" />
              <Button 
                onClick={() => router.push('/dashboard/new')} 
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                New Verification
              </Button>
            </CardContent>
          </Card>

          {/* Risk Breakdown */}
          <Card className="glass border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <div className={`text-4xl font-bold mb-2 ${
                  riskLevel === 'low' ? 'text-green-400' :
                  riskLevel === 'medium' ? 'text-yellow-400' :
                  riskLevel === 'high' ? 'text-orange-400' :
                  'text-red-400'
                }`}>
                  {riskLevel === 'low' ? '🟢' :
                   riskLevel === 'medium' ? '🟡' :
                   riskLevel === 'high' ? '🟠' :
                   '🔴'}
                </div>
                <div className="text-white font-medium capitalize">{result.risk_level} Risk</div>
                <div className="text-[#6b7280] text-sm">Score: {riskScore}/100</div>
              </div>
              <Separator className="bg-white/10" />
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-[#6b7280]">Fraud Flags:</span>
                  <span className="text-white font-medium">
                    {result.fraud_flags?.length || 0}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#6b7280]">GitHub Verified:</span>
                  <span className="text-white font-medium">
                    {result.github_summary ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[#6b7280]">References Checked:</span>
                  <span className="text-white font-medium">
                    {result.reference_summary ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}

