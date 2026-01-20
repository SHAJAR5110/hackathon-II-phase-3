import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Link from 'next/link';
import { CheckCircle, Zap, Shield, Users, Clock, BarChart3 } from 'lucide-react';

export default function LandingPage() {
  const features = [
    {
      icon: CheckCircle,
      title: 'Easy Task Management',
      description: 'Create, organize, and manage your tasks with an intuitive interface.',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Built with modern technologies for blazing fast performance.',
    },
    {
      icon: Shield,
      title: 'Secure & Private',
      description: 'Your data is encrypted and protected with enterprise-grade security.',
    },
    {
      icon: Users,
      title: 'Collaborate',
      description: 'Share tasks and collaborate with team members in real-time.',
    },
    {
      icon: Clock,
      title: 'Time Tracking',
      description: 'Track time spent on tasks and improve productivity.',
    },
    {
      icon: BarChart3,
      title: 'Analytics',
      description: 'Get insights into your productivity with detailed analytics and reports.',
    },
  ];

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <Header />

      {/* Hero Section */}
      <section className="flex-1 bg-gradient-to-br from-blue-50 via-white to-blue-50 px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="max-w-7xl mx-auto text-center">
          <div className="mb-8 inline-block">
            <span className="inline-flex items-center rounded-full bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-600">
              ✨ Get organized today
            </span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Master Your{' '}
            <span className="bg-gradient-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">
              Tasks & Goals
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto mb-10 leading-relaxed">
            Boost your productivity with TaskMaster. Create, organize, and track your tasks
            effortlessly. Stay focused, accomplish more, and achieve your goals with our
            powerful and intuitive task management platform.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link
              href="/auth/signup"
              className="inline-flex items-center justify-center px-8 py-4 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition transform hover:scale-105 active:scale-95"
              aria-label="Get started with TaskMaster"
            >
              Get Started Free
            </Link>
            <Link
              href="/auth/signin"
              className="inline-flex items-center justify-center px-8 py-4 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-gray-400 hover:bg-gray-50 transition"
            >
              Sign In
            </Link>
          </div>

          {/* Hero Image */}
          <div className="relative rounded-2xl overflow-hidden shadow-2xl">
            <div className="bg-gradient-to-br from-gray-200 to-gray-300 h-96 sm:h-96 md:h-[500px] flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl mb-4">📊</div>
                <p className="text-gray-600 font-medium">Dashboard Preview</p>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <p className="text-3xl font-bold text-blue-600 mb-2">10K+</p>
              <p className="text-gray-600">Active Users</p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <p className="text-3xl font-bold text-blue-600 mb-2">100K+</p>
              <p className="text-gray-600">Tasks Completed</p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
              <p className="text-3xl font-bold text-blue-600 mb-2">99.9%</p>
              <p className="text-gray-600">Uptime</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="px-4 sm:px-6 lg:px-8 py-20 sm:py-32 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Powerful Features
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Everything you need to stay organized and productive in one place.
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div
                  key={index}
                  className="bg-white rounded-lg p-8 shadow-sm border border-gray-200 hover:shadow-lg hover:border-blue-200 transition transform hover:scale-105"
                >
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
                    <Icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            {/* Left Side - Content */}
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
                Why Choose TaskMaster?
              </h2>
              <p className="text-lg text-gray-600 mb-4 leading-relaxed">
                TaskMaster is built on modern technology with security and usability as
                top priorities. Our platform is designed to help individuals and teams
                manage their work more effectively.
              </p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                  <span className="text-gray-700">Free to start, upgrade anytime</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                  <span className="text-gray-700">24/7 customer support</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                  <span className="text-gray-700">Enterprise-grade security</span>
                </li>
                <li className="flex items-center gap-3">
                  <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0" />
                  <span className="text-gray-700">Sync across all devices</span>
                </li>
              </ul>
              <Link
                href="/auth/signup"
                className="inline-block px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
              >
                Start Free Trial
              </Link>
            </div>

            {/* Right Side - Image */}
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-100 to-blue-50 rounded-2xl h-96 flex items-center justify-center shadow-lg">
                <div className="text-center">
                  <div className="text-6xl mb-4">🎯</div>
                  <p className="text-gray-600 font-medium">Achieve Your Goals</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 sm:px-6 lg:px-8 py-20 sm:py-32 bg-gradient-to-r from-blue-600 to-blue-700">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">
            Ready to get started?
          </h2>
          <p className="text-lg mb-8 text-blue-100 max-w-2xl mx-auto">
            Join thousands of users who are already using TaskMaster to organize their
            work and boost their productivity.
          </p>
          <Link
            href="/auth/signup"
            className="inline-block px-8 py-4 bg-white text-blue-600 font-semibold rounded-lg hover:bg-blue-50 transition transform hover:scale-105 active:scale-95"
          >
            Get Started Free - No Credit Card Required
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
}
