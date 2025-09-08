import { apiService } from './api'
import { DashboardStats, ReportFilters } from '@/types/api'

export interface DashboardFilters {
  period_year?: number
  period_month?: number
  department_id?: number
  user_id?: number
}

export interface PerformanceMetrics {
  total_score: number
  average_score: number
  score_change: number
  score_change_percent: number
  total_events: number
  events_change: number
  positive_events: number
  negative_events: number
  pending_events: number
  approval_rate: number
}

export interface ScoreDistribution {
  score_range: string
  count: number
  percentage: number
}

export interface TopPerformer {
  user_id: number
  user_name: string
  user_employee_id: string
  department_name: string
  total_score: number
  rank: number
  change_from_last_period: number
}

export interface RecentActivity {
  id: number
  type: 'event_created' | 'event_approved' | 'event_rejected' | 'score_calculated'
  title: string
  description: string
  user_name: string
  timestamp: string
  metadata?: Record<string, any>
}

export interface TrendData {
  period: string
  value: number
  change?: number
}

export interface DashboardData {
  metrics: PerformanceMetrics
  score_distribution: ScoreDistribution[]
  top_performers: TopPerformer[]
  recent_activities: RecentActivity[]
  score_trend: TrendData[]
  events_trend: TrendData[]
  department_comparison?: Array<{
    department_id: number
    department_name: string
    total_score: number
    average_score: number
    total_events: number
    rank: number
  }>
}

export interface DashboardService {
  getDashboardData(filters?: DashboardFilters): Promise<DashboardData>
  getPerformanceMetrics(filters?: DashboardFilters): Promise<PerformanceMetrics>
  getScoreDistribution(filters?: DashboardFilters): Promise<ScoreDistribution[]>
  getTopPerformers(filters?: DashboardFilters, limit?: number): Promise<TopPerformer[]>
  getRecentActivities(limit?: number): Promise<RecentActivity[]>
  getScoreTrend(filters?: DashboardFilters, months?: number): Promise<TrendData[]>
  getEventsTrend(filters?: DashboardFilters, months?: number): Promise<TrendData[]>
  getDepartmentComparison(year: number, month: number): Promise<Array<{
    department_id: number
    department_name: string
    total_score: number
    average_score: number
    total_events: number
    rank: number
  }>>
  
  // Export functions
  exportDashboardReport(filters?: DashboardFilters): Promise<Blob>
  exportPerformanceReport(filters?: ReportFilters): Promise<Blob>
  exportComparisonReport(filters?: DashboardFilters): Promise<Blob>
}

class DashboardServiceImpl implements DashboardService {
  async getDashboardData(filters?: DashboardFilters): Promise<DashboardData> {
    return await apiService.get<DashboardData>('/api/dashboard', filters)
  }

  async getPerformanceMetrics(filters?: DashboardFilters): Promise<PerformanceMetrics> {
    return await apiService.get<PerformanceMetrics>('/api/dashboard/metrics', filters)
  }

  async getScoreDistribution(filters?: DashboardFilters): Promise<ScoreDistribution[]> {
    return await apiService.get<ScoreDistribution[]>('/api/dashboard/score-distribution', filters)
  }

  async getTopPerformers(filters?: DashboardFilters, limit = 10): Promise<TopPerformer[]> {
    const params = { ...filters, limit }
    return await apiService.get<TopPerformer[]>('/api/dashboard/top-performers', params)
  }

  async getRecentActivities(limit = 20): Promise<RecentActivity[]> {
    return await apiService.get<RecentActivity[]>('/api/dashboard/recent-activities', { limit })
  }

  async getScoreTrend(filters?: DashboardFilters, months = 12): Promise<TrendData[]> {
    const params = { ...filters, months }
    return await apiService.get<TrendData[]>('/api/dashboard/score-trend', params)
  }

  async getEventsTrend(filters?: DashboardFilters, months = 12): Promise<TrendData[]> {
    const params = { ...filters, months }
    return await apiService.get<TrendData[]>('/api/dashboard/events-trend', params)
  }

  async getDepartmentComparison(year: number, month: number): Promise<Array<{
    department_id: number
    department_name: string
    total_score: number
    average_score: number
    total_events: number
    rank: number
  }>> {
    const params = { period_year: year, period_month: month }
    return await apiService.get('/api/dashboard/department-comparison', params)
  }

  // Export functions
  async exportDashboardReport(filters?: DashboardFilters): Promise<Blob> {
    const response = await apiService.getAxiosInstance().get('/api/dashboard/export', {
      params: filters,
      responseType: 'blob',
    })
    return response.data
  }

  async exportPerformanceReport(filters?: ReportFilters): Promise<Blob> {
    const response = await apiService.getAxiosInstance().get('/api/reports/performance/export', {
      params: filters,
      responseType: 'blob',
    })
    return response.data
  }

  async exportComparisonReport(filters?: DashboardFilters): Promise<Blob> {
    const response = await apiService.getAxiosInstance().get('/api/dashboard/comparison/export', {
      params: filters,
      responseType: 'blob',
    })
    return response.data
  }
}

export const dashboardService = new DashboardServiceImpl()
export default dashboardService