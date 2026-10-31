
import 'dotenv/config';
import { hash } from 'bcryptjs';
import { createDataSource } from '../dist/database/data-source.js';
import { seedDevelopment } from '../dist/database/seed.js';
import { AccountSchema } from '../dist/database/entities.js';

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
      console.log(
        await source.showMigrations()
          ? 'Pending migrations.'
          : 'All migrations applied.',
      );
      break;

    case 'revert':
      await source.undoLastMigration();
      console.log('Reverted last migration.');
      break;

    case 'seed':
      if (await source.showMigrations()) {
        throw new Error('Run migrations before seeding.');
      }

      await seedDevelopment(source);
      console.log('Development seed completed. Existing records were preserved.');
      break;

    case 'reset-admin': {
      const password = process.env.SEED_PASSWORD;

      if (
        !password ||
        password.length < 12 ||
        Buffer.byteLength(password, 'utf8') > 72
      ) {
        throw new Error(
          'SEED_PASSWORD must be 12–72 UTF-8 bytes.',
        );
      }

      const repository = source.getRepository(AccountSchema);

      const admin = await repository.findOneBy({
        email: 'admin@arimms.local',
      });

      if (!admin) {
        throw new Error('Admin account does not exist. Run the seed first.');
      }

      await repository.update(
        { id: admin.id },
        { passwordHash: await hash(password, 10) },
      );

      console.log('Admin password updated successfully.');
      break;
    }

    default:
      throw new Error(
        'Expected run, status, revert, seed or reset-admin.',
      );
  }
} catch (error) {
  console.error(
    `Database command failed (${error.code ?? error.message ?? 'unknown error'}).`,
  );
  process.exitCode = 1;
} finally {
  if (source.isInitialized) {
    await source.destroy();
  }
}
