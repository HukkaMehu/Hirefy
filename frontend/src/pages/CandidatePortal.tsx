import { useState, useEffect, useRef, type ChangeEvent, type DragEvent } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Send,
  Upload,
  FileText,
  Image as ImageIcon,
  Loader2,
  CheckCircle,
  AlertCircle,
  X,
  FileCheck,
  Paperclip,
  Bot,
  User as UserIcon,
} from 'lucide-react'
import { apiClient } from '@/lib/api'
import { cn } from '@/lib/utils'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  document?: UploadedDocument
}

interface UploadedDocument {
  filename: string
  type: string
  size: number
  preview?: string
}

interface ExtractedData {
  type: string
  data: Record<string, unknown>
  confidence?: number
}

interface ChatSession {
  session_id: string
  stage: string
  conversation_history: Array<{ role: string; content: string }>
  documents: Array<{ filename: string; type: string }>
  extracted_data: ExtractedData[]
  inconsistencies: unknown[]
  employment_gaps: unknown[]
}

export default function CandidatePortal() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)

  const [messages, setMessages] = useState<Message[]>([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [chatSessionId, setChatSessionId] = useState<string | null>(null)
  const [_session, setSession] = useState<ChatSession | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploadingFile, setUploadingFile] = useState(false)
  const [showConsent, setShowConsent] = useState(false)
  const [consentSigned, setConsentSigned] = useState(false)
  const [signature, setSignature] = useState('')
  const [progress, setProgress] = useState(0)

  // Initialize chat session
  useEffect(() => {
    if (sessionId) {
      initializeChatSession()
    }
  }, [sessionId])

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const initializeChatSession = async () => {
    setIsLoading(true)
    setError(null)

    try {
      // Create chat session
      const response = await apiClient.post<{
        success: boolean
        session_id: string
        initial_message: string
      }>('/api/chat/sessions', {
        verification_session_id: sessionId,
      })

      if (response.success) {
        setChatSessionId(response.session_id)
        
        // Add initial message
        setMessages([
          {
            id: '1',
            role: 'assistant',
            content: response.initial_message,
            timestamp: new Date(),
          },
        ])

        // Fetch session state
        await fetchSessionState(response.session_id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize chat session')
    } finally {
      setIsLoading(false)
    }
  }

  const fetchSessionState = async (sessionId: string) => {
    try {
      const response = await apiClient.get<{
        success: boolean
        session: ChatSession
      }>(`/api/chat/sessions/${sessionId}`)

      if (response.success) {
        setSession(response.session)
        calculateProgress(response.session)
      }
    } catch (err) {
      console.error('Failed to fetch session state:', err)
    }
  }

  const calculateProgress = (session: ChatSession) => {
    // Calculate progress based on documents collected
    const stages = ['INITIAL', 'CV_REQUESTED', 'CV_PROCESSED', 'SUPPORTING_DOCS', 'COMPLETE']
    const currentStageIndex = stages.indexOf(session.stage)
    const progressPercent = ((currentStageIndex + 1) / stages.length) * 100
    setProgress(progressPercent)

    // Show consent form when all documents are collected
    if (session.stage === 'COMPLETE' && !consentSigned) {
      setShowConsent(true)
    }
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !chatSessionId || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)
    setIsTyping(true)
    setError(null)

    try {
      const response = await apiClient.post<{
        success: boolean
        message: string
        session: ChatSession
      }>(`/api/chat/sessions/${chatSessionId}/messages`, {
        message: inputMessage,
      })

      if (response.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.message,
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, assistantMessage])
        setSession(response.session)
        calculateProgress(response.session)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
    } finally {
      setIsLoading(false)
      setIsTyping(false)
    }
  }

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files && files.length > 0) {
      handleFileUpload(files[0])
    }
  }

  const handleFileUpload = async (file: File) => {
    if (!chatSessionId) return

    setUploadingFile(true)
    setError(null)

    try {
      // Create preview for images
      let preview: string | undefined
      if (file.type.startsWith('image/')) {
        preview = URL.createObjectURL(file)
      }

      // Add user message with document
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: `Uploaded: ${file.name}`,
        timestamp: new Date(),
        document: {
          filename: file.name,
          type: file.type,
          size: file.size,
          preview,
        },
      }

      setMessages((prev) => [...prev, userMessage])
      setIsTyping(true)

      // Upload to backend
      const response = await apiClient.uploadFile<{
        success: boolean
        message: string
        extracted_data?: ExtractedData
        session: ChatSession
      }>(`/api/chat/sessions/${chatSessionId}/documents`, file)

      if (response.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.message,
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, assistantMessage])
        setSession(response.session)
        calculateProgress(response.session)

        // Don't show extracted data separately - the conversational message already includes it
        // The agent formats the response appropriately based on what was extracted
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload document')
    } finally {
      setUploadingFile(false)
      setIsTyping(false)
    }
  }

  const handleSignConsent = async () => {
    if (!signature.trim() || !chatSessionId) return

    setIsLoading(true)

    try {
      // Finalize the session
      const response = await apiClient.post<{
        success: boolean
        verification_session_id: string
      }>(`/api/chat/sessions/${chatSessionId}/finalize`)

      if (response.success) {
        setConsentSigned(true)
        setShowConsent(false)

        // Show success message
        const successMessage: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'Thank you! Your documents have been submitted successfully. We\'ll begin the verification process and you\'ll receive updates via email.',
          timestamp: new Date(),
        }

        setMessages((prev) => [...prev, successMessage])

        // Redirect after a delay
        setTimeout(() => {
          navigate('/')
        }, 3000)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to finalize consent')
    } finally {
      setIsLoading(false)
    }
  }

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) {
      return <ImageIcon className="h-5 w-5" />
    }
    return <FileText className="h-5 w-5" />
  }

  if (isLoading && messages.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Initializing your verification session...</p>
        </div>
      </div>
    )
  }

  if (error && messages.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background p-4">
        <div className="max-w-md w-full bg-card border border-border rounded-lg p-8 text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-foreground mb-2">Failed to Load Session</h2>
          <p className="text-muted-foreground mb-6">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="bg-card border-b border-border px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold text-foreground mb-1">Document Verification Portal</h1>
          <p className="text-sm text-muted-foreground">
            Upload your documents and answer questions to complete your verification
          </p>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs text-muted-foreground mb-2">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="h-2 bg-accent rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-primary"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div
        ref={chatContainerRef}
        className="flex-1 overflow-y-auto px-6 py-6"
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <div className="max-w-4xl mx-auto space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={cn(
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                {message.role === 'assistant' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                    <Bot className="h-5 w-5 text-primary-foreground" />
                  </div>
                )}

                <div
                  className={cn(
                    'max-w-[70%] rounded-lg px-4 py-3',
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-card border border-border text-foreground'
                  )}
                >
                  {message.document ? (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        {getFileIcon(message.document.type)}
                        <span className="text-sm font-medium">{message.document.filename}</span>
                      </div>
                      {message.document.preview && (
                        <img
                          src={message.document.preview}
                          alt={message.document.filename}
                          className="rounded-md max-w-full h-auto"
                        />
                      )}
                      <p className="text-xs opacity-75">
                        {(message.document.size / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  )}
                  <p className="text-xs opacity-50 mt-2">
                    {message.timestamp.toLocaleTimeString()}
                  </p>
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent flex items-center justify-center">
                    <UserIcon className="h-5 w-5 text-foreground" />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex gap-3"
            >
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <Bot className="h-5 w-5 text-primary-foreground" />
              </div>
              <div className="bg-card border border-border rounded-lg px-4 py-3">
                <div className="flex gap-1">
                  <motion.div
                    className="w-2 h-2 bg-muted-foreground rounded-full"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-muted-foreground rounded-full"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                  />
                  <motion.div
                    className="w-2 h-2 bg-muted-foreground rounded-full"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                  />
                </div>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Drag and Drop Overlay */}
        <AnimatePresence>
          {isDragging && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-primary/10 backdrop-blur-sm flex items-center justify-center z-50"
            >
              <div className="bg-card border-2 border-dashed border-primary rounded-lg p-12 text-center">
                <Upload className="h-16 w-16 text-primary mx-auto mb-4" />
                <p className="text-xl font-medium text-foreground">Drop your document here</p>
                <p className="text-sm text-muted-foreground mt-2">
                  PDF, JPG, PNG, or HEIC (max 10MB)
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Input Area */}
      <div className="bg-card border-t border-border px-6 py-4">
        <div className="max-w-4xl mx-auto">
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-3 flex items-start gap-2"
            >
              <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          )}

          <div className="space-y-2">
            <div className="flex gap-2">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileSelect}
                accept=".pdf,.jpg,.jpeg,.png,.heic"
                className="hidden"
              />

              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={uploadingFile || isLoading}
                className="flex-shrink-0 p-3 rounded-md border border-border bg-background hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                title="Upload document"
              >
                {uploadingFile ? (
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                ) : (
                  <Paperclip className="h-5 w-5 text-muted-foreground" />
                )}
              </button>

              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                placeholder="Type your message..."
                disabled={isLoading || uploadingFile}
                className="flex-1 px-4 py-3 bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
              />

              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading || uploadingFile}
                className="flex-shrink-0 px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Send className="h-5 w-5" />
                <span className="hidden sm:inline">Send</span>
              </button>
            </div>

            {/* Quick action buttons */}
            <div className="flex gap-2 justify-center">
              <button
                onClick={() => {
                  setInputMessage("I don't have this document, can we skip it?")
                  setTimeout(() => handleSendMessage(), 100)
                }}
                disabled={isLoading || uploadingFile}
                className="text-xs px-3 py-1.5 border border-border bg-background hover:bg-accent rounded-md text-muted-foreground transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Skip this document
              </button>
              <button
                onClick={() => setShowConsent(true)}
                disabled={isLoading || uploadingFile || !chatSessionId}
                className="text-xs px-3 py-1.5 bg-primary text-primary-foreground hover:bg-primary/90 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                Finish & Submit Documents
              </button>
            </div>
          </div>

          <p className="text-xs text-muted-foreground mt-2 text-center">
            Supported formats: PDF, JPG, PNG, HEIC (max 10MB)
          </p>
        </div>
      </div>

      {/* Consent Modal */}
      <AnimatePresence>
        {showConsent && !consentSigned && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-card border border-border rounded-lg p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <FileCheck className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-foreground">Consent Form</h2>
                  <p className="text-sm text-muted-foreground">
                    Please review and sign to proceed
                  </p>
                </div>
              </div>

              <div className="bg-accent/50 border border-border rounded-lg p-6 mb-6 max-h-64 overflow-y-auto">
                <h3 className="font-semibold text-foreground mb-3">
                  Background Verification Authorization
                </h3>
                <div className="text-sm text-muted-foreground space-y-2">
                  <p>
                    I hereby authorize the verification platform to conduct a comprehensive
                    background verification including:
                  </p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li>Employment history verification with previous employers</li>
                    <li>Reference checks with provided contacts</li>
                    <li>Education credential verification with institutions</li>
                    <li>Technical profile analysis (GitHub, portfolio)</li>
                    <li>Document authenticity verification</li>
                  </ul>
                  <p className="mt-4">
                    I understand that all information provided will be verified and any
                    discrepancies will be reported to the hiring company. I certify that all
                    information provided is true and accurate to the best of my knowledge.
                  </p>
                  <p className="mt-4">
                    I understand that I can revoke this authorization at any time by contacting
                    the verification platform.
                  </p>
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-foreground mb-2">
                  Electronic Signature
                </label>
                <input
                  type="text"
                  value={signature}
                  onChange={(e) => setSignature(e.target.value)}
                  placeholder="Type your full name to sign"
                  className="w-full px-4 py-3 bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent font-signature text-lg"
                  style={{ fontFamily: 'cursive' }}
                />
                <p className="text-xs text-muted-foreground mt-2">
                  By typing your name, you agree to the terms above
                </p>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={handleSignConsent}
                  disabled={!signature.trim() || isLoading}
                  className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-5 w-5" />
                      Sign and Submit
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowConsent(false)}
                  disabled={isLoading}
                  className="px-6 py-3 border border-border bg-background text-foreground rounded-md hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Review Later
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
