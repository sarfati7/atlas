/**
 * Catalog TanStack Query hooks.
 */

import { useQuery } from '@tanstack/react-query'
import { catalogApi } from '../api/catalogApi'
import type { CatalogFilters } from '../types'

/**
 * Query key factory for catalog queries.
 */
export const catalogKeys = {
  all: ['catalog'] as const,
  lists: () => [...catalogKeys.all, 'list'] as const,
  list: (filters: CatalogFilters) => [...catalogKeys.lists(), filters] as const,
  details: () => [...catalogKeys.all, 'detail'] as const,
  detail: (id: string) => [...catalogKeys.details(), id] as const,
}

/**
 * Hook to fetch paginated catalog items with filters.
 */
export function useCatalogItems(filters: CatalogFilters = {}) {
  return useQuery({
    queryKey: catalogKeys.list(filters),
    queryFn: () => catalogApi.getItems(filters),
  })
}

/**
 * Hook to fetch a single catalog item by ID.
 */
export function useCatalogItem(id: string) {
  return useQuery({
    queryKey: catalogKeys.detail(id),
    queryFn: () => catalogApi.getItemById(id),
    enabled: !!id,
  })
}
