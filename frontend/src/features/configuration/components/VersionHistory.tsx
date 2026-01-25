import { useState } from 'react'
import { History, ChevronDown } from 'lucide-react'
import { Timeline } from '@/components/ui/timeline'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import { useVersionHistory } from '../hooks/useConfiguration'
import { VersionHistoryItem } from './VersionHistoryItem'
import type { Version } from '../types'

const INITIAL_LIMIT = 10
const LOAD_MORE_INCREMENT = 10

interface VersionHistoryProps {
  currentCommitSha?: string // SHA of current configuration to determine isLatest
  onVersionSelect?: (version: Version) => void
}

export function VersionHistory({ currentCommitSha, onVersionSelect }: VersionHistoryProps) {
  const [limit, setLimit] = useState(INITIAL_LIMIT)
  const { data, isLoading, error, isFetching } = useVersionHistory(limit)

  const handleLoadMore = () => {
    setLimit((prev) => prev + LOAD_MORE_INCREMENT)
  }

  if (isLoading) {
    return <VersionHistorySkeleton />
  }

  if (error) {
    return (
      <div className="text-center py-12 text-destructive">
        <p>Failed to load version history</p>
      </div>
    )
  }

  if (!data?.versions.length) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <History className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p>No version history yet</p>
        <p className="text-sm mt-1">Save your configuration to create the first version</p>
      </div>
    )
  }

  const hasMore = data.versions.length < data.total

  return (
    <div className="space-y-4">
      <Timeline>
        {data.versions.map((version, index) => (
          <VersionHistoryItem
            key={version.commit_sha}
            version={version}
            isLatest={currentCommitSha ? version.commit_sha === currentCommitSha : index === 0}
            onSelect={onVersionSelect}
          />
        ))}
      </Timeline>

      {hasMore && (
        <div className="flex justify-center pt-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleLoadMore}
            disabled={isFetching}
            className="gap-2"
          >
            {isFetching ? (
              'Loading...'
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                Load more ({data.total - data.versions.length} remaining)
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  )
}

export function VersionHistorySkeleton() {
  return (
    <div className="space-y-4 pl-6">
      {[1, 2, 3].map((i) => (
        <div key={i} className="relative">
          <Skeleton className="absolute -left-6 top-1.5 h-3 w-3 rounded-full" />
          <div className="p-3 rounded-lg border">
            <Skeleton className="h-4 w-3/4 mb-2" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        </div>
      ))}
    </div>
  )
}
