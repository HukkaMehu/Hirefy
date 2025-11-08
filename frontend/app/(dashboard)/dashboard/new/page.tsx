"use client";

import { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Upload, FileText, User, Mail, Phone, CheckCircle, Loader2, X } from 'lucide-react';
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

  const handleSubmit = async () => {
    if (!isFormValid) {
      toast.error('Please fill in all required fields and upload a resume');
      return;
    }

    setIsSubmitting(true);
    
    try {
      // TODO: Upload resume to Supabase Storage first
      // For now, we'll just send the form data without the file
      
      const response = await fetch('/api/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          candidateName,
          candidateEmail,
          candidatePhone,
          // Resume URL will be added after upload implementation
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
      className="space-y-6 max-w-3xl mx-auto"
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
          Upload a resume and provide basic contact information. Our AI will extract all the details and handle the verification automatically.
        </p>
      </div>

      {/* Main Form Card */}
      <Card className="glass border-white/10">
        <CardHeader>
          <CardTitle className="text-white">Candidate Information</CardTitle>
          <CardDescription>
            Upload the candidate&apos;s resume and provide their contact details
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* File Upload Area */}
          <div className="space-y-2">
            <Label className="text-white">Resume (PDF) *</Label>
            
            {!resumeFile ? (
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragActive 
                    ? 'border-purple-500 bg-purple-500/10' 
                    : 'border-white/20 hover:border-white/40'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <Upload className="w-12 h-12 text-[#6b7280] mx-auto mb-4" />
                <p className="text-white mb-2">
                  Drag and drop your PDF here, or click to browse
                </p>
                <p className="text-sm text-[#6b7280] mb-4">
                  Supports PDF files up to 10MB
                </p>
                <input
                  type="file"
                  id="resume-upload"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => document.getElementById('resume-upload')?.click()}
                  className="border-white/10 hover:bg-white/5"
                >
                  Choose File
                </Button>
              </div>
            ) : (
              <div className="glass-hover rounded-lg p-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-8 h-8 text-green-400" />
                  <div>
                    <p className="text-white font-medium">{resumeFile.name}</p>
                    <p className="text-sm text-[#6b7280]">
                      {(resumeFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={removeFile}
                  className="hover:bg-red-500/10 hover:text-red-400"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            )}
          </div>

          {/* Contact Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="name" className="text-white">
                <User className="w-4 h-4 inline mr-2" />
                Full Name *
              </Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                value={candidateName}
                onChange={(e) => setCandidateName(e.target.value)}
                className="bg-white/5 border-white/10 focus:border-purple-500/50"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email" className="text-white">
                <Mail className="w-4 h-4 inline mr-2" />
                Email *
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="john@example.com"
                value={candidateEmail}
                onChange={(e) => setCandidateEmail(e.target.value)}
                className="bg-white/5 border-white/10 focus:border-purple-500/50"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone" className="text-white">
                <Phone className="w-4 h-4 inline mr-2" />
                Phone *
              </Label>
              <Input
                id="phone"
                type="tel"
                placeholder="+1 (555) 123-4567"
                value={candidatePhone}
                onChange={(e) => setCandidatePhone(e.target.value)}
                className="bg-white/5 border-white/10 focus:border-purple-500/50"
                required
              />
            </div>
          </div>

          {/* Info Message */}
          <div className="glass rounded-lg p-4 border border-blue-500/30">
            <div className="flex gap-3">
              <CheckCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="text-white font-medium mb-1">
                  Automated Verification Process
                </p>
                <p className="text-[#9ca3af]">
                  Our AI will automatically extract employment history, contact references, analyze GitHub activity, and conduct verification calls with HR and references. No additional input needed!
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Submit Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSubmit}
          disabled={!isFormValid || isSubmitting}
          className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:opacity-50"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Starting Verification...
            </>
          ) : (
            <>
              <CheckCircle className="w-4 h-4 mr-2" />
              Start Verification
            </>
          )}
        </Button>
      </div>
    </motion.div>
  );
}
