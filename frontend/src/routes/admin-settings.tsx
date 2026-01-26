/**
 * AdminSettings - Application settings management for admin users.
 */

import { useState } from 'react'
import { Github, CheckCircle, XCircle, Loader2, Trash2, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import {
  useGitHubSettings,
  useUpdateGitHubSettings,
  useTestGitHubConnection,
  useRemoveGitHubSettings,
} from '@/features/admin/hooks'

export function AdminSettingsPage() {
  const { data: settings, isLoading } = useGitHubSettings()
  const updateSettings = useUpdateGitHubSettings()
  const testConnection = useTestGitHubConnection()
  const removeSettings = useRemoveGitHubSettings()

  const [repo, setRepo] = useState('')
  const [token, setToken] = useState('')
  const [isDirty, setIsDirty] = useState(false)

  // Initialize form when settings load
  const handleRepoChange = (value: string) => {
    setRepo(value)
    setIsDirty(true)
  }

  const handleTokenChange = (value: string) => {
    setToken(value)
    setIsDirty(true)
  }

  const handleSave = () => {
    updateSettings.mutate(
      { repo: repo || settings?.repo || '', token },
      {
        onSuccess: () => {
          setToken('')
          setIsDirty(false)
        },
      }
    )
  }

  const handleTest = () => {
    testConnection.mutate()
  }

  const handleRemove = () => {
    removeSettings.mutate(undefined, {
      onSuccess: () => {
        setRepo('')
        setToken('')
        setIsDirty(false)
      },
    })
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto max-w-3xl px-4 py-8">
          <Skeleton className="h-8 w-48 mb-2" />
          <Skeleton className="h-4 w-96 mb-8" />
          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  const isConfigured = settings?.token_configured
  const repoValue = repo || settings?.repo || ''

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto max-w-3xl px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-2xl font-semibold text-foreground">Settings</h1>
          <p className="text-muted-foreground">Configure application integrations</p>
        </header>

        {/* GitHub Integration Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Github className="h-5 w-5" />
              GitHub Integration
            </CardTitle>
            <CardDescription>
              Connect to a GitHub repository to store and sync catalog items
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Connection Status */}
            <div className="flex items-center gap-3 p-3 rounded-lg bg-muted">
              {isConfigured ? (
                <>
                  <CheckCircle className="h-5 w-5 text-emerald-500" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Connected</p>
                    <p className="text-xs text-muted-foreground">
                      Repository: {settings?.repo}
                      {settings?.updated_by && (
                        <> &middot; Last updated by {settings.updated_by}</>
                      )}
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleTest}
                    disabled={testConnection.isPending}
                  >
                    {testConnection.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <RefreshCw className="h-4 w-4" />
                    )}
                    <span className="ml-2">Test</span>
                  </Button>
                </>
              ) : (
                <>
                  <XCircle className="h-5 w-5 text-muted-foreground" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Not configured</p>
                    <p className="text-xs text-muted-foreground">
                      Enter your GitHub repository and token below
                    </p>
                  </div>
                </>
              )}
            </div>

            {/* Test Result */}
            {testConnection.data && (
              <div
                className={`flex items-center gap-2 p-3 rounded-lg ${
                  testConnection.data.success
                    ? 'bg-emerald-500/10 border border-emerald-500/20'
                    : 'bg-destructive/10 border border-destructive/20'
                }`}
              >
                {testConnection.data.success ? (
                  <CheckCircle className="h-4 w-4 text-emerald-500" />
                ) : (
                  <XCircle className="h-4 w-4 text-destructive" />
                )}
                <span
                  className={`text-sm ${
                    testConnection.data.success ? 'text-emerald-500' : 'text-destructive'
                  }`}
                >
                  {testConnection.data.message}
                </span>
              </div>
            )}

            {/* Form Fields */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="repo">Repository</Label>
                <Input
                  id="repo"
                  placeholder="owner/repo"
                  value={repoValue}
                  onChange={(e) => handleRepoChange(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  The GitHub repository in owner/repo format (e.g., acme/catalog)
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="token">Personal Access Token</Label>
                <Input
                  id="token"
                  type="password"
                  placeholder={isConfigured ? '••••••••••••••••' : 'ghp_xxxxxxxxxxxx'}
                  value={token}
                  onChange={(e) => handleTokenChange(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  A GitHub personal access token with repo access.{' '}
                  <a
                    href="https://github.com/settings/tokens/new"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:underline"
                  >
                    Create one here
                  </a>
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t">
              <div>
                {isConfigured && (
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="ghost" size="sm" className="text-destructive">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Remove
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Remove GitHub Integration?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This will remove the stored GitHub credentials. The system will fall back
                          to environment variables if configured, otherwise use an in-memory
                          catalog.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                          onClick={handleRemove}
                          className="bg-destructive text-destructive-foreground"
                        >
                          Remove
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                )}
              </div>

              <Button
                onClick={handleSave}
                disabled={
                  updateSettings.isPending ||
                  (!isDirty && !token) ||
                  (!repoValue && !token)
                }
              >
                {updateSettings.isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                {isConfigured ? 'Update' : 'Save'}
              </Button>
            </div>

            {/* Error State */}
            {updateSettings.isError && (
              <div className="flex items-center gap-2 p-3 rounded-lg bg-destructive/10 border border-destructive/20">
                <XCircle className="h-4 w-4 text-destructive" />
                <span className="text-sm text-destructive">
                  {updateSettings.error instanceof Error
                    ? updateSettings.error.message
                    : 'Failed to save settings'}
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
