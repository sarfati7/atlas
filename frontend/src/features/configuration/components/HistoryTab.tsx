import { useState } from 'react'
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
import { VersionHistory } from './VersionHistory'
import { VersionDetail } from './VersionDetail'
import { useConfiguration } from '../hooks/useConfiguration'
import type { Version } from '../types'

interface HistoryTabProps {
  isDirty: boolean
  onRollbackSuccess: () => void
}

export function HistoryTab({ isDirty, onRollbackSuccess }: HistoryTabProps) {
  const { data: config } = useConfiguration()
  const [selectedVersion, setSelectedVersion] = useState<Version | null>(null)
  const [showDirtyWarning, setShowDirtyWarning] = useState(false)
  const [pendingVersion, setPendingVersion] = useState<Version | null>(null)

  const currentCommitSha = config?.commit_sha

  const handleVersionSelect = (version: Version) => {
    // If dirty, warn user first
    if (isDirty) {
      setPendingVersion(version)
      setShowDirtyWarning(true)
      return
    }

    setSelectedVersion(version)
  }

  const handleDirtyWarningConfirm = () => {
    setShowDirtyWarning(false)
    if (pendingVersion) {
      setSelectedVersion(pendingVersion)
      setPendingVersion(null)
    }
  }

  const handleBack = () => {
    setSelectedVersion(null)
  }

  const handleRollbackSuccess = () => {
    setSelectedVersion(null)
    onRollbackSuccess()
  }

  // Determine if selected version is the current version
  const isLatest = selectedVersion
    ? currentCommitSha === selectedVersion.commit_sha
    : false

  if (selectedVersion) {
    return (
      <VersionDetail
        version={selectedVersion}
        isLatest={isLatest}
        onBack={handleBack}
        onRollbackSuccess={handleRollbackSuccess}
      />
    )
  }

  return (
    <>
      <VersionHistory
        currentCommitSha={currentCommitSha}
        onVersionSelect={handleVersionSelect}
      />

      <AlertDialog open={showDirtyWarning} onOpenChange={setShowDirtyWarning}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Unsaved changes</AlertDialogTitle>
            <AlertDialogDescription>
              You have unsaved changes in the editor. Viewing a previous version
              will not discard your changes, but rolling back will replace your
              current content.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setPendingVersion(null)}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction onClick={handleDirtyWarningConfirm}>
              Continue
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
