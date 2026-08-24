// frontend/src/stores/authStore.ts
/**
 * Authentication state management with Zustand
 * Persists to localStorage for session continuity
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserSummary } from '@/types/user';

interface AuthState {
  accessToken: string | null;
  user: UserSummary | null;
  isAuthenticated: boolean;

  // Actions
  setAuth: (token: string, user: UserSummary) => void;
  clearAuth: () => void;
  updateUser: (user: UserSummary) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      user: null,
      isAuthenticated: false,

      setAuth: (token: string, user: UserSummary) => {
        set({
          accessToken: token,
          user,
          isAuthenticated: true,
        });
      },

      clearAuth: () => {
        set({
          accessToken: null,
          user: null,
          isAuthenticated: false,
        });
      },

      updateUser: (user: UserSummary) => {
        set({ user });
      },
    }),
    {
      name: 'auth-storage',
      // Only persist token and user, not computed isAuthenticated
      partialize: (state) => ({
        accessToken: state.accessToken,
        user: state.user,
      }),
      // Recompute isAuthenticated on rehydration
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isAuthenticated = !!state.accessToken;
        }
      },
    }
  )
);
