/**
 * CatalogCard - Display a catalog item as a clickable card.
 */

import { Link } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { CatalogItemSummary, CatalogItemType } from '../types'

interface CatalogCardProps {
  item: CatalogItemSummary
}

const TYPE_STYLES: Record<CatalogItemType, { label: string; className: string }> = {
  SKILL: {
    label: 'Skill',
    className: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  },
  MCP: {
    label: 'MCP',
    className: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  },
  TOOL: {
    label: 'Tool',
    className: 'bg-green-500/20 text-green-400 border-green-500/30',
  },
}

export function CatalogCard({ item }: CatalogCardProps) {
  const typeStyle = TYPE_STYLES[item.type]

  return (
    <Link to={`/catalog/${item.id}`} className="block group">
      <Card className="h-full transition-colors hover:border-muted-foreground/50">
        <CardHeader className="pb-2">
          <div className="flex items-start justify-between gap-2">
            <CardTitle className="text-base line-clamp-1">{item.name}</CardTitle>
            <Badge variant="outline" className={typeStyle.className}>
              {typeStyle.label}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="pt-0 space-y-3">
          <p className="text-sm text-muted-foreground line-clamp-2">
            {item.description || 'No description'}
          </p>
          {item.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {item.tags.slice(0, 3).map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {item.tags.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{item.tags.length - 3}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </Link>
  )
}
