import { useCallback } from 'react'
import { useDropzone, type FileRejection } from 'react-dropzone'
import { Upload, FileText, AlertCircle, CheckCircle2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface ImportDropzoneProps {
  onFileAccepted: (file: File) => void
  onFileRejected?: (reason: string) => void
  isUploading?: boolean
  disabled?: boolean
}

export function ImportDropzone({
  onFileAccepted,
  onFileRejected,
  isUploading,
  disabled,
}: ImportDropzoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: FileRejection[]) => {
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0]
        const error = rejection.errors[0]

        if (error.code === 'file-too-large') {
          onFileRejected?.('File must be less than 1MB')
        } else if (error.code === 'file-invalid-type') {
          onFileRejected?.('File must be a .md file')
        } else {
          onFileRejected?.(error.message)
        }
        return
      }

      if (acceptedFiles.length > 0) {
        onFileAccepted(acceptedFiles[0])
      }
    },
    [onFileAccepted, onFileRejected]
  )

  const { getRootProps, getInputProps, isDragActive, isDragReject, acceptedFiles } =
    useDropzone({
      onDrop,
      accept: {
        'text/markdown': ['.md'],
        'text/plain': ['.md'],
      },
      maxFiles: 1,
      maxSize: 1024 * 1024, // 1MB (matches backend limit)
      disabled: isUploading || disabled,
    })

  const hasFile = acceptedFiles.length > 0

  return (
    <div
      {...getRootProps()}
      className={cn(
        'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
        isDragActive && !isDragReject && 'border-primary bg-primary/5',
        isDragReject && 'border-destructive bg-destructive/5',
        !isDragActive && !hasFile && 'border-border hover:border-muted-foreground',
        hasFile && 'border-primary/50 bg-primary/5',
        (isUploading || disabled) && 'opacity-50 cursor-not-allowed'
      )}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-3">
        {hasFile ? (
          <>
            <CheckCircle2 className="h-10 w-10 text-primary" />
            <div>
              <p className="font-medium text-foreground">{acceptedFiles[0].name}</p>
              <p className="text-sm text-muted-foreground">
                {(acceptedFiles[0].size / 1024).toFixed(1)} KB
              </p>
            </div>
          </>
        ) : isDragReject ? (
          <>
            <AlertCircle className="h-10 w-10 text-destructive" />
            <p className="text-sm text-destructive">Invalid file type</p>
          </>
        ) : isDragActive ? (
          <>
            <FileText className="h-10 w-10 text-primary" />
            <p className="text-sm text-muted-foreground">Drop the file here</p>
          </>
        ) : (
          <>
            <Upload className="h-10 w-10 text-muted-foreground" />
            <div>
              <p className="text-foreground">
                Drag and drop your claude.md file here
              </p>
              <p className="text-sm text-muted-foreground mt-1">
                or click to select a file
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs text-muted-foreground mt-2">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" /> .md files only
              </span>
              <span className="flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" /> Max 1MB
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
