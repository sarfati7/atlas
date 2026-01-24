/**
 * Profile API layer for user dashboard, available items, and effective configuration.
 */
import { apiClient } from '@/lib/api'
import type { AvailableItem, DashboardData, EffectiveConfiguration } from '../types'

export const profileApi = {
  /**
   * Get current user's dashboard summary.
   */
  getDashboard: async (): Promise<DashboardData> => {
    const response = await apiClient.get<DashboardData>('/api/v1/profile/dashboard')
    return response.data
  },

  /**
   * Get catalog items available to current user.
   * Optionally filter by item type.
   */
  getAvailableItems: async (type?: 'skill' | 'mcp' | 'tool'): Promise<AvailableItem[]> => {
    const params = type ? { type } : {}
    const response = await apiClient.get<AvailableItem[]>('/api/v1/profile/available-items', {
      params,
    })
    return response.data
  },

  /**
   * Get user's effective configuration with inheritance chain.
   */
  getEffectiveConfiguration: async (): Promise<EffectiveConfiguration> => {
    const response = await apiClient.get<EffectiveConfiguration>(
      '/api/v1/profile/effective-configuration'
    )
    return response.data
  },
}
