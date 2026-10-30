import 'dotenv/config';
import { createDataSource } from '../dist/database/data-source.js';
import { seedDevelopment } from '../dist/database/seed.js';

const source = createDataSource();
try {
  await source.initialize();
  switch (process.argv[2]) {
    case 'run': {
      const migrations = await source.runMigrations();
      console.log(`Applied ${migrations.length} migration(s).`);
      break;
    }
    case 'status':
      console.log(await source.showMigrations() ? 'Pending migrations.' : 'All migrations applied.');
      break;
    case 'revert':
      await source.undoLastMigration();
      console.log('Reverted last migration.');
      break;
    case 'seed':
      if (await source.showMigrations()) throw new Error('Run migrations before seeding.');
      await seedDevelopment(source);
      console.log('Development seed completed. Existing records were preserved.');
      break;
    default: throw new Error('Expected run, status, revert or seed.');
  }
} catch (error) {
  console.error(`Database command failed (${error.code ?? 'configuration or migration error'}). Verify connection, migration state and seed configuration.`);
  process.exitCode = 1;
} finally {
  if (source.isInitialized) await source.destroy();
}
