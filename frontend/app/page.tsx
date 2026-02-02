import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Link from 'next/link';
import { CheckCircle, Zap, Clock, Users, ArrowRight, Star } from 'lucide-react';

export default function Home() {
  const features = [
    {
      icon: CheckCircle,
      title: 'Simple Task Management',
      description: 'Organize your tasks with an intuitive, distraction-free interface.',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Built for speed. Works smoothly across all your devices.',
    },
    {
      icon: Users,
      title: 'Collaborate Seamlessly',
      description: 'Share tasks and work together with your team in real-time.',
    },
    {
      icon: Clock,
      title: 'Time Tracking',
      description: 'Track how you spend your time and boost productivity.',
    },
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'Product Manager',
      content: 'TaskMaster transformed how our team manages projects. We\'ve cut planning time in half.',
      avatar: '👩‍💼',
    },
    {
      name: 'Marcus Rodriguez',
      role: 'Freelancer',
      content: 'Finally, a tool that\'s simple enough to get started immediately, but powerful enough to grow with me.',
      avatar: '👨‍💻',
    },
    {
      name: 'Emma Thompson',
      role: 'Design Lead',
      content: 'The minimalist design is exactly what I needed. No clutter, just pure productivity.',
      avatar: '👩‍🎨',
    },
  ];

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <Header />

      {/* Hero Section */}
      <section className="flex-1 px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
            Stay focused on{' '}
            <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-clip-text text-transparent">
              what matters
            </span>
          </h1>

          <p className="text-xl sm:text-2xl text-gray-600 mb-12 leading-relaxed max-w-2xl mx-auto font-light">
            The simplest way to organize your tasks and achieve your goals. No distractions. Just results.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 sm:mb-24">
            <Link
              href="/auth/signup"
              className="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition duration-200 gap-2 group"
            >
              Get Started Free
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
            </Link>
            <Link
              href="/auth/signin"
              className="inline-flex items-center justify-center px-8 py-4 border-2 border-gray-300 text-gray-900 font-semibold rounded-lg hover:border-gray-400 hover:bg-gray-50 transition duration-200"
            >
              Sign In
            </Link>
          </div>

          {/* Minimal Stats */}
          <div className="flex justify-center gap-12 sm:gap-16 pt-8 border-t border-gray-200">
            <div className="text-center">
              <p className="text-2xl sm:text-3xl font-bold text-gray-900">50K+</p>
              <p className="text-sm text-gray-600 mt-1">Active Users</p>
            </div>
            <div className="text-center">
              <p className="text-2xl sm:text-3xl font-bold text-gray-900">2M+</p>
              <p className="text-sm text-gray-600 mt-1">Tasks Completed</p>
            </div>
            <div className="text-center">
              <p className="text-2xl sm:text-3xl font-bold text-gray-900">99.9%</p>
              <p className="text-sm text-gray-600 mt-1">Uptime</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="px-4 sm:px-6 lg:px-8 py-24 sm:py-32 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 lg:gap-16">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="flex gap-6">
                  <div className="flex-shrink-0">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br from-blue-100 to-purple-100">
                      <Icon className="w-6 h-6 text-blue-600" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials Section - About */}
      <section id="about" className="px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Loved by thousands of users
            </h2>
            <p className="text-gray-600 text-lg">
              See what people are saying about TaskMaster
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-lg p-8 hover:shadow-lg transition duration-200"
              >
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className="w-4 h-4 fill-yellow-400 text-yellow-400"
                    />
                  ))}
                </div>
                <p className="text-gray-700 mb-6 leading-relaxed">
                  "{testimonial.content}"
                </p>
                <div className="flex items-center gap-3">
                  <div className="text-2xl">{testimonial.avatar}</div>
                  <div>
                    <p className="font-semibold text-gray-900">
                      {testimonial.name}
                    </p>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
            Ready to get organized?
          </h2>
          <p className="text-lg text-gray-600 mb-8">
            Start your free account today. No credit card required.
          </p>
          <Link
            href="/auth/signup"
            className="inline-flex items-center justify-center px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:shadow-lg transition duration-200 gap-2 group"
          >
            Get Started Free
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
}
