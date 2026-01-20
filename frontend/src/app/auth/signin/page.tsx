'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AuthLayout from '@/components/AuthLayout';
import SigninForm from '@/components/SigninForm';
import { useAuth } from '@/lib/use-auth';

export default function SigninPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // Redirect to dashboard if already authenticated
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading || (!isLoading && isAuthenticated)) {
    // Show a loading state or nothing while redirecting
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <AuthLayout
      title="Sign In"
      subtitle="Welcome back! Sign in to your account"
    >
      <SigninForm />
    </AuthLayout>
  );
}
