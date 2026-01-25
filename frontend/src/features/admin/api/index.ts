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
}
