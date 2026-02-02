'use client';

import { useState, useEffect, useCallback } from 'react';
import { Task, TaskCreateRequest, api } from '@/lib/api';
import TaskForm from '@/components/TaskForm';
import TaskList from '@/components/TaskList';
import Header from '@/components/Header';
import ProtectedRoute from '@/components/ProtectedRoute';
import ChatBotPopup from '@/components/ChatBotPopup';
import { AlertCircle } from 'lucide-react';

function DashboardContent() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Fetch all tasks on mount
  const fetchTasks = useCallback(async () => {
    try {
      setError(null);
      const data = await api.getTasks();
      setTasks(data.tasks);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to load tasks');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  // Create new task
  const handleCreateTask = async (data: TaskCreateRequest) => {
    try {
      const newTask = await api.createTask(data);
      setTasks((prev) => [newTask, ...prev]); // Add to beginning
      showSuccess('Task created successfully!');

      // Refresh tasks after 1 second to ensure sync with backend
      setTimeout(() => {
        fetchTasks();
      }, 1000);
    } catch (err: unknown) {
      throw new Error(
        err instanceof Error ? err.message : 'Failed to create task'
      );
    }
  };

  // Update existing task
  const handleUpdateTask = async (updatedTask: Task) => {
    try {
      const updated = await api.updateTask(updatedTask.id, {
        title: updatedTask.title,
        description: updatedTask.description,
      });
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
      showSuccess('Task updated successfully!');

      // Refresh tasks after 1 second to ensure sync with backend
      setTimeout(() => {
        fetchTasks();
      }, 1000);
    } catch (err: unknown) {
      throw new Error(
        err instanceof Error ? err.message : 'Failed to update task'
      );
    }
  };

  // Toggle task completion
  const handleToggleComplete = async (taskId: number) => {
    try {
      const updated = await api.toggleTaskComplete(taskId);
      setTasks((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to toggle task');
      }
    }
  };

  // Delete task
  const handleDeleteTask = async (taskId: number) => {
    try {
      await api.deleteTask(taskId);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      showSuccess('Task deleted successfully!');

      // Refresh tasks after 1 second to ensure sync with backend
      setTimeout(() => {
        fetchTasks();
      }, 1000);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to delete task');
      }
    }
  };

  // Show success message and auto-dismiss
  const showSuccess = (message: string) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <ChatBotPopup onTasksModified={fetchTasks} />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success Message */}
        {successMessage && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800 animate-slideDown">
            <p className="text-sm font-medium">{successMessage}</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-xs underline mt-1 hover:no-underline"
              >
                Dismiss
              </button>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Task Form */}
          <div className="lg:col-span-1">
            <div className="card sticky top-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Create New Task</h2>
              <TaskForm onSubmit={handleCreateTask} />
            </div>
          </div>

          {/* Right Column: Task List */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                My Tasks{' '}
                <span className="text-lg font-normal text-gray-500">({tasks.length})</span>
              </h2>
              <button
                onClick={fetchTasks}
                disabled={loading}
                className="text-sm text-primary-600 hover:text-primary-700 font-medium"
              >
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>

            <TaskList
              tasks={tasks}
              onTaskUpdate={handleUpdateTask}
              onTaskDelete={handleDeleteTask}
              onToggleComplete={handleToggleComplete}
              isLoading={loading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}
