import { apiService } from './api'
import { Score, ScoreCalculationRequest, PaginatedResponse } from '@/types/api'

export interface ScoreListRequest {
  skip?: number
  limit?: number
  user_id?: number
  department_id?: number
  period_year?: number
  period_month?: number
  period_quarter?: number
  period_type?: 'monthly' | 'quarterly' | 'yearly'
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface ScoreRankingRequest {
  period_year: number
  period_month?: number
  period_quarter?: number
  department_id?: number
  limit?: number
}

export interface ScoreRanking {
  user_id: number
  user_name: string
  user_employee_id: string
  department_name: string
  total_score: number
  rank_department?: number
  rank_company?: number
  percentile_department?: number
  percentile_company?: number
}

export interface ScoreTrend {
  period: string
  period_year: number
  period_month: number
  total_score: number
  positive_score: number
  negative_score: number
  total_events: number
  rank_department?: number
  rank_company?: number
}

export interface ScoreService {
  getScores(params?: ScoreListRequest): Promise<PaginatedResponse<Score>>
  getScore(id: number): Promise<Score>
  getUserScore(userId: number, year: number, month: number): Promise<Score | null>
  calculateUserScore(data: ScoreCalculationRequest): Promise<Score>
  calculateDepartmentScores(departmentId: number, year: number, month: number): Promise<Score[]>
  calculateCompanyScores(year: number, month: number): Promise<Score[]>
  recalculatePeriod(year: number, month: number, departmentId?: number): Promise<{ successful: number; failed: number; errors: string[] }>
  
  // Rankings and trends
  getTopPerformers(params: ScoreRankingRequest): Promise<ScoreRanking[]>
  getDepartmentRankings(departmentId: number, year: number, month: number): Promise<ScoreRanking[]>
  getCompanyRankings(year: number, month: number): Promise<ScoreRanking[]>
  getUserScoreTrend(userId: number, months: number): Promise<ScoreTrend[]>
  getDepartmentScoreTrend(departmentId: number, months: number): Promise<ScoreTrend[]>
  getCompanyScoreTrend(months: number): Promise<ScoreTrend[]>
  
  // Export functions
  exportScores(params?: ScoreListRequest): Promise<Blob>
  exportRankings(params: ScoreRankingRequest): Promise<Blob>
  exportScoreTrend(userId?: number, departmentId?: number, months?: number): Promise<Blob>
}

class ScoreServiceImpl implements ScoreService {
  async getScores(params?: ScoreListRequest): Promise<PaginatedResponse<Score>> {
    return await apiService.get<PaginatedResponse<Score>>('/api/scores', params)
  }

  async getScore(id: number): Promise<Score> {
    return await apiService.get<Score>(`/api/scores/${id}`)
  }

  async getUserScore(userId: number, year: number, month: number): Promise<Score | null> {
    try {
      return await apiService.get<Score>(`/api/scores/user/${userId}`, {
        period_year: year,
        period_month: month,
      })
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw error
    }
  }

  async calculateUserScore(data: ScoreCalculationRequest): Promise<Score> {
    return await apiService.post<Score>('/api/scores/calculate', data)
  }

  async calculateDepartmentScores(departmentId: number, year: number, month: number): Promise<Score[]> {
    const data = {
      department_id: departmentId,
      period_year: year,
      period_month: month,
    }
    return await apiService.post<Score[]>('/api/scores/calculate-department', data)
  }

  async calculateCompanyScores(year: number, month: number): Promise<Score[]> {
    const data = {
      period_year: year,
      period_month: month,
    }
    return await apiService.post<Score[]>('/api/scores/calculate-company', data)
  }

  async recalculatePeriod(year: number, month: number, departmentId?: number): Promise<{ successful: number; failed: number; errors: string[] }> {
    const data = {
      period_year: year,
      period_month: month,
      department_id: departmentId,
    }
    return await apiService.post<{ successful: number; failed: number; errors: string[] }>('/api/scores/recalculate', data)
  }

  // Rankings and trends
  async getTopPerformers(params: ScoreRankingRequest): Promise<ScoreRanking[]> {
    return await apiService.get<ScoreRanking[]>('/api/scores/top-performers', params)
  }

  async getDepartmentRankings(departmentId: number, year: number, month: number): Promise<ScoreRanking[]> {
    const params = {
      department_id: departmentId,
      period_year: year,
      period_month: month,
    }
    return await apiService.get<ScoreRanking[]>('/api/scores/department-rankings', params)
  }

  async getCompanyRankings(year: number, month: number): Promise<ScoreRanking[]> {
    const params = {
      period_year: year,
      period_month: month,
    }
    return await apiService.get<ScoreRanking[]>('/api/scores/company-rankings', params)
  }

  async getUserScoreTrend(userId: number, months = 12): Promise<ScoreTrend[]> {
    const params = {
      user_id: userId,
      months,
    }
    return await apiService.get<ScoreTrend[]>('/api/scores/user-trend', params)
  }

  async getDepartmentScoreTrend(departmentId: number, months = 12): Promise<ScoreTrend[]> {
    const params = {
      department_id: departmentId,
      months,
    }
    return await apiService.get<ScoreTrend[]>('/api/scores/department-trend', params)
  }

  async getCompanyScoreTrend(months = 12): Promise<ScoreTrend[]> {
    const params = { months }
    return await apiService.get<ScoreTrend[]>('/api/scores/company-trend', params)
  }

  // Export functions
  async exportScores(params?: ScoreListRequest): Promise<Blob> {
    const response = await apiService.getAxiosInstance().get('/api/scores/export', {
      params,
      responseType: 'blob',
    })
    return response.data
  }

  async exportRankings(params: ScoreRankingRequest): Promise<Blob> {
    const response = await apiService.getAxiosInstance().get('/api/scores/rankings/export', {
      params,
      responseType: 'blob',
    })
    return response.data
  }

  async exportScoreTrend(userId?: number, departmentId?: number, months = 12): Promise<Blob> {
    const params: any = { months }
    if (userId) params.user_id = userId
    if (departmentId) params.department_id = departmentId

    const response = await apiService.getAxiosInstance().get('/api/scores/trend/export', {
      params,
      responseType: 'blob',
    })
    return response.data
  }
}

export const scoreService = new ScoreServiceImpl()
export default scoreService