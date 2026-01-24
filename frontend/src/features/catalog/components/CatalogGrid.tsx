/**
 * CatalogGrid - Display catalog items in a responsive grid.
 */

import { Skeleton } from '@/components/ui/skeleton'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import type { CatalogItemSummary } from '../types'
import { CatalogCard } from './CatalogCard'

interface CatalogGridProps {
  items?: CatalogItemSummary[]
  isLoading: boolean
}

function CatalogCardSkeleton() {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <Skeleton className="h-5 w-32" />
          <Skeleton className="h-5 w-12" />
        </div>
      </CardHeader>
      <CardContent className="pt-0 space-y-3">
        <div className="space-y-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-3/4" />
        </div>
        <div className="flex gap-1">
          <Skeleton className="h-5 w-14" />
          <Skeleton className="h-5 w-16" />
        </div>
      </CardContent>
    </Card>
  )
}

function EmptyState() {
  return (
    <div className="col-span-full flex flex-col items-center justify-center py-12 text-center">
      <div className="text-muted-foreground">
        <p className="text-lg font-medium">No items found</p>
        <p className="text-sm mt-1">Try adjusting your search or filters</p>
      </div>
    </div>
  )
}

export function CatalogGrid({ items, isLoading }: CatalogGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <CatalogCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  if (!items || items.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <EmptyState />
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {items.map((item) => (
        <CatalogCard key={item.id} item={item} />
      ))}
    </div>
  )
}
