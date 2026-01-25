# Phase 7: Web Frontend Configuration - Research

**Researched:** 2026-01-25
**Domain:** Configuration editing UI with code editor, version history, file import, and inheritance visualization
**Confidence:** HIGH

## Summary

Phase 7 implements web UI for configuration management: editing claude.md through a code editor, viewing version history, rolling back to previous versions, importing files from local machine, and visualizing configuration inheritance. The backend APIs are complete (Phase 4) - this phase connects them to React components.

The standard approach uses CodeMirror 6 via `@uiw/react-codemirror` for the markdown editor (lightweight, mobile-friendly, dark theme support), a custom timeline component for version history (built on shadcn/ui patterns since timeline is not yet official), `react-dropzone` via `shadcn-dropzone` for file import, and TanStack Query mutations with optimistic updates for responsive UI.

Key findings: The existing frontend already has all foundational patterns established - TanStack Query hooks pattern, React Hook Form with Zod, feature directory structure, and dark theme with OKLCH colors. Phase 7 follows these patterns exactly, adding a new `configuration` feature directory with its own API, hooks, and components.

**Primary recommendation:** Use `@uiw/react-codemirror` with markdown language support for the editor (lighter than Monaco, dark theme built-in), create a custom Timeline component following shadcn/ui patterns for version history, and leverage the existing `EffectiveConfiguration` type from profile feature for inheritance display.

## Standard Stack

The established libraries/tools for configuration editing UI:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| @uiw/react-codemirror | 4.x | Code/markdown editor | Lightweight (~200KB vs Monaco 5MB), mobile-friendly, native dark theme, TypeScript |
| @codemirror/lang-markdown | 6.x | Markdown syntax highlighting | Official CodeMirror extension, supports code blocks |
| @codemirror/language-data | 6.x | Code block language support | Auto-highlight code in markdown fenced blocks |
| react-dropzone | 14.x | File drag-and-drop | De facto standard for React file uploads, accessible |
| date-fns | 4.x (already installed) | Date formatting | Tree-shakeable, already in project |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @uiw/codemirror-theme-github | latest | GitHub dark theme | Match project's dark theme aesthetic |
| shadcn-timeline (pattern) | - | Version history display | Build custom component following shadcn patterns |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| @uiw/react-codemirror | @monaco-editor/react | Monaco is 5MB bundle, not mobile-friendly; use for full IDE features |
| @uiw/react-codemirror | @uiw/react-md-editor | MD editor has split preview; we want editor-only with markdown syntax |
| react-dropzone | shadcn-dropzone | shadcn-dropzone wraps react-dropzone; use raw for more control |
| Custom Timeline | shadcn-timeline npm | External package; build our own for consistency with existing components |

**Installation:**
```bash
cd frontend
npm install @uiw/react-codemirror @codemirror/lang-markdown @codemirror/language-data @uiw/codemirror-theme-github react-dropzone
```

## Architecture Patterns

### Recommended Project Structure
```
frontend/src/
├── features/
│   └── configuration/              # NEW feature directory
│       ├── api/
│       │   └── configurationApi.ts  # API calls to /api/v1/configuration/*
│       ├── hooks/
│       │   └── useConfiguration.ts  # TanStack Query hooks
│       ├── components/
│       │   ├── ConfigurationEditor.tsx    # CodeMirror markdown editor
│       │   ├── VersionHistory.tsx         # Timeline of versions
│       │   ├── VersionHistoryItem.tsx     # Single version row
│       │   ├── ImportDropzone.tsx         # File upload dropzone
│       │   ├── InheritanceIndicator.tsx   # Org/Team/User badges (reuse from profile)
│       │   └── index.ts
│       ├── types.ts                 # Configuration types matching backend
│       └── index.ts
├── routes/
│   └── settings.tsx                 # Settings page using configuration components
└── components/
    └── ui/
        └── timeline.tsx             # NEW shadcn-style timeline component
```

