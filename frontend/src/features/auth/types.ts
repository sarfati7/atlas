/**
 * Auth feature type definitions.
 * Maps to backend API response schemas.
 */

export interface User {
  id: string
  email: string
  username: string
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface RegisterResponse {
  message: string
  user_id: string
}

export interface MessageResponse {
  message: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterCredentials {
  email: string
  username: string
  password: string
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ResetPasswordRequest {
  token: string
  new_password: string
}
