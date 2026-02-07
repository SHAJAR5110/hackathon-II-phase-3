/**
 * Centralized API Client
 * Phase II - Todo Full-Stack Web Application
 *
 * Provides type-safe HTTP methods with automatic JWT token attachment.
 * All API calls should go through this client for consistency.
 */

// ============================================================================
// Type Definitions
// ============================================================================

export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface TaskCreateRequest {
  title: string;
  description?: string | null;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string | null;
}

export interface TaskListResponse {
  tasks: Task[];
}

export interface ErrorResponse {
  detail: string;
  status: number;
}

// ============================================================================
// API Client Configuration
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Get JWT token from localStorage or cookies.
 * In production, this should retrieve the token from HTTP-only cookies.
 *
 * @returns JWT token string or null if not authenticated
 */
function getAuthToken(): string | null {
  if (typeof window === "undefined") {
    // Server-side rendering: can't access localStorage
    return null;
  }

  // Try localStorage first (development)
  const token = localStorage.getItem("auth-token");
  if (token) {
    return token;
  }

  // TODO: In production, retrieve from HTTP-only cookies via Better Auth
  return null;
}

/**
 * Custom error class for API errors.
 * Includes HTTP status code and error message from server.
 */
export class APIError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "APIError";
    this.status = status;
  }
}

// ============================================================================
// HTTP Request Helper
// ============================================================================

/**
 * Internal fetch wrapper with error handling and token attachment.
 *
 * @param endpoint - API endpoint (e.g., "/api/tasks")
 * @param options - Fetch options (method, body, headers)
 * @returns Parsed JSON response
 * @throws APIError if request fails
 */
async function request<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  // Attach JWT token to Authorization header
  const token = getAuthToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (options.headers instanceof Headers) {
    options.headers.forEach((value, key) => {
      headers[key] = value;
    });
  } else if (options.headers) {
    Object.assign(headers, options.headers);
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);

    // Handle non-JSON responses (e.g., 204 No Content)
    if (response.status === 204) {
      return undefined as T;
    }

    // Parse JSON response
    const data = await response.json();

    // Handle HTTP errors
    if (!response.ok) {
      const errorData = data as ErrorResponse;
      throw new APIError(
        errorData.detail || "An error occurred",
        response.status,
      );
    }

    return data as T;
  } catch (error) {
    // Re-throw APIError as-is
    if (error instanceof APIError) {
      throw error;
    }

    // Wrap network errors
    if (error instanceof TypeError) {
      throw new APIError("Network error: Unable to connect to server", 0);
    }

    // Wrap other errors
    throw new APIError(
      error instanceof Error ? error.message : "Unknown error occurred",
      500,
    );
  }
}

// ============================================================================
// API Methods
// ============================================================================