### Pattern 1: Configuration API Layer
**What:** API calls matching backend routes from Phase 4
**When to use:** All configuration data fetching and mutations
**Example:**
```typescript
// src/features/configuration/api/configurationApi.ts
import { apiClient } from '@/lib/api'
import type { Configuration, VersionHistory, ConfigurationUpdate } from '../types'

export const configurationApi = {
  // GET /api/v1/configuration/me
  getMyConfiguration: async (): Promise<Configuration> => {
    const { data } = await apiClient.get('/api/v1/configuration/me')
    return data
  },

  // PUT /api/v1/configuration/me
  updateConfiguration: async (update: ConfigurationUpdate): Promise<Configuration> => {
    const { data } = await apiClient.put('/api/v1/configuration/me', update)
    return data
  },

  // GET /api/v1/configuration/me/history
  getVersionHistory: async (limit = 50): Promise<VersionHistory> => {
    const { data } = await apiClient.get('/api/v1/configuration/me/history', {
      params: { limit },
    })
    return data
  },

  // POST /api/v1/configuration/me/rollback/{commit_sha}
  rollback: async (commitSha: string): Promise<Configuration> => {
    const { data } = await apiClient.post(`/api/v1/configuration/me/rollback/${commitSha}`)
    return data
  },

  // POST /api/v1/configuration/me/import (multipart form)
  importFile: async (file: File): Promise<Configuration> => {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await apiClient.post('/api/v1/configuration/me/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
}
```

### Pattern 2: TanStack Query Hooks with Cache Invalidation
**What:** Query and mutation hooks that properly invalidate related caches
**When to use:** All configuration data interactions
**Example:**
```typescript
// src/features/configuration/hooks/useConfiguration.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { configurationApi } from '../api/configurationApi'
import type { ConfigurationUpdate } from '../types'

export const useConfiguration = () => {
  return useQuery({
    queryKey: ['configuration', 'me'],
    queryFn: configurationApi.getMyConfiguration,
  })
}

export const useUpdateConfiguration = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (update: ConfigurationUpdate) =>
      configurationApi.updateConfiguration(update),
    onSuccess: () => {
      // Invalidate configuration and version history
      queryClient.invalidateQueries({ queryKey: ['configuration'] })
      // Also invalidate effective configuration in profile
      queryClient.invalidateQueries({ queryKey: ['profile', 'effectiveConfiguration'] })
    },
  })
}

export const useVersionHistory = (limit = 50) => {
  return useQuery({
    queryKey: ['configuration', 'history', limit],
    queryFn: () => configurationApi.getVersionHistory(limit),
  })
}

export const useRollback = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commitSha: string) => configurationApi.rollback(commitSha),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configuration'] })
      queryClient.invalidateQueries({ queryKey: ['profile', 'effectiveConfiguration'] })
    },
  })
}

export const useImportConfiguration = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (file: File) => configurationApi.importFile(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['configuration'] })
      queryClient.invalidateQueries({ queryKey: ['profile', 'effectiveConfiguration'] })
    },
  })
}
```

### Pattern 3: CodeMirror Editor with Dark Theme
**What:** Markdown editor matching the app's dark theme
**When to use:** Configuration editing
**Example:**
```typescript
// src/features/configuration/components/ConfigurationEditor.tsx
import { useCallback } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { markdown, markdownLanguage } from '@codemirror/lang-markdown'
import { languages } from '@codemirror/language-data'
import { githubDark } from '@uiw/codemirror-theme-github'

interface ConfigurationEditorProps {
  value: string
  onChange: (value: string) => void
  readOnly?: boolean
}

export function ConfigurationEditor({ value, onChange, readOnly = false }: ConfigurationEditorProps) {
  const handleChange = useCallback((val: string) => {
    onChange(val)
  }, [onChange])

  return (
    <CodeMirror
      value={value}
      height="400px"
      theme={githubDark}
      extensions={[
        markdown({
          base: markdownLanguage,
          codeLanguages: languages,
        }),
      ]}
      onChange={handleChange}
      readOnly={readOnly}
      placeholder="# Your claude.md configuration\n\nStart writing your configuration here..."
      className="border border-border rounded-lg overflow-hidden"
    />
  )
}
```

### Pattern 4: File Import with Dropzone
**What:** Drag-and-drop file upload for .md files
**When to use:** Import existing claude.md from local machine
**Example:**
```typescript
// src/features/configuration/components/ImportDropzone.tsx
import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ImportDropzoneProps {
  onFileAccepted: (file: File) => void
  isUploading?: boolean
}

export function ImportDropzone({ onFileAccepted, isUploading }: ImportDropzoneProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      onFileAccepted(acceptedFiles[0])
    }
  }, [onFileAccepted])

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: { 'text/markdown': ['.md'] },
    maxFiles: 1,
    maxSize: 1024 * 1024, // 1MB (matches backend limit)
    disabled: isUploading,
  })

  return (
    <div
      {...getRootProps()}
      className={cn(
        'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
        isDragActive && !isDragReject && 'border-primary bg-primary/5',
        isDragReject && 'border-destructive bg-destructive/5',
        !isDragActive && 'border-border hover:border-muted-foreground',
        isUploading && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-2">
        {isDragActive ? (
          <FileText className="h-8 w-8 text-primary" />
        ) : (
          <Upload className="h-8 w-8 text-muted-foreground" />
        )}
        <p className="text-sm text-muted-foreground">
          {isDragActive
            ? 'Drop the file here'
            : 'Drag and drop a .md file, or click to select'}
        </p>
        <p className="text-xs text-muted-foreground">Max 1MB</p>
      </div>
    </div>
  )
}
```

