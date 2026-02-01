/**
 * Root Layout
 * Phase II - Todo Full-Stack Web Application
 *
 * Root layout component that wraps all pages.
 * Includes global styles, fonts, and metadata.
 * Wrapped with AuthProvider for authentication state management.
 */

import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "@/styles/globals.css";
import Providers from "./providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "TaskMaster - Todo App",
  description: "Full-stack todo application with Next.js and FastAPI",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        {/* ChatKit CDN - Loaded by client-side script in Providers */}
      </head>
      <body className="min-h-screen bg-gray-50">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
