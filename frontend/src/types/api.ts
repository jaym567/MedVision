// frontend/src/types/api.ts
/**
 * Base API types for error handling and pagination
 */

export interface ApiError {
  detail: string;
  status?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiResponse<T> {
  data: T;
  error?: ApiError;
}
