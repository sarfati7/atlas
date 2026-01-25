/**
 * UsageSummaryCards - Grid of stat cards showing usage metrics.
 */

import { Activity, Users, Package, TrendingUp } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { UsageSummary } from '../types'

interface StatCardProps {
  label: string
  value: number | string
  icon: React.ReactNode
  trend?: string
}

function StatCard({ label, value, icon, trend }: StatCardProps) {
  return (
    <Card className="py-4">
      <CardContent className="flex items-center justify-between">
        <div>
          <p className="text-sm text-muted-foreground">{label}</p>
          <p className="text-2xl font-semibold text-foreground">{value}</p>
          {trend && <p className="text-xs text-muted-foreground mt-1">{trend}</p>}
        </div>
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent text-accent-foreground">
          {icon}
        </div>
      </CardContent>
    </Card>
  )
}

export function UsageSummaryCardsSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {[1, 2, 3, 4].map((i) => (
        <Card key={i} className="py-4">
          <CardContent className="flex items-center justify-between">
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-8 w-16" />
            </div>
            <Skeleton className="h-10 w-10 rounded-lg" />
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

interface UsageSummaryCardsProps {
  data: UsageSummary
}

export function UsageSummaryCards({ data }: UsageSummaryCardsProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        label="Total Events"
        value={data.total_events.toLocaleString()}
        icon={<Activity className="h-5 w-5" />}
        trend={`${data.events_today} today`}
      />
      <StatCard
        label="Active Users"
        value={data.total_users}
        icon={<Users className="h-5 w-5" />}
        trend={`${data.events_this_week} events this week`}
      />
      <StatCard
        label="Items Used"
        value={data.total_items}
        icon={<Package className="h-5 w-5" />}
        trend={`${data.events_this_month} events this month`}
      />
      <StatCard
        label="Top Action"
        value={data.top_action || 'N/A'}
        icon={<TrendingUp className="h-5 w-5" />}
      />
    </div>
  )
}
