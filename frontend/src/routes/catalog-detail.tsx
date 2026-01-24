/**
 * Catalog detail page.
 *
 * Displays full information about a catalog item including documentation.
 */

import { useParams, Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useCatalogItem } from '@/features/catalog/hooks/useCatalog'
import { CatalogDetail, CatalogDetailSkeleton } from '@/features/catalog/components/CatalogDetail'
import { Button } from '@/components/ui/button'

export function CatalogDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { data, isLoading, isError } = useCatalogItem(id!)

  if (isLoading) {
    return (
      <div className="p-6">
        <CatalogDetailSkeleton />
      </div>
    )
  }

  if (isError || !data) {
    return (
      <div className="p-6 space-y-4">
        <Link to="/catalog">
          <Button variant="ghost" size="sm" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to catalog
          </Button>
        </Link>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold text-destructive">Item not found</h2>
          <p className="text-muted-foreground mt-2">
            The catalog item you're looking for doesn't exist or has been removed.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <CatalogDetail item={data} />
    </div>
  )
}
