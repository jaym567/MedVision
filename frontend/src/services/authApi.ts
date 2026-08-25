// frontend/src/services/authApi.ts
/**
 * Authentication API service
 * Handles user registration, login, and session validation
 */

import apiClient from './api';
import {
  UserRegisterRequest,
  LoginRequest,
  TokenResponse,
} from '@/types/auth';
import { UserRead, CurrentUser } from '@/types/user';

/**
 * Register a new user account
 * @param userData - User registration data
 * @returns Created user information
 */
export async function register(
  userData: UserRegisterRequest
): Promise<UserRead> {
  const response = await apiClient.post<UserRead>('/auth/register', userData);
  return response.data;
}

/**
 * Authenticate user and receive JWT token
 * @param credentials - User login credentials
 * @returns Token response with access token and user info
 */
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const response = await apiClient.post<TokenResponse>(
    '/auth/login',
    credentials
  );
  return response.data;
}

/**
 * Get current authenticated user information
 * Requires valid JWT token in request
 * @returns Current user data
 */
export async function getCurrentUser(): Promise<CurrentUser> {
  const response = await apiClient.get<CurrentUser>('/auth/me');
  return response.data;
}

/**
 * Logout user (client-side only)
 * Clears auth state and token
 * Note: No backend endpoint needed for stateless JWT auth
 */
export function logout(): void {
  // Clear is handled by auth store
  // This function exists for consistency and future server-side logout
}
