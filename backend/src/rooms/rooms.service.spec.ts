import {
  BadRequestException,
  ConflictException,
  NotFoundException,
} from '@nestjs/common';
import { Test } from '@nestjs/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DatabaseService } from '../database/database.service.js';
import { RoomsService } from './rooms.service.js';

describe('RoomsService', () => {
  let service: RoomsService;

  const roomId = '00000000-0000-4000-8000-000000000001';

  const input = {
    siteId: '00000000-0000-4000-8000-000000000002',
    code: 'ROOM-TEST',
    name: 'Test Room',
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
        RoomsService,
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

    service = moduleRef.get(RoomsService);
  });

  it('trả 404 khi Room không tồn tại', async () => {
    repository.findOne.mockResolvedValue(null);

    await expect(
      service.findOne(roomId),
    ).rejects.toBeInstanceOf(NotFoundException);
  });

  it('trả 409 khi mã Room bị trùng trong Site', async () => {
    repository.save.mockRejectedValue(
      Object.assign(new Error('Duplicate Room'), {
        code: '23505',
      }),
    );

    await expect(
      service.create(input),
    ).rejects.toBeInstanceOf(ConflictException);
  });

  it('trả 400 khi Site được tham chiếu không tồn tại', async () => {
    repository.save.mockRejectedValue(
      Object.assign(new Error('Site does not exist'), {
        code: '23503',
      }),
    );

    await expect(
      service.create(input),
    ).rejects.toBeInstanceOf(BadRequestException);
  });

  it('trả 409 khi xóa Room đang chứa Rack', async () => {
    repository.findOne.mockResolvedValue({
      id: roomId,
      ...input,
    });

    repository.remove.mockRejectedValue(
      Object.assign(new Error('Room still contains racks'), {
        code: '23503',
      }),
    );

    await expect(
      service.remove(roomId),
    ).rejects.toBeInstanceOf(ConflictException);
  });
});