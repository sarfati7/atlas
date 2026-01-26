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

// Analytics types

export interface UsageSummary {
  total_events: number
  total_users: number
  total_items: number
  events_today: number
  events_this_week: number
  events_this_month: number
  top_action: string | null
}

export interface UsageByUserItem {
  user_id: string
  user_email: string | null
  count: number
}

export interface UsageByUser {
  items: UsageByUserItem[]
  total: number
}

export interface UsageByItemItem {
  item_id: string
  item_type: string
  count: number
}

export interface UsageByItem {
  items: UsageByItemItem[]
  total: number
}

export interface UsageTimelineItem {
  date: string
  count: number
}

export interface UsageTimeline {
  items: UsageTimelineItem[]
}

// Audit log types

export interface AuditLog {
  id: string
  user_id: string
  user_email: string | null
  action: string
  resource_type: string
  resource_id: string
  details: Record<string, unknown>
  created_at: string
}

export interface AuditLogsResponse {
  items: AuditLog[]
  total: number
  page: number
  page_size: number
}

// Admin settings types

export interface GitHubSettings {
  repo: string | null
  token_configured: boolean
  updated_at: string | null
  updated_by: string | null
}

export interface GitHubSettingsRequest {
  repo: string
  token: string
}

export interface ConnectionTestResponse {
  success: boolean
  message: string
  repo_name: string | null
}
