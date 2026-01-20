'use client';

import { useState, FormEvent, ChangeEvent } from 'react';
import { TaskCreateRequest } from '@/lib/api';

interface TaskFormProps {
  onSubmit: (data: TaskCreateRequest) => Promise<void>;
  isLoading?: boolean;
  initialValues?: TaskCreateRequest;
  onCancel?: () => void;
  submitLabel?: string;
}

export default function TaskForm({
  onSubmit,
  isLoading = false,
  initialValues,
  onCancel,
  submitLabel = 'Create Task',
}: TaskFormProps) {
  const [title, setTitle] = useState(initialValues?.title || '');
  const [description, setDescription] = useState(initialValues?.description || '');
  const [errors, setErrors] = useState<{ title?: string; description?: string; form?: string }>({});

  const MAX_TITLE_LENGTH = 200;
  const MAX_DESCRIPTION_LENGTH = 1000;

  // Real-time validation
  const validateTitle = (value: string): string | undefined => {
    const trimmed = value.trim();
    if (!trimmed) {
      return 'Title is required';
    }
    if (trimmed.length > MAX_TITLE_LENGTH) {
      return `Title must be ${MAX_TITLE_LENGTH} characters or less`;
    }
    return undefined;
  };

  const validateDescription = (value: string): string | undefined => {
    if (value.length > MAX_DESCRIPTION_LENGTH) {
      return `Description must be ${MAX_DESCRIPTION_LENGTH} characters or less`;
    }
    return undefined;
  };

  const handleTitleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setTitle(value);
    const error = validateTitle(value);
    setErrors((prev) => ({ ...prev, title: error }));
  };

  const handleDescriptionChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setDescription(value);
    const error = validateDescription(value);
    setErrors((prev) => ({ ...prev, description: error }));
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrors({});

    // Validate before submission
    const titleError = validateTitle(title);
    const descriptionError = validateDescription(description);

    if (titleError || descriptionError) {
      setErrors({
        title: titleError,
        description: descriptionError,
      });
      return;
    }

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
      });

      // Reset form after successful submission (if not editing)
      if (!initialValues) {
        setTitle('');
        setDescription('');
        setErrors({});
      }
    } catch (error: unknown) {
      setErrors({
        form:
          error instanceof Error ? error.message : 'Failed to save task. Please try again.',
      });
    }
  };

  const titleCharsRemaining = MAX_TITLE_LENGTH - title.length;
  const descriptionCharsRemaining = MAX_DESCRIPTION_LENGTH - description.length;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Form-level error */}
      {errors.form && (
        <div className="alert alert-error">
          <p className="text-sm text-red-600">{errors.form}</p>
        </div>
      )}

      {/* Title Input */}
      <div>
        <label htmlFor="task-title" className="block text-sm font-medium text-gray-700 mb-1">
          Title <span className="text-red-500">*</span>
        </label>
        <input
          id="task-title"
          type="text"
          value={title}
          onChange={handleTitleChange}
          placeholder="What needs to be done?"
          disabled={isLoading}
          className={`input w-full ${errors.title ? 'border-red-500 focus:ring-red-500' : ''}`}
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? 'title-error' : undefined}
        />
        <div className="flex justify-between items-center mt-1">
          {errors.title && (
            <p id="title-error" className="text-sm text-red-600">
              {errors.title}
            </p>
          )}
          <p
            className={`text-xs ml-auto ${
              titleCharsRemaining < 20 ? 'text-red-600' : 'text-gray-500'
            }`}
          >
            {title.length} / {MAX_TITLE_LENGTH}
          </p>
        </div>
      </div>

      {/* Description Input */}
      <div>
        <label htmlFor="task-description" className="block text-sm font-medium text-gray-700 mb-1">
          Description <span className="text-gray-400 text-xs">(optional)</span>
        </label>
        <textarea
          id="task-description"
          value={description}
          onChange={handleDescriptionChange}
          placeholder="Add more details..."
          rows={4}
          disabled={isLoading}
          className={`input w-full resize-none ${
            errors.description ? 'border-red-500 focus:ring-red-500' : ''
          }`}
          aria-invalid={!!errors.description}
          aria-describedby={errors.description ? 'description-error' : undefined}
        />
        <div className="flex justify-between items-center mt-1">
          {errors.description && (
            <p id="description-error" className="text-sm text-red-600">
              {errors.description}
            </p>
          )}
          <p
            className={`text-xs ml-auto ${
              descriptionCharsRemaining < 50 ? 'text-red-600' : 'text-gray-500'
            }`}
          >
            {description.length} / {MAX_DESCRIPTION_LENGTH}
          </p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isLoading || !title.trim() || !!errors.title || !!errors.description}
          className="btn btn-primary flex-1"
        >
          {isLoading ? (
            <>
              <span className="spinner mr-2"></span>
              Saving...
            </>
          ) : (
            submitLabel
          )}
        </button>
        {onCancel && (
          <button type="button" onClick={onCancel} disabled={isLoading} className="btn px-6">
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
