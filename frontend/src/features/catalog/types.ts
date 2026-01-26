/**
 * Catalog feature types.
 *
 * Maps to backend catalog API responses.
 */

export type CatalogItemType = 'skill' | 'mcp' | 'tool'

/**
 * Scope determines visibility of catalog items.
 * - org: Visible to everyone in the organization
 * - team: Visible only to team members
 * - user: Visible only to that specific user
 */
export type CatalogScope = 'org' | 'team' | 'user'

export interface CatalogItemSummary {
  id: string
  type: CatalogItemType
  name: string
  description: string
  tags: string[]
  scope: CatalogScope
  scope_id: string | null  // team_id or user_id (null for org)
}

export interface CatalogItemDetail extends CatalogItemSummary {
  git_path: string
  documentation: string
}

export interface PaginatedCatalog {
  items: CatalogItemSummary[]
  total: number
  page: number
  size: number
  pages: number
}

export interface CatalogQueryParams {
  type?: CatalogItemType
  q?: string
  page?: number
  size?: number
}
