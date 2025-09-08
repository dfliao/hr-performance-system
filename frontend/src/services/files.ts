import { apiService } from './api'
import { FileUploadResponse } from '@/types/api'

export interface FileInfo {
  filename: string
  size: number
  created_at: number
  modified_at: number
  exists: boolean
}

export interface FileUploadOptions {
  onProgress?: (progress: number) => void
  eventId?: number | string
  userId?: number
}

export interface FileService {
  uploadFile(file: File, options?: FileUploadOptions): Promise<FileUploadResponse>
  uploadEvidence(file: File, eventId: number, userId: number, onProgress?: (progress: number) => void): Promise<FileUploadResponse>
  deleteFile(filePath: string): Promise<boolean>
  getFileInfo(filePath: string): Promise<FileInfo>
  downloadFile(filePath: string, filename?: string): Promise<void>
  
  // Batch operations
  uploadMultipleFiles(files: File[], options?: FileUploadOptions): Promise<FileUploadResponse[]>
  deleteMultipleFiles(filePaths: string[]): Promise<boolean[]>
  
  // Validation
  validateFile(file: File): { valid: boolean; error?: string }
  getMaxFileSize(): number
  getAllowedExtensions(): string[]
}

class FileServiceImpl implements FileService {
  private readonly maxFileSize = 10 * 1024 * 1024 // 10MB
  private readonly allowedExtensions = [
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', // Images
    'pdf', // PDF
    'doc', 'docx', 'txt', 'rtf', // Documents
    'xls', 'xlsx', 'csv', // Spreadsheets
    'ppt', 'pptx', // Presentations
    'zip', 'rar', '7z', // Archives
    'mp3', 'wav', 'mp4', 'avi', 'mov' // Media (if needed)
  ]

  async uploadFile(file: File, options?: FileUploadOptions): Promise<FileUploadResponse> {
    const validation = this.validateFile(file)
    if (!validation.valid) {
      throw new Error(validation.error || '檔案驗證失敗')
    }

    const formData = new FormData()
    formData.append('file', file)
    
    if (options?.eventId) {
      formData.append('event_id', String(options.eventId))
    }
    if (options?.userId) {
      formData.append('user_id', String(options.userId))
    }

    return await apiService.uploadFile<FileUploadResponse>(
      '/api/files/upload',
      formData,
      options?.onProgress
    )
  }

  async uploadEvidence(file: File, eventId: number, userId: number, onProgress?: (progress: number) => void): Promise<FileUploadResponse> {
    return await this.uploadFile(file, {
      eventId,
      userId,
      onProgress,
    })
  }

  async deleteFile(filePath: string): Promise<boolean> {
    const response = await apiService.post<{ success: boolean }>('/api/files/delete', {
      file_path: filePath,
    })
    return response.success
  }

  async getFileInfo(filePath: string): Promise<FileInfo> {
    return await apiService.get<FileInfo>('/api/files/info', {
      file_path: filePath,
    })
  }

  async downloadFile(filePath: string, filename?: string): Promise<void> {
    await apiService.downloadFile(`/api/files/download?file_path=${encodeURIComponent(filePath)}`, filename)
  }

  // Batch operations
  async uploadMultipleFiles(files: File[], options?: FileUploadOptions): Promise<FileUploadResponse[]> {
    const uploadPromises = files.map(file => this.uploadFile(file, options))
    
    try {
      return await Promise.all(uploadPromises)
    } catch (error) {
      // If any upload fails, we still return partial results
      const results: FileUploadResponse[] = []
      for (const promise of uploadPromises) {
        try {
          results.push(await promise)
        } catch (err) {
          console.error('File upload failed:', err)
          // You might want to add a way to return partial results with errors
        }
      }
      return results
    }
  }

  async deleteMultipleFiles(filePaths: string[]): Promise<boolean[]> {
    const deletePromises = filePaths.map(path => this.deleteFile(path))
    return await Promise.all(deletePromises)
  }

  // Validation
  validateFile(file: File): { valid: boolean; error?: string } {
    // Check file size
    if (file.size > this.maxFileSize) {
      return {
        valid: false,
        error: `檔案大小不能超過 ${this.maxFileSize / (1024 * 1024)}MB`,
      }
    }

    // Check file extension
    const extension = file.name.split('.').pop()?.toLowerCase()
    if (!extension || !this.allowedExtensions.includes(extension)) {
      return {
        valid: false,
        error: `不支援的檔案格式：${extension}`,
      }
    }

    // Check file name
    if (file.name.length > 255) {
      return {
        valid: false,
        error: '檔案名稱過長',
      }
    }

    // Check for potentially dangerous file names
    const dangerousPatterns = [
      /\.\./,
      /[<>:"|?*]/,
      /^(con|prn|aux|nul|com[0-9]|lpt[0-9])(\.|$)/i,
    ]

    for (const pattern of dangerousPatterns) {
      if (pattern.test(file.name)) {
        return {
          valid: false,
          error: '檔案名稱包含不允許的字符',
        }
      }
    }

    return { valid: true }
  }

  getMaxFileSize(): number {
    return this.maxFileSize
  }

  getAllowedExtensions(): string[] {
    return [...this.allowedExtensions]
  }
}

export const fileService = new FileServiceImpl()
export default fileService