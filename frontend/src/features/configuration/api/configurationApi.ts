/**
 * Configuration API layer.
 *
 * Maps to backend /api/v1/configuration endpoints.
 */

import { apiClient } from '@/lib/api'
import type { Configuration, ConfigurationUpdate, VersionHistory } from '../types'

export const configurationApi = {
  /**
   * Get current user's configuration.
   * GET /api/v1/configuration/me
   */
  async getMyConfiguration(): Promise<Configuration> {
    const { data } = await apiClient.get<Configuration>('/api/v1/configuration/me')
    return data
  },

  /**
   * Update current user's configuration.
   * PUT /api/v1/configuration/me
   */
  async updateConfiguration(update: ConfigurationUpdate): Promise<Configuration> {
    const { data } = await apiClient.put<Configuration>('/api/v1/configuration/me', update)
    return data
  },

  /**
   * Get version history of user's configuration.
   * GET /api/v1/configuration/me/history
   */
  async getVersionHistory(limit = 50): Promise<VersionHistory> {
    const { data } = await apiClient.get<VersionHistory>('/api/v1/configuration/me/history', {
      params: { limit },
    })
    return data
  },

  /**
   * Rollback configuration to a previous version.
   * POST /api/v1/configuration/me/rollback/{commit_sha}
   */
  async rollback(commitSha: string): Promise<Configuration> {
    const { data } = await apiClient.post<Configuration>(
      `/api/v1/configuration/me/rollback/${commitSha}`
    )
    return data
  },

  /**
   * Import configuration from uploaded .md file.
   * POST /api/v1/configuration/me/import (multipart form)
   */
  async importFile(file: File): Promise<Configuration> {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await apiClient.post<Configuration>(
      '/api/v1/configuration/me/import',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    )
    return data
  },
}