### Pattern 5: Version History Timeline
**What:** Custom timeline component for version history
**When to use:** Displaying commit history
**Example:**
```typescript
// src/components/ui/timeline.tsx (shadcn-style component)
import * as React from 'react'
import { cn } from '@/lib/utils'

interface TimelineProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Timeline({ className, children, ...props }: TimelineProps) {
  return (
    <div className={cn('relative space-y-4 pl-6', className)} {...props}>
      <div className="absolute left-[9px] top-2 bottom-2 w-px bg-border" />
      {children}
    </div>
  )
}

interface TimelineItemProps extends React.HTMLAttributes<HTMLDivElement> {
  active?: boolean
}

export function TimelineItem({ className, active, children, ...props }: TimelineItemProps) {
  return (
    <div className={cn('relative', className)} {...props}>
      <div
        className={cn(
          'absolute -left-6 top-1.5 h-3 w-3 rounded-full border-2',
          active
            ? 'border-primary bg-primary'
            : 'border-muted-foreground bg-background'
        )}
      />
      {children}
    </div>
  )
}
```

### Anti-Patterns to Avoid
- **Storing editor content in global state:** Keep editor value in component state; only persist on explicit save
- **Not debouncing auto-save:** If implementing auto-save, debounce to avoid excessive API calls
- **Fetching history on every edit:** Query history separately, don't refetch on content change
- **Using Monaco for simple markdown:** Overkill; CodeMirror is 25x smaller and sufficient
- **Manual file reading with FileReader:** Use FormData directly; backend handles file parsing

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Markdown editor | textarea with manual highlighting | @uiw/react-codemirror | Syntax highlighting, undo/redo, keyboard shortcuts |
| File drag-and-drop | onDragOver/onDrop handlers | react-dropzone | Accessibility, file validation, browser quirks |
| Date formatting | new Date().toLocaleString() | date-fns (already installed) | Consistency, tree-shaking, timezone handling |
| Diff viewing | String comparison | react-diff-viewer-continued | Syntax highlighting, side-by-side view |
| Form state for editor | useState for content + dirty tracking | React Hook Form or local state + TanStack Query | Built-in dirty state, validation |

**Key insight:** The configuration editor is simpler than a full IDE. Don't over-engineer with Monaco or complex state management. CodeMirror + local state + TanStack Query mutations is sufficient.

## Common Pitfalls

### Pitfall 1: Not Handling Empty Configuration State
**What goes wrong:** Assuming user always has a configuration; crashing on null/empty content
```typescript
// BAD
const { data } = useConfiguration()
return <Editor value={data.content} /> // Crashes if data undefined

// GOOD
const { data, isLoading } = useConfiguration()
if (isLoading) return <Skeleton />
return <Editor value={data?.content ?? ''} />
```
**Why it happens:** Backend returns empty content for new users, not 404
**How to avoid:** Always provide default empty string; show helpful empty state UI
**Warning signs:** White screen for new users, "cannot read property" errors

### Pitfall 2: Losing Edits on Navigation
**What goes wrong:** User edits content, navigates away, loses changes without warning
```typescript
// BAD - no unsaved changes warning
<Link to="/dashboard">Dashboard</Link>

// GOOD - track dirty state and warn
const [isDirty, setIsDirty] = useState(false)

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
```
**Why it happens:** No dirty tracking; no navigation guards
**How to avoid:** Track dirty state; use beforeunload event; consider React Router's useBlocker
**Warning signs:** Users complaining about lost work

### Pitfall 3: File Upload Content-Type
**What goes wrong:** File upload fails because Content-Type header is wrong
```typescript
// BAD - axios auto-sets wrong Content-Type for FormData
await apiClient.post('/api/v1/configuration/me/import', formData)

// GOOD - let browser set correct multipart boundary
await apiClient.post('/api/v1/configuration/me/import', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
})
```
**Why it happens:** axios default Content-Type interferes with FormData
**How to avoid:** Explicitly set Content-Type for file uploads; browser adds boundary automatically
**Warning signs:** 400/415 errors on file upload, "invalid file" errors

