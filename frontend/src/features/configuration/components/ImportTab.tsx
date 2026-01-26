import { useState, useEffect } from 'react'
import { FileUp, Replace, PlusCircle, CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { ImportDropzone } from './ImportDropzone'
import { useImportConfiguration, useDraftStore } from '../index'

interface ImportTabProps {
  hasExistingContent: boolean
  onImportSuccess: () => void
}

type MergeMode = 'replace' | 'append'

export function ImportTab({ hasExistingContent, onImportSuccess }: ImportTabProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [fileContent, setFileContent] = useState<string>('')
  const [error, setError] = useState<string | null>(null)
  const [showMergeDialog, setShowMergeDialog] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)

  const importConfig = useImportConfiguration()
  const { content: currentContent, setOriginalContent } = useDraftStore()

  // Clear success message after 3 seconds
  useEffect(() => {
    if (showSuccess) {
      const timer = setTimeout(() => setShowSuccess(false), 3000)
      return () => clearTimeout(timer)
    }
  }, [showSuccess])

  const handleFileAccepted = async (file: File) => {
    setError(null)
    setSelectedFile(file)

    // Read file content
    try {
      const text = await file.text()
      setFileContent(text)

      // If user has existing content, show merge dialog
      if (hasExistingContent && currentContent.trim()) {
        setShowMergeDialog(true)
      } else {
        // No existing content, just import
        handleImport('replace', text)
      }
    } catch {
      setError('Failed to read file')
      setSelectedFile(null)
    }
  }

  const handleFileRejected = (reason: string) => {
    setError(reason)
    setSelectedFile(null)
  }

  const handleImport = async (mode: MergeMode, content?: string) => {
    const contentToUse = content ?? fileContent
    setShowMergeDialog(false)
    setError(null)

    if (mode === 'append' && currentContent.trim()) {
      // Append: merge new content after existing
      const mergedContent = `${currentContent.trim()}\n\n---\n\n${contentToUse}`
      // Update draft store directly for append mode
      setOriginalContent(mergedContent)
      setSelectedFile(null)
      setShowSuccess(true)
      onImportSuccess()
    } else {
      // Replace: use the import endpoint which creates a git commit
      if (selectedFile) {
        importConfig.mutate(selectedFile, {
          onSuccess: () => {
            setSelectedFile(null)
            setFileContent('')
            setShowSuccess(true)
            onImportSuccess()
          },
          onError: (err) => {
            setError(err instanceof Error ? err.message : 'Import failed')
          },
        })
      }
    }
  }

  const handleClearFile = () => {
    setSelectedFile(null)
    setFileContent('')
    setError(null)
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileUp className="h-5 w-5" />
            Import Configuration
          </CardTitle>
          <CardDescription>
            Upload an existing claude.md file to use as your configuration
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <ImportDropzone
            onFileAccepted={handleFileAccepted}
            onFileRejected={handleFileRejected}
            isUploading={importConfig.isPending}
          />

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          {showSuccess && (
            <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
              <CheckCircle className="h-5 w-5 text-emerald-500" />
              <span className="text-sm text-emerald-500">
                Configuration imported and saved successfully!
              </span>
            </div>
          )}

          {selectedFile && !showMergeDialog && (
            <div className="flex items-center justify-between p-3 rounded-lg bg-muted">
              <span className="text-sm">{selectedFile.name}</span>
              <Button variant="ghost" size="sm" onClick={handleClearFile}>
                Clear
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Merge mode dialog */}
      <AlertDialog open={showMergeDialog} onOpenChange={setShowMergeDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Import Options</AlertDialogTitle>
            <AlertDialogDescription>
              You already have configuration content. How would you like to import the new file?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="grid gap-3 py-4">
            <Button
              variant="outline"
              className="justify-start gap-3 h-auto py-3"
              onClick={() => handleImport('replace')}
              disabled={importConfig.isPending}
            >
              <Replace className="h-5 w-5" />
              <div className="text-left">
                <p className="font-medium">Replace</p>
                <p className="text-sm text-muted-foreground">
                  Replace current content with imported file
                </p>
              </div>
            </Button>
            <Button
              variant="outline"
              className="justify-start gap-3 h-auto py-3"
              onClick={() => handleImport('append')}
              disabled={importConfig.isPending}
            >
              <PlusCircle className="h-5 w-5" />
              <div className="text-left">
                <p className="font-medium">Append</p>
                <p className="text-sm text-muted-foreground">
                  Add imported content after existing configuration
                </p>
              </div>
            </Button>
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={handleClearFile}>Cancel</AlertDialogCancel>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
