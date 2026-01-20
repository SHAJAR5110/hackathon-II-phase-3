/**
 * Authentication Layout Component
 * Phase II - Todo Full-Stack Web Application
 *
 * Layout wrapper for signup and signin pages.
 * Provides centered card design with title and subtitle.
 */

interface AuthLayoutProps {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
}

export default function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Todo App
          </h1>
          <h2 className="text-2xl font-semibold text-gray-800">
            {title}
          </h2>
          {subtitle && (
            <p className="mt-2 text-sm text-gray-600">
              {subtitle}
            </p>
          )}
        </div>

        {/* Card */}
        <div className="bg-white rounded-lg shadow-md p-8">
          {children}
        </div>
      </div>
    </div>
  );
}
