/**
 * TopItemsTable - Table showing most used catalog items.
 */

import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import type { UsageByItem } from '../types'

const typeColors: Record<string, string> = {
  skill: 'bg-emerald-500/10 text-emerald-500',
  mcp: 'bg-blue-500/10 text-blue-500',
  tool: 'bg-amber-500/10 text-amber-500',
}

export function TopItemsTableSkeleton() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Items</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Item</TableHead>
              <TableHead>Type</TableHead>
              <TableHead className="text-right">Events</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[1, 2, 3, 4, 5].map((i) => (
              <TableRow key={i}>
                <TableCell>
                  <Skeleton className="h-4 w-24" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-5 w-12" />
                </TableCell>
                <TableCell className="text-right">
                  <Skeleton className="ml-auto h-4 w-8" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

interface TopItemsTableProps {
  data: UsageByItem
}

export function TopItemsTable({ data }: TopItemsTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Items</CardTitle>
      </CardHeader>
      <CardContent>
        {data.items.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground">No usage data</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Item</TableHead>
                <TableHead>Type</TableHead>
                <TableHead className="text-right">Events</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((item) => (
                <TableRow key={item.item_id}>
                  <TableCell className="font-mono text-sm">
                    {item.item_id.slice(0, 8)}...
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="secondary"
                      className={typeColors[item.item_type.toLowerCase()] || ''}
                    >
                      {item.item_type}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">{item.count}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  )
}
