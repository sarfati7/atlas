/**
 * Configuration preview card with inheritance status.
 */
import { Link } from 'react-router-dom'
import { Building2, FileText, Settings, User, Users } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import type { EffectiveConfiguration } from '../types'

interface ConfigurationPreviewProps {
  config: EffectiveConfiguration
}

interface InheritanceIndicatorProps {
  label: string
  icon: React.ReactNode
  applied: boolean
}

function InheritanceIndicator({ label, icon, applied }: InheritanceIndicatorProps) {
  return (
    <div className="flex items-center gap-2">
      {icon}
      <span className="text-sm">{label}</span>
      <Badge variant={applied ? 'default' : 'outline'} className="text-[10px]">
        {applied ? 'Active' : 'None'}
      </Badge>
    </div>
  )
}

export function ConfigurationPreview({ config }: ConfigurationPreviewProps) {
  const hasAnyConfig = config.org_applied || config.team_applied || config.user_applied
  const previewContent = config.content.slice(0, 200)
  const isTruncated = config.content.length > 200

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-base font-medium">Effective Configuration</CardTitle>
        <Button variant="ghost" size="sm" asChild>
          <Link to="/settings" className="flex items-center gap-1">
            <Settings className="h-4 w-4" />
            Edit
          </Link>
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-4">
          <InheritanceIndicator
            label="Organization"
            icon={<Building2 className="h-4 w-4 text-muted-foreground" />}
            applied={config.org_applied}
          />
          <InheritanceIndicator
            label="Team"
            icon={<Users className="h-4 w-4 text-muted-foreground" />}
            applied={config.team_applied}
          />
          <InheritanceIndicator
            label="Personal"
            icon={<User className="h-4 w-4 text-muted-foreground" />}
            applied={config.user_applied}
          />
        </div>

        {hasAnyConfig ? (
          <div className="rounded-lg bg-muted p-3">
            <pre className="overflow-hidden text-xs text-muted-foreground">
              {previewContent}
              {isTruncated && '...'}
            </pre>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-6 text-center">
            <FileText className="mb-2 h-8 w-8 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">No configuration set</p>
            <Button variant="outline" size="sm" className="mt-3" asChild>
              <Link to="/settings">Create configuration</Link>
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export function ConfigurationPreviewSkeleton() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <Skeleton className="h-5 w-40" />
        <Skeleton className="h-8 w-16" />
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-4" />
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-12" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-4" />
            <Skeleton className="h-4 w-12" />
            <Skeleton className="h-4 w-12" />
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="h-4 w-4" />
            <Skeleton className="h-4 w-16" />
            <Skeleton className="h-4 w-12" />
          </div>
        </div>
        <Skeleton className="h-24 w-full" />
      </CardContent>
    </Card>
  )
}
