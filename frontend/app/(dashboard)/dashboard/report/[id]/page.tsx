"use client";

import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  AlertTriangle, 
  XCircle, 
  Github, 
  Users, 
  AlertCircle, 
  MessageSquare,
  Download,
  Phone,
  Mail,
  Calendar,
  ArrowLeft,
  Copy,
  Check
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { RiskBadge, getRiskLevel } from '@/src/components/dashboard/RiskBadge';
import { Button } from '@/src/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/src/components/ui/card';
import { Badge } from '@/src/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/src/components/ui/accordion';
import { Separator } from '@/src/components/ui/separator';
import { staggerChildren, fadeIn, slideUp } from '@/lib/animations';
import { toast } from 'sonner';

// Mock data - will be replaced with Supabase query
const mockReport = {
  id: '1',
  candidateName: 'Sarah Johnson',
  position: 'Senior Software Engineer',
  company: 'Tech Corp',
  email: 'sarah.johnson@example.com',
  phone: '+1 (555) 123-4567',
  linkedIn: 'linkedin.com/in/sarahjohnson',
  riskScore: 15,
  status: 'completed',
  timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
  
  summary: 'Candidate verification completed successfully. Minor discrepancies found in employment dates but verified through HR call. Overall low-risk profile with strong technical background.',
  
  githubAnalysis: {
    commits: 1247,
    repositories: 23,
    accountAge: '4.2 years',
    languages: ['TypeScript', 'Python', 'Go', 'Rust'],
    suspicious: false,
    contributionLevel: 'Very Active',
  },
  
  hrVerification: {
    contacted: true,
    verified: true,
    company: 'Tech Corp',
    position: 'Senior Software Engineer',
    startDate: '2021-03-01',
    endDate: '2024-06-30',
    notes: 'Employment verified. Candidate left in good standing. Eligible for rehire.',
    transcript: `HR: Thank you for calling Tech Corp HR. How can I help you?\n\nAgent: Hi, I'm verifying employment for Sarah Johnson who worked as a Senior Software Engineer.\n\nHR: Yes, I can confirm Sarah Johnson worked here from March 2021 to June 2024 as a Senior Software Engineer. She left voluntarily and is eligible for rehire.\n\nAgent: Thank you for confirming. Were there any performance issues?\n\nHR: No, she was a valued member of the team with consistently strong performance reviews.`,
  },
  
  referenceVerification: {
    provided: 3,
    contacted: 3,
    verified: 2,
    responseRate: '67%',
    flagged: 0,
    references: [
      {
        name: 'John Smith',
        relationship: 'Former Manager',
        company: 'Tech Corp',
        verified: true,
        feedback: 'Excellent engineer, strong problem-solving skills, great team player.',
      },
      {
        name: 'Emily Chen',
        relationship: 'Former Colleague',
        company: 'Tech Corp',
        verified: true,
        feedback: 'Very collaborative, always willing to help teammates, writes clean code.',
      },
      {
        name: 'Michael Brown',
        relationship: 'Former Tech Lead',
        company: 'Tech Corp',
        verified: false,
        feedback: 'Did not respond to verification request.',
      },
    ],
  },
  
  fraudFlags: [
    {
      severity: 'low',
      type: 'Date Discrepancy',
      description: 'Employment end date on resume (July 2024) differs from HR records (June 2024) by 1 month.',
      resolved: true,
    },
  ],
  
  interviewQuestions: [
    'Can you describe a challenging technical problem you solved at Tech Corp?',
    'Tell me about your experience working with TypeScript and Python in production environments.',
    'How do you approach code reviews and mentoring junior developers?',
    'What prompted your decision to leave Tech Corp after 3 years?',
    'Describe your experience with distributed systems and microservices architecture.',
  ],
  
  timeline: [
    { date: new Date(Date.now() - 5 * 60 * 1000).toISOString(), event: 'Verification completed', type: 'success' },
    { date: new Date(Date.now() - 15 * 60 * 1000).toISOString(), event: 'Reference checks completed', type: 'info' },
    { date: new Date(Date.now() - 30 * 60 * 1000).toISOString(), event: 'HR verification call completed', type: 'info' },
    { date: new Date(Date.now() - 45 * 60 * 1000).toISOString(), event: 'GitHub analysis completed', type: 'info' },
    { date: new Date(Date.now() - 60 * 60 * 1000).toISOString(), event: 'Verification initiated', type: 'info' },
  ],
};

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

