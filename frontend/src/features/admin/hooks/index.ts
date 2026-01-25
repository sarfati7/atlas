/**
 * Admin TanStack Query hooks for team and user management.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../api'
import type { CreateTeamRequest, UpdateTeamRequest, UpdateUserRoleRequest } from '../types'

/**
 * Query key factory for admin queries.
 */
export const adminKeys = {
  all: ['admin'] as const,
  teams: () => [...adminKeys.all, 'teams'] as const,
  teamsList: (page: number, pageSize: number) =>
    [...adminKeys.teams(), 'list', { page, pageSize }] as const,
  team: (id: string) => [...adminKeys.teams(), id] as const,
  users: () => [...adminKeys.all, 'users'] as const,
  usersList: (page: number, pageSize: number, search?: string) =>
    [...adminKeys.users(), 'list', { page, pageSize, search }] as const,
  user: (id: string) => [...adminKeys.users(), id] as const,
}

// Team hooks

/**
 * Hook to fetch paginated teams.
 */
export function useTeams(page = 1, pageSize = 10) {
  return useQuery({
    queryKey: adminKeys.teamsList(page, pageSize),
    queryFn: () => adminApi.fetchTeams(page, pageSize),
  })
}

/**
 * Hook to fetch a single team with members.
 */
export function useTeam(id: string) {
  return useQuery({
    queryKey: adminKeys.team(id),
    queryFn: () => adminApi.fetchTeam(id),
    enabled: !!id,
  })
}

/**
 * Hook to create a new team.
 */
export function useCreateTeam() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateTeamRequest) => adminApi.createTeam(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.teams() })
    },
  })
}

/**
 * Hook to update a team.
 */
export function useUpdateTeam() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateTeamRequest }) =>
      adminApi.updateTeam(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.teams() })
      queryClient.invalidateQueries({ queryKey: adminKeys.team(variables.id) })
    },
  })
}

/**
 * Hook to delete a team.
 */
export function useDeleteTeam() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => adminApi.deleteTeam(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.teams() })
    },
  })
}

/**
 * Hook to add a member to a team.
 */
export function useAddTeamMember() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ teamId, userId }: { teamId: string; userId: string }) =>
      adminApi.addTeamMember(teamId, userId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.team(variables.teamId) })
      queryClient.invalidateQueries({ queryKey: adminKeys.teams() })
      queryClient.invalidateQueries({ queryKey: adminKeys.users() })
    },
  })
}

/**
 * Hook to remove a member from a team.
 */
export function useRemoveTeamMember() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ teamId, userId }: { teamId: string; userId: string }) =>
      adminApi.removeTeamMember(teamId, userId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.team(variables.teamId) })
      queryClient.invalidateQueries({ queryKey: adminKeys.teams() })
      queryClient.invalidateQueries({ queryKey: adminKeys.users() })
    },
  })
}

// User hooks

/**
 * Hook to fetch paginated users with optional search.
 */
export function useUsers(page = 1, pageSize = 10, search?: string) {
  return useQuery({
    queryKey: adminKeys.usersList(page, pageSize, search),
    queryFn: () => adminApi.fetchUsers(page, pageSize, search),
  })
}

/**
 * Hook to fetch a single user.
 */
export function useUser(id: string) {
  return useQuery({
    queryKey: adminKeys.user(id),
    queryFn: () => adminApi.fetchUser(id),
    enabled: !!id,
  })
}

/**
 * Hook to update a user's role.
 */
export function useUpdateUserRole() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateUserRoleRequest }) =>
      adminApi.updateUserRole(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: adminKeys.users() })
      queryClient.invalidateQueries({ queryKey: adminKeys.user(variables.id) })
    },
  })
}

/**
 * Hook to delete a user.
 */
export function useDeleteUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => adminApi.deleteUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminKeys.users() })
    },
  })
}

// Analytics hooks

/**
 * Hook to fetch usage summary.
 */
export function useUsageSummary(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: [...adminKeys.all, 'analytics', 'summary', { startDate, endDate }] as const,
    queryFn: () => adminApi.fetchUsageSummary(startDate, endDate),
  })
}

/**
 * Hook to fetch usage by user.
 */
export function useUsageByUser(startDate?: string, endDate?: string, limit = 20) {
  return useQuery({
    queryKey: [...adminKeys.all, 'analytics', 'by-user', { startDate, endDate, limit }] as const,
    queryFn: () => adminApi.fetchUsageByUser(startDate, endDate, limit),
  })
}

/**
 * Hook to fetch usage by item.
 */
export function useUsageByItem(startDate?: string, endDate?: string, limit = 20) {
  return useQuery({
    queryKey: [...adminKeys.all, 'analytics', 'by-item', { startDate, endDate, limit }] as const,
    queryFn: () => adminApi.fetchUsageByItem(startDate, endDate, limit),
  })
}

/**
 * Hook to fetch usage timeline.
 */
export function useUsageTimeline(startDate?: string, endDate?: string) {
  return useQuery({
    queryKey: [...adminKeys.all, 'analytics', 'timeline', { startDate, endDate }] as const,
    queryFn: () => adminApi.fetchUsageTimeline(startDate, endDate),
  })
}

// Audit log hooks

/**
 * Hook to fetch paginated audit logs.
 */
export function useAuditLogs(
  page = 1,
  pageSize = 50,
  filters?: {
    resource_type?: string
    resource_id?: string
    user_id?: string
    action?: string
  }
) {
  return useQuery({
    queryKey: [...adminKeys.all, 'audit', 'logs', { page, pageSize, ...filters }] as const,
    queryFn: () => adminApi.fetchAuditLogs(page, pageSize, filters),
  })
}

/**
 * Hook to fetch a single audit log.
 */
export function useAuditLog(id: string) {
  return useQuery({
    queryKey: [...adminKeys.all, 'audit', 'log', id] as const,
    queryFn: () => adminApi.fetchAuditLog(id),
    enabled: !!id,
  })
}

/**
 * Hook to fetch audit trail for a resource.
 */
export function useResourceAuditTrail(resourceType: string, resourceId: string) {
  return useQuery({
    queryKey: [...adminKeys.all, 'audit', 'trail', resourceType, resourceId] as const,
    queryFn: () => adminApi.fetchResourceAuditTrail(resourceType, resourceId),
    enabled: !!resourceType && !!resourceId,
  })
}