### Pitfall 4: Version History Pagination Missing
**What goes wrong:** Loading all versions at once causes slow load for active users
**Why it happens:** Not using the limit parameter; loading full history
**How to avoid:** Use limit parameter (default 50); add "Load more" if needed
**Warning signs:** Slow settings page for power users with many versions

### Pitfall 5: Not Invalidating Related Caches
**What goes wrong:** After updating config, dashboard still shows old "has_configuration" status
```typescript
// BAD - only invalidate configuration
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: ['configuration'] })
}

// GOOD - invalidate all related queries
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: ['configuration'] })
  queryClient.invalidateQueries({ queryKey: ['profile', 'effectiveConfiguration'] })
  queryClient.invalidateQueries({ queryKey: ['profile', 'dashboard'] })
}
```
**Why it happens:** Not understanding cache relationships
**How to avoid:** Map out which queries depend on configuration state; invalidate all
**Warning signs:** Stale data in other parts of UI after config changes

### Pitfall 6: CodeMirror Theme Not Matching App Theme
**What goes wrong:** Editor looks jarring with different colors than the rest of the app
**Why it happens:** Using default CodeMirror theme instead of GitHub dark
**How to avoid:** Use `@uiw/codemirror-theme-github` with `githubDark`; optionally customize to match OKLCH colors
**Warning signs:** Bright white editor in dark app, color mismatch

## Code Examples

Verified patterns from official sources and existing project code:

### Types Matching Backend API
```typescript
// src/features/configuration/types.ts
// Matches backend/src/atlas/entrypoints/api/routes/configuration.py

export interface Configuration {
  content: string
  commit_sha: string
  updated_at: string
}

export interface ConfigurationUpdate {
  content: string
  message?: string
}

export interface Version {
  commit_sha: string
  message: string
  author: string
  timestamp: string
}

export interface VersionHistory {
  versions: Version[]
  total: number
}
```

### Settings Page Layout
```typescript
// src/routes/settings.tsx
import { useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Save } from 'lucide-react'
import { ConfigurationEditor } from '@/features/configuration/components/ConfigurationEditor'
import { VersionHistory } from '@/features/configuration/components/VersionHistory'
import { ImportDropzone } from '@/features/configuration/components/ImportDropzone'
import { useConfiguration, useUpdateConfiguration } from '@/features/configuration/hooks/useConfiguration'
import { useEffectiveConfiguration } from '@/features/profile/hooks/useProfile'

export function SettingsPage() {
  const { data: config, isLoading } = useConfiguration()
  const { data: effective } = useEffectiveConfiguration()
  const updateConfig = useUpdateConfiguration()

  const [content, setContent] = useState('')
  const [isDirty, setIsDirty] = useState(false)

  // Sync content when config loads
  useEffect(() => {
    if (config?.content) {
      setContent(config.content)
      setIsDirty(false)
    }
  }, [config?.content])

  const handleSave = () => {
    updateConfig.mutate({ content }, {
      onSuccess: () => setIsDirty(false)
    })
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground mt-1">
            Manage your claude.md configuration
          </p>
        </div>
        <Button onClick={handleSave} disabled={!isDirty || updateConfig.isPending}>
          <Save className="h-4 w-4 mr-2" />
          {updateConfig.isPending ? 'Saving...' : 'Save'}
        </Button>
      </div>

      {/* Inheritance indicator */}
      {effective && (
        <InheritanceIndicator
          orgApplied={effective.org_applied}
          teamApplied={effective.team_applied}
          userApplied={effective.user_applied}
        />
      )}

      <Tabs defaultValue="editor">
        <TabsList>
          <TabsTrigger value="editor">Editor</TabsTrigger>
          <TabsTrigger value="history">Version History</TabsTrigger>
          <TabsTrigger value="import">Import</TabsTrigger>
        </TabsList>

        <TabsContent value="editor" className="mt-4">
          <ConfigurationEditor
            value={content}
            onChange={(val) => {
              setContent(val)
              setIsDirty(true)
            }}
          />
        </TabsContent>

        <TabsContent value="history" className="mt-4">
          <VersionHistory />
        </TabsContent>

        <TabsContent value="import" className="mt-4">
          <ImportDropzone
            onFileAccepted={(file) => importConfig.mutate(file)}
            isUploading={importConfig.isPending}
          />
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

### Version History with Rollback
```typescript
// src/features/configuration/components/VersionHistory.tsx
import { formatDistanceToNow } from 'date-fns'
import { History, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Timeline, TimelineItem } from '@/components/ui/timeline'
import { useVersionHistory, useRollback } from '../hooks/useConfiguration'

