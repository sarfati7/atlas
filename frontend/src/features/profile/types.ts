/**
 * Profile feature types matching backend API responses.
 */

/** Team membership info for dashboard. */
export interface Team {
  id: string
  name: string
  role: string
}

/** Dashboard summary data from /api/v1/profile/dashboard. */
export interface DashboardData {
  user_id: string
  username: string
  teams: Team[]
  available_items_count: number
  has_configuration: boolean
}

/** Effective configuration with inheritance breakdown. */
export interface EffectiveConfiguration {
  content: string
  org_applied: boolean
  team_applied: boolean
  user_applied: boolean
}

/** Catalog item summary (matches backend CatalogItem entity). */
export interface AvailableItem {
  id: string
  name: string
  type: 'skill' | 'mcp' | 'tool'
  description: string | null
  tags: string[]
  git_path: string
  created_at: string
  updated_at: string
}
