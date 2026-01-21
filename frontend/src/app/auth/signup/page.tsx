"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import AuthLayout from "@/components/AuthLayout";
import SignupForm from "@/components/SignupForm";
import { useAuth } from "@/lib/use-auth";

export const dynamic = "force-dynamic";

export default function SignupPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  useEffect(() => {
    // Redirect to dashboard if already authenticated
    if (!isLoading && isAuthenticated) {
      router.push("/dashboard");
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
      title="Create Account"
      subtitle="Start organizing your tasks today"
    >
      <SignupForm />
    </AuthLayout>
  );
}
