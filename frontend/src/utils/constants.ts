/**
 * Application constants
 */

// Storage keys
export const TOKEN_KEY = 'hr_token'
export const USER_KEY = 'hr_user'
export const THEME_KEY = 'hr_theme'
export const LANG_KEY = 'hr_lang'

// API endpoints
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// File upload
export const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB
export const ALLOWED_FILE_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation'
]

// Pagination
export const DEFAULT_PAGE_SIZE = 20
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100]

// Date formats
export const DATE_FORMAT = 'YYYY-MM-DD'
export const DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss'
export const DISPLAY_DATE_FORMAT = 'YYYY年MM月DD日'
export const DISPLAY_DATETIME_FORMAT = 'YYYY年MM月DD日 HH:mm'

// Score grades
export const SCORE_GRADES = [
  { min: 90, label: 'A+', color: '#16a34a' },
  { min: 80, label: 'A', color: '#22c55e' },
  { min: 70, label: 'B+', color: '#84cc16' },
  { min: 60, label: 'B', color: '#eab308' },
  { min: 50, label: 'C+', color: '#f59e0b' },
  { min: 40, label: 'C', color: '#f97316' },
  { min: 0, label: 'D', color: '#ef4444' }
]

// Risk levels
export const RISK_LEVELS = [
  { min: 80, label: '嚴重', color: '#ef4444' },
  { min: 60, label: '高', color: '#f97316' },
  { min: 40, label: '中等', color: '#eab308' },
  { min: 20, label: '低', color: '#22c55e' },
  { min: 0, label: '極低', color: '#6b7280' }
]

// Chart colors
export const CHART_COLORS = [
  '#2563eb',
  '#16a34a', 
  '#eab308',
  '#ef4444',
  '#8b5cf6',
  '#06b6d4',
  '#f59e0b',
  '#ec4899',
  '#10b981',
  '#6366f1'
]

// User roles
export const USER_ROLES = [
  { value: 'admin', label: '系統管理員', color: '#ef4444' },
  { value: 'auditor', label: '審計員', color: '#8b5cf6' },
  { value: 'manager', label: '部門主管', color: '#2563eb' },
  { value: 'employee', label: '一般員工', color: '#6b7280' }
] as const

// Event statuses
export const EVENT_STATUSES = [
  { value: 'draft', label: '草稿', color: '#6b7280' },
  { value: 'pending', label: '待審核', color: '#eab308' },
  { value: 'approved', label: '已核准', color: '#16a34a' },
  { value: 'rejected', label: '已拒絕', color: '#ef4444' },
  { value: 'archived', label: '已封存', color: '#94a3b8' }
] as const

// Event sources
export const EVENT_SOURCES = [
  { value: 'manual', label: '手動輸入', icon: 'Edit' },
  { value: 'redmine', label: 'Redmine', icon: 'Link' },
  { value: 'n8n', label: 'n8n 自動化', icon: 'Connection' },
  { value: 'note', label: 'Note Station', icon: 'Document' },
  { value: 'api', label: 'API', icon: 'Coordinate' }
] as const

// Project statuses
export const PROJECT_STATUSES = [
  { value: 'active', label: '進行中', color: '#16a34a' },
  { value: 'inactive', label: '暫停', color: '#eab308' },
  { value: 'completed', label: '已完成', color: '#2563eb' },
  { value: 'archived', label: '已封存', color: '#6b7280' }
] as const

// Rule directions
export const RULE_DIRECTIONS = [
  { value: 'positive', label: '加分', color: '#16a34a', symbol: '+' },
  { value: 'negative', label: '扣分', color: '#ef4444', symbol: '-' }
] as const

// Period types
export const PERIOD_TYPES = [
  { value: 'monthly', label: '月度' },
  { value: 'quarterly', label: '季度' },
  { value: 'yearly', label: '年度' }
] as const

// Performance trends
export const PERFORMANCE_TRENDS = [
  { value: 'improving', label: '上升', color: '#16a34a', icon: 'TrendChartUp' },
  { value: 'stable', label: '穩定', color: '#6b7280', icon: 'Minus' },
  { value: 'declining', label: '下降', color: '#ef4444', icon: 'TrendChartDown' },
  { value: 'new', label: '新員工', color: '#2563eb', icon: 'Plus' }
] as const