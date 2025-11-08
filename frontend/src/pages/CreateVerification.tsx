import { useState, type FormEvent, type ChangeEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { UserPlus, Mail, User, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { cn } from '@/lib/utils'

interface FormData {
  candidate_name: string
  candidate_email: string
}

interface FormErrors {
  candidate_name?: string
  candidate_email?: string
}

interface CreateVerificationResponse {
  session_id: string
  candidate_portal_url: string
  status: string
  created_at: string
}

export default function CreateVerification() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<FormData>({
    candidate_name: '',
    candidate_email: '',
  })
  const [errors, setErrors] = useState<FormErrors>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [successData, setSuccessData] = useState<CreateVerificationResponse | null>(null)

  // Real-time validation
  const validateField = (name: keyof FormData, value: string): string | undefined => {
    switch (name) {
      case 'candidate_name':
        if (!value.trim()) {
          return 'Candidate name is required'
        }
        if (value.trim().length < 2) {
          return 'Name must be at least 2 characters'
        }
        return undefined

      case 'candidate_email':
        if (!value.trim()) {
          return 'Email is required'
        }
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(value)) {
          return 'Please enter a valid email address'
        }
        return undefined

      default:
        return undefined
    }
  }

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))

    // Clear submit error when user starts typing
    if (submitError) {
      setSubmitError(null)
    }

    // Real-time validation
    const error = validateField(name as keyof FormData, value)
    setErrors((prev) => ({
      ...prev,
      [name]: error,
    }))
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}
    let isValid = true

    Object.keys(formData).forEach((key) => {
      const error = validateField(key as keyof FormData, formData[key as keyof FormData])
      if (error) {
        newErrors[key as keyof FormErrors] = error
        isValid = false
      }
    })

    setErrors(newErrors)
    return isValid
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    // Validate form
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)
    setSubmitError(null)

    try {
      const response = await apiClient.post<CreateVerificationResponse>(
        '/api/verifications',
        formData
      )

      setSuccessData(response)

      // Don't auto-redirect - let user copy the URL first
    } catch (error) {
      setSubmitError(
        error instanceof Error ? error.message : 'Failed to create verification'
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCopyUrl = () => {
    if (successData?.candidate_portal_url) {
      navigator.clipboard.writeText(successData.candidate_portal_url)
    }
  }

  // Success state
  if (successData) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-2xl mx-auto"
      >
        <div className="bg-card border border-border rounded-lg p-8 text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            className="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900/20 rounded-full mb-4"
          >
            <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-2xl font-bold text-foreground mb-2"
          >
            Verification Created Successfully!
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-muted-foreground mb-6"
          >
            The candidate portal link has been generated. Share this link with{' '}
            <span className="font-medium text-foreground">{formData.candidate_name}</span> to
            begin the verification process.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-accent/50 border border-border rounded-lg p-4 mb-6"
          >
            <p className="text-sm text-muted-foreground mb-2">Candidate Portal URL</p>
            <div className="flex items-center gap-2">
              <code className="flex-1 text-sm bg-background px-3 py-2 rounded border border-border text-foreground break-all">
                {successData.candidate_portal_url}
              </code>
              <button
                onClick={handleCopyUrl}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors text-sm font-medium whitespace-nowrap"
              >
                Copy
              </button>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="flex gap-3 justify-center"
          >
            <button
              onClick={() => navigate('/')}
              className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors font-medium"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => window.open(successData.candidate_portal_url, '_blank')}
              className="px-6 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 transition-colors font-medium"
            >
              Open Portal
            </button>
          </motion.div>
        </div>
      </motion.div>
    )
  }

  // Form state
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-2xl mx-auto"
    >
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Create New Verification</h1>
        <p className="text-muted-foreground">
          Start a new candidate verification by providing their basic information. They'll
          receive a secure portal link to upload their documents.
        </p>
      </div>

      <div className="bg-card border border-border rounded-lg p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Candidate Name Field */}
          <div>
            <label
              htmlFor="candidate_name"
              className="block text-sm font-medium text-foreground mb-2"
            >
              Candidate Name
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-muted-foreground" />
              </div>
              <input
                type="text"
                id="candidate_name"
                name="candidate_name"
                value={formData.candidate_name}
                onChange={handleInputChange}
                className={cn(
                  'w-full pl-10 pr-4 py-2 bg-background border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all',
                  errors.candidate_name
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-border'
                )}
                placeholder="John Doe"
                disabled={isSubmitting}
              />
            </div>
            {errors.candidate_name && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-1 text-sm text-red-500 flex items-center gap-1"
              >
                <AlertCircle className="h-4 w-4" />
                {errors.candidate_name}
              </motion.p>
            )}
          </div>

          {/* Candidate Email Field */}
          <div>
            <label
              htmlFor="candidate_email"
              className="block text-sm font-medium text-foreground mb-2"
            >
              Email Address
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Mail className="h-5 w-5 text-muted-foreground" />
              </div>
              <input
                type="email"
                id="candidate_email"
                name="candidate_email"
                value={formData.candidate_email}
                onChange={handleInputChange}
                className={cn(
                  'w-full pl-10 pr-4 py-2 bg-background border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all',
                  errors.candidate_email
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-border'
                )}
                placeholder="john.doe@example.com"
                disabled={isSubmitting}
              />
            </div>
            {errors.candidate_email && (
              <motion.p
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-1 text-sm text-red-500 flex items-center gap-1"
              >
                <AlertCircle className="h-4 w-4" />
                {errors.candidate_email}
              </motion.p>
            )}
          </div>

          {/* Submit Error */}
          {submitError && (
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4"
            >
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                    Failed to create verification
                  </h3>
                  <p className="text-sm text-red-700 dark:text-red-300 mt-1">{submitError}</p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Submit Button */}
          <div className="flex items-center gap-4 pt-4">
            <button
              type="submit"
              disabled={isSubmitting || Object.keys(errors).some((key) => errors[key as keyof FormErrors])}
              className={cn(
                'flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-md font-medium transition-all',
                'bg-primary text-primary-foreground hover:bg-primary/90',
                'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Creating Verification...
                </>
              ) : (
                <>
                  <UserPlus className="h-5 w-5" />
                  Create Verification
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => navigate('/')}
              disabled={isSubmitting}
              className="px-6 py-3 rounded-md font-medium border border-border bg-background text-foreground hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>

      {/* Info Box */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4"
      >
        <h3 className="text-sm font-medium text-blue-900 dark:text-blue-200 mb-2">
          What happens next?
        </h3>
        <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
          <li>• The candidate will receive a secure portal link via email</li>
          <li>• They'll upload their CV, diplomas, and supporting documents</li>
          <li>• Our AI will guide them through the process conversationally</li>
          <li>• Verification activities will begin automatically once documents are collected</li>
          <li>• You'll receive a comprehensive report within 48 hours</li>
        </ul>
      </motion.div>
    </motion.div>
  )
}
