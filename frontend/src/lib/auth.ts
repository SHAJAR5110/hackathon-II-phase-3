/**
 * Authentication Utilities
 * Phase II - Todo Full-Stack Web Application
 *
 * Provides authentication helpers for Better Auth integration.
 * In MVP, we use simple localStorage for token management.
 * In production, Better Auth will manage tokens via HTTP-only cookies.
 */

'use client';

import { useState, useEffect } from 'react';

// ============================================================================
// Type Definitions
// ============================================================================

export interface User {
  id: string;
  email: string;
  name: string;
}

export interface SignupData {
  email: string;
  password: string;
  name: string;
}

export interface SigninData {
  email: string;
  password: string;
}

// ============================================================================
// Token Management
// ============================================================================

/**
 * Save JWT token to localStorage.
 * In production, Better Auth will handle this via HTTP-only cookies.
 *
 * @param token - JWT token string
 */
export function saveToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth-token', token);
  }
}

/**
 * Get JWT token from localStorage.
 *
 * @returns JWT token or null if not authenticated
 */
export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth-token');
  }
  return null;
}

/**
 * Remove JWT token from localStorage and cookies.
 */
export function clearToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth-token');
    localStorage.removeItem('user');
    // Clear auth token cookie
    document.cookie = 'auth-token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  }
}

// ============================================================================
// User Management
// ============================================================================

/**
 * Save user data to localStorage.
 *
 * @param user - User object
 */
export function saveUser(user: User): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('user', JSON.stringify(user));
  }
}

/**
 * Get user data from localStorage.
 *
 * @returns User object or null if not authenticated
 */
export function getUser(): User | null {
  if (typeof window !== 'undefined') {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr) as User;
      } catch {
        return null;
      }
    }
  }
  return null;
}

/**
 * Check if user is authenticated.
 *
 * @returns true if token exists, false otherwise
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

// ============================================================================
// Authentication Hook
// ============================================================================

/**
 * Hook for accessing authentication state and methods.
 *
 * Usage:
 *   const { user, isLoading, logout } = useAuth();
 *
 * @returns Authentication state and methods
 */
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load user from localStorage on mount
    const storedUser = getUser();
    setUser(storedUser);
    setIsLoading(false);
  }, []);

  /**
   * Logout the current user.
   * Clears token and user data from localStorage.
   */
  function logout() {
    clearToken();
    setUser(null);
    // Redirect to signin page
    if (typeof window !== 'undefined') {
      window.location.href = '/auth/signin';
    }
  }

  /**
   * Set the current user and save to localStorage.
   *
   * @param userData - User object
   * @param token - JWT token
   */
  function login(userData: User, token: string) {
    saveUser(userData);
    saveToken(token);
    setUser(userData);
  }

  return {
    user,
    isLoading,
    isAuthenticated: user !== null,
    login,
    logout,
  };
}

// ============================================================================
// Authentication API Methods (Better Auth Integration Placeholder)
// ============================================================================

/**
 * Sign up a new user.
 * In MVP, this is a placeholder. In production, use Better Auth.
 *
 * @param data - Signup data (email, password, name)
 * @returns User object and JWT token
 */
export async function signup(data: SignupData): Promise<{ user: User; token: string }> {
  // TODO: Integrate with Better Auth
  // For MVP, this is a mock implementation
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/signup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Signup failed');
  }

  const result = await response.json();

  // Set auth token in cookie for middleware authentication
  if (result.token) {
    // Set cookie using document.cookie
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + 7); // 7 days expiry
    if (typeof window !== 'undefined') {
      document.cookie = `auth-token=${result.token}; expires=${expiryDate.toUTCString()}; path=/`;
    }
  }

  return result;
}

/**
 * Sign in an existing user.
 * In MVP, this is a placeholder. In production, use Better Auth.
 *
 * @param data - Signin data (email, password)
 * @returns User object and JWT token
 */
export async function signin(data: SigninData): Promise<{ user: User; token: string }> {
  // TODO: Integrate with Better Auth
  // For MVP, this is a mock implementation
  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/signin`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Signin failed');
  }

  const result = await response.json();

  // Set auth token in cookie for middleware authentication
  if (result.token) {
    // Set cookie using document.cookie
    const expiryDate = new Date();
    expiryDate.setDate(expiryDate.getDate() + 7); // 7 days expiry
    if (typeof window !== 'undefined') {
      document.cookie = `auth-token=${result.token}; expires=${expiryDate.toUTCString()}; path=/`;
    }
  }

  return result;
}