export function VersionHistory() {
  const { data, isLoading } = useVersionHistory()
  const rollback = useRollback()

  if (isLoading) {
    return <VersionHistorySkeleton />
  }

  if (!data?.versions.length) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <History className="h-8 w-8 mx-auto mb-2" />
        <p>No version history yet</p>
      </div>
    )
  }

  return (
    <Timeline>
      {data.versions.map((version, index) => (
        <TimelineItem key={version.commit_sha} active={index === 0}>
          <div className="flex items-start justify-between">
            <div>
              <p className="font-medium">{version.message}</p>
              <p className="text-sm text-muted-foreground">
                {version.author} - {formatDistanceToNow(new Date(version.timestamp), { addSuffix: true })}
              </p>
            </div>
            {index > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => rollback.mutate(version.commit_sha)}
                disabled={rollback.isPending}
              >
                <RotateCcw className="h-4 w-4 mr-1" />
                Restore
              </Button>
            )}
          </div>
        </TimelineItem>
      ))}
    </Timeline>
  )
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Monaco Editor for all code | CodeMirror 6 for lightweight needs | 2022-2023 | 25x smaller bundle, mobile support |
| textarea + manual markdown | @uiw/react-codemirror | 2023 | Built-in syntax highlighting, undo/redo |
| Custom file upload handling | react-dropzone | Long-standing | Accessibility, validation, browser quirks handled |
| HSL color variables | OKLCH color variables | 2024 (Tailwind 4) | Better color accessibility |
| Timeline as npm package | Build using shadcn patterns | 2024 | Consistency, no external dependency |

**Deprecated/outdated:**
- CodeMirror 5: Use CodeMirror 6 (completely rewritten, better React support)
- @monaco-editor/react for simple editors: Overkill; use CodeMirror
- Manual FormData handling: Use react-dropzone for file validation

## Open Questions

Things that couldn't be fully resolved:

1. **Auto-save vs Manual Save**
   - What we know: Current design uses manual save button
   - What's unclear: Should we add auto-save with debounce?
   - Recommendation: Start with manual save; add auto-save later if users request it

2. **Diff View for Rollback Preview**
   - What we know: react-diff-viewer-continued exists for showing diffs
   - What's unclear: Should rollback show diff before confirming?
   - Recommendation: Start without diff preview; add as enhancement if users want to preview before rolling back

3. **Real-time Collaboration**
   - What we know: CodeMirror 6 supports collaborative editing
   - What's unclear: Backend doesn't support real-time collaboration
   - Recommendation: Out of scope for Phase 7; not in requirements

## Sources

### Primary (HIGH confidence)
- [Backend configuration.py](/Users/roysarfati/PycharmProjects/atlas/backend/src/atlas/entrypoints/api/routes/configuration.py) - Exact API contract
- [GitHub uiwjs/react-codemirror](https://github.com/uiwjs/react-codemirror) - Installation and usage
- [TanStack Query Optimistic Updates](https://tanstack.com/query/latest/docs/framework/react/guides/optimistic-updates) - Mutation patterns
- Existing project code: LoginForm.tsx, useAuth.ts, catalogApi.ts - Established patterns

### Secondary (MEDIUM confidence)
- [CodeMirror vs Monaco comparison](https://dev.to/suraj975/monaco-vs-codemirror-in-react-5kf) - Size/feature tradeoffs
- [shadcn-dropzone GitHub](https://github.com/diragb/shadcn-dropzone) - Dropzone component pattern
- [shadcn-timeline GitHub](https://github.com/timDeHof/shadcn-timeline) - Timeline component pattern

### Tertiary (LOW confidence)
- [LogRocket Code Editors](https://blog.logrocket.com/best-code-editor-components-react/) - General comparison
- WebSearch results for "React markdown editor 2026" - Ecosystem overview

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Libraries verified, existing patterns in project
- Architecture: HIGH - Following established feature directory pattern from Phase 6
- Pitfalls: HIGH - Based on backend API contract and common React patterns

**Research date:** 2026-01-25
**Valid until:** 2026-03-25 (60 days - stable, well-established libraries)

**Notes:**
- Backend APIs complete from Phase 4 - just need UI
- Existing profile feature has EffectiveConfiguration type and API - reuse
- Dark theme already uses OKLCH - ensure CodeMirror theme matches
- Router already has /settings route with protectedLoader - just need page component
