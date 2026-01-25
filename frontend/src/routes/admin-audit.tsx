/**
 * AdminAuditLogs - Audit log viewer for admins.
 */

import { useState } from 'react'
import { AlertCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAuditLogs } from '@/features/admin/hooks'
import { AuditLogList, AuditLogListSkeleton } from '@/features/admin/components/AuditLogList'

function AuditError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <Card className="border-destructive/50 bg-destructive/10">
      <CardContent className="flex items-center gap-4 py-4">
        <AlertCircle className="h-5 w-5 text-destructive" />
        <div className="flex-1">
          <p className="text-sm text-destructive">{message}</p>
        </div>
        <Button variant="outline" size="sm" onClick={onRetry}>
          Retry
        </Button>
      </CardContent>
    </Card>
  )
}

export function AdminAuditLogsPage() {
  const [page, setPage] = useState(1)
  const pageSize = 50
  const [filters, setFilters] = useState<{
    resource_type?: string
    action?: string
    user_id?: string
  }>({})

  const { data, isLoading, error, refetch } = useAuditLogs(page, pageSize, filters)

  const handleFilterChange = (newFilters: {
    resource_type?: string
    action?: string
    user_id?: string
  }) => {
    setFilters(newFilters)
    setPage(1) // Reset to first page when filters change
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-6xl px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-2xl font-semibold text-foreground">Audit Logs</h1>
          <p className="text-muted-foreground">View system-wide change history</p>
        </header>

        {/* Audit Log List */}
        {error ? (
          <AuditError message="Failed to load audit logs" onRetry={() => refetch()} />
        ) : isLoading || !data ? (
          <AuditLogListSkeleton />
        ) : (
          <AuditLogList
            data={data}
            page={page}
            onPageChange={setPage}
            filters={filters}
            onFilterChange={handleFilterChange}
          />
        )}
      </div>
    </div>
  )
}
