'use client';

import { useState } from 'react';
import { Task, TaskUpdateRequest } from '@/lib/api';
import { Pencil, Trash2, Check } from 'lucide-react';
import TaskForm from './TaskForm';
import DeleteConfirmModal from './DeleteConfirmModal';

interface TaskItemProps {
  task: Task;
  onUpdate?: (task: Task) => void;
  onDelete?: (taskId: number) => void;
  onToggleComplete?: (taskId: number, completed: boolean) => void;
}

export default function TaskItem({ task, onUpdate, onDelete, onToggleComplete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const handleEdit = async (data: TaskUpdateRequest) => {
    if (!onUpdate) return;

    setIsUpdating(true);
    try {
      await onUpdate({ ...task, ...data } as Task);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update task:', error);
      throw error; // Let TaskForm handle the error display
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async () => {
    if (!onDelete) return;

    setIsDeleting(true);
    try {
      await onDelete(task.id);
      setShowDeleteModal(false);
    } catch (error) {
      console.error('Failed to delete task:', error);
      setIsDeleting(false);
      // Error will be handled by parent component
    }
  };

  const handleToggleComplete = async () => {
    if (!onToggleComplete) return;

    setIsToggling(true);
    try {
      await onToggleComplete(task.id, !task.completed);
    } catch (error) {
      console.error('Failed to toggle task:', error);
    } finally {
      setIsToggling(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Edit mode
  if (isEditing) {
    return (
      <div className="card bg-blue-50 border-blue-200">
        <TaskForm
          onSubmit={handleEdit}
          initialValues={{ title: task.title, description: task.description || '' }}
          isLoading={isUpdating}
          onCancel={() => setIsEditing(false)}
          submitLabel="Save Changes"
        />
      </div>
    );
  }

  // Display mode
  return (
    <>
      <div
        className={`card transition-all duration-200 ${
          task.completed ? 'bg-gray-50 border-gray-200' : 'bg-white hover:shadow-md'
        }`}
      >
        <div className="flex items-start gap-3">
          {/* Checkbox */}
          <div className="flex-shrink-0 pt-1">
            <button
              onClick={handleToggleComplete}
              disabled={isToggling}
              className={`w-6 h-6 rounded border-2 flex items-center justify-center transition-all ${
                task.completed
                  ? 'bg-green-500 border-green-500 text-white'
                  : 'border-gray-300 hover:border-green-500'
              } ${isToggling ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              aria-label={task.completed ? 'Mark as pending' : 'Mark as complete'}
            >
              {task.completed && <Check className="w-4 h-4" />}
              {isToggling && <span className="spinner text-xs"></span>}
            </button>
          </div>

          {/* Task Content */}
          <div className="flex-1 min-w-0">
            <h3
              className={`font-medium text-gray-900 mb-1 ${
                task.completed ? 'line-through text-gray-500' : ''
              }`}
            >
              {task.title}
            </h3>
            {task.description && (
              <p className={`text-sm text-gray-600 mb-2 ${task.completed ? 'line-through' : ''}`}>
                {task.description}
              </p>
            )}
            <div className="flex items-center gap-4 text-xs text-gray-500">
              <span>Created {formatDate(task.created_at)}</span>
              {task.updated_at !== task.created_at && (
                <span>Updated {formatDate(task.updated_at)}</span>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex-shrink-0 flex gap-2">
            <button
              onClick={() => setIsEditing(true)}
              disabled={isToggling || isDeleting}
              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded transition-colors"
              aria-label="Edit task"
            >
              <Pencil className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowDeleteModal(true)}
              disabled={isToggling || isDeleting}
              className="p-2 text-gray-500 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
              aria-label="Delete task"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <DeleteConfirmModal
          taskTitle={task.title}
          onConfirm={handleDelete}
          onCancel={() => setShowDeleteModal(false)}
          isDeleting={isDeleting}
        />
      )}
    </>
  );
}
