import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  withCredentials: true, // Include httpOnly cookies
})

// Track if we're currently refreshing to prevent multiple refresh calls
let isRefreshing = false
let failedQueue: Array<{
  resolve: (token: string | null) => void
  reject: (error: unknown) => void
}> = []

const processQueue = (error: unknown | null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(null)
    }
  })
  failedQueue = []
}

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(() => {
          return apiClient(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        // Refresh token endpoint (uses httpOnly cookie)
        await axios.post('/api/v1/auth/refresh', {}, { withCredentials: true })

        processQueue(null)

        // Retry original request
        return apiClient(originalRequest)
      } catch (refreshError) {
        processQueue(refreshError)

        // Refresh failed - clear auth state and redirect to login
        // The auth store will handle this
        window.dispatchEvent(new CustomEvent('auth:logout'))

        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  }
)
