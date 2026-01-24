/**
 * CatalogFilters - Tab bar for filtering by catalog item type.
 */

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import type { CatalogItemType } from '../types'

type FilterValue = CatalogItemType | 'ALL'

interface CatalogFiltersProps {
  value: FilterValue
  onValueChange: (value: FilterValue) => void
}

export function CatalogFilters({ value, onValueChange }: CatalogFiltersProps) {
  return (
    <Tabs value={value} onValueChange={(v) => onValueChange(v as FilterValue)}>
      <TabsList>
        <TabsTrigger value="ALL">All</TabsTrigger>
        <TabsTrigger value="SKILL">Skills</TabsTrigger>
        <TabsTrigger value="MCP">MCPs</TabsTrigger>
        <TabsTrigger value="TOOL">Tools</TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
