import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import * as schema from './schema';
import dotenv from 'dotenv';

dotenv.config();

// Next.js will automatically load environment variables from .env files
// No need for manual dotenv.config() in a Next.js environment

const isDev = process.env.NODE_ENV !== 'production';

// Use environment-specific URLs, with fallback only for development
const connectionString = isDev 
  ? (process.env.DATABASE_URL_DEV || process.env.DATABASE_URL)
  : process.env.DATABASE_URL_PROD; // Production requires explicit prod URL

  console.log('connectionString', connectionString);
  console.log('isDev', isDev);
  console.log('process.env.DATABASE_URL_DEV', process.env.DATABASE_URL_DEV);
  console.log('process.env.DATABASE_URL_PROD', process.env.DATABASE_URL_PROD);
  console.log('process.env.DATABASE_URL', process.env.DATABASE_URL);
  console.log('process.env.NODE_ENV', process.env.NODE_ENV);

if (!connectionString) {
  const availableVars = [
    process.env.DATABASE_URL_DEV && 'DATABASE_URL_DEV',
    process.env.DATABASE_URL_PROD && 'DATABASE_URL_PROD', 
    process.env.DATABASE_URL && 'DATABASE_URL'
  ].filter(Boolean);
  
  throw new Error(
    `No database URL found. Looking for: ${isDev ? 'DATABASE_URL_DEV' : 'DATABASE_URL_PROD'} or DATABASE_URL.\n` +
    `Available environment variables: ${availableVars.length > 0 ? availableVars.join(', ') : 'none'}\n` +
    `Current NODE_ENV: ${process.env.NODE_ENV || 'undefined'}`
  );
}

const sql = neon(connectionString);
export const db = drizzle(sql, { schema });

export type DbClient = typeof db;