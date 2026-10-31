import { NestFactory } from '@nestjs/core';
import { AppModule, ObserveInstrument, observeEnabled } from './app.module.js';
import { configureApplication } from './config/application.js';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger'; // Thêm import này

async function bootstrap() {
  const app = await NestFactory.create(
    AppModule,
    observeEnabled ? { instrument: ObserveInstrument } : {},
  );

  // Cấu hình ứng dụng chung của nhóm
  configureApplication(app);

  // === THÊM CẤU HÌNH SWAGGER UI ĐỂ ĐÁP ỨNG YÊU CẦU TASK 30 ===
  const config = new DocumentBuilder()
    .setTitle('AR-IMMS API Documentation')
    .setDescription('Tài liệu hệ thống Backend AR-IMMS (Task 30 - JWT Auth)')
    .setVersion('1.0')
    .addBearerAuth() // Hỗ trợ test token trên giao diện Swagger
    .build();

  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup('api', app, document); // Truy cập tài liệu tại: http://localhost:3000/api
  // ========================================================

  app.enableShutdownHooks();
  
  const port = Number(process.env.PORT ?? 3000);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error('PORT must be an integer between 1 and 65535');
  }
  
  await app.listen(port);
}
bootstrap();