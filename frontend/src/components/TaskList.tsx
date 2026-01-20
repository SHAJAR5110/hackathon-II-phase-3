'use client';

import { Task } from '@/lib/api';
import TaskItem from './TaskItem';
import { CheckCircle2 } from 'lucide-react';

interface TaskListProps {
  tasks: Task[];
  onTaskUpdate?: (task: Task) => void;
  onTaskDelete?: (taskId: number) => void;
  onToggleComplete?: (taskId: number, completed: boolean) => void;
  isLoading?: boolean;
}

export default function TaskList({
  tasks,
  onTaskUpdate,
  onTaskDelete,
  onToggleComplete,
  isLoading = false,
}: TaskListProps) {
  // Empty state
  if (!isLoading && tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <CheckCircle2 className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-700 mb-2">No tasks yet</h3>
        <p className="text-gray-500">Create your first task to get started!</p>
      </div>
    );
  }

  // Loading state
  if (isLoading && tasks.length === 0) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={onTaskUpdate}
          onDelete={onTaskDelete}
          onToggleComplete={onToggleComplete}
        />
      ))}
    </div>
  );
}
