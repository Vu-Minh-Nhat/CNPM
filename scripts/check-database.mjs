import 'dotenv/config';
import pg from 'pg';

if (!process.env.DATABASE_URL) {
  console.error(
    'DATABASE_URL is required. Configure it in .env before running db:check.',
  );
  process.exitCode = 1;
} else {
  const pool = new pg.Pool({
    connectionString: process.env.DATABASE_URL,
    connectionTimeoutMillis: 5000,
    query_timeout: 5000,
  });

  try {
    await pool.query('SELECT 1');
    console.log('PostgreSQL connection successful.');
  } catch (error) {
    // Do not print the connection string, which may contain credentials.
    console.error(
      `PostgreSQL connection failed (${error.code ?? 'connection error'}).`,
    );
    process.exitCode = 1;
  } finally {
    await pool.end();
  }
}
