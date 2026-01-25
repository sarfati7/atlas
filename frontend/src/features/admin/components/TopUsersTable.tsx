/**
 * TopUsersTable - Table showing users with most usage.
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
import { Skeleton } from '@/components/ui/skeleton'
import type { UsageByUser } from '../types'

export function TopUsersTableSkeleton() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Users</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead className="text-right">Events</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[1, 2, 3, 4, 5].map((i) => (
              <TableRow key={i}>
                <TableCell>
                  <Skeleton className="h-4 w-32" />
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

interface TopUsersTableProps {
  data: UsageByUser
}

export function TopUsersTable({ data }: TopUsersTableProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Top Users</CardTitle>
      </CardHeader>
      <CardContent>
        {data.items.length === 0 ? (
          <div className="py-8 text-center text-muted-foreground">No usage data</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead className="text-right">Events</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.items.map((item) => (
                <TableRow key={item.user_id}>
                  <TableCell className="font-medium">
                    {item.user_email || item.user_id.slice(0, 8)}
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
