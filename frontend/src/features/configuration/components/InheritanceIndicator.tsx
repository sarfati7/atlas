import { Building2, Users, User } from 'lucide-react'
import { Badge } from '@/components/ui/badge'

interface InheritanceIndicatorProps {
  orgApplied: boolean
  teamApplied: boolean
  userApplied: boolean
}

export function InheritanceIndicator({
  orgApplied,
  teamApplied,
  userApplied,
}: InheritanceIndicatorProps) {
  const sources = [
    { applied: orgApplied, label: 'Organization', icon: Building2 },
    { applied: teamApplied, label: 'Team', icon: Users },
    { applied: userApplied, label: 'Personal', icon: User },
  ]

  const appliedSources = sources.filter((s) => s.applied)

  if (appliedSources.length === 0) {
    return null
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-muted-foreground">Configuration from:</span>
      <div className="flex gap-1">
        {sources.map((source) => {
          const Icon = source.icon
          return (
            <Badge
              key={source.label}
              variant={source.applied ? 'default' : 'outline'}
              className={`gap-1 ${source.applied ? '' : 'opacity-40'}`}
            >
              <Icon className="h-3 w-3" />
              {source.label}
            </Badge>
          )
        })}
      </div>
    </div>
  )
}
