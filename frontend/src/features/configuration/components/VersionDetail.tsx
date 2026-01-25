import { useState } from 'react'
import { formatDistanceToNow, format } from 'date-fns'
import { ArrowLeft, RotateCcw, Check, Calendar, User, GitCommit, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useRollback } from '../hooks/useConfiguration'
import type { Version } from '../types'

interface VersionDetailProps {
  version: Version
  isLatest: boolean
  onBack: () => void
  onRollbackSuccess: () => void
}

export function VersionDetail({
  version,
  isLatest,
  onBack,
  onRollbackSuccess,
}: VersionDetailProps) {
  const rollback = useRollback()
  const [showConfirm, setShowConfirm] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const handleRollback = () => {
    setShowConfirm(false)
    rollback.mutate(version.commit_sha, {
      onSuccess: () => {
        setShowSuccess(true)
        // Brief success message, then navigate back
        setTimeout(() => {
          onRollbackSuccess()
        }, 1500)
      },
    })
  }

  return (
    <div className="space-y-4">
      {/* Header with back button */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="sm" onClick={onBack} className="gap-2">
          <ArrowLeft className="h-4 w-4" />
          Back to history
        </Button>
      </div>

      {/* Version metadata card */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                {version.message || 'Configuration update'}
              </CardTitle>
              <CardDescription className="mt-2">
                {isLatest ? 'This is your current configuration.' : 'You can restore this version to replace your current configuration.'}
              </CardDescription>
            </div>

            {isLatest ? (
              <span className="text-sm font-medium text-primary bg-primary/10 px-3 py-1 rounded-full">
                Current version
              </span>
            ) : showSuccess ? (
              <Button variant="outline" disabled className="gap-2">
                <Check className="h-4 w-4 text-primary" />
                Restored
              </Button>
            ) : (
              <Button
                onClick={() => setShowConfirm(true)}
                disabled={rollback.isPending}
                className="gap-2"
              >
                <RotateCcw className="h-4 w-4" />
                {rollback.isPending ? 'Restoring...' : 'Restore this version'}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {/* Version metadata details */}
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex items-start gap-3">
              <User className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm font-medium">Author</p>
                <p className="text-sm text-muted-foreground">{version.author}</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Calendar className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm font-medium">Date</p>
                <p className="text-sm text-muted-foreground">
                  {format(new Date(version.timestamp), 'PPpp')}
                </p>
                <p className="text-xs text-muted-foreground">
                  ({formatDistanceToNow(new Date(version.timestamp), { addSuffix: true })})
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3 sm:col-span-2">
              <GitCommit className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-sm font-medium">Commit SHA</p>
                <code className="text-sm text-muted-foreground font-mono bg-muted px-2 py-0.5 rounded">
                  {version.commit_sha}
                </code>
              </div>
            </div>
          </div>

          {rollback.error && (
            <p className="text-sm text-destructive mt-4">
              Failed to restore version. Please try again.
            </p>
          )}
        </CardContent>
      </Card>

      {/* What happens notice */}
      {!isLatest && !showSuccess && (
        <Card className="border-muted">
          <CardContent className="py-4">
            <p className="text-sm text-muted-foreground">
              <strong>What happens when you restore:</strong> A new commit will be created with the content from this version. Your current configuration will be replaced, and you can always rollback again if needed.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Rollback confirmation dialog */}
      <AlertDialog open={showConfirm} onOpenChange={setShowConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Restore this version?</AlertDialogTitle>
            <AlertDialogDescription className="space-y-2">
              <p>
                You are about to restore your configuration to the version from{' '}
                <strong>{format(new Date(version.timestamp), 'PPp')}</strong>.
              </p>
              <p className="text-xs">
                Commit: <code className="bg-muted px-1 rounded">{version.commit_sha.slice(0, 7)}</code>
              </p>
              <p>
                This will replace your current configuration. You can always rollback again if needed.
              </p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleRollback}>
              Restore version
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
