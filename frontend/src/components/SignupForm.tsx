'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/use-auth';

interface FormErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  name?: string;
}

interface PasswordStrength {
  score: number; // 0-4
  feedback: string;
  color: string;
}

export default function SignupForm() {
  const router = useRouter();
  const { signup } = useAuth();

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: '',
  });

  // UI state
  const [errors, setErrors] = useState<FormErrors>({});
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [termsAccepted, setTermsAccepted] = useState(false);

  /**
   * Calculate password strength score.
   */
  function calculatePasswordStrength(password: string): PasswordStrength {
    if (!password) {
      return { score: 0, feedback: '', color: 'bg-gray-200' };
    }

    let score = 0;
    const checks = {
      length: password.length >= 8,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
    };

    // Base score from length
    if (checks.length) score += 1;
    if (password.length >= 12) score += 1;

    // Character variety
    if (checks.uppercase) score += 1;
    if (checks.lowercase) score += 1;
    if (checks.number) score += 1;
    if (checks.special) score += 1;

    // Normalize to 0-4
    score = Math.min(Math.floor(score / 1.5), 4);

    const feedbacks = [
      { score: 0, feedback: 'Too weak', color: 'bg-gray-200' },
      { score: 1, feedback: 'Weak', color: 'bg-red-500' },
      { score: 2, feedback: 'Fair', color: 'bg-yellow-500' },
      { score: 3, feedback: 'Good', color: 'bg-blue-500' },
      { score: 4, feedback: 'Strong', color: 'bg-green-500' },
    ];

    return feedbacks[score] as PasswordStrength;
  }

  const passwordStrength = calculatePasswordStrength(formData.password);

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

    // Name validation
    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    } else if (formData.name.trim().length < 1 || formData.name.trim().length > 100) {
      newErrors.name = 'Name must be 1-100 characters';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    } else if (!/[A-Z]/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one uppercase letter';
    } else if (!/[a-z]/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one lowercase letter';
    } else if (!/\d/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one number';
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
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

    // Check terms acceptance
    if (!termsAccepted) {
      setServerError('Please accept the terms and conditions');
      return;
    }

    setIsLoading(true);

    try {
      // Call signup through auth context
      await signup(formData.email, formData.password, formData.name);

      // Store success message in sessionStorage to display on signin page
      sessionStorage.setItem('signupSuccess', 'Account created successfully! Please sign in.');

      // Redirect to signin page
      router.push('/auth/signin');
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
  function handleChange(field: keyof typeof formData, value: string) {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Server Error */}
      {serverError && (
        <div className="p-4 text-sm text-red-800 bg-red-100 rounded-md border border-red-200">
          {serverError}
        </div>
      )}

      {/* Name Field */}
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
          Full Name
        </label>
        <input
          id="name"
          type="text"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          className={`w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 transition-colors ${
            errors.name
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="John Doe"
          disabled={isLoading}
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name}</p>
        )}
        <p className="mt-1 text-xs text-gray-500">
          {formData.name.length}/100 characters
        </p>
      </div>

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
          placeholder="Min 8 characters, 1 uppercase, 1 number"
          disabled={isLoading}
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password}</p>
        )}

        {/* Password Strength Indicator */}
        {formData.password && (
          <div className="mt-2">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-600">Password strength:</span>
              <span className="text-xs font-medium text-gray-900">{passwordStrength.feedback}</span>
            </div>
            <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${passwordStrength.color}`}
                style={{ width: `${(passwordStrength.score / 4) * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Confirm Password Field */}
      <div>
        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
          Confirm Password
        </label>
        <input
          id="confirmPassword"
          type="password"
          value={formData.confirmPassword}
          onChange={(e) => handleChange('confirmPassword', e.target.value)}
          className={`w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 transition-colors ${
            errors.confirmPassword
              ? 'border-red-500 focus:ring-red-500'
              : 'border-gray-300 focus:ring-blue-500'
          }`}
          placeholder="Re-enter your password"
          disabled={isLoading}
        />
        {errors.confirmPassword && (
          <p className="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
        )}
      </div>

      {/* Terms Acceptance */}
      <div className="flex items-start">
        <input
          id="terms"
          type="checkbox"
          checked={termsAccepted}
          onChange={(e) => setTermsAccepted(e.target.checked)}
          className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          disabled={isLoading}
        />
        <label htmlFor="terms" className="ml-2 text-sm text-gray-700">
          I accept the{' '}
          <Link href="/terms" className="text-blue-600 hover:underline">
            terms and conditions
          </Link>
        </label>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Creating account...' : 'Create Account'}
      </button>

      {/* Signin Link */}
      <p className="text-center text-sm text-gray-600">
        Already have an account?{' '}
        <Link href="/auth/signin" className="text-blue-600 hover:underline font-medium">
          Sign in
        </Link>
      </p>
    </form>
  );
}
