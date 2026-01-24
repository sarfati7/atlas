import { apiClient } from '@/lib/api'
import type {
  User,
  LoginResponse,
  RegisterResponse,
  MessageResponse,
  LoginCredentials,
  RegisterCredentials,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from '../types'

const AUTH_BASE = '/api/v1/auth'

export const authApi = {
  /**
   * Register a new user account.
   */
  register: async (credentials: RegisterCredentials): Promise<RegisterResponse> => {
    const response = await apiClient.post<RegisterResponse>(
      `${AUTH_BASE}/register`,
      credentials
    )
    return response.data
  },

  /**
   * Login with email and password.
   * Uses OAuth2 form data format as required by backend.
   */
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    // Backend expects OAuth2 form data with 'username' field containing email
    const formData = new URLSearchParams()
    formData.append('username', credentials.email)
    formData.append('password', credentials.password)

    const response = await apiClient.post<LoginResponse>(`${AUTH_BASE}/login`, formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  /**
   * Logout the current user.
   * Clears the httpOnly refresh token cookie.
   */
  logout: async (): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>(`${AUTH_BASE}/logout`)
    return response.data
  },

  /**
   * Get the current authenticated user's information.
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>(`${AUTH_BASE}/me`)
    return response.data
  },

  /**
   * Request a password reset email.
   */
  forgotPassword: async (request: ForgotPasswordRequest): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>(
      `${AUTH_BASE}/forgot-password`,
      request
    )
    return response.data
  },

  /**
   * Reset password using a valid reset token.
   */
  resetPassword: async (request: ResetPasswordRequest): Promise<MessageResponse> => {
    const response = await apiClient.post<MessageResponse>(
      `${AUTH_BASE}/reset-password`,
      request
    )
    return response.data
  },
}
