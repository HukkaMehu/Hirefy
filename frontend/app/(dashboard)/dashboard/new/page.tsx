"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowLeft,
  Upload,
  FileText,
  User,
  Mail,
  Phone,
  CheckCircle,
  Loader2,
  X
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { Button } from '@/src/components/ui/button';
import { Input } from '@/src/components/ui/input';
import { Label } from '@/src/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/src/components/ui/card';
import { fadeIn } from '@/lib/animations';
import { toast } from 'sonner';

export default function NewVerificationPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  // Form state
  const [candidateName, setCandidateName] = useState('');
  const [candidateEmail, setCandidateEmail] = useState('');
  const [candidatePhone, setCandidatePhone] = useState('');

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === 'application/pdf') {
        setResumeFile(file);
      } else {
        toast.error('Please upload a PDF file');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type === 'application/pdf') {
        setResumeFile(file);
      } else {
        toast.error('Please upload a PDF file');
      }
    }
  };

  const removeFile = () => {
    setResumeFile(null);
  };

  const isFormValid = candidateName && candidateEmail && candidatePhone && resumeFile;

  const handleNext = () => {
    if (currentStep < 4 && canProceed()) {
      setCurrentStep((prev) => (prev + 1) as Step);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => (prev - 1) as Step);
    }
  };

  const handleSubmit = async () => {
    if (!canProceed()) {
      toast.error('Please complete all required fields');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const response = await fetch('/api/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidateName: candidateInfo.name,
          candidateEmail: candidateInfo.email,
          candidatePhone: candidateInfo.phone,
          candidateLinkedIn: candidateInfo.linkedin,
          company: employmentHistory.company,
          position: employmentHistory.position,
          startDate: employmentHistory.startDate,
          endDate: employmentHistory.endDate,
          verificationOptions: verificationOptions,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create verification');
      }

      toast.success('Verification started successfully!');
      
      // Redirect to progress page
      router.push(`/dashboard/progress/${data.verification_id}`);
    } catch (error) {
      console.error('Error creating verification:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to create verification');
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={fadeIn}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <Button
          variant="ghost"
          onClick={() => router.back()}
          className="mb-4 -ml-2 hover:bg-white/5"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <h1 className="text-4xl font-bold gradient-text">New Verification</h1>
        <p className="text-[#9ca3af] mt-2">
          Start a comprehensive background check and verification process
        </p>
      </div>

      {/* Progress Steps */}
      <Card className="glass border-white/10">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const Icon = step.icon;
              const isActive = currentStep === step.number;
              const isComplete = currentStep > step.number;
              
              return (
                <div key={step.number} className="flex items-center flex-1">
                  <div className="flex flex-col items-center flex-1">
                    <div
                      className={`w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all ${
                        isComplete
                          ? 'bg-green-500 border-green-500'
                          : isActive
                          ? 'bg-purple-500 border-purple-500'
                          : 'bg-transparent border-white/20'
                      }`}
                    >
                      {isComplete ? (
                        <Check className="w-6 h-6 text-white" />
                      ) : (
                        <Icon className={`w-6 h-6 ${isActive ? 'text-white' : 'text-[#6b7280]'}`} />
                      )}
                    </div>
                    <span
                      className={`text-sm mt-2 ${
                        isActive || isComplete ? 'text-white' : 'text-[#6b7280]'
                      }`}
                    >
                      {step.title}
                    </span>
                  </div>
                  {index < steps.length - 1 && (
                    <div
                      className={`h-0.5 flex-1 mx-4 transition-all ${
                        isComplete ? 'bg-green-500' : 'bg-white/10'
                      }`}
                    />
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Form Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {/* Step 1: Candidate Info */}
          {currentStep === 1 && (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Candidate Information</CardTitle>
                <CardDescription>Enter the candidate&apos;s basic details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-white">
                    <User className="w-4 h-4 inline mr-2" />
                    Full Name *
                  </Label>
                  <Input
                    id="name"
                    placeholder="John Doe"
                    value={candidateInfo.name}
                    onChange={(e) => setCandidateInfo({ ...candidateInfo, name: e.target.value })}
                    className="bg-white/5 border-white/10 focus:border-purple-500/50"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-white">
                    <Mail className="w-4 h-4 inline mr-2" />
                    Email Address *
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="john.doe@example.com"
                    value={candidateInfo.email}
                    onChange={(e) => setCandidateInfo({ ...candidateInfo, email: e.target.value })}
                    className="bg-white/5 border-white/10 focus:border-purple-500/50"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone" className="text-white">
                    <Phone className="w-4 h-4 inline mr-2" />
                    Phone Number *
                  </Label>
                  <Input
                    id="phone"
                    type="tel"
                    placeholder="+1 (555) 123-4567"
                    value={candidateInfo.phone}
                    onChange={(e) => setCandidateInfo({ ...candidateInfo, phone: e.target.value })}
                    className="bg-white/5 border-white/10 focus:border-purple-500/50"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="linkedin" className="text-white">
                    <Linkedin className="w-4 h-4 inline mr-2" />
                    LinkedIn Profile (Optional)
                  </Label>
                  <Input
                    id="linkedin"
                    placeholder="linkedin.com/in/johndoe"
                    value={candidateInfo.linkedin}
                    onChange={(e) => setCandidateInfo({ ...candidateInfo, linkedin: e.target.value })}
                    className="bg-white/5 border-white/10 focus:border-purple-500/50"
                  />
                </div>
              </CardContent>
            </Card>
          )}

          {/* Step 2: Employment History */}
          {currentStep === 2 && (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Employment History</CardTitle>
                <CardDescription>Enter the candidate&apos;s most recent employment</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="company" className="text-white">
                    <Building className="w-4 h-4 inline mr-2" />
                    Company Name *
                  </Label>
                  <Input
                    id="company"
                    placeholder="Tech Corp Inc."
                    value={employmentHistory.company}
                    onChange={(e) => setEmploymentHistory({ ...employmentHistory, company: e.target.value })}
                    className="bg-white/5 border-white/10 focus:border-purple-500/50"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="position" className="text-white">
                    <Briefcase className="w-4 h-4 inline mr-2" />
                    Job Title *
                  </Label>
                  <Input
                    id="position"
                    placeholder="Senior Software Engineer"
                    value={employmentHistory.position}
                    onChange={(e) => setEmploymentHistory({ ...employmentHistory, position: e.target.value })}
                    className="bg-white/5 border-white/10 focus:border-purple-500/50"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="startDate" className="text-white">
                      <Calendar className="w-4 h-4 inline mr-2" />
                      Start Date *
                    </Label>
                    <Input
                      id="startDate"
                      type="date"
                      value={employmentHistory.startDate}
                      onChange={(e) => setEmploymentHistory({ ...employmentHistory, startDate: e.target.value })}
                      className="bg-white/5 border-white/10 focus:border-purple-500/50"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="endDate" className="text-white">
                      <Calendar className="w-4 h-4 inline mr-2" />
                      End Date
                    </Label>
                    <Input
                      id="endDate"
                      type="date"
                      value={employmentHistory.endDate}
                      onChange={(e) => setEmploymentHistory({ ...employmentHistory, endDate: e.target.value })}
                      className="bg-white/5 border-white/10 focus:border-purple-500/50"
                    />
                  </div>
                </div>

                <p className="text-sm text-[#6b7280]">
                  Leave end date empty if the candidate is currently employed
                </p>
              </CardContent>
            </Card>
          )}

          {/* Step 3: Verification Options */}
          {currentStep === 3 && (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Verification Options</CardTitle>
                <CardDescription>Select which verification methods to use</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start space-x-3 glass-hover p-4 rounded-lg">
                  <Checkbox
                    id="hrCall"
                    checked={verificationOptions.hrCall}
                    onCheckedChange={(checked) => 
                      setVerificationOptions({ ...verificationOptions, hrCall: checked as boolean })
                    }
                  />
                  <div className="flex-1">
                    <Label htmlFor="hrCall" className="text-white font-medium cursor-pointer">
                      HR Verification Call
                    </Label>
                    <p className="text-sm text-[#9ca3af] mt-1">
                      AI agent calls the company&apos;s HR department to verify employment history
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 glass-hover p-4 rounded-lg">
                  <Checkbox
                    id="referenceCheck"
                    checked={verificationOptions.referenceCheck}
                    onCheckedChange={(checked) => 
                      setVerificationOptions({ ...verificationOptions, referenceCheck: checked as boolean })
                    }
                  />
                  <div className="flex-1">
                    <Label htmlFor="referenceCheck" className="text-white font-medium cursor-pointer">
                      Reference Checks
                    </Label>
                    <p className="text-sm text-[#9ca3af] mt-1">
                      Contact and verify references provided by the candidate
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 glass-hover p-4 rounded-lg">
                  <Checkbox
                    id="resumeAnalysis"
                    checked={verificationOptions.resumeAnalysis}
                    onCheckedChange={(checked) => 
                      setVerificationOptions({ ...verificationOptions, resumeAnalysis: checked as boolean })
                    }
                  />
                  <div className="flex-1">
                    <Label htmlFor="resumeAnalysis" className="text-white font-medium cursor-pointer">
                      Resume Analysis
                    </Label>
                    <p className="text-sm text-[#9ca3af] mt-1">
                      AI-powered analysis of resume for inconsistencies and red flags
                    </p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 glass-hover p-4 rounded-lg">
                  <Checkbox
                    id="githubAnalysis"
                    checked={verificationOptions.githubAnalysis}
                    onCheckedChange={(checked) => 
                      setVerificationOptions({ ...verificationOptions, githubAnalysis: checked as boolean })
                    }
                  />
                  <div className="flex-1">
                    <Label htmlFor="githubAnalysis" className="text-white font-medium cursor-pointer">
                      GitHub Analysis
                    </Label>
                    <p className="text-sm text-[#9ca3af] mt-1">
                      Analyze GitHub profile for coding activity and contributions
                    </p>
                  </div>
                </div>

                {!isStep3Valid && (
                  <p className="text-sm text-orange-400">
                    Please select at least one verification method
                  </p>
                )}
              </CardContent>
            </Card>
          )}

          {/* Step 4: Review & Submit */}
          {currentStep === 4 && (
            <Card className="glass border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Review & Submit</CardTitle>
                <CardDescription>Review all information before starting verification</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Candidate Info Summary */}
                <div>
                  <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <User className="w-5 h-5" />
                    Candidate Information
                  </h3>
                  <div className="bg-white/5 rounded-lg p-4 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-[#9ca3af]">Name:</span>
                      <span className="text-white font-medium">{candidateInfo.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#9ca3af]">Email:</span>
                      <span className="text-white font-medium">{candidateInfo.email}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#9ca3af]">Phone:</span>
                      <span className="text-white font-medium">{candidateInfo.phone}</span>
                    </div>
                    {candidateInfo.linkedin && (
                      <div className="flex justify-between">
                        <span className="text-[#9ca3af]">LinkedIn:</span>
                        <span className="text-white font-medium">{candidateInfo.linkedin}</span>
                      </div>
                    )}
                  </div>
                </div>

                <Separator className="bg-white/10" />

                {/* Employment Summary */}
                <div>
                  <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <Briefcase className="w-5 h-5" />
                    Employment History
                  </h3>
                  <div className="bg-white/5 rounded-lg p-4 space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-[#9ca3af]">Company:</span>
                      <span className="text-white font-medium">{employmentHistory.company}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#9ca3af]">Position:</span>
                      <span className="text-white font-medium">{employmentHistory.position}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-[#9ca3af]">Duration:</span>
                      <span className="text-white font-medium">
                        {new Date(employmentHistory.startDate).toLocaleDateString()} - 
                        {employmentHistory.endDate ? new Date(employmentHistory.endDate).toLocaleDateString() : 'Present'}
                      </span>
                    </div>
                  </div>
                </div>

                <Separator className="bg-white/10" />

                {/* Verification Options Summary */}
                <div>
                  <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    Selected Verifications
                  </h3>
                  <div className="bg-white/5 rounded-lg p-4 space-y-2 text-sm">
                    {verificationOptions.hrCall && (
                      <div className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-green-400" />
                        <span className="text-white">HR Verification Call</span>
                      </div>
                    )}
                    {verificationOptions.referenceCheck && (
                      <div className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-green-400" />
                        <span className="text-white">Reference Checks</span>
                      </div>
                    )}
                    {verificationOptions.resumeAnalysis && (
                      <div className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-green-400" />
                        <span className="text-white">Resume Analysis</span>
                      </div>
                    )}
                    {verificationOptions.githubAnalysis && (
                      <div className="flex items-center gap-2">
                        <Check className="w-4 h-4 text-green-400" />
                        <span className="text-white">GitHub Analysis</span>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </AnimatePresence>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={handleBack}
          disabled={currentStep === 1}
          className="border-white/10 hover:bg-white/5"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>

        {currentStep < 4 ? (
          <Button
            onClick={handleNext}
            disabled={!canProceed()}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
          >
            Next
            <ArrowRight className="w-4 h-4 ml-2" />
          </Button>
        ) : (
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
          >
            {isSubmitting ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"
                />
                Starting...
              </>
            ) : (
              <>
                <CheckCircle className="w-4 h-4 mr-2" />
                Start Verification
              </>
            )}
          </Button>
        )}
      </div>
    </motion.div>
  );
}
