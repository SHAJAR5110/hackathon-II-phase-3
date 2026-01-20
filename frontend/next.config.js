/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Image configuration (if using Next.js Image component)
  images: {
    domains: [],
    formats: ['image/avif', 'image/webp'],
  },

  // TypeScript strict mode
  typescript: {
    ignoreBuildErrors: false,
  },

  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://abbasshajar-todo-backend.hf.space/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig
