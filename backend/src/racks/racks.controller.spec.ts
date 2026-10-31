import { Test } from '@nestjs/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RacksController } from './racks.controller.js';
import { RacksService } from './racks.service.js';

describe('RacksController', () => {
  let controller: RacksController;

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [RacksController],
      providers: [
        {
          provide: RacksService,
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

    controller = moduleRef.get(RacksController);
  });

  it('khởi tạo được controller với service giả lập', () => {
    expect(controller).toBeDefined();
  });
});