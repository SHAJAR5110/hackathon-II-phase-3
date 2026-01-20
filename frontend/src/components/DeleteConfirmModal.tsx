'use client';

import { AlertTriangle } from 'lucide-react';
import { useEffect } from 'react';

interface DeleteConfirmModalProps {
  taskTitle: string;
  onConfirm: () => void;
  onCancel: () => void;
  isDeleting: boolean;
}

export default function DeleteConfirmModal({
  taskTitle,
  onConfirm,
  onCancel,
  isDeleting,
}: DeleteConfirmModalProps) {
  // Prevent background scroll when modal is open
  useEffect(() => {
    document.body.classList.add('modal-open');
    return () => {
      document.body.classList.remove('modal-open');
    };
  }, []);

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !isDeleting) {
        onCancel();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isDeleting, onCancel]);

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 animate-fadeIn"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isDeleting) {
          onCancel();
        }
      }}
    >
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 animate-slideUp">
        {/* Icon */}
        <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full">
          <AlertTriangle className="w-6 h-6 text-red-600" />
        </div>

        {/* Title */}
        <h2 className="text-xl font-semibold text-gray-900 text-center mb-2">Delete Task?</h2>

        {/* Message */}
        <p className="text-gray-600 text-center mb-6">
          Are you sure you want to delete{' '}
          <span className="font-medium text-gray-900">&ldquo;{taskTitle}&rdquo;</span>? This action
          cannot be undone.
        </p>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={isDeleting}
            className="btn flex-1"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isDeleting}
            className="btn bg-red-600 hover:bg-red-700 text-white flex-1"
          >
            {isDeleting ? (
              <>
                <span className="spinner mr-2"></span>
                Deleting...
              </>
            ) : (
              'Delete'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
