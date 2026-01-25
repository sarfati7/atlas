/**
 * Admin feature types for team and user management.
 *
 * Maps to backend /api/v1/admin/* endpoints.
 */

export type UserRole = 'admin' | 'user'

export interface Team {
  id: string
  name: string
  member_ids: string[]
  created_at: string
  updated_at: string
}

export interface AdminUser {
  id: string
  email: string
  username: string
  role: UserRole
  team_ids: string[]
  created_at: string
}

export interface TeamWithMembers {
  team: Team
  members: AdminUser[]
}

export interface AdminUserWithTeams {
  user: AdminUser
  teams: Team[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface CreateTeamRequest {
  name: string
}

export interface UpdateTeamRequest {
  name: string
}

export interface AddTeamMemberRequest {
  user_id: string
}

export interface UpdateUserRoleRequest {
  role: UserRole
}
