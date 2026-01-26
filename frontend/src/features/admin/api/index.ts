/**
 * Admin API layer for team and user management.
 *
 * Maps to backend /api/v1/admin/* endpoints.
 */

import { apiClient } from '@/lib/api'
import type {
  Team,
  TeamWithMembers,
  AdminUser,
  PaginatedResponse,
  CreateTeamRequest,
  UpdateTeamRequest,
  UpdateUserRoleRequest,
  UsageSummary,
  UsageByUser,
  UsageByItem,
  UsageTimeline,
  AuditLogsResponse,
  AuditLog,
  GitHubSettings,
  GitHubSettingsRequest,
  ConnectionTestResponse,
} from '../types'

export const adminApi = {
  // Team endpoints

  /**
   * Get paginated list of teams.
   */
  async fetchTeams(page = 1, pageSize = 10): Promise<PaginatedResponse<Team>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })
    const response = await apiClient.get<PaginatedResponse<Team>>(`/api/v1/admin/teams?${params}`)
    return response.data
  },

  /**
   * Get a single team with its members.
   */
  async fetchTeam(id: string): Promise<TeamWithMembers> {
    const response = await apiClient.get<TeamWithMembers>(`/api/v1/admin/teams/${id}`)
    return response.data
  },

  /**
   * Create a new team.
   */
  async createTeam(data: CreateTeamRequest): Promise<Team> {
    const response = await apiClient.post<Team>('/api/v1/admin/teams', data)
    return response.data
  },

  /**
   * Update a team.
   */
  async updateTeam(id: string, data: UpdateTeamRequest): Promise<Team> {
    const response = await apiClient.put<Team>(`/api/v1/admin/teams/${id}`, data)
    return response.data
  },

  /**
   * Delete a team.
   */
  async deleteTeam(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/admin/teams/${id}`)
  },

  /**
   * Add a member to a team.
   */
  async addTeamMember(teamId: string, userId: string): Promise<Team> {
    const response = await apiClient.post<Team>(`/api/v1/admin/teams/${teamId}/members`, {
      user_id: userId,
    })
    return response.data
  },

  /**
   * Remove a member from a team.
   */
  async removeTeamMember(teamId: string, userId: string): Promise<Team> {
    const response = await apiClient.delete<Team>(
      `/api/v1/admin/teams/${teamId}/members/${userId}`
    )
    return response.data
  },

  // User endpoints

  /**
   * Get paginated list of users with optional search.
   */
  async fetchUsers(
    page = 1,
    pageSize = 10,
    search?: string
  ): Promise<PaginatedResponse<AdminUser>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })
    if (search) {
      params.set('search', search)
    }
    const response = await apiClient.get<PaginatedResponse<AdminUser>>(
      `/api/v1/admin/users?${params}`
    )
    return response.data
  },

  /**
   * Get a single user with their teams.
   */
  async fetchUser(id: string): Promise<AdminUser> {
    const response = await apiClient.get<AdminUser>(`/api/v1/admin/users/${id}`)
    return response.data
  },

  /**
   * Update a user's role.
   */
  async updateUserRole(id: string, data: UpdateUserRoleRequest): Promise<AdminUser> {
    const response = await apiClient.put<AdminUser>(`/api/v1/admin/users/${id}/role`, data)
    return response.data
  },

  /**
   * Delete a user.
   */
  async deleteUser(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/admin/users/${id}`)
  },

  // Analytics endpoints

  /**
   * Get usage summary.
   */
  async fetchUsageSummary(startDate?: string, endDate?: string): Promise<UsageSummary> {
    const params = new URLSearchParams()
    if (startDate) params.set('start_date', startDate)
    if (endDate) params.set('end_date', endDate)
    const query = params.toString()
    const response = await apiClient.get<UsageSummary>(
      `/api/v1/admin/analytics/summary${query ? `?${query}` : ''}`
    )
    return response.data
  },

  /**
   * Get usage by user.
   */
  async fetchUsageByUser(
    startDate?: string,
    endDate?: string,
    limit = 20
  ): Promise<UsageByUser> {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (startDate) params.set('start_date', startDate)
    if (endDate) params.set('end_date', endDate)
    const response = await apiClient.get<UsageByUser>(
      `/api/v1/admin/analytics/usage-by-user?${params}`
    )
    return response.data
  },

  /**
   * Get usage by item.
   */
  async fetchUsageByItem(
    startDate?: string,
    endDate?: string,
    limit = 20
  ): Promise<UsageByItem> {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (startDate) params.set('start_date', startDate)
    if (endDate) params.set('end_date', endDate)
    const response = await apiClient.get<UsageByItem>(
      `/api/v1/admin/analytics/usage-by-item?${params}`
    )
    return response.data
  },

  /**
   * Get usage timeline.
   */
  async fetchUsageTimeline(startDate?: string, endDate?: string): Promise<UsageTimeline> {
    const params = new URLSearchParams()
    if (startDate) params.set('start_date', startDate)
    if (endDate) params.set('end_date', endDate)
    const query = params.toString()
    const response = await apiClient.get<UsageTimeline>(
      `/api/v1/admin/analytics/usage-timeline${query ? `?${query}` : ''}`
    )
    return response.data
  },

  // Audit log endpoints

  /**
   * Get paginated audit logs.
   */
  async fetchAuditLogs(
    page = 1,
    pageSize = 50,
    filters?: {
      resource_type?: string
      resource_id?: string
      user_id?: string
      action?: string
    }
  ): Promise<AuditLogsResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    })
    if (filters?.resource_type) params.set('resource_type', filters.resource_type)
    if (filters?.resource_id) params.set('resource_id', filters.resource_id)
    if (filters?.user_id) params.set('user_id', filters.user_id)
    if (filters?.action) params.set('action', filters.action)
    const response = await apiClient.get<AuditLogsResponse>(
      `/api/v1/admin/audit/logs?${params}`
    )
    return response.data
  },

  /**
   * Get a single audit log.
   */
  async fetchAuditLog(id: string): Promise<AuditLog> {
    const response = await apiClient.get<AuditLog>(`/api/v1/admin/audit/logs/${id}`)
    return response.data
  },

  /**
   * Get audit trail for a resource.
   */
  async fetchResourceAuditTrail(
    resourceType: string,
    resourceId: string
  ): Promise<{ items: AuditLog[] }> {
    const response = await apiClient.get<{ items: AuditLog[] }>(
      `/api/v1/admin/audit/resources/${resourceType}/${resourceId}`
    )
    return response.data
  },

  // Settings endpoints

  /**
   * Get GitHub integration settings.
   */
  async fetchGitHubSettings(): Promise<GitHubSettings> {
    const response = await apiClient.get<GitHubSettings>('/api/v1/admin/settings/github')
    return response.data
  },

  /**
   * Update GitHub integration settings.
   */
  async updateGitHubSettings(data: GitHubSettingsRequest): Promise<GitHubSettings> {
    const response = await apiClient.put<GitHubSettings>('/api/v1/admin/settings/github', data)
    return response.data
  },

  /**
   * Test GitHub connection.
   */
  async testGitHubConnection(): Promise<ConnectionTestResponse> {
    const response = await apiClient.post<ConnectionTestResponse>(
      '/api/v1/admin/settings/github/test'
    )
    return response.data
  },

  /**
   * Remove GitHub integration settings.
   */
  async removeGitHubSettings(): Promise<void> {
    await apiClient.delete('/api/v1/admin/settings/github')
  },
}
