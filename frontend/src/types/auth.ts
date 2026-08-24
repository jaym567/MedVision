// frontend/src/types/auth.ts
/**
 * Authentication types matching backend auth schemas
 */

import { UserRole, UserSummary } from "./user";

export interface UserRegisterRequest {
  email: string;
  password: string;
  full_name: string;
  role: UserRole;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserSummary;
}

export interface TokenPayload {
  sub: string;
  email: string;
  role: UserRole;
  exp: number;
}
