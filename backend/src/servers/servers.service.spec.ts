import {
  BadRequestException,
  ConflictException,
  NotFoundException,
} from '@nestjs/common';
import { Test } from '@nestjs/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DatabaseService } from '../database/database.service.js';
import { ServersService } from './servers.service.js';

describe('ServersService', () => {
  let service: ServersService;

  const serverId = '00000000-0000-4000-8000-000000000001';

  const input = {
    rackId: '00000000-0000-4000-8000-000000000002',
    code: 'SERVER-TEST',
    name: 'Test Server',
    serialNumber: 'SN-TEST-001',
  };

  const repository = {
    findOne: vi.fn(),
    create: vi.fn(),
    save: vi.fn(),
  };

  beforeEach(async () => {
    vi.resetAllMocks();
    repository.create.mockReturnValue({ ...input });

    const moduleRef = await Test.createTestingModule({
      providers: [
        ServersService,
        {
          provide: DatabaseService,
          useValue: {
            source: {
              isInitialized: true,
              getRepository: vi.fn().mockReturnValue(repository),
            },
          },
        },
      ],
    }).compile();

    service = moduleRef.get(ServersService);
  });

  it('trả 404 khi Server không tồn tại', async () => {
    repository.findOne.mockResolvedValue(null);

    await expect(
      service.findOne(serverId),
    ).rejects.toBeInstanceOf(NotFoundException);
  });

  it('trả 409 khi database báo dữ liệu Server trùng', async () => {
    repository.save.mockRejectedValue(
      Object.assign(new Error('Duplicate Server'), {
        code: '23505',
      }),
    );

    await expect(
      service.create(input),
    ).rejects.toBeInstanceOf(ConflictException);
  });

  it('trả 400 khi Rack được tham chiếu không tồn tại', async () => {
    repository.save.mockRejectedValue(
      Object.assign(new Error('Rack does not exist'), {
        code: '23503',
      }),
    );

    await expect(
      service.create(input),
    ).rejects.toBeInstanceOf(BadRequestException);
  });

  it('không biến lỗi database khác thành lỗi trùng dữ liệu', async () => {
    const databaseError = new Error('Database unavailable');

    repository.save.mockRejectedValue(databaseError);

    await expect(
      service.create(input),
    ).rejects.toBe(databaseError);
  });
});