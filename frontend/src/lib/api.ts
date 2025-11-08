const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface RequestOptions extends RequestInit {
  params?: Record<string, string>
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  private async request<T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<T> {
    const { params, ...fetchOptions } = options

    let url = `${this.baseUrl}${endpoint}`

    // Add query parameters if provided
    if (params) {
      const searchParams = new URLSearchParams(params)
      url += `?${searchParams.toString()}`
    }

    // Set default headers
    const headers = {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    }

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          message: response.statusText,
        }))
        throw new Error(error.message || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('An unexpected error occurred')
    }
  }

  async get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' })
  }

  async post<T>(
    endpoint: string,
    data?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async put<T>(
    endpoint: string,
    data?: unknown,
    options?: RequestOptions
  ): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' })
  }

  async uploadFile<T>(
    endpoint: string,
    file: File,
    additionalData?: Record<string, string>
  ): Promise<T> {
    const formData = new FormData()
    formData.append('file', file)

    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value)
      })
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: response.statusText,
      }))
      throw new Error(error.message || `HTTP error! status: ${response.status}`)
    }

    return await response.json()
  }
}

export const apiClient = new ApiClient(API_BASE_URL)

// Verification API methods
export const verificationApi = {
  createVerification: (data: { candidate_name: string; candidate_email: string; candidate_phone?: string }) =>
    apiClient.post('/api/verifications', data),

  getVerification: (sessionId: string) =>
    apiClient.get(`/api/verifications/${sessionId}`),

  listVerifications: () =>
    apiClient.get('/api/verifications'),

  getVerificationStatus: (sessionId: string) =>
    apiClient.get(`/api/verifications/${sessionId}/status`),

  startVerification: (sessionId: string) =>
    apiClient.post(`/api/verifications/${sessionId}/start-verification`),

  uploadDocument: (sessionId: string, file: File, documentType?: string) =>
    apiClient.uploadFile(
      `/api/verifications/${sessionId}/documents`,
      file,
      documentType ? { document_type: documentType } : undefined
    ),

  sendChatMessage: (sessionId: string, message: string) =>
    apiClient.post(`/api/verifications/${sessionId}/chat`, { message }),
}
