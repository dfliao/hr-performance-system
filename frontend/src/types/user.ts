/**
 * User-related type definitions
 */

export type UserRole = 'admin' | 'auditor' | 'manager' | 'employee'

export type UserStatus = 'active' | 'inactive' | 'suspended'

export interface User {
  id: number
  ldap_uid: string
  username: string
  email: string
  name: string
  display_name?: string
  department_id?: number
  title?: string
  employee_id?: string
  status: UserStatus
  role: UserRole
  phone?: string
  avatar_url?: string
  created_at: string
  updated_at?: string
  
  // Computed/related fields
  department_name?: string
  is_active?: boolean
}

export interface UserCreate {
  ldap_uid: string
  username: string
  email: string
  name: string
  department_id?: number
  title?: string
  employee_id?: string
  role?: UserRole
  phone?: string
}

export interface UserUpdate {
  name?: string
  email?: string
  department_id?: number
  title?: string
  employee_id?: string
  role?: UserRole
  status?: UserStatus
  phone?: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Department {
  id: number
  name: string
  code: string
  description?: string
  parent_id?: number
  level: number
  path?: string
  manager_user_id?: number
  is_active: boolean
  email?: string
  phone?: string
  location?: string
  
  // Computed fields
  manager_name?: string
  user_count?: number
  child_count?: number
  full_path?: string
}