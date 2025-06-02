import { defineConfig } from 'drizzle-kit';
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables from the root .env file
dotenv.config({ path: path.resolve(__dirname, '../../.env') });

const isDev = process.env.NODE_ENV !== 'production';
const connectionString = isDev 
  ? process.env.DATABASE_URL_DEV 
  : process.env.DATABASE_URL_PROD;

if (!connectionString) {
  throw new Error(`${isDev ? 'DATABASE_URL_DEV' : 'DATABASE_URL_PROD'} is not defined in environment variables`);
}

export default defineConfig({
  schema: './src/schema/index.ts',
  out: './drizzle',
  dialect: 'postgresql',
  dbCredentials: {
    url: connectionString,
  },
  verbose: true,
  strict: true,
});