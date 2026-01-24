/**
 * Dashboard stats grid showing user's counts.
 */
import { Code, Puzzle, Users, Wrench } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { DashboardData } from '../types'

interface DashboardStatsProps {
  data: DashboardData
}

interface StatCardProps {
  label: string
  value: number
  icon: React.ReactNode
}

function StatCard({ label, value, icon }: StatCardProps) {
  return (
    <Card className="py-4">
      <CardContent className="flex items-center gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
          {icon}
        </div>
        <div>
          <p className="text-2xl font-semibold">{value}</p>
          <p className="text-sm text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  )
}

function StatCardSkeleton() {
  return (
    <Card className="py-4">
      <CardContent className="flex items-center gap-4">
        <Skeleton className="h-12 w-12 rounded-lg" />
        <div className="space-y-2">
          <Skeleton className="h-7 w-12" />
          <Skeleton className="h-4 w-16" />
        </div>
      </CardContent>
    </Card>
  )
}

export function DashboardStats({ data }: DashboardStatsProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCard
        label="Teams"
        value={data.teams.length}
        icon={<Users className="h-5 w-5 text-muted-foreground" />}
      />
      <StatCard
        label="Skills"
        value={data.available_items_count}
        icon={<Code className="h-5 w-5 text-muted-foreground" />}
      />
      <StatCard
        label="MCPs"
        value={0}
        icon={<Puzzle className="h-5 w-5 text-muted-foreground" />}
      />
      <StatCard
        label="Tools"
        value={0}
        icon={<Wrench className="h-5 w-5 text-muted-foreground" />}
      />
    </div>
  )
}

export function DashboardStatsSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatCardSkeleton />
      <StatCardSkeleton />
      <StatCardSkeleton />
      <StatCardSkeleton />
    </div>
  )
}
