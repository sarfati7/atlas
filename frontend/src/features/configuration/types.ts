/**
 * Configuration feature types.
 *
 * Maps to backend configuration API responses.
 */

export interface Configuration {
  content: string
  commit_sha: string
  updated_at: string // ISO datetime from backend
}

export interface ConfigurationUpdate {
  content: string
  message?: string
}

export interface Version {
  commit_sha: string
  message: string
  author: string
  timestamp: string // ISO datetime
}

export interface VersionHistory {
  versions: Version[]
  total: number
}
