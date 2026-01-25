/**
 * Configuration editor component with Monaco editor and preview toggle.
 */

import { useCallback, useState } from 'react'
import Editor, { type OnChange, type OnMount } from '@monaco-editor/react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Eye, Code } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ConfigurationEditorProps {
  value: string
  onChange: (value: string) => void
  readOnly?: boolean
}

export function ConfigurationEditor({
  value,
  onChange,
  readOnly = false,
}: ConfigurationEditorProps) {
  const [mode, setMode] = useState<'edit' | 'preview'>('edit')

  const handleChange: OnChange = useCallback(
    (val) => {
      if (val !== undefined) {
        onChange(val)
      }
    },
    [onChange]
  )

  const handleMount: OnMount = useCallback(
    (editor) => {
      // Focus editor on mount (only in edit mode)
      if (!readOnly) {
        editor.focus()
      }
    },
    [readOnly]
  )

  return (
    <div className="border border-border rounded-lg overflow-hidden">
      {/* Toolbar with mode toggle */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border bg-muted/30">
        <span className="text-sm text-muted-foreground">
          {readOnly ? 'Read-only preview' : 'claude.md'}
        </span>
        {!readOnly && (
          <div className="flex items-center gap-1">
            <Button
              variant={mode === 'edit' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setMode('edit')}
              className="gap-1.5 h-7 px-2"
            >
              <Code className="h-3.5 w-3.5" />
              Edit
            </Button>
            <Button
              variant={mode === 'preview' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setMode('preview')}
              className="gap-1.5 h-7 px-2"
            >
              <Eye className="h-3.5 w-3.5" />
              Preview
            </Button>
          </div>
        )}
      </div>

      {/* Content area */}
      <div className="h-[500px]">
        {mode === 'edit' && !readOnly ? (
          <Editor
            height="100%"
            defaultLanguage="markdown"
            value={value}
            onChange={handleChange}
            onMount={handleMount}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              wordWrap: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              padding: { top: 16, bottom: 16 },
              renderLineHighlight: 'line',
              cursorBlinking: 'smooth',
              tabSize: 2,
            }}
            loading={
              <div className="h-full flex items-center justify-center text-muted-foreground">
                Loading editor...
              </div>
            }
          />
        ) : (
          <div className="h-full overflow-auto p-6 prose prose-invert max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {value || '*No content*'}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}
