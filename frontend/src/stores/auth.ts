import { defineStore } from 'pinia'
import type { User, UserRole } from '@/types/user'
import { authApi } from '@/services/auth'
import { TOKEN_KEY } from '@/utils/constants'
import Cookies from 'js-cookie'

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  loginError: string | null
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: null,
    isLoading: false,
    loginError: null
  }),

  getters: {
    isAuthenticated: (state): boolean => {
      return !!(state.token && state.user)
    },

    userRole: (state): UserRole | null => {
      return state.user?.role || null
    },

    isAdmin: (state): boolean => {
      return state.user?.role === 'admin'
    },

    isManager: (state): boolean => {
      return ['admin', 'manager'].includes(state.user?.role || '')
    },

    isEmployee: (state): boolean => {
      return state.user?.role === 'employee'
    },

    isAuditor: (state): boolean => {
      return state.user?.role === 'auditor'
    },

    departmentId: (state): number | null => {
      return state.user?.department_id || null
    },

    permissions: (state): string[] => {
      if (!state.user?.role) return []
      
      // Define role permissions (should match backend SecurityScopes)
      const rolePermissions: Record<UserRole, string[]> = {
        admin: [
          'events:create', 'events:read', 'events:update', 'events:delete', 'events:approve',
          'reports:read', 'reports:export',
          'rules:create', 'rules:read', 'rules:update', 'rules:delete',
          'users:create', 'users:read', 'users:update', 'users:delete',
          'audit:read'
        ],
        auditor: [
          'events:read',
          'reports:read', 'reports:export',
          'rules:read',
          'users:read',
          'audit:read'
        ],
        manager: [
          'events:create', 'events:read', 'events:update', 'events:approve',
          'reports:read', 'reports:export',
          'rules:read',
          'users:read'
        ],
        employee: [
          'events:read',
          'reports:read'
        ]
      }
      
      return rolePermissions[state.user.role] || []
    }
  },

  actions: {
    async login(credentials: { username: string; password: string }) {
      this.isLoading = true
      this.loginError = null
      
      try {
        const response = await authApi.login(credentials)
        
        // Store token and user data
        this.token = response.access_token
        this.user = response.user
        
        // Persist token
        Cookies.set(TOKEN_KEY, response.access_token, { 
          expires: 7, // 7 days
          secure: true,
          sameSite: 'strict'
        })
        
        return response
      } catch (error: any) {
        this.loginError = error.response?.data?.detail || '登入失敗'
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async logout() {
      try {
        if (this.token) {
          await authApi.logout()
        }
      } catch (error) {
        console.error('Logout API error:', error)
      } finally {
        // Clear state
        this.user = null
        this.token = null
        this.loginError = null
        
        // Remove token
        Cookies.remove(TOKEN_KEY)
        
        // Clear any cached data
        localStorage.clear()
      }
    },

    async initializeAuth() {
      // Get token from cookie
      const token = Cookies.get(TOKEN_KEY)
      
      if (!token) {
        return false
      }
      
      try {
        this.token = token
        
        // Validate token and get user info
        const user = await authApi.getCurrentUser()
        this.user = user
        
        return true
      } catch (error) {
        console.error('Token validation failed:', error)
        
        // Clear invalid token
        this.token = null
        Cookies.remove(TOKEN_KEY)
        
        return false
      }
    },

    async refreshUserData() {
      if (!this.token) return
      
      try {
        const user = await authApi.getCurrentUser()
        this.user = user
      } catch (error) {
        console.error('Failed to refresh user data:', error)
      }
    },

    // Permission helpers
    hasRole(role: UserRole): boolean {
      return this.userRole === role
    },

    hasAnyRole(roles: UserRole[]): boolean {
      return roles.includes(this.userRole as UserRole)
    },

    hasPermission(permission: string): boolean {
      return this.permissions.includes(permission)
    },

    hasAnyPermission(permissions: string[]): boolean {
      return permissions.some(permission => this.permissions.includes(permission))
    },

    // Department access helpers
    canAccessDepartment(departmentId: number): boolean {
      // Admins and auditors can access all departments
      if (this.isAdmin || this.isAuditor) {
        return true
      }
      
      // Users can only access their own department
      return this.departmentId === departmentId
    },

    canAccessUser(userId: number): boolean {
      // Admins and auditors can access all users
      if (this.isAdmin || this.isAuditor) {
        return true
      }
      
      // Users can access their own data
      if (this.user?.id === userId) {
        return true
      }
      
      // Managers can access users in their department
      // (This would need additional logic to check if user is in same department)
      return false
    }
  }
})