'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 font-bold text-xl text-gray-900 hover:text-blue-600 transition">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center text-white font-bold">
              ✓
            </div>
            <span className="hidden sm:inline">TaskMaster</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <Link href="/" className="text-gray-700 hover:text-blue-600 font-medium transition">
              Home
            </Link>
            <Link href="/#features" className="text-gray-700 hover:text-blue-600 font-medium transition">
              Features
            </Link>
            <Link href="/#about" className="text-gray-700 hover:text-blue-600 font-medium transition">
              About
            </Link>
          </div>

          {/* Right Side Actions */}
          <div className="hidden md:flex items-center gap-4">
            <Link
              href="/auth/signin"
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition"
            >
              Sign In
            </Link>
            <Link
              href="/auth/signup"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
            >
              Sign Up
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMenu}
            className="md:hidden p-2 text-gray-700 hover:bg-gray-100 rounded-lg transition"
            aria-label="Toggle navigation menu"
            aria-expanded={isMenuOpen}
            aria-controls="mobile-menu"
          >
            {isMenuOpen ? (
              <X className="w-6 h-6" />
            ) : (
              <Menu className="w-6 h-6" />
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div id="mobile-menu" className="md:hidden pb-4 border-t border-gray-200">
            <div className="flex flex-col gap-2 mt-4">
              <Link
                href="/"
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition"
              >
                Home
              </Link>
              <Link
                href="/#features"
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition"
              >
                Features
              </Link>
              <Link
                href="/#about"
                className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition"
              >
                About
              </Link>

              <div className="border-t border-gray-200 my-2 pt-2">
                <Link
                  href="/auth/signin"
                  className="block px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg font-medium transition"
                >
                  Sign In
                </Link>
                <Link
                  href="/auth/signup"
                  className="block px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
                >
                  Sign Up
                </Link>
              </div>
            </div>
          </div>
        )}
      </nav>
    </header>
  );
}
