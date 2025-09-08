import { apiService } from './api'
import { User, Department, PaginatedResponse } from '@/types/api'

export interface UserListRequest {
  skip?: number
  limit?: number
  department_id?: number
  role?: string
  is_active?: boolean
  search?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface UserService {
  getUsers(params?: UserListRequest): Promise<PaginatedResponse<User>>
  getUser(id: number): Promise<User>
  searchUsers(query: string, limit?: number): Promise<User[]>
  getUsersByDepartment(departmentId: number): Promise<User[]>
  getUsersByRole(role: string): Promise<User[]>
  syncUsersFromLDAP(): Promise<{ synced: number; errors: string[] }>
}

class UserServiceImpl implements UserService {
  async getUsers(params?: UserListRequest): Promise<PaginatedResponse<User>> {
    return await apiService.get<PaginatedResponse<User>>('/api/users', params)
  }

  async getUser(id: number): Promise<User> {
    return await apiService.get<User>(`/api/users/${id}`)
  }

  async searchUsers(query: string, limit = 20): Promise<User[]> {
    const params = {
      search: query,
      limit,
      is_active: true,
    }
    const response = await apiService.get<PaginatedResponse<User>>('/api/users/search', params)
    return response.items
  }

  async getUsersByDepartment(departmentId: number): Promise<User[]> {
    const params = {
      department_id: departmentId,
      is_active: true,
      limit: 1000, // Get all users in department
    }
    const response = await apiService.get<PaginatedResponse<User>>('/api/users', params)
    return response.items
  }

  async getUsersByRole(role: string): Promise<User[]> {
    const params = {
      role,
      is_active: true,
      limit: 1000, // Get all users with role
    }
    const response = await apiService.get<PaginatedResponse<User>>('/api/users', params)
    return response.items
  }

  async syncUsersFromLDAP(): Promise<{ synced: number; errors: string[] }> {
    return await apiService.post<{ synced: number; errors: string[] }>('/api/users/sync-ldap')
  }
}

export const userService = new UserServiceImpl()
export default userService