/**
 * Catalog feature types.
 *
 * Maps to backend catalog API responses.
 */

export type CatalogItemType = 'skill' | 'mcp' | 'tool'

export interface CatalogItemSummary {
  id: string
  type: CatalogItemType
  name: string
  description: string
  tags: string[]
  author_id: string
  team_id: string | null
  usage_count: number
}

export interface CatalogItemDetail extends CatalogItemSummary {
  git_path: string
  created_at: string
  updated_at: string
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
