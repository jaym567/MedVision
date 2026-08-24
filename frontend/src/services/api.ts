// frontend/src/services/api.ts (UPDATED)
/**
 * Base API client with JWT authentication and error handling
 */

import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
  AxiosResponse
} from "axios";
import { ApiError } from "../types/api";

// Get API base URL from environment
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds
});

/**
 * Request interceptor to attach JWT token
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Get token from localStorage (Zustand persist storage)
    const authData = localStorage.getItem("auth-storage");

    if (authData) {
      try {
        const parsed = JSON.parse(authData);
        const token = parsed.state?.accessToken;

        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
      } catch (error) {
        console.error("Failed to parse auth data:", error);
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor to handle errors globally
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError<ApiError>) => {
    // Handle 401 Unauthorized - clear auth and redirect to login
    if (error.response?.status === 401) {
      // Clear auth storage
      localStorage.removeItem("auth-storage");

      // Only redirect if not already on login/register page
      const publicPaths = ['/login', '/register'];
      const currentPath = window.location.pathname;

      if (!publicPaths.includes(currentPath)) {
        window.location.href = "/login";
      }
    }

    // Normalize error response
    const apiError: ApiError = {
      detail: error.response?.data?.detail || error.message || "An unexpected error occurred",
      status: error.response?.status,
    };

    return Promise.reject(apiError);
  }
);

export default apiClient;

/**
 * Type-safe API request wrapper
 */
export async function apiRequest<T>(
  method: "get" | "post" | "patch" | "delete",
  url: string,
  data?: any,
  config?: any
): Promise<T> {
  const response = await apiClient.request<T>({
    method,
    url,
    data,
    ...config,
  });
  return response.data;
}
