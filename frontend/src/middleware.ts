/**
 * Next.js Middleware - Vercel Edge Compatible
 * Protects dashboard route with authentication
 *
 * CRITICAL: Matcher limited to /dashboard only to avoid:
 * - Static route conflicts
 * - Edge Runtime invocation failures
 * - Double authentication logic
 *
 * Client-side auth handles:
 * - SigninPage/SignupPage redirects
 * - Public route access
 * - Auth state management
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware - Protects /dashboard route
 * Checks for auth token and redirects to signin if missing
 */
export function middleware(request: NextRequest) {
  // Check for auth token in cookies
  const authToken = request.cookies.get('auth-token')?.value;

  // If no token, redirect to signin
  if (!authToken) {
    return NextResponse.redirect(new URL('/auth/signin', request.url));
  }

  // Token exists, persist in response headers
  const response = NextResponse.next();
  response.headers.set('x-auth-token', authToken);
  return response;
}

// Matcher configuration - ONLY for protected dashboard route
// This prevents Edge Runtime issues with static routes
export const config = {
  
  matcher: ['/dashboard/:path*'],
};