export const api = {
  /**
   * GET request
   *
   * @param endpoint - API endpoint
   * @returns Parsed response data
   */
  get: <T>(endpoint: string): Promise<T> => {
    return request<T>(endpoint, {
      method: "GET",
    });
  },

  /**
   * POST request
   *
   * @param endpoint - API endpoint
   * @param body - Request body (will be JSON-stringified)
   * @returns Parsed response data
   */
  post: <T>(endpoint: string, body?: unknown): Promise<T> => {
    return request<T>(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * PUT request
   *
   * @param endpoint - API endpoint
   * @param body - Request body (will be JSON-stringified)
   * @returns Parsed response data
   */
  put: <T>(endpoint: string, body?: unknown): Promise<T> => {
    return request<T>(endpoint, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * PATCH request
   *
   * @param endpoint - API endpoint
   * @param body - Request body (will be JSON-stringified)
   * @returns Parsed response data
   */
  patch: <T>(endpoint: string, body?: unknown): Promise<T> => {
    return request<T>(endpoint, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  /**
   * DELETE request
   *
   * @param endpoint - API endpoint
   * @returns Parsed response data (or undefined for 204)
   */
  delete: <T>(endpoint: string): Promise<T> => {
    return request<T>(endpoint, {
      method: "DELETE",
    });
  },

  // ========================================================================
  // Task-Specific Convenience Methods
  // ========================================================================

  /**
   * Get all tasks for the authenticated user.
   *
   * @param filters - Optional filters (status, sort)
   * @returns List of tasks
   */
  async getTasks(filters?: {
    status?: "all" | "pending" | "completed";
    sort?: "created" | "title" | "updated";
  }): Promise<{ tasks: Task[] }> {
    const params = new URLSearchParams();
    if (filters?.status) params.append("status", filters.status);
    if (filters?.sort) params.append("sort", filters.sort);

    const query = params.toString();
    const endpoint = query ? `/api/tasks?${query}` : "/api/tasks";

    // Backend returns { tasks: [...] } (TaskListResponse)
    const response = await api.get<TaskListResponse>(endpoint);
    return { tasks: Array.isArray(response.tasks) ? response.tasks : [] };
  },

  /**
   * Get a single task by ID.
   *
   * @param id - Task ID
   * @returns Task details
   */
  async getTask(id: number): Promise<Task> {
    return api.get<Task>(`/api/tasks/${id}`);
  },

  /**
   * Create a new task.
   *
   * @param data - Task creation data (title, description)
   * @returns Created task
   */
  async createTask(data: TaskCreateRequest): Promise<Task> {
    return api.post<Task>("/api/tasks", data);
  },

  /**
   * Update an existing task.
   *
   * @param id - Task ID
   * @param data - Task update data (title, description)
   * @returns Updated task
   */
  async updateTask(id: number, data: TaskUpdateRequest): Promise<Task> {
    return api.put<Task>(`/api/tasks/${id}`, data);
  },

  /**
   * Delete a task.
   *
   * @param id - Task ID
   */
  async deleteTask(id: number): Promise<void> {
    return api.delete<void>(`/api/tasks/${id}`);
  },

  /**
   * Toggle task completion status.
   *
   * @param id - Task ID
   * @returns Updated task
   */
  async toggleTaskComplete(id: number): Promise<Task> {
    return api.patch<Task>(`/api/tasks/${id}/complete`, {});
  },
};

// ============================================================================
// Task-Specific API Methods
// ============================================================================

export const taskAPI = {
  /**
   * Get all tasks for the authenticated user.
   *
   * @param filters - Optional filters (status, sort)
   * @returns List of tasks
   */
  async getTasks(filters?: {
    status?: "all" | "pending" | "completed";
    sort?: "created" | "title" | "updated";
  }): Promise<Task[]> {
    const params = new URLSearchParams();
    if (filters?.status) params.append("status", filters.status);
    if (filters?.sort) params.append("sort", filters.sort);

    const query = params.toString();
    const endpoint = query ? `/api/tasks?${query}` : "/api/tasks";

    const response = await api.get<TaskListResponse>(endpoint);
    return response.tasks;
  },

  /**
   * Get a single task by ID.
   *
   * @param id - Task ID
   * @returns Task details
   */
  async getTask(id: number): Promise<Task> {
    return api.get<Task>(`/api/tasks/${id}`);
  },

  /**
   * Create a new task.
   *
   * @param data - Task creation data (title, description)
   * @returns Created task
   */
  async createTask(data: TaskCreateRequest): Promise<Task> {
    return api.post<Task>("/api/tasks", data);
  },

  /**
   * Update an existing task.
   *
   * @param id - Task ID
   * @param data - Task update data (title, description)
   * @returns Updated task
   */
  async updateTask(id: number, data: TaskUpdateRequest): Promise<Task> {
    return api.put<Task>(`/api/tasks/${id}`, data);
  },

  /**
   * Delete a task.
   *
   * @param id - Task ID
   */
  async deleteTask(id: number): Promise<void> {
    return api.delete<void>(`/api/tasks/${id}`);
  },

  /**
   * Toggle task completion status.
   *
   * @param id - Task ID
   * @returns Updated task
   */
  async toggleComplete(id: number): Promise<Task> {
    return api.patch<Task>(`/api/tasks/${id}/complete`, {});
  },
};
