import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api/authApi'
import { useAuthStore } from '@/stores/authStore'
import type {
  LoginCredentials,
  RegisterCredentials,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from '../types'

/**
 * Query the current authenticated user.
 * Only fetches when isAuthenticated is true.
 */
export function useCurrentUser() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  return useQuery({
    queryKey: ['auth', 'currentUser'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

/**
 * Login mutation.
 * Updates auth store on success.
 */
export function useLogin() {
  const queryClient = useQueryClient()
  const setAccessToken = useAuthStore((state) => state.setAccessToken)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (credentials: LoginCredentials) => authApi.login(credentials),
    onSuccess: (data) => {
      setAccessToken(data.access_token)
      queryClient.invalidateQueries({ queryKey: ['auth'] })
      navigate('/dashboard')
    },
  })
}

/**
 * Register mutation.
 * Does not auto-login - user must login after registration.
 */
export function useRegister() {
  return useMutation({
    mutationFn: (credentials: RegisterCredentials) => authApi.register(credentials),
  })
}

/**
 * Logout mutation.
 * Clears auth store and navigates to login.
 */
export function useLogout() {
  const queryClient = useQueryClient()
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      logout()
      queryClient.clear()
      navigate('/login')
    },
    onError: () => {
      // Even on error, clear local state
      logout()
      queryClient.clear()
      navigate('/login')
    },
  })
}

/**
 * Forgot password mutation.
 */
export function useForgotPassword() {
  return useMutation({
    mutationFn: (request: ForgotPasswordRequest) => authApi.forgotPassword(request),
  })
}

/**
 * Reset password mutation.
 * Redirects to login on success.
 */
export function useResetPassword() {
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (request: ResetPasswordRequest) => authApi.resetPassword(request),
    onSuccess: () => {
      navigate('/login')
    },
  })
}
