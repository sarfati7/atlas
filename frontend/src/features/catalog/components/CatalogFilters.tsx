/**
 * CatalogFilters - Tab bar for filtering by catalog item type.
 */

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { CatalogItemType } from '../types'

type FilterValue = CatalogItemType | 'all'

interface CatalogFiltersProps {
  value: FilterValue
  onValueChange: (value: FilterValue) => void
}

export function CatalogFilters({ value, onValueChange }: CatalogFiltersProps) {
  return (
    <Tabs value={value} onValueChange={(v) => onValueChange(v as FilterValue)}>
      <TabsList>
        <TabsTrigger value="all">All</TabsTrigger>
        <TabsTrigger value="skill">Skills</TabsTrigger>
        <TabsTrigger value="mcp">MCPs</TabsTrigger>
        <TabsTrigger value="tool">Tools</TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
