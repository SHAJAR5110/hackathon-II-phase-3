"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  ReactNode,
} from "react";
import { setAuthCookie, clearAuthCookie } from "@/lib/auth-cookies";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined,
);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is already authenticated on mount
  useEffect(() => {
    let isMounted = true;

    const checkAuth = async () => {
      try {
        // Try to get token from localStorage first
        let token = localStorage.getItem("auth-token");

        // If not in localStorage, try to get from cookie (restore session)
        if (!token) {
          // Parse cookie from document.cookie
          const name = "auth-token=";
          const decodedCookie = decodeURIComponent(document.cookie);
          const cookieArray = decodedCookie.split(";");

          for (let cookie of cookieArray) {
            cookie = cookie.trim();
            if (cookie.startsWith(name)) {
              token = cookie.substring(name.length);
              // Restore token to localStorage
              if (token && isMounted) {
                localStorage.setItem("auth-token", token);
              }
              break;
            }
          }
        }

        if (token && isMounted) {
          // Try to fetch user data to verify token is valid
          const response = await fetch(`${API_URL}/api/users/me`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          if (response.ok && isMounted) {
            const userData = await response.json();
            setUser(userData);
          } else if (isMounted) {
            // Token is invalid, clear it
            localStorage.removeItem("auth-token");
            clearAuthCookie();
          }
        }
      } catch (error) {
        console.error("Failed to check auth status:", error);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    checkAuth();

    // Cleanup to prevent state updates on unmounted component
    return () => {
      isMounted = false;
    };
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/signin`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
      }

      const data = await response.json();
      const token = data.access_token || data.token;

      // Store token in both localStorage and cookie
      // localStorage: for client-side persistence
      // cookie: for middleware authentication checks (Vercel compatibility)
      localStorage.setItem("auth-token", token);
      setAuthCookie(token);

      // Set and save user data
      if (data.user) {
        setUser(data.user);
        localStorage.setItem("user", JSON.stringify(data.user));
      }
    } catch (error) {
      // Clear both localStorage and cookie on error
      localStorage.removeItem("auth-token");
      clearAuthCookie();
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      const token = localStorage.getItem("auth-token");
      if (token) {
        await fetch(`${API_URL}/api/auth/logout`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      }
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Clear both localStorage and cookie
      localStorage.removeItem("auth-token");
      localStorage.removeItem("user");
      clearAuthCookie();
      setUser(null);
    }
  }, []);

  const signup = useCallback(
    async (email: string, password: string, name: string) => {
      try {
        const response = await fetch(`${API_URL}/api/auth/signup`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, password, name }),
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || "Signup failed");
        }

        // Signup successful, no need to set user here
        // User will need to login next
      } catch (error) {
        throw error;
      }
    },
    [],
  );

  const value: AuthContextType = {
    user,
    isAuthenticated: user !== null,
    isLoading,
    login,
    logout,
    signup,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

/**
 * Hook to use auth context
 * Must be called within AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
