import { config } from 'dotenv';
import * as path from 'path';

// Load environment variables before importing db-connection
config({ path: path.join(__dirname, '..', '.env') });

import { migrate } from 'drizzle-orm/neon-http/migrator';
import { db } from './db-connection';

async function runMigration() {
  console.log('Running migrations...');
  
  try {
    await migrate(db, { migrationsFolder: './drizzle' });
    console.log('Migrations completed successfully');
  } catch (error) {
    console.error('Migration failed:', error);
    process.exit(1);
  }
}

runMigration();