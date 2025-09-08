/**
 * Authentication API service
 */

import type { LoginCredentials, LoginResponse, User } from '@/types/user'
import { apiClient } from '@/utils/request'

export const authApi = {
  /**
   * Login with username and password
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    const response = await apiClient.post<LoginResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    return response.data
  },

  /**
   * Logout current user
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout')
  },

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me')
    return response.data
  },

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/refresh')
    return response.data
  },

  /**
   * Change password
   */
  async changePassword(data: {
    current_password: string
    new_password: string
    confirm_password: string
  }): Promise<void> {
    await apiClient.post('/auth/change-password', data)
  },

  /**
   * Update user profile
   */
  async updateProfile(data: {
    name?: string
    email?: string
    phone?: string
  }): Promise<User> {
    const response = await apiClient.patch<User>('/auth/profile', data)
    return response.data
  },

  /**
   * Upload user avatar
   */
  async uploadAvatar(file: File): Promise<{ avatar_url: string }> {
    const formData = new FormData()
    formData.append('avatar', file)
    
    const response = await apiClient.post<{ avatar_url: string }>(
      '/auth/avatar', 
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )
    
    return response.data
  }
}