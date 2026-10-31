import { ConflictException, NotFoundException } from '@nestjs/common';
import { Test } from '@nestjs/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { DatabaseService } from '../database/database.service.js';
import { SitesService } from './sites.service.js';

describe('SitesService', () => {
  let service: SitesService;

  const repository = {
    findOneBy: vi.fn(),
    create: vi.fn(),
    save: vi.fn(),
  };

  beforeEach(async () => {
    vi.resetAllMocks();

    const moduleRef = await Test.createTestingModule({
      providers: [
        SitesService,
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

    service = moduleRef.get(SitesService);
  });

  it('trả 404 khi Site không tồn tại', async () => {
    repository.findOneBy.mockResolvedValue(null);

    await expect(
      service.findOne('00000000-0000-4000-8000-000000000001'),
    ).rejects.toBeInstanceOf(NotFoundException);
  });

  it('trả 409 khi database báo mã Site trùng', async () => {
const input = {
  code: 'SITE-TEST',
  name: 'Test Site',
};

    repository.create.mockReturnValue(input);
    repository.save.mockRejectedValue(
      Object.assign(new Error('Duplicate Site'), {
        code: '23505',
      }),
    );

    await expect(
      service.create(input),
    ).rejects.toBeInstanceOf(ConflictException);
  });

  it('không biến lỗi database khác thành lỗi trùng mã', async () => {
const input = {
  code: 'SITE-TEST',
  name: 'Test Site',
};

    const databaseError = new Error('Database unavailable');

    repository.create.mockReturnValue(input);
    repository.save.mockRejectedValue(databaseError);

    await expect(
      service.create(input),
    ).rejects.toBe(databaseError);
  });
});