import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  isAuthenticated: boolean
  accessToken: string | null
  setAuthenticated: (authenticated: boolean) => void
  setAccessToken: (token: string | null) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      accessToken: null,

      setAuthenticated: (authenticated) => set({ isAuthenticated: authenticated }),

      setAccessToken: (token) =>
        set({
          accessToken: token,
          isAuthenticated: token !== null,
        }),

      logout: () =>
        set({
          isAuthenticated: false,
          accessToken: null,
        }),
    }),
    {
      name: 'atlas-auth',
      partialize: (state) => ({
        isAuthenticated: state.isAuthenticated,
        accessToken: state.accessToken,
      }),
    }
  )
)

// Listen for auth:logout event from API interceptor on refresh failure
if (typeof window !== 'undefined') {
  window.addEventListener('auth:logout', () => {
    useAuthStore.getState().logout()
  })
}
