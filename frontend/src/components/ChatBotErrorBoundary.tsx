'use client';

import React, { ReactNode, ErrorInfo } from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary for ChatBot Component
 *
 * Catches rendering errors in ChatKit and provides graceful fallback UI.
 * Features:
 * - Error logging for debugging
 * - User-friendly error messages
 * - Retry functionality
 * - Prevents white screen of death
 */
export class ChatBotErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error: error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error details for debugging
    console.error('ChatBot Error:', error);
    console.error('Error Info:', errorInfo);

    // In production, you might want to send this to an error tracking service
    // e.g., Sentry, LogRocket, etc.
    if (process.env.NODE_ENV === 'production') {
      // Send to error tracking service
      // captureException(error, errorInfo);
    }
  }

  handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="flex flex-col items-center justify-center p-6 bg-gradient-to-br from-red-50 to-orange-50 rounded-lg border border-red-200">
            <div className="mb-4 p-3 bg-red-100 rounded-full">
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>

            <h3 className="text-lg font-semibold text-red-900 mb-2">
              Chat temporarily unavailable
            </h3>

            <p className="text-sm text-red-700 text-center mb-4">
              We encountered an error loading the chat interface. This has
              been logged and our team will investigate.
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="w-full mb-4 bg-white p-3 rounded border border-red-300">
                <summary className="text-xs text-red-600 cursor-pointer font-mono">
                  Error details (dev only)
                </summary>
                <pre className="text-xs text-red-700 mt-2 overflow-auto max-h-32 font-mono">
                  {this.state.error.toString()}
                </pre>
              </details>
            )}

            <button
              onClick={this.handleRetry}
              className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
            >
              <RotateCcw className="w-4 h-4" />
              Try again
            </button>

            <p className="text-xs text-red-600 mt-4">
              If this continues, please refresh the page or contact support.
            </p>
          </div>
        )
      );
    }

    return this.props.children;
  }
}

/**
 * Functional wrapper for using error boundary with hooks
 */
export default ChatBotErrorBoundary;
