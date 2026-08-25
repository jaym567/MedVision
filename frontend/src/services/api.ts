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

// Base URL is a relative path — the Vite dev proxy forwards /api/* to http://localhost:8000
// This avoids all Axios baseURL path-stripping issues and CORS problems.
const API_BASE_URL = "/api/v1";

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000, // 30 seconds
});

/**
 * Request interceptor: attach JWT token from Zustand persisted auth store.
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
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
