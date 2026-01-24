/**
 * Dashboard page showing user stats, available items, and configuration preview.
 */
import { AlertCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  useDashboard,
  useAvailableItems,
  useEffectiveConfiguration,
} from '@/features/profile/hooks/useProfile'
import {
  DashboardStats,
  DashboardStatsSkeleton,
  AvailableItems,
  AvailableItemsSkeleton,
  ConfigurationPreview,
  ConfigurationPreviewSkeleton,
} from '@/features/profile/components'

function DashboardError({ message, onRetry }: { message: string; onRetry: () => void }) {
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

export function DashboardPage() {
  const dashboard = useDashboard()
  const availableItems = useAvailableItems()
  const effectiveConfig = useEffectiveConfiguration()

  const isLoading = dashboard.isLoading
  const username = dashboard.data?.username ?? 'User'

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-6xl px-4 py-8">
        <header className="mb-8">
          <h1 className="text-2xl font-semibold text-foreground">
            Welcome back, {isLoading ? '...' : username}
          </h1>
          <p className="text-muted-foreground">Here's an overview of your configuration</p>
        </header>

        {dashboard.error ? (
          <DashboardError
            message="Failed to load dashboard data"
            onRetry={() => dashboard.refetch()}
          />
        ) : dashboard.isLoading || !dashboard.data ? (
          <DashboardStatsSkeleton />
        ) : (
          <DashboardStats data={dashboard.data} />
        )}

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          {availableItems.error ? (
            <DashboardError
              message="Failed to load available items"
              onRetry={() => availableItems.refetch()}
            />
          ) : availableItems.isLoading || !availableItems.data ? (
            <AvailableItemsSkeleton />
          ) : (
            <AvailableItems items={availableItems.data} />
          )}

          {effectiveConfig.error ? (
            <DashboardError
              message="Failed to load configuration"
              onRetry={() => effectiveConfig.refetch()}
            />
          ) : effectiveConfig.isLoading || !effectiveConfig.data ? (
            <ConfigurationPreviewSkeleton />
          ) : (
            <ConfigurationPreview config={effectiveConfig.data} />
          )}
        </div>
      </div>
    </div>
  )
}
