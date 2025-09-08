export interface User {
  id: number
  username: string
  name: string
  email: string
  employee_id: string
  role: 'admin' | 'manager' | 'employee' | 'auditor'
  department_id: number
  department_name?: string
  is_active: boolean
  last_login?: string
  created_at: string
  updated_at: string
}

export interface Department {
  id: number
  name: string
  code: string
  manager_id?: number
  manager_name?: string
  parent_id?: number
  is_active: boolean
  created_at: string
}

export interface Rule {
  id: number
  name: string
  code: string
  description: string
  category: string
  base_score: number
  weight: number
  caps?: number
  evidence_required: boolean
  active: boolean
  rule_pack_id: number
  rule_pack_name?: string
  created_at: string
  updated_at: string
}

export interface RulePack {
  id: number
  name: string
  version: string
  description: string
  status: 'draft' | 'active' | 'archived'
  scope: 'company' | 'department' | 'role'
  effective_from: string
  effective_to?: string
  rules_count: number
  created_by: number
  creator_name?: string
  created_at: string
  updated_at: string
}

export interface Event {
  id: number
  user_id: number
  user_name?: string
  user_employee_id?: string
  reporter_id: number
  reporter_name?: string
  reviewer_id?: number
  reviewer_name?: string
  department_id: number
  department_name?: string
  project_id?: number
  project_name?: string
  rule_id: number
  rule_name?: string
  rule_code?: string
  rule_category?: string
  title?: string
  description?: string
  original_score: number
  adjusted_score?: number
  adjustment_reason?: string
  final_score: number
  status: 'draft' | 'pending' | 'approved' | 'rejected' | 'archived'
  occurred_at: string
  evidence_urls: string[]
  evidence_count: number
  needs_evidence?: boolean
  has_sufficient_evidence?: boolean
  can_approve?: boolean
  is_positive?: boolean
  is_adjusted?: boolean
  is_locked?: boolean
  source: 'manual' | 'api' | 'import'
  external_id?: string
  source_metadata?: Record<string, any>
  period_year: number
  period_month: number
  period_quarter: number
  period_key?: string
  quarter_key?: string
  reviewed_at?: string
  review_notes?: string
  created_at: string
  updated_at: string
}

export interface Score {
  id: number
  user_id: number
  user_name?: string
  user_employee_id?: string
  department_id: number
  department_name?: string
  period_id: number
  period_year: number
  period_month: number
  period_quarter: number
  period_type: 'monthly' | 'quarterly' | 'yearly'
  total_score: number
  positive_score: number
  negative_score: number
  adjusted_score: number
  total_events: number
  positive_events: number
  negative_events: number
  pending_events: number
  rank_department?: number
  rank_company?: number
  percentile_department?: number
  percentile_company?: number
  rule_breakdown: Record<string, any>
  events_computed_count: number
  computation_version: string
  has_adjustments: boolean
  computed_at: string
  is_locked: boolean
  needs_recalculation: boolean
  created_at: string
  updated_at: string
}

export interface Period {
  id: number
  type: 'monthly' | 'quarterly' | 'yearly'
  year: number
  month?: number
  quarter?: number
  start_date: string
  end_date: string
  is_current: boolean
  is_locked: boolean
  scores_calculated: boolean
  created_at: string
  updated_at: string
}

export interface Project {
  id: number
  name: string
  code: string
  description?: string
  status: 'active' | 'completed' | 'cancelled'
  start_date?: string
  end_date?: string
  manager_id?: number
  manager_name?: string
  created_at: string
  updated_at: string
}

// Request/Response types
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface EventCreateRequest {
  user_id: number
  rule_id: number
  title?: string
  description?: string
  occurred_at: string
  department_id?: number
  project_id?: number
  evidence_urls?: string[]
  source?: 'manual' | 'api' | 'import'
  external_id?: string
  source_metadata?: Record<string, any>
}

export interface EventUpdateRequest {
  title?: string
  description?: string
  occurred_at?: string
  evidence_urls?: string[]
  adjusted_score?: number
  adjustment_reason?: string
  source_metadata?: Record<string, any>
}

export interface EventApprovalRequest {
  status: 'approved' | 'rejected'
  review_notes?: string
}

export interface EventListRequest {
  skip?: number
  limit?: number
  status_filter?: string
  user_id?: number
  department_id?: number
  rule_id?: number
  project_id?: number
  date_from?: string
  date_to?: string
  search?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface ScoreCalculationRequest {
  user_id?: number
  department_id?: number
  period_year: number
  period_month: number
  recalculate?: boolean
}

export interface FileUploadResponse {
  url: string
  filename: string
  size: number
  content_type: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
  has_next: boolean
  has_prev: boolean
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  errors?: Record<string, string[]>
}

export interface ApiError {
  detail: string
  status_code: number
  type?: string
}

// Dashboard types
export interface DashboardStats {
  total_events: number
  pending_events: number
  approved_events: number
  rejected_events: number
  total_users: number
  active_users: number
  total_score: number
  average_score: number
  top_performers: Array<{
    user_id: number
    user_name: string
    total_score: number
    rank: number
  }>
  recent_events: Event[]
  score_trend: Array<{
    period: string
    total_score: number
    event_count: number
  }>
}

export interface ReportFilters {
  user_ids?: number[]
  department_ids?: number[]
  date_from?: string
  date_to?: string
  rule_ids?: number[]
  status_filter?: string
  include_adjustments?: boolean
}

export interface EventsSummary {
  period: string
  total_events: number
  approved_events: number
  pending_events: number
  rejected_events: number
  total_score: number
  positive_score: number
  negative_score: number
  positive_events: number
  negative_events: number
  average_score: number
}