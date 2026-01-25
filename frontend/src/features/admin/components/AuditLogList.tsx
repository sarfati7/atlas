/**
 * AuditLogList - Table of audit log entries with expandable details.
 */

import { useState } from 'react'
import { ChevronDown, ChevronRight, Filter } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
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
import type { AuditLog, AuditLogsResponse } from '../types'

const actionColors: Record<string, string> = {
  created: 'bg-emerald-500/10 text-emerald-500',
  updated: 'bg-blue-500/10 text-blue-500',
  deleted: 'bg-red-500/10 text-red-500',
  changed: 'bg-amber-500/10 text-amber-500',
}

function getActionColor(action: string): string {
  for (const [key, color] of Object.entries(actionColors)) {
    if (action.toLowerCase().includes(key)) {
      return color
    }
  }
  return ''
}

interface AuditLogRowProps {
  log: AuditLog
  isExpanded: boolean
  onToggle: () => void
}

function AuditLogRow({ log, isExpanded, onToggle }: AuditLogRowProps) {
  const hasDetails = Object.keys(log.details).length > 0

  return (
    <>
      <TableRow className="cursor-pointer hover:bg-accent/50" onClick={onToggle}>
        <TableCell className="w-8">
          {hasDetails && (
            <span className="text-muted-foreground">
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </span>
          )}
        </TableCell>
        <TableCell>
          <Badge variant="secondary" className={getActionColor(log.action)}>
            {log.action}
          </Badge>
        </TableCell>
        <TableCell>{log.resource_type}</TableCell>
        <TableCell className="font-mono text-sm">{log.resource_id.slice(0, 8)}...</TableCell>
        <TableCell>{log.user_email || log.user_id.slice(0, 8)}</TableCell>
        <TableCell className="text-muted-foreground text-sm">
          {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
        </TableCell>
      </TableRow>
      {isExpanded && hasDetails && (
        <TableRow>
          <TableCell colSpan={6} className="bg-muted/30">
            <div className="p-4">
              <pre className="text-sm text-muted-foreground overflow-auto max-h-48 rounded-md bg-background p-3 border">
                {JSON.stringify(log.details, null, 2)}
              </pre>
            </div>
          </TableCell>
        </TableRow>
      )}
    </>
  )
}

export function AuditLogListSkeleton() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Audit Logs</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-8" />
              <TableHead>Action</TableHead>
              <TableHead>Resource</TableHead>
              <TableHead>ID</TableHead>
              <TableHead>User</TableHead>
              <TableHead>Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <TableRow key={i}>
                <TableCell />
                <TableCell>
                  <Skeleton className="h-5 w-20" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-16" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-20" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-32" />
                </TableCell>
                <TableCell>
                  <Skeleton className="h-4 w-24" />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

interface AuditLogListProps {
  data: AuditLogsResponse
  page: number
  onPageChange: (page: number) => void
  onFilterChange?: (filters: {
    resource_type?: string
    action?: string
    user_id?: string
  }) => void
  filters?: {
    resource_type?: string
    action?: string
    user_id?: string
  }
}

export function AuditLogList({
  data,
  page,
  onPageChange,
  onFilterChange,
  filters = {},
}: AuditLogListProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [filterInput, setFilterInput] = useState({
    resource_type: filters.resource_type || '',
    action: filters.action || '',
  })

  const totalPages = Math.ceil(data.total / data.page_size)

  const handleToggle = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  const handleApplyFilters = () => {
    onFilterChange?.({
      resource_type: filterInput.resource_type || undefined,
      action: filterInput.action || undefined,
    })
  }

  const handleClearFilters = () => {
    setFilterInput({ resource_type: '', action: '' })
    onFilterChange?.({})
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Audit Logs</CardTitle>
        <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)}>
          <Filter className="mr-2 h-4 w-4" />
          Filters
        </Button>
      </CardHeader>
      <CardContent>
        {showFilters && (
          <div className="mb-4 flex gap-2 flex-wrap">
            <Input
              placeholder="Resource type..."
              value={filterInput.resource_type}
              onChange={(e) =>
                setFilterInput({ ...filterInput, resource_type: e.target.value })
              }
              className="w-40"
            />
            <Input
              placeholder="Action..."
              value={filterInput.action}
              onChange={(e) => setFilterInput({ ...filterInput, action: e.target.value })}
              className="w-40"
            />
            <Button size="sm" onClick={handleApplyFilters}>
              Apply
            </Button>
            <Button size="sm" variant="outline" onClick={handleClearFilters}>
              Clear
            </Button>
          </div>
        )}

        {data.items.length === 0 ? (
          <div className="py-12 text-center text-muted-foreground">No audit logs found</div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-8" />
                  <TableHead>Action</TableHead>
                  <TableHead>Resource</TableHead>
                  <TableHead>ID</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Time</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((log) => (
                  <AuditLogRow
                    key={log.id}
                    log={log}
                    isExpanded={expandedId === log.id}
                    onToggle={() => handleToggle(log.id)}
                  />
                ))}
              </TableBody>
            </Table>

            {totalPages > 1 && (
              <div className="mt-4 flex items-center justify-between">
                <p className="text-sm text-muted-foreground">
                  Page {page} of {totalPages} ({data.total} entries)
                </p>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onPageChange(page - 1)}
                    disabled={page <= 1}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onPageChange(page + 1)}
                    disabled={page >= totalPages}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
