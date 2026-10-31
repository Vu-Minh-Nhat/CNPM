import { Test } from '@nestjs/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { SitesController } from './sites.controller.js';
import { SitesService } from './sites.service.js';

describe('SitesController', () => {
  let controller: SitesController;

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [SitesController],
      providers: [
        {
          provide: SitesService,
          useValue: {
            create: vi.fn(),
            findAll: vi.fn(),
            findOne: vi.fn(),
            update: vi.fn(),
            remove: vi.fn(),
          },
        },
      ],
    }).compile();

    controller = moduleRef.get(SitesController);
  });

  it('khởi tạo được controller với service giả lập', () => {
    expect(controller).toBeDefined();
  });
});