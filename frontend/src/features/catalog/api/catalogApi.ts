/**
 * Catalog API layer.
 *
 * Maps to backend /api/v1/catalog endpoints.
 */

import { apiClient } from '@/lib/api'
import type { CatalogFilters, CatalogItemDetail, PaginatedCatalog } from '../types'

export const catalogApi = {
  /**
   * Get paginated catalog items with optional filters.
   */
  async getItems(filters: CatalogFilters = {}): Promise<PaginatedCatalog> {
    const params = new URLSearchParams()

    if (filters.type) {
      params.set('type', filters.type)
    }
    if (filters.q) {
      params.set('q', filters.q)
    }
    if (filters.page) {
      params.set('page', filters.page.toString())
    }
    if (filters.size) {
      params.set('size', filters.size.toString())
    }

    const response = await apiClient.get<PaginatedCatalog>('/api/v1/catalog', { params })
    return response.data
  },

  /**
   * Get a single catalog item by ID with full documentation.
   */
  async getItemById(id: string): Promise<CatalogItemDetail> {
    const response = await apiClient.get<CatalogItemDetail>(`/api/v1/catalog/${id}`)
    return response.data
  },
}
