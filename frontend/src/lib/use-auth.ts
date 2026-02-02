'use client';

import { useContext } from 'react';
import { AuthContext, AuthContextType } from './auth-context';

/**
 * Hook to access authentication state and methods
 * Must be used inside AuthProvider
 *
 * @returns Auth context with user, isAuthenticated, isLoading, and auth methods
 * @throws Error if used outside of AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used inside AuthProvider');
  }

  return context;
}
