// frontend/src/hooks/useAuth.ts (UPDATED)
/**
 * Custom hooks for authentication operations
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import * as authApi from '@/services/authApi';
import {
  UserRegisterRequest,
  LoginRequest,
  TokenResponse,
} from '@/types/auth';
import { CurrentUser } from '@/types/user';
import { ApiError } from '@/types/api';
import toast from 'react-hot-toast';

/**
 * Hook to access auth state and actions
 */
export function useAuth() {
  const authStore = useAuthStore();
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  const logout = () => {
    authStore.clearAuth();
    queryClient.clear(); // Clear all cached queries
    navigate('/login');
    toast.success('Logged out successfully');
  };

  return {
    ...authStore,
    logout,
  };
}

/**
 * Hook for user registration
 */
export function useRegister() {
  const navigate = useNavigate();

  return useMutation<void, ApiError, UserRegisterRequest>({
    mutationFn: async (userData: UserRegisterRequest) => {
      await authApi.register(userData);
    },
    onSuccess: () => {
      toast.success('Registration successful! Please log in.');
      navigate('/login');
    },
    onError: (error: ApiError) => {
      toast.error(error.detail || 'Registration failed');
    },
  });
}

/**
 * Hook for user login
 */
export function useLogin() {
  const { setAuth } = useAuthStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation<TokenResponse, ApiError, LoginRequest>({
    mutationFn: async (credentials: LoginRequest) => {
      return await authApi.login(credentials);
    },
    onSuccess: (data: TokenResponse) => {
      // Store token and user in auth store
      setAuth(data.access_token, data.user);

      // Invalidate queries to refetch with new auth
      queryClient.invalidateQueries();

      toast.success(`Welcome back, ${data.user.full_name}!`);
      navigate('/dashboard');
    },
    onError: (error: ApiError) => {
      toast.error(error.detail || 'Login failed');
    },
  });
}

/**
 * Hook to get current user information
 * Only fetches if user is authenticated
 */
export function useCurrentUser() {
  const { isAuthenticated, user: cachedUser } = useAuthStore();

  return useQuery<CurrentUser, ApiError>({
    queryKey: ['currentUser'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false,
    // Use cached user as placeholder data
    placeholderData: cachedUser as CurrentUser,
  });
}

/**
 * Hook to validate current session
 * Useful for protected routes
 * Clears auth if validation fails
 */
export function useValidateSession() {
  const { isAuthenticated, clearAuth } = useAuthStore();
  const queryClient = useQueryClient();

  const query = useQuery<CurrentUser, ApiError>({
    queryKey: ['validateSession'],
    queryFn: authApi.getCurrentUser,
    enabled: isAuthenticated,
    retry: false,
    staleTime: Infinity, // Only validate once per mount
  });

  // Handle errors using useEffect instead of onError callback
  useEffect(() => {
    if (query.isError) {
      // If validation fails, clear auth
      clearAuth();
      queryClient.clear();
      toast.error('Session expired. Please log in again.');
    }
  }, [query.isError, clearAuth, queryClient]);

  return query;
}
