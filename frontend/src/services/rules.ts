import { apiService } from './api'
import { Rule, RulePack, PaginatedResponse } from '@/types/api'

export interface RuleListRequest {
  skip?: number
  limit?: number
  rule_pack_id?: number
  category?: string
  active?: boolean
  search?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface RulePackListRequest {
  skip?: number
  limit?: number
  status?: 'draft' | 'active' | 'archived'
  scope?: 'company' | 'department' | 'role'
  search?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface RuleCreateRequest {
  name: string
  code: string
  description: string
  category: string
  base_score: number
  weight: number
  caps?: number
  evidence_required: boolean
  rule_pack_id: number
}

export interface RuleUpdateRequest {
  name?: string
  code?: string
  description?: string
  category?: string
  base_score?: number
  weight?: number
  caps?: number
  evidence_required?: boolean
  active?: boolean
}

export interface RulePackCreateRequest {
  name: string
  version: string
  description: string
  scope: 'company' | 'department' | 'role'
  effective_from: string
  effective_to?: string
}

export interface RulePackUpdateRequest {
  name?: string
  description?: string
  status?: 'draft' | 'active' | 'archived'
  effective_from?: string
  effective_to?: string
}

export interface RuleService {
  // Rule operations
  getRules(params?: RuleListRequest): Promise<PaginatedResponse<Rule>>
  getRule(id: number): Promise<Rule>
  createRule(data: RuleCreateRequest): Promise<Rule>
  updateRule(id: number, data: RuleUpdateRequest): Promise<Rule>
  deleteRule(id: number): Promise<void>
  getActiveRules(): Promise<Rule[]>
  getRulesByCategory(category: string): Promise<Rule[]>
  
  // Rule pack operations
  getRulePacks(params?: RulePackListRequest): Promise<PaginatedResponse<RulePack>>
  getRulePack(id: number): Promise<RulePack>
  createRulePack(data: RulePackCreateRequest): Promise<RulePack>
  updateRulePack(id: number, data: RulePackUpdateRequest): Promise<RulePack>
  deleteRulePack(id: number): Promise<void>
  activateRulePack(id: number): Promise<RulePack>
  archiveRulePack(id: number): Promise<RulePack>
  getRulePackRules(rulePackId: number): Promise<Rule[]>
  
  // Bulk operations
  bulkUpdateRules(ruleIds: number[], data: Partial<RuleUpdateRequest>): Promise<Rule[]>
  duplicateRulePack(rulePackId: number, newName: string, newVersion: string): Promise<RulePack>
}

class RuleServiceImpl implements RuleService {
  // Rule operations
  async getRules(params?: RuleListRequest): Promise<PaginatedResponse<Rule>> {
    return await apiService.get<PaginatedResponse<Rule>>('/api/rules', params)
  }

  async getRule(id: number): Promise<Rule> {
    return await apiService.get<Rule>(`/api/rules/${id}`)
  }

  async createRule(data: RuleCreateRequest): Promise<Rule> {
    return await apiService.post<Rule>('/api/rules', data)
  }

  async updateRule(id: number, data: RuleUpdateRequest): Promise<Rule> {
    return await apiService.patch<Rule>(`/api/rules/${id}`, data)
  }

  async deleteRule(id: number): Promise<void> {
    await apiService.delete<void>(`/api/rules/${id}`)
  }

  async getActiveRules(): Promise<Rule[]> {
    const response = await apiService.get<PaginatedResponse<Rule>>('/api/rules', {
      active: true,
      limit: 1000,
    })
    return response.items
  }

  async getRulesByCategory(category: string): Promise<Rule[]> {
    const response = await apiService.get<PaginatedResponse<Rule>>('/api/rules', {
      category,
      active: true,
      limit: 1000,
    })
    return response.items
  }

  // Rule pack operations
  async getRulePacks(params?: RulePackListRequest): Promise<PaginatedResponse<RulePack>> {
    return await apiService.get<PaginatedResponse<RulePack>>('/api/rule-packs', params)
  }

  async getRulePack(id: number): Promise<RulePack> {
    return await apiService.get<RulePack>(`/api/rule-packs/${id}`)
  }

  async createRulePack(data: RulePackCreateRequest): Promise<RulePack> {
    return await apiService.post<RulePack>('/api/rule-packs', data)
  }

  async updateRulePack(id: number, data: RulePackUpdateRequest): Promise<RulePack> {
    return await apiService.patch<RulePack>(`/api/rule-packs/${id}`, data)
  }

  async deleteRulePack(id: number): Promise<void> {
    await apiService.delete<void>(`/api/rule-packs/${id}`)
  }

  async activateRulePack(id: number): Promise<RulePack> {
    return await apiService.post<RulePack>(`/api/rule-packs/${id}/activate`)
  }

  async archiveRulePack(id: number): Promise<RulePack> {
    return await apiService.post<RulePack>(`/api/rule-packs/${id}/archive`)
  }

  async getRulePackRules(rulePackId: number): Promise<Rule[]> {
    const response = await apiService.get<PaginatedResponse<Rule>>('/api/rules', {
      rule_pack_id: rulePackId,
      limit: 1000,
    })
    return response.items
  }

  // Bulk operations
  async bulkUpdateRules(ruleIds: number[], data: Partial<RuleUpdateRequest>): Promise<Rule[]> {
    const requestData = {
      rule_ids: ruleIds,
      ...data,
    }
    return await apiService.post<Rule[]>('/api/rules/bulk-update', requestData)
  }

  async duplicateRulePack(rulePackId: number, newName: string, newVersion: string): Promise<RulePack> {
    const data = {
      name: newName,
      version: newVersion,
    }
    return await apiService.post<RulePack>(`/api/rule-packs/${rulePackId}/duplicate`, data)
  }
}

export const ruleService = new RuleServiceImpl()
export default ruleService