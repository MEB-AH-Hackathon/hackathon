import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  distDir: '.next',
  env: {
    DATABASE_URL_DEV: process.env.DATABASE_URL_DEV,
    DATABASE_URL_PROD: process.env.DATABASE_URL_PROD,
  },
  // Add custom webpack config to log build details
  webpack: (config, { buildId, dev, isServer, defaultLoaders, nextRuntime, webpack }) => {
    console.log('=== Next.js Build Debug Info ===');
    console.log('Build ID:', buildId);
    console.log('Is Development:', dev);
    console.log('Is Server:', isServer);
    console.log('Next Runtime:', nextRuntime);
    console.log('Output Directory:', config.output?.path);
    console.log('Current Working Directory:', process.cwd());
    console.log('NODE_ENV:', process.env.NODE_ENV);
    console.log('VERCEL:', process.env.VERCEL);
    console.log('VERCEL_ENV:', process.env.VERCEL_ENV);
    console.log('DATABASE_URL_DEV:', process.env.DATABASE_URL_DEV ? '[SET]' : '[NOT SET]');
    console.log('================================');
    
    return config;
  },
};

export default nextConfig;
