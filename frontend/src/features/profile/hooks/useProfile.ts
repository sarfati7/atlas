/**
 * TanStack Query hooks for profile data fetching.
 */
import { useQuery } from '@tanstack/react-query'
import { profileApi } from '../api/profileApi'

/** Query keys for profile-related queries. */
export const profileKeys = {
  all: ['profile'] as const,
  dashboard: () => [...profileKeys.all, 'dashboard'] as const,
  availableItems: (type?: string) => [...profileKeys.all, 'available-items', type] as const,
  effectiveConfiguration: () => [...profileKeys.all, 'effective-configuration'] as const,
}

/**
 * Hook for fetching user dashboard data.
 */
export function useDashboard() {
  return useQuery({
    queryKey: profileKeys.dashboard(),
    queryFn: profileApi.getDashboard,
  })
}

/**
 * Hook for fetching available catalog items.
 * @param type - Optional filter by item type
 */
export function useAvailableItems(type?: 'skill' | 'mcp' | 'tool') {
  return useQuery({
    queryKey: profileKeys.availableItems(type),
    queryFn: () => profileApi.getAvailableItems(type),
  })
}

/**
 * Hook for fetching effective configuration.
 */
export function useEffectiveConfiguration() {
  return useQuery({
    queryKey: profileKeys.effectiveConfiguration(),
    queryFn: profileApi.getEffectiveConfiguration,
  })
}
