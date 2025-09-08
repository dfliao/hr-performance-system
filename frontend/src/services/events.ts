import { apiService } from './api'
import {
  Event,
  EventCreateRequest,
  EventUpdateRequest,
  EventApprovalRequest,
  EventListRequest,
  EventsSummary,
  PaginatedResponse,
} from '@/types/api'

export interface EventService {
  getEvents(params?: EventListRequest): Promise<PaginatedResponse<Event>>
  getEvent(id: number): Promise<Event>
  createEvent(data: EventCreateRequest): Promise<Event>
  updateEvent(id: number, data: EventUpdateRequest): Promise<Event>
  deleteEvent(id: number): Promise<void>
  approveEvent(id: number, data: EventApprovalRequest): Promise<Event>
  getEventsSummary(userId?: number, year?: number, month?: number): Promise<EventsSummary>
  exportEvents(params?: EventListRequest): Promise<Blob>
  bulkApproveEvents(eventIds: number[], data: EventApprovalRequest): Promise<Event[]>
  bulkDeleteEvents(eventIds: number[]): Promise<void>
}

class EventServiceImpl implements EventService {
  async getEvents(params?: EventListRequest): Promise<PaginatedResponse<Event>> {
    return await apiService.get<PaginatedResponse<Event>>('/api/events', params)
  }

  async getEvent(id: number): Promise<Event> {
    return await apiService.get<Event>(`/api/events/${id}`)
  }

  async createEvent(data: EventCreateRequest): Promise<Event> {
    return await apiService.post<Event>('/api/events', data)
  }

  async updateEvent(id: number, data: EventUpdateRequest): Promise<Event> {
    return await apiService.patch<Event>(`/api/events/${id}`, data)
  }

  async deleteEvent(id: number): Promise<void> {
    await apiService.delete<void>(`/api/events/${id}`)
  }

  async approveEvent(id: number, data: EventApprovalRequest): Promise<Event> {
    return await apiService.post<Event>(`/api/events/${id}/approve`, data)
  }

  async getEventsSummary(userId?: number, year?: number, month?: number): Promise<EventsSummary> {
    const params: any = {}
    if (userId) params.user_id = userId
    if (year) params.year = year
    if (month) params.month = month

    return await apiService.get<EventsSummary>('/api/events/summary', params)
  }

  async exportEvents(params?: EventListRequest): Promise<Blob> {
    const response = await apiService.getAxiosInstance().get('/api/events/export', {
      params,
      responseType: 'blob',
    })
    return response.data
  }

  async bulkApproveEvents(eventIds: number[], data: EventApprovalRequest): Promise<Event[]> {
    const requestData = {
      event_ids: eventIds,
      ...data,
    }
    return await apiService.post<Event[]>('/api/events/bulk-approve', requestData)
  }

  async bulkDeleteEvents(eventIds: number[]): Promise<void> {
    const requestData = {
      event_ids: eventIds,
    }
    await apiService.post<void>('/api/events/bulk-delete', requestData)
  }
}

export const eventService = new EventServiceImpl()
export default eventService