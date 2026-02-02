'use client';

import { ReactNode, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/use-auth';

interface ProtectedRouteProps {
  children: ReactNode;
  redirectTo?: string;
}

// Helper function to check if token exists in localStorage or cookies
function hasAuthToken(): boolean {
  if (typeof window === 'undefined') return false;

  // Check localStorage
  if (localStorage.getItem('auth-token')) {
    return true;
  }

  // Check cookies
  const name = 'auth-token=';
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(';');

  for (let cookie of cookieArray) {
    cookie = cookie.trim();
    if (cookie.startsWith(name)) {
      return true;
    }
  }

  return false;
}

export default function ProtectedRoute({
  children,
  redirectTo = '/auth/signin',
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [hasToken, setHasToken] = useState(false);

  // Check for token on mount to prevent redirect race condition
  useEffect(() => {
    setHasToken(hasAuthToken());
  }, []);

  // Handle redirect in useEffect to avoid setState during render
  useEffect(() => {
    // Only redirect if:
    // 1. Auth check is complete (isLoading = false)
    // 2. User is not authenticated (isAuthenticated = false)
    // 3. There's no token to restore (hasToken = false)
    // This prevents redirecting while session is being restored from cookies
    if (!isLoading && !isAuthenticated && !hasToken) {
      router.push(redirectTo);
    }
  }, [isAuthenticated, isLoading, hasToken, router, redirectTo]);

  if (isLoading) {
    // Show a loading indicator while checking auth status
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Return null while redirecting
    return null;
  }

  // If authenticated, render the protected content
  return <>{children}</>;
}
