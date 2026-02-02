import Link from 'next/link';
import { Github, Linkedin, Twitter } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Section */}
          <div className="md:col-span-1">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-700 rounded-lg flex items-center justify-center text-white font-bold">
                ✓
              </div>
              <span className="font-bold text-white text-lg">TaskMaster</span>
            </Link>
            <p className="text-sm text-gray-400">
              Organize your tasks efficiently with our powerful todo management application.
            </p>
          </div>

          {/* Product Links */}
          <div>
            <h3 className="font-semibold text-white mb-4">Product</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/#features" className="text-sm hover:text-white transition">
                  Features
                </Link>
              </li>
              <li>
                <Link href="/auth/signin" className="text-sm hover:text-white transition">
                  Pricing
                </Link>
              </li>
              <li>
                <a href="#security" className="text-sm hover:text-white transition">
                  Security
                </a>
              </li>
              <li>
                <a href="#updates" className="text-sm hover:text-white transition">
                  Updates
                </a>
              </li>
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="font-semibold text-white mb-4">Company</h3>
            <ul className="space-y-2">
              <li>
                <a href="#about" className="text-sm hover:text-white transition">
                  About Us
                </a>
              </li>
              <li>
                <a href="#blog" className="text-sm hover:text-white transition">
                  Blog
                </a>
              </li>
              <li>
                <a href="#careers" className="text-sm hover:text-white transition">
                  Careers
                </a>
              </li>
              <li>
                <a href="#contact" className="text-sm hover:text-white transition">
                  Contact
                </a>
              </li>
            </ul>
          </div>

          {/* Legal & Support */}
          <div>
            <h3 className="font-semibold text-white mb-4">Legal</h3>
            <ul className="space-y-2">
              <li>
                <a href="#privacy" className="text-sm hover:text-white transition">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#terms" className="text-sm hover:text-white transition">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="#cookies" className="text-sm hover:text-white transition">
                  Cookie Policy
                </a>
              </li>
              <li>
                <a href="#support" className="text-sm hover:text-white transition">
                  Support
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-800 py-8">
          {/* Social Links */}
          <div className="flex justify-center md:justify-start gap-6 mb-6">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition"
              aria-label="LinkedIn"
            >
              <Linkedin className="w-5 h-5" />
            </a>
            <a
              href="https://twitter.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition"
              aria-label="Twitter"
            >
              <Twitter className="w-5 h-5" />
            </a>
          </div>

          {/* Bottom Bar */}
          <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-400">
            <p>
              &copy; {currentYear} TaskMaster. All rights reserved.
            </p>
            <p>
              Made with ❤️ by the TaskMaster Team
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
