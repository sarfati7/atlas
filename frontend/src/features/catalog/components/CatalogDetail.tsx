/**
 * Catalog item detail view component.
 *
 * Displays full metadata and documentation for a catalog item.
 */

import { format } from 'date-fns'
import { ArrowLeft, Calendar, GitBranch, Users } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { DocumentationViewer } from './DocumentationViewer'
import type { CatalogItemDetail as CatalogItemDetailType, CatalogItemType } from '../types'

const typeColors: Record<CatalogItemType, string> = {
  SKILL: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  MCP: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  TOOL: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
}

const typeLabels: Record<CatalogItemType, string> = {
  SKILL: 'Skill',
  MCP: 'MCP',
  TOOL: 'Tool',
}

interface CatalogDetailProps {
  item: CatalogItemDetailType
}

export function CatalogDetail({ item }: CatalogDetailProps) {
  return (
    <div className="space-y-6">
      {/* Back button */}
      <Link to="/catalog">
        <Button variant="ghost" size="sm" className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to catalog
        </Button>
      </Link>

      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold">{item.name}</h1>
            <p className="text-muted-foreground mt-2">{item.description}</p>
          </div>
          <Badge variant="outline" className={typeColors[item.type]}>
            {typeLabels[item.type]}
          </Badge>
        </div>

        {/* Tags */}
        {item.tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {item.tags.map((tag) => (
              <span
                key={tag}
                className="text-sm text-muted-foreground bg-muted px-3 py-1 rounded-full"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Metadata row */}
        <div className="flex flex-wrap gap-6 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>Created {format(new Date(item.created_at), 'MMM d, yyyy')}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <span>Updated {format(new Date(item.updated_at), 'MMM d, yyyy')}</span>
          </div>
          <div className="flex items-center gap-2">
            <GitBranch className="h-4 w-4" />
            <span className="font-mono text-xs">{item.git_path}</span>
          </div>
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            <span>{item.usage_count} uses</span>
          </div>
        </div>
      </div>

      {/* Documentation */}
      <Card>
        <CardHeader>
          <CardTitle>Documentation</CardTitle>
        </CardHeader>
        <CardContent>
          <DocumentationViewer content={item.documentation} />
        </CardContent>
      </Card>
    </div>
  )
}

export function CatalogDetailSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-32" />
      <div className="space-y-4">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <Skeleton className="h-9 w-64" />
            <Skeleton className="h-5 w-96" />
          </div>
          <Skeleton className="h-6 w-16" />
        </div>
        <div className="flex gap-2">
          <Skeleton className="h-6 w-20" />
          <Skeleton className="h-6 w-24" />
          <Skeleton className="h-6 w-16" />
        </div>
        <div className="flex gap-6">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-4 w-48" />
        </div>
      </div>
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-32" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-4 w-2/3" />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
