'use client';

import { ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/use-auth';

interface ProtectedRouteProps {
  children: ReactNode;
  redirectTo?: string;
}

export default function ProtectedRoute({
  children,
  redirectTo = '/auth/signin',
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  if (isLoading) {
    // Show a loading indicator while checking auth status
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Redirect to signin page if not authenticated
    if (typeof window !== 'undefined') {
      router.push(redirectTo);
    }
    return null; // Render nothing while redirecting
  }

  // If authenticated, render the protected content
  return <>{children}</>;
}
