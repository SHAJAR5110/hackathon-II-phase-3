/**
 * Root Layout
 * Phase II - Todo Full-Stack Web Application
 *
 * Root layout component that wraps all pages.
 * Includes global styles, fonts, and metadata.
 * Wrapped with AuthProvider for authentication state management.
 */

import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import Providers from './providers';

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'Todo App - Phase II',
  description: 'Full-stack todo application with Next.js and FastAPI',
  icons: {
    icon: '/favicon.svg',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen bg-gray-50">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
