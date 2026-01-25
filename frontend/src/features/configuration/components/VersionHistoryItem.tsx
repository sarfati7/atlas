import { formatDistanceToNow } from 'date-fns'
import { TimelineItem } from '@/components/ui/timeline'
import type { Version } from '../types'

interface VersionHistoryItemProps {
  version: Version
  isLatest: boolean
  onSelect?: (version: Version) => void
}

export function VersionHistoryItem({ version, isLatest, onSelect }: VersionHistoryItemProps) {
  return (
    <TimelineItem active={isLatest}>
      <div
        className={`p-3 rounded-lg border bg-card ${onSelect ? 'cursor-pointer hover:bg-accent' : ''}`}
        onClick={() => onSelect?.(version)}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <p className="font-medium text-foreground truncate">
              {version.message || 'Configuration update'}
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {version.author} - {formatDistanceToNow(new Date(version.timestamp), { addSuffix: true })}
            </p>
          </div>
          <code className="text-xs text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
            {version.commit_sha.slice(0, 7)}
          </code>
        </div>
        {isLatest && (
          <span className="inline-flex items-center text-xs text-primary mt-2">
            Current version
          </span>
        )}
      </div>
    </TimelineItem>
  )
}
