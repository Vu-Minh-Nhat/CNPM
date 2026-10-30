import 'dotenv/config';
import { Module } from '@nestjs/common';
import { APP_GUARD } from '@nestjs/core';
import { createObserveModule } from '@nestjs/observe';
import { AppController } from './app.controller.js';
import { AppService } from './app.service.js';
import { AssetsModule } from './assets/assets.module.js'; // [RBAC]
import { AuthModule } from './auth/auth.module.js'; // [RBAC]
import { JwtAuthGuard } from './auth/jwt-auth.guard.js'; // [RBAC]
import { RolesGuard } from './auth/roles.guard.js'; // [RBAC]
import { HealthModule } from './health/health.module.js';
import { UsersModule } from './users/users.module.js'; // [RBAC]
import { DatabaseModule } from './database/database.module.js';

export const { ObserveModule, ObserveInstrument } = createObserveModule();
export const observeEnabled = Boolean(
  process.env.OBSERVE_APP_KEY && process.env.OBSERVE_APP_SECRET,
);

@Module({
  imports: [
    DatabaseModule,
    ...(observeEnabled
      ? [
          ObserveModule.forRoot({
            appKey: process.env.OBSERVE_APP_KEY!,
            appSecret: process.env.OBSERVE_APP_SECRET!,
            serviceId: 'backend',
          }),
        ]
      : []),
    HealthModule,
    AuthModule, // [RBAC]
    UsersModule, // [RBAC]
    AssetsModule, // [RBAC]
  ],
  controllers: [AppController],
  providers: [
    AppService,

    { provide: APP_GUARD, useClass: JwtAuthGuard },
    { provide: APP_GUARD, useClass: RolesGuard },
  ],
})
export class AppModule {}
