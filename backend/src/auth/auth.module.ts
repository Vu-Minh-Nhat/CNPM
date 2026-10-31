import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { PassportModule } from '@nestjs/passport';
import { ConfigModule, ConfigService } from '@nestjs/config';
import type { StringValue } from 'ms';
import { UsersModule } from '../users/users.module.js';
import { AuthController } from './auth.controller.js';
import { AuthService } from './auth.service.js';
import { JwtStrategy } from './jwt.strategy.js';
import { getJwtSecret } from './jwt.config.js';


@Module({
  imports: [
    UsersModule,

    PassportModule.register({
      defaultStrategy: 'jwt',
    }),

    JwtModule.registerAsync({
      imports: [ConfigModule],

      useFactory: (configService: ConfigService) => ({
        secret: getJwtSecret(),

        signOptions: {
          expiresIn: (
            configService.get<string>('JWT_EXPIRES_IN') || '1d'
          ) as StringValue,
        },
      }),

      inject: [ConfigService],
    }),
  ],

  controllers: [AuthController],

  providers: [
    AuthService,
    JwtStrategy,
  ],

  exports: [
    JwtModule,
    AuthService,
    PassportModule,
  ],
})
export class AuthModule {}