import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import * as schema from './schema';

// Next.js will automatically load environment variables from .env files
// No need for manual dotenv.config() in a Next.js environment

const isDev = process.env.NODE_ENV !== 'production';
const connectionString = isDev 
  ? process.env.DATABASE_URL_DEV 
  : process.env.DATABASE_URL_PROD;

if (!connectionString) {
  throw new Error(`${isDev ? 'DATABASE_URL_DEV' : 'DATABASE_URL_PROD'} environment variable is not set`);
}

const sql = neon(connectionString);
export const db = drizzle(sql, { schema });

export type DbClient = typeof db;