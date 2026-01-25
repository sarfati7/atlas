import { useEffect, useRef } from 'react'
import { Save, AlertTriangle, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  ConfigurationEditor,
  useConfiguration,
  useUpdateConfiguration,
  useImportConfiguration,
  useDraftStore,
} from '@/features/configuration'

function EditorSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-[500px] w-full rounded-lg" />
    </div>
  )
}

function EditorError({ onRetry }: { onRetry: () => void }) {
  return (
    <Card className="border-destructive/50 bg-destructive/10">
      <CardContent className="flex items-center gap-4 py-4">
        <AlertTriangle className="h-5 w-5 text-destructive" />
        <div className="flex-1">
          <p className="text-sm text-destructive">Failed to load configuration</p>
        </div>
        <Button variant="outline" size="sm" onClick={onRetry}>
          Retry
        </Button>
      </CardContent>
    </Card>
  )
}

export function SettingsPage() {
  const { data: config, isLoading, error, refetch } = useConfiguration()
  const updateConfig = useUpdateConfiguration()
  const importConfig = useImportConfiguration()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const { content, isDirty, setContent, setOriginalContent } = useDraftStore()

  // Sync server config to draft store on load
  useEffect(() => {
    if (config?.content !== undefined) {
      setOriginalContent(config.content)
    }
  }, [config?.content, setOriginalContent])

  // Warn on browser close/reload with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (isDirty) {
        e.preventDefault()
        e.returnValue = ''
      }
    }
    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [isDirty])

  const handleSave = () => {
    updateConfig.mutate(
      { content },
      {
        onSuccess: (newConfig) => {
          setOriginalContent(newConfig.content)
        },
      }
    )
  }

  const handleImportClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      // Validate file type
      if (!file.name.endsWith('.md')) {
        // Reset input and ignore
        e.target.value = ''
        return
      }

      importConfig.mutate(file, {
        onSuccess: () => {
          refetch()
          e.target.value = '' // Reset for next import
        },
        onError: () => {
          e.target.value = '' // Reset on error too
        },
      })
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-5xl px-4 py-8">
        {/* Header with Save and Import buttons */}
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Settings</h1>
            <p className="text-muted-foreground">Manage your claude.md configuration</p>
          </div>
          <div className="flex items-center gap-2">
            {/* Hidden file input for import */}
            <input
              ref={fileInputRef}
              type="file"
              accept=".md"
              className="hidden"
              onChange={handleFileChange}
            />
            <Button
              variant="outline"
              onClick={handleImportClick}
              disabled={importConfig.isPending}
              className="gap-2"
            >
              <Upload className="h-4 w-4" />
              {importConfig.isPending ? 'Importing...' : 'Import'}
            </Button>
            <Button
              onClick={handleSave}
              disabled={!isDirty || updateConfig.isPending}
              className="gap-2"
            >
              <Save className="h-4 w-4" />
              {updateConfig.isPending ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </header>

        {/* Dirty indicator */}
        {isDirty && (
          <div className="mb-4 flex items-center gap-2 text-sm text-amber-500">
            <div className="h-2 w-2 rounded-full bg-amber-500" />
            Unsaved changes
          </div>
        )}

        {/* Tabs */}
        <Tabs defaultValue="editor" className="space-y-4">
          <TabsList>
            <TabsTrigger value="editor">Editor</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="import">Import</TabsTrigger>
          </TabsList>

          <TabsContent value="editor">
            {error ? (
              <EditorError onRetry={refetch} />
            ) : isLoading ? (
              <EditorSkeleton />
            ) : (
              <ConfigurationEditor value={content} onChange={setContent} />
            )}
          </TabsContent>

          <TabsContent value="history">
            <div className="text-muted-foreground py-12 text-center">
              History tab (coming in Plan 07-04)
            </div>
          </TabsContent>

          <TabsContent value="import">
            <div className="text-muted-foreground py-12 text-center">
              Import tab (coming in Plan 07-05)
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
