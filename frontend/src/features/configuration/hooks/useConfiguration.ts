/**
 * Configuration TanStack Query hooks.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { configurationApi } from '../api/configurationApi'
import type { ConfigurationUpdate } from '../types'

/**
 * Query key factory for configuration queries.
 */
export const configurationKeys = {
  all: ['configuration'] as const,
  me: () => [...configurationKeys.all, 'me'] as const,
  history: (limit?: number) => [...configurationKeys.all, 'history', limit] as const,
}

/**
 * Hook to fetch current user's configuration.
 */
export function useConfiguration() {
  return useQuery({
    queryKey: configurationKeys.me(),
    queryFn: configurationApi.getMyConfiguration,
  })
}

/**
 * Hook to update configuration.
 */
export function useUpdateConfiguration() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (update: ConfigurationUpdate) => configurationApi.updateConfiguration(update),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: configurationKeys.all })
      queryClient.invalidateQueries({ queryKey: ['profile', 'effectiveConfiguration'] })
      queryClient.invalidateQueries({ queryKey: ['profile', 'dashboard'] })
    },
  })
}

/**
 * Hook to fetch configuration version history.
 */
export function useVersionHistory(limit = 50) {
  return useQuery({
    queryKey: configurationKeys.history(limit),
    queryFn: () => configurationApi.getVersionHistory(limit),
  })
}

/**
 * Hook to rollback configuration to a previous version.
 */
export function useRollback() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (commitSha: string) => configurationApi.rollback(commitSha),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: configurationKeys.all })
      queryClient.invalidateQueries({ queryKey: ['profile', 'effectiveConfiguration'] })
      queryClient.invalidateQueries({ queryKey: ['profile', 'dashboard'] })
    },
  })
}

/**
 * Hook to import configuration from file.
 */
export function useImportConfiguration() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (file: File) => configurationApi.importFile(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: configurationKeys.all })
      queryClient.invalidateQueries({ queryKey: ['profile', 'effectiveConfiguration'] })
      queryClient.invalidateQueries({ queryKey: ['profile', 'dashboard'] })
    },
  })
}
