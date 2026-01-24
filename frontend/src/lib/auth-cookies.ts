/**
 * Authentication Cookie Utilities
 *
 * Handles setting and clearing auth tokens in cookies
 * for better security and server-side middleware compatibility
 */

const AUTH_COOKIE_NAME = "auth-token";
const COOKIE_MAX_AGE = 60 * 60 * 24; // 24 hours in seconds

/**
 * Set auth token in cookie
 * @param token - JWT token to store
 */
export function setAuthCookie(token: string): void {
  if (typeof document === "undefined") {
    // Can't set cookies on server-side
    return;
  }

  // Set cookie with secure flags
  document.cookie = `${AUTH_COOKIE_NAME}=${token}; max-age=${COOKIE_MAX_AGE}; path=/; SameSite=Strict`;
}

/**
 * Clear auth token from cookie
 */
export function clearAuthCookie(): void {
  if (typeof document === "undefined") {
    // Can't clear cookies on server-side
    return;
  }

  // Clear cookie by setting max-age to 0
  document.cookie = `${AUTH_COOKIE_NAME}=; max-age=0; path=/`;
}

/**
 * Get auth token from cookie
 * @returns JWT token or null if not found
 */
export function getAuthCookie(): string | null {
  if (typeof document === "undefined") {
    // Can't read cookies on server-side
    return null;
  }

  const name = `${AUTH_COOKIE_NAME}=`;
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(";");

  for (let cookie of cookieArray) {
    cookie = cookie.trim();
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length, cookie.length);
    }
  }

  return null;
}
