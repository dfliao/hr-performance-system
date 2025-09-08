/**
 * HTTP client configuration with interceptors
 */

import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage, ElLoading } from 'element-plus'
import { TOKEN_KEY, API_BASE_URL } from '@/utils/constants'
import Cookies from 'js-cookie'
import router from '@/router'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json'
  }
})

// Loading instance
let loadingInstance: any = null
let requestCount = 0

// Show loading
const showLoading = () => {
  if (requestCount === 0) {
    loadingInstance = ElLoading.service({
      text: '載入中...',
      background: 'rgba(0, 0, 0, 0.7)',
      spinner: 'el-icon-loading'
    })
  }
  requestCount++
}

// Hide loading
const hideLoading = () => {
  requestCount--
  if (requestCount === 0 && loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

// Request interceptor
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // Add loading for non-background requests
    if (!config.background) {
      showLoading()
    }
    
    // Add authorization token
    const token = Cookies.get(TOKEN_KEY)
    if (token) {
      config.headers = config.headers || {}
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    // Add request timestamp
    config.metadata = { startTime: new Date() }
    
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    
    return config
  },
  (error) => {
    hideLoading()
    console.error('Request interceptor error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    const config = response.config as any
    
    // Hide loading
    if (!config.background) {
      hideLoading()
    }
    
    // Log response time
    if (config.metadata?.startTime) {
      const duration = new Date().getTime() - config.metadata.startTime.getTime()
      console.log(`✅ API Response: ${config.method?.toUpperCase()} ${config.url} (${duration}ms)`)
    }
    
    return response
  },
  (error) => {
    const config = error.config as any
    
    // Hide loading
    if (!config?.background) {
      hideLoading()
    }
    
    // Log error
    console.error(`❌ API Error: ${config?.method?.toUpperCase()} ${config?.url}`, error)
    
    // Handle different error status codes
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          ElMessage.error('登入已過期，請重新登入')
          Cookies.remove(TOKEN_KEY)
          router.push('/auth/login')
          break
          
        case 403:
          // Forbidden
          ElMessage.error('權限不足，無法執行此操作')
          break
          
        case 404:
          // Not found
          ElMessage.error('請求的資源不存在')
          break
          
        case 422:
          // Validation error
          const message = data?.detail || '資料驗證失敗'
          if (Array.isArray(data?.detail)) {
            const errors = data.detail.map((err: any) => 
              `${err.loc?.join('.')}: ${err.msg}`
            ).join(', ')
            ElMessage.error(`驗證錯誤: ${errors}`)
          } else {
            ElMessage.error(message)
          }
          break
          
        case 429:
          // Rate limit
          ElMessage.error('請求頻率過高，請稍後再試')
          break
          
        case 500:
          // Server error
          ElMessage.error('伺服器發生錯誤，請聯繫系統管理員')
          break
          
        default:
          // Other errors
          const errorMessage = data?.detail || data?.message || `請求失敗 (${status})`
          ElMessage.error(errorMessage)
      }
    } else if (error.code === 'ECONNABORTED') {
      // Timeout
      ElMessage.error('請求超時，請檢查網路連線')
    } else {
      // Network error
      ElMessage.error('網路連線錯誤，請檢查網路狀態')
    }
    
    return Promise.reject(error)
  }
)

// Request helper functions
export const request = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) => 
    apiClient.get<T>(url, config),
    
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.post<T>(url, data, config),
    
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.put<T>(url, data, config),
    
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.patch<T>(url, data, config),
    
  delete: <T = any>(url: string, config?: AxiosRequestConfig) => 
    apiClient.delete<T>(url, config),

  // Background requests (no loading spinner)
  getBackground: <T = any>(url: string, config?: AxiosRequestConfig) => 
    apiClient.get<T>(url, { ...config, background: true }),
    
  postBackground: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) => 
    apiClient.post<T>(url, data, { ...config, background: true })
}

export { apiClient }
export default apiClient