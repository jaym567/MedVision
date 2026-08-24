// frontend/src/types/user.ts
/**
 * User-related types matching backend schemas
 */

export enum UserRole {
  PHYSICIAN = "physician",
  RESEARCHER = "researcher",
  ADMIN = "admin"
}

export interface UserRead {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserSummary {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
}
