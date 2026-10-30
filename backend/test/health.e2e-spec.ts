import type { INestApplication } from '@nestjs/common';
import { Test } from '@nestjs/testing';
import request from 'supertest';
import { AppModule } from '../src/app.module.js';
import { configureApplication } from '../src/config/application.js';

describe('AI-27 health and CORS (e2e)', () => {
  let app: INestApplication;
  const frontendOrigin = 'http://localhost:3001';

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();
    app = moduleRef.createNestApplication();
    configureApplication(app, [frontendOrigin]);
    await app.init();
  });

  afterAll(async () => {
    await app?.close();
  });

  it('serves liveness without a JWT while global guards are enabled', async () => {
    const response = await request(app.getHttpServer())
      .get('/health')
      .expect(200);
    expect(response.body).toMatchObject({
      status: 'ok',
      service: 'ar-imms-backend',
    });
    expect(Number.isNaN(Date.parse(response.body.timestamp))).toBe(false);
    expect(response.body.uptimeSeconds).toBeGreaterThanOrEqual(0);
  });

  it('allows the configured browser origin and Authorization preflight', async () => {
    const response = await request(app.getHttpServer())
      .options('/assets')
      .set('Origin', frontendOrigin)
      .set('Access-Control-Request-Method', 'GET')
      .set('Access-Control-Request-Headers', 'authorization')
      .expect(204);
    expect(response.headers['access-control-allow-origin']).toBe(
      frontendOrigin,
    );
    expect(
      response.headers['access-control-allow-headers'].toLowerCase(),
    ).toContain('authorization');
  });

  it('does not grant browser access to an unlisted origin', async () => {
    const response = await request(app.getHttpServer())
      .get('/health')
      .set('Origin', 'https://unlisted.example')
      .expect(200);
    expect(response.headers['access-control-allow-origin']).toBeUndefined();
  });

  it('keeps asset endpoints protected without a JWT', async () => {
    await request(app.getHttpServer()).get('/assets').expect(401);
  });
});
