/**
 * Route loaders for authentication guards.
 */
import { redirect } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

/**
 * Loader for protected routes.
 * Redirects to /login if user is not authenticated.
 */
export function protectedLoader() {
  const isAuthenticated = useAuthStore.getState().isAuthenticated

  if (!isAuthenticated) {
    return redirect('/login')
  }

  return null
}

/**
 * Loader for guest-only routes (login, signup).
 * Redirects to /dashboard if user is already authenticated.
 */
export function guestLoader() {
  const isAuthenticated = useAuthStore.getState().isAuthenticated

  if (isAuthenticated) {
    return redirect('/dashboard')
  }

  return null
}
