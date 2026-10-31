import {
  BadRequestException,
  ConflictException,
  NotFoundException,
} from '@nestjs/common';
import { Test } from '@nestjs/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DatabaseService } from '../database/database.service.js';
import { RacksService } from './racks.service.js';

describe('RacksService', () => {
  let service: RacksService;

  const rackId = '00000000-0000-4000-8000-000000000001';

  const input = {
    roomId: '00000000-0000-4000-8000-000000000002',
    code: 'RACK-TEST',
    name: 'Test Rack',
    capacityU: 42,
  };

  const repository = {
    findOne: vi.fn(),
    create: vi.fn(),
    save: vi.fn(),
    remove: vi.fn(),
  };

  beforeEach(async () => {
    vi.resetAllMocks();
    repository.create.mockReturnValue({ ...input });

    const moduleRef = await Test.createTestingModule({
      providers: [
        RacksService,
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

    service = moduleRef.get(RacksService);
  });

  it('trả 404 khi Rack không tồn tại', async () => {
    repository.findOne.mockResolvedValue(null);

    await expect(
      service.findOne(rackId),
    ).rejects.toBeInstanceOf(NotFoundException);
  });

  it('trả 409 khi mã Rack bị trùng trong Room', async () => {
    repository.save.mockRejectedValue(
      Object.assign(new Error('Duplicate Rack'), {
        code: '23505',
      }),
    );

    await expect(
      service.create(input),
    ).rejects.toBeInstanceOf(ConflictException);
  });

  it('trả 400 khi Room được tham chiếu không tồn tại', async () => {
    repository.save.mockRejectedValue(
      Object.assign(new Error('Room does not exist'), {
        code: '23503',
      }),
    );

    await expect(
      service.create(input),
    ).rejects.toBeInstanceOf(BadRequestException);
  });

  it('trả 409 khi xóa Rack đang chứa Server', async () => {
    repository.findOne.mockResolvedValue({
      id: rackId,
      ...input,
    });

    repository.remove.mockRejectedValue(
      Object.assign(new Error('Rack still contains servers'), {
        code: '23503',
      }),
    );

    await expect(
      service.remove(rackId),
    ).rejects.toBeInstanceOf(ConflictException);
  });
});