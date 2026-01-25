/**
 * AdminAnalytics - Usage analytics dashboard for admins.
 */

import { AlertCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  useUsageSummary,
  useUsageTimeline,
  useUsageByUser,
  useUsageByItem,
} from '@/features/admin/hooks'
import {
  UsageSummaryCards,
  UsageSummaryCardsSkeleton,
} from '@/features/admin/components/UsageSummaryCards'
import { UsageChart, UsageChartSkeleton } from '@/features/admin/components/UsageChart'
import { TopUsersTable, TopUsersTableSkeleton } from '@/features/admin/components/TopUsersTable'
import { TopItemsTable, TopItemsTableSkeleton } from '@/features/admin/components/TopItemsTable'

function AnalyticsError({ message, onRetry }: { message: string; onRetry: () => void }) {
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

export function AdminAnalyticsPage() {
  const summary = useUsageSummary()
  const timeline = useUsageTimeline()
  const byUser = useUsageByUser()
  const byItem = useUsageByItem()

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-6xl px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-2xl font-semibold text-foreground">Usage Analytics</h1>
          <p className="text-muted-foreground">Monitor tool usage across your organization</p>
        </header>

        {/* Summary Cards */}
        <section className="mb-8">
          {summary.error ? (
            <AnalyticsError
              message="Failed to load usage summary"
              onRetry={() => summary.refetch()}
            />
          ) : summary.isLoading || !summary.data ? (
            <UsageSummaryCardsSkeleton />
          ) : (
            <UsageSummaryCards data={summary.data} />
          )}
        </section>

        {/* Timeline Chart */}
        <section className="mb-8">
          {timeline.error ? (
            <AnalyticsError
              message="Failed to load timeline"
              onRetry={() => timeline.refetch()}
            />
          ) : timeline.isLoading || !timeline.data ? (
            <UsageChartSkeleton />
          ) : (
            <UsageChart data={timeline.data} />
          )}
        </section>

        {/* Top Users and Items */}
        <div className="grid gap-6 lg:grid-cols-2">
          {byUser.error ? (
            <AnalyticsError
              message="Failed to load top users"
              onRetry={() => byUser.refetch()}
            />
          ) : byUser.isLoading || !byUser.data ? (
            <TopUsersTableSkeleton />
          ) : (
            <TopUsersTable data={byUser.data} />
          )}

          {byItem.error ? (
            <AnalyticsError
              message="Failed to load top items"
              onRetry={() => byItem.refetch()}
            />
          ) : byItem.isLoading || !byItem.data ? (
            <TopItemsTableSkeleton />
          ) : (
            <TopItemsTable data={byItem.data} />
          )}
        </div>
      </div>
    </div>
  )
}
