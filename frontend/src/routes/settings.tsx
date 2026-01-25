import { useEffect } from 'react'
import { Save, AlertTriangle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  ConfigurationEditor,
  useConfiguration,
  useUpdateConfiguration,
  useDraftStore,
  HistoryTab,
  ImportTab,
  InheritanceIndicator,
} from '@/features/configuration'
import { useEffectiveConfiguration } from '@/features/profile/hooks/useProfile'

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
  const { data: effective } = useEffectiveConfiguration()
  const updateConfig = useUpdateConfiguration()

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

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-5xl px-4 py-8">
        {/* Header with save button */}
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Settings</h1>
            <p className="text-muted-foreground">Manage your claude.md configuration</p>
          </div>
          <Button
            onClick={handleSave}
            disabled={!isDirty || updateConfig.isPending}
            className="gap-2"
          >
            <Save className="h-4 w-4" />
            {updateConfig.isPending ? 'Saving...' : 'Save'}
          </Button>
        </header>

        {/* Inheritance indicator */}
        {effective && (
          <div className="mb-4">
            <InheritanceIndicator
              orgApplied={effective.org_applied}
              teamApplied={effective.team_applied}
              userApplied={effective.user_applied}
            />
          </div>
        )}

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
            <HistoryTab
              isDirty={isDirty}
              onRollbackSuccess={() => {
                refetch()
              }}
            />
          </TabsContent>

          <TabsContent value="import">
            <ImportTab
              hasExistingContent={!!content.trim()}
              onImportSuccess={() => {
                refetch()
              }}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
