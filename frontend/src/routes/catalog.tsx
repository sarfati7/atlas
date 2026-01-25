/**
 * CatalogPage - Browse catalog items with search and filters.
 */

import { useState, useMemo } from 'react'
import { useCatalogItems } from '@/features/catalog/hooks/useCatalog'
import { CatalogGrid } from '@/features/catalog/components/CatalogGrid'
import { CatalogFilters } from '@/features/catalog/components/CatalogFilters'
import { CatalogSearch } from '@/features/catalog/components/CatalogSearch'
import type { CatalogItemType } from '@/features/catalog/types'

type FilterValue = CatalogItemType | 'all'

export function CatalogPage() {
  const [typeFilter, setTypeFilter] = useState<FilterValue>('all')
  const [searchQuery, setSearchQuery] = useState('')

  // Build query params
  const queryParams = useMemo(() => {
    const params: { type?: CatalogItemType; q?: string } = {}
    if (typeFilter !== 'all') {
      params.type = typeFilter
    }
    if (searchQuery.trim()) {
      params.q = searchQuery.trim()
    }
    return params
  }, [typeFilter, searchQuery])

  const { data, isLoading } = useCatalogItems(queryParams)

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Page header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Catalog</h1>
        <p className="text-muted-foreground mt-1">
          Browse available skills, MCPs, and tools
        </p>
      </div>

      {/* Filters and search */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <CatalogFilters value={typeFilter} onValueChange={setTypeFilter} />
        <CatalogSearch value={searchQuery} onChange={setSearchQuery} />
      </div>

      {/* Catalog grid */}
      <CatalogGrid items={data?.items} isLoading={isLoading} />

      {/* Pagination info */}
      {data && data.total > 0 && (
        <div className="mt-6 text-sm text-muted-foreground text-center">
          Showing {data.items.length} of {data.total} items
          {data.pages > 1 && ` (page ${data.page} of ${data.pages})`}
        </div>
      )}
    </div>
  )
}
