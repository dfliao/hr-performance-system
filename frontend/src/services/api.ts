import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'
import { useAuthStore } from '@/stores/auth'

export interface ApiConfig {
  baseURL: string
  timeout: number
}

export interface ApiErrorResponse {
  detail: string
  status_code: number
  type?: string
}

class ApiService {
  private api: AxiosInstance
  private authStore: any

  constructor(config: ApiConfig) {
    this.api = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor - add auth token
    this.api.interceptors.request.use(
      (config) => {
        // Get auth store instance
        if (!this.authStore) {
          this.authStore = useAuthStore()
        }

        const token = this.authStore.token
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor - handle errors
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      async (error: AxiosError<ApiErrorResponse>) => {
        const { response } = error

        if (response) {
          const { status, data } = response

          switch (status) {
            case 401:
              // Unauthorized - clear auth and redirect to login
              if (this.authStore) {
                this.authStore.logout()
              }
              router.push('/login')
              ElMessage.error('登入已過期，請重新登入')
              break

            case 403:
              // Forbidden
              ElMessage.error('權限不足')
              break

            case 404:
              // Not found
              ElMessage.error('找不到請求的資源')
              break

            case 422:
              // Validation error
              if (data.detail) {
                ElMessage.error(data.detail)
              } else {
                ElMessage.error('請求資料格式錯誤')
              }
              break

            case 429:
              // Rate limit
              ElMessage.error('請求過於頻繁，請稍後再試')
              break

            case 500:
              // Server error
              ElMessage.error('伺服器內部錯誤')
              break

            default:
              // Other errors
              const message = data?.detail || '請求失敗，請稍後再試'
              ElMessage.error(message)
          }
        } else if (error.code === 'ECONNABORTED') {
          // Timeout
          ElMessage.error('請求超時，請檢查網路連線')
        } else {
          // Network error
          ElMessage.error('網路連線錯誤')
        }

        return Promise.reject(error)
      }
    )
  }

  // Generic HTTP methods
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.api.get<T>(url, { params })
    return response.data
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.post<T>(url, data)
    return response.data
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.put<T>(url, data)
    return response.data
  }

  async patch<T>(url: string, data?: any): Promise<T> {
    const response = await this.api.patch<T>(url, data)
    return response.data
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.api.delete<T>(url)
    return response.data
  }

  // File upload method
  async uploadFile<T>(url: string, formData: FormData, onProgress?: (progress: number) => void): Promise<T> {
    const response = await this.api.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    return response.data
  }

  // Download file method
  async downloadFile(url: string, filename?: string): Promise<void> {
    const response = await this.api.get(url, {
      responseType: 'blob',
    })

    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename || 'download'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
  }

  // Get raw axios instance for advanced usage
  getAxiosInstance(): AxiosInstance {
    return this.api
  }
}

// Create API service instance
const apiConfig: ApiConfig = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds
}

export const apiService = new ApiService(apiConfig)
export default apiService