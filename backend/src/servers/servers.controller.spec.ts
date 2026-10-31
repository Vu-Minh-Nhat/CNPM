import { Test } from '@nestjs/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ServersController } from './servers.controller.js';
import { ServersService } from './servers.service.js';

describe('ServersController', () => {
  let controller: ServersController;

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [ServersController],
      providers: [
        {
          provide: ServersService,
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

    controller = moduleRef.get(ServersController);
  });

  it('khởi tạo được controller với service giả lập', () => {
    expect(controller).toBeDefined();
  });
});