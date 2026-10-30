import { Injectable, Logger, type OnModuleInit, type OnModuleDestroy } from '@nestjs/common';
import type { DataSource } from 'typeorm';
import { createDataSource } from './data-source.js';

@Injectable()
export class DatabaseService implements OnModuleInit, OnModuleDestroy {
  source?: DataSource;

  async onModuleInit(): Promise<void> {
    if (!process.env.DATABASE_URL?.trim()) {
      if (process.env.NODE_ENV === 'production') throw new Error('DATABASE_URL is required in production.');
      new Logger(DatabaseService.name).warn('DATABASE_URL not configured: using the development-only in-memory demo.');
      return;
    }
    this.source = createDataSource();
    await this.source.initialize();
    if (await this.source.showMigrations()) {
      await this.source.destroy();
      throw new Error('Pending database migrations. Run npm run migration:run before starting the backend.');
    }
  }

  async onModuleDestroy(): Promise<void> {
    if (this.source?.isInitialized) await this.source.destroy();
  }
}
