import { neon } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-http';
import * as schema from './schema';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables from the root .env file
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });

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