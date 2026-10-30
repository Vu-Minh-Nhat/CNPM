import type { INestApplication } from '@nestjs/common';
import { Test } from '@nestjs/testing';
import request from 'supertest';
import { AppModule } from '../src/app.module.js';
import { DatabaseService } from '../src/database/database.service.js';

describe('AI-29 PostgreSQL và RBAC (e2e)', () => {
  let app: INestApplication;
  let password: string;

  const token: Record<string, string> = {};

  async function login(email: string) {
    const response = await request(app.getHttpServer())
      .post('/auth/login')
      .send({ email, password })
      .expect(200);

    expect(typeof response.body.accessToken).toBe('string');

    return response.body.accessToken as string;
  }

  function call(
    method: 'get' | 'post' | 'put' | 'delete',
    url: string,
    accessToken?: string,
  ) {
    const operation = request(app.getHttpServer())[method](url);

    return accessToken
      ? operation.set('Authorization', `Bearer ${accessToken}`)
      : operation;
  }

  beforeAll(async () => {
    if (!process.env.DATABASE_URL || !process.env.SEED_PASSWORD) {
      throw new Error(
        'Cần DATABASE_URL và SEED_PASSWORD trong backend/.env',
      );
    }

    password = process.env.SEED_PASSWORD;

    const moduleRef = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleRef.createNestApplication();
    await app.init();

    const database = app.get(DatabaseService);
    expect(database.source?.isInitialized).toBe(true);

    token.admin = await login('admin@arimms.local');
    token.operator = await login('operator@arimms.local');
    token.technician = await login('tech@arimms.local');
  }, 30000);

  afterAll(async () => {
    await app?.close();
  });

  it('TC01: Không có token → 401', async () => {
    await call('get', '/assets').expect(401);
  });

  it('TC02: Token sai → 401', async () => {
    await call('get', '/assets', 'abc.def.ghi').expect(401);
  });

  it('TC03: Sai mật khẩu → 401', async () => {
    await request(app.getHttpServer())
      .post('/auth/login')
      .send({
        email: 'admin@arimms.local',
        password: 'sai',
      })
      .expect(401);
  });

  it('TC04: Administrator đọc tài khoản từ database', async () => {
    const response = await call(
      'get',
      '/users',
      token.admin,
    ).expect(200);

    expect(Array.isArray(response.body)).toBe(true);

    expect(response.body).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          email: 'admin@arimms.local',
          role: 'Administrator',
        }),
        expect.objectContaining({
          email: 'operator@arimms.local',
          role: 'Operator',
        }),
        expect.objectContaining({
          email: 'tech@arimms.local',
          role: 'Technician',
        }),
      ]),
    );

    for (const user of response.body) {
      expect(user).not.toHaveProperty('passwordHash');
      expect(user).not.toHaveProperty('password_hash');
    }
  });

  it('TC05: Operator không được xem tài khoản → 403', async () => {
    await call('get', '/users', token.operator).expect(403);
  });

  it('TC06: Technician không được xem tài khoản → 403', async () => {
    await call('get', '/users', token.technician).expect(403);
  });

  it('TC07: Technician được xem tài sản → 200', async () => {
    await call('get', '/assets', token.technician).expect(200);
  });

  it('TC08: Technician không được tạo tài sản → 403', async () => {
    await call('post', '/assets', token.technician).expect(403);
  });

  it('TC09: Operator có quyền nhưng chức năng tạo chưa triển khai → 501', async () => {
    await call('post', '/assets', token.operator).expect(501);
  });

  it('TC10: Operator không được xóa tài sản → 403', async () => {
    await call(
      'delete',
      '/assets/test-id',
      token.operator,
    ).expect(403);
  });

  it('TC11: Administrator có quyền nhưng chức năng xóa chưa triển khai → 501', async () => {
    await call(
      'delete',
      '/assets/test-id',
      token.admin,
    ).expect(501);
  });

  it('TC12: Đọc đầy đủ quan hệ tài sản từ PostgreSQL', async () => {
    const response = await call(
      'get',
      '/assets',
      token.admin,
    ).expect(200);

    expect(Array.isArray(response.body)).toBe(true);

    const node = response.body.find(
      (item: { code: string }) => item.code === 'DEMO-NODE-01',
    );

    expect(node).toBeDefined();
    expect(node.rack.code).toBe('RACK-01');
    expect(node.rack.room.code).toBe('ROOM-01');
    expect(node.rack.room.site.code).toBe('DEMO-SITE');

    expect(node.workloads).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          code: 'DEMO-WORKLOAD-01',
          nodeId: node.id,
        }),
      ]),
    );
  });
});