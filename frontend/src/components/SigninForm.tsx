'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/use-auth';

interface FormErrors {
  email?: string;
  password?: string;
}

export default function SigninForm() {
  const router = useRouter();
  const { login } = useAuth();

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  // UI state
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [rememberMe, setRememberMe] = useState(false);

  // Check for signup success message
  useEffect(() => {
    const message = sessionStorage.getItem('signupSuccess');
    if (message) {
      setSuccessMessage(message);
      sessionStorage.removeItem('signupSuccess');
    }
  }, []);

  /**
   * Validate form inputs.
   */
  function validateForm(): boolean {
    const newErrors: FormErrors = {};

    // Email validation
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!emailPattern.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  /**
   * Handle form submission.
   */
  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setServerError(null);

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call login through auth context
      await login(formData.email, formData.password);

      // Store remember me preference if checked
      if (rememberMe) {
        localStorage.setItem('rememberMe', 'true');
      }

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error) {
      // Display server error
      if (error instanceof Error) {
        setServerError(error.message);
      } else {
        setServerError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }

  /**
   * Handle input change.
   */
  function handleChange(field: 'email' | 'password', value: string) {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Success Message */}
      {successMessage && (
        <div className="p-4 text-sm text-green-800 bg-green-100 rounded-md border border-green-200">
          {successMessage}
        </div>
      )}

      {/* Server Error */}
      {serverError && (
        <div className="p-4 text-sm text-red-800 bg-red-100 rounded-md border border-red-200">
          {serverError}
        </div>
      )}

      {/* Email Field */}
      <div>
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
          Email Address
        </label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={(e) => handleChange('email', e.target.value)}
          className={`w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 transition-colors ${
            errors.email
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="you@example.com"
          autoComplete="email"
          disabled={isLoading}
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email}</p>
        )}
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
          Password
        </label>
        <input
          id="password"
          type="password"
          value={formData.password}
          onChange={(e) => handleChange('password', e.target.value)}
          className={`w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 transition-colors ${
            errors.password
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="Enter your password"
          autoComplete="current-password"
          disabled={isLoading}
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password}</p>
        )}
      </div>

      {/* Remember Me & Forgot Password */}
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <input
            id="remember-me"
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            disabled={isLoading}
          />
          <label htmlFor="remember-me" className="ml-2 text-sm text-gray-700">
            Remember me
          </label>
        </div>

        <Link
          href="/auth/forgot-password"
          className="text-sm text-blue-600 hover:underline"
        >
          Forgot password?
        </Link>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Signing in...' : 'Sign In'}
      </button>

      {/* Signup Link */}
      <p className="text-center text-sm text-gray-600">
        Don&apos;t have an account?{' '}
        <Link href="/auth/signup" className="text-blue-600 hover:underline font-medium">
          Create account
        </Link>
      </p>
    </form>
  );
}
