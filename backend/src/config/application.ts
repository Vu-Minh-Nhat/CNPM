import type { INestApplication } from '@nestjs/common';

export function configureApplication(
  app: INestApplication,
  corsOrigins = (
    process.env.CORS_ORIGINS ?? 'http://localhost:3001,http://localhost:5173'
  )
    .split(',')
    .map((origin) => origin.trim())
    .filter(Boolean),
): void {
  app.enableCors({
    origin: corsOrigins,
    methods: ['GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  });
}
