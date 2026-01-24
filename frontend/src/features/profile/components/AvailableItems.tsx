/**
 * Available items card showing recent catalog items.
 */
import { Link } from 'react-router-dom'
import { ArrowRight, Package } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { AvailableItem } from '../types'

interface AvailableItemsProps {
  items: AvailableItem[]
}

const TYPE_BADGE_VARIANT: Record<string, 'default' | 'secondary' | 'outline'> = {
  skill: 'default',
  mcp: 'secondary',
  tool: 'outline',
}

function ItemRow({ item }: { item: AvailableItem }) {
  return (
    <Link
      to={`/catalog/${item.id}`}
      className="flex items-center gap-3 rounded-lg p-2 transition-colors hover:bg-muted"
    >
      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-muted">
        <Package className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="truncate font-medium">{item.name}</span>
          <Badge variant={TYPE_BADGE_VARIANT[item.type]} className="text-[10px] uppercase">
            {item.type}
          </Badge>
        </div>
        {item.description && (
          <p className="truncate text-sm text-muted-foreground">{item.description}</p>
        )}
      </div>
    </Link>
  )
}

function ItemRowSkeleton() {
  return (
    <div className="flex items-center gap-3 p-2">
      <Skeleton className="h-9 w-9 rounded-md" />
      <div className="flex-1 space-y-2">
        <div className="flex items-center gap-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-12" />
        </div>
        <Skeleton className="h-3 w-48" />
      </div>
    </div>
  )
}

export function AvailableItems({ items }: AvailableItemsProps) {
  const displayItems = items.slice(0, 5)

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base font-medium">Available Items</CardTitle>
        <Button variant="ghost" size="sm" asChild>
          <Link to="/catalog" className="flex items-center gap-1">
            View all
            <ArrowRight className="h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>
      <CardContent>
        {displayItems.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <Package className="mb-2 h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">No items available yet</p>
          </div>
        ) : (
          <div className="space-y-1">
            {displayItems.map((item) => (
              <ItemRow key={item.id} item={item} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function AvailableItemsSkeleton() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-8 w-20" />
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          <ItemRowSkeleton />
          <ItemRowSkeleton />
          <ItemRowSkeleton />
        </div>
      </CardContent>
    </Card>
  )
}
