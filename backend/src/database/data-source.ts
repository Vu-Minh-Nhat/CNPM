import 'reflect-metadata';
import 'dotenv/config';
import { DataSource } from 'typeorm';
import { entities } from './entities.js';
import { InitialDatabase1793318400000 } from './migrations/1793318400000-InitialDatabase.js';

export function createDataSource(url = process.env.DATABASE_URL): DataSource {
  if (!url?.trim()) throw new Error('DATABASE_URL is required. Configure backend/.env.');
  const parsed = new URL(url);
  if (!['postgres:', 'postgresql:'].includes(parsed.protocol)) {
    throw new Error('DATABASE_URL must use postgres:// or postgresql://.');
  }
  return new DataSource({
    type: 'postgres', url, entities,
    migrations: [InitialDatabase1793318400000],
    migrationsTableName: 'schema_migrations',
    synchronize: false, migrationsRun: false,
    migrationsTransactionMode: 'all',
    logging: false, connectTimeoutMS: 5000,
    extra: { max: 10, statement_timeout: 10000 },
  });
}