export default function ReportDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  
  const riskLevel = getRiskLevel(mockReport.riskScore);

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    toast.success('Copied to clipboard');
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const downloadReport = () => {
    toast.info('PDF download feature coming soon');
  };

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={staggerChildren}
      className="space-y-6"
    >
      {/* Header */}
      <motion.div variants={fadeIn} className="flex items-center justify-between">
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
            Generated {getRelativeTime(mockReport.timestamp)}
          </p>
        </div>
        <Button onClick={downloadReport} className="bg-gradient-to-r from-purple-600 to-blue-600">
          <Download className="w-4 h-4 mr-2" />
          Download PDF
        </Button>
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
                  <h2 className="text-2xl font-bold text-white">{mockReport.candidateName}</h2>
                  <RiskBadge level={riskLevel} score={mockReport.riskScore} />
                </div>
                <p className="text-[#9ca3af] mb-4">{mockReport.summary}</p>
                <div className="flex flex-wrap gap-4 text-sm text-[#9ca3af]">
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    {mockReport.email}
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4" />
                    {mockReport.phone}
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    {new Date(mockReport.timestamp).toLocaleDateString()}
                  </div>
                </div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-bold gradient-text mb-2">{mockReport.riskScore}</div>
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
          <Card className="glass border-white/10">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Github className="w-5 h-5 text-purple-400" />
                GitHub Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{mockReport.githubAnalysis.commits}</div>
                  <div className="text-sm text-[#6b7280]">Commits</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{mockReport.githubAnalysis.repositories}</div>
                  <div className="text-sm text-[#6b7280]">Repositories</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-white">{mockReport.githubAnalysis.accountAge}</div>
                  <div className="text-sm text-[#6b7280]">Account Age</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-400">{mockReport.githubAnalysis.contributionLevel}</div>
                  <div className="text-sm text-[#6b7280]">Activity</div>
                </div>
              </div>
              <Separator className="my-4 bg-white/10" />
              <div>
                <p className="text-sm text-[#9ca3af] mb-2">Primary Languages:</p>
                <div className="flex flex-wrap gap-2">
                  {mockReport.githubAnalysis.languages.map((lang) => (
                    <Badge key={lang} variant="outline" className="bg-blue-500/10 text-blue-400 border-blue-500/30">
                      {lang}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* HR Verification */}
          {mockReport.hrVerification && (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Phone className="w-5 h-5 text-green-400" />
                  HR Verification Call
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-green-400" />
                  <span className="text-white font-medium">Employment Verified</span>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-[#6b7280]">Company</div>
                    <div className="text-white font-medium">{mockReport.hrVerification.company}</div>
                  </div>
                  <div>
                    <div className="text-[#6b7280]">Position</div>
                    <div className="text-white font-medium">{mockReport.hrVerification.position}</div>
                  </div>
                  <div>
                    <div className="text-[#6b7280]">Start Date</div>
                    <div className="text-white font-medium">
                      {new Date(mockReport.hrVerification.startDate).toLocaleDateString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-[#6b7280]">End Date</div>
                    <div className="text-white font-medium">
                      {new Date(mockReport.hrVerification.endDate).toLocaleDateString()}
                    </div>
                  </div>
                </div>
                <Separator className="bg-white/10" />
                <div>
                  <p className="text-sm text-[#9ca3af] mb-2">Notes:</p>
                  <p className="text-white">{mockReport.hrVerification.notes}</p>
                </div>
                <Accordion type="single" collapsible>
                  <AccordionItem value="transcript" className="border-white/10">
                    <AccordionTrigger className="text-white hover:text-purple-400">
                      View Call Transcript
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="bg-black/30 rounded-lg p-4 font-mono text-sm text-[#9ca3af] whitespace-pre-wrap">
                        {mockReport.hrVerification.transcript}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              </CardContent>
            </Card>
          )}

          {/* Reference Checks */}
          <Card className="glass border-white/10">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <Users className="w-5 h-5 text-blue-400" />
                Reference Verification
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-4 gap-4 text-center">
                <div>
                  <div className="text-2xl font-bold text-white">{mockReport.referenceVerification.provided}</div>
                  <div className="text-sm text-[#6b7280]">Provided</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-white">{mockReport.referenceVerification.contacted}</div>
                  <div className="text-sm text-[#6b7280]">Contacted</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-green-400">{mockReport.referenceVerification.verified}</div>
                  <div className="text-sm text-[#6b7280]">Verified</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-blue-400">{mockReport.referenceVerification.responseRate}</div>
                  <div className="text-sm text-[#6b7280]">Response Rate</div>
                </div>
              </div>
              <Separator className="bg-white/10" />
              <div className="space-y-3">
                {mockReport.referenceVerification.references.map((ref, index) => (
                  <div key={index} className="glass-hover p-4 rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <div className="font-medium text-white">{ref.name}</div>
                        <div className="text-sm text-[#6b7280]">{ref.relationship} • {ref.company}</div>
                      </div>
                      {ref.verified ? (
                        <CheckCircle className="w-5 h-5 text-green-400" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-400" />
                      )}
                    </div>
                    <p className="text-sm text-[#9ca3af]">{ref.feedback}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Interview Questions */}
          <Card className="glass border-white/10">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white">
                <MessageSquare className="w-5 h-5 text-purple-400" />
                Recommended Interview Questions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mockReport.interviewQuestions.map((question, index) => (
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
        </motion.div>

        {/* Sidebar */}
        <motion.div variants={fadeIn} className="space-y-6">
          {/* Timeline */}
          <Card className="glass border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Verification Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockReport.timeline.map((item, index) => (
                  <div key={index} className="flex gap-3">
                    <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                      item.type === 'success' ? 'bg-green-400' : 'bg-blue-400'
                    }`} />
                    <div>
                      <div className="text-sm text-white">{item.event}</div>
                      <div className="text-xs text-[#6b7280]">{getRelativeTime(item.date)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Fraud Flags */}
          {mockReport.fraudFlags.length > 0 && (
            <Card className="glass border-orange-500/30">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <AlertCircle className="w-5 h-5 text-orange-400" />
                  Fraud Flags
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {mockReport.fraudFlags.map((flag, index) => (
                    <div key={index} className="glass-hover p-4 rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <Badge 
                          variant="outline" 
                          className={`${
                            flag.severity === 'low' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30' :
                            flag.severity === 'medium' ? 'bg-orange-500/10 text-orange-400 border-orange-500/30' :
                            'bg-red-500/10 text-red-400 border-red-500/30'
                          }`}
                        >
                          {flag.type}
                        </Badge>
                        {flag.resolved && (
                          <CheckCircle className="w-4 h-4 text-green-400" />
                        )}
                      </div>
                      <p className="text-sm text-[#9ca3af]">{flag.description}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </motion.div>
  );
}
