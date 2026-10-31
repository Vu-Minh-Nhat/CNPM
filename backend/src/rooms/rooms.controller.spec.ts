import { Test } from '@nestjs/testing';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { RoomsController } from './rooms.controller.js';
import { RoomsService } from './rooms.service.js';

describe('RoomsController', () => {
  let controller: RoomsController;

  beforeEach(async () => {
    const moduleRef = await Test.createTestingModule({
      controllers: [RoomsController],
      providers: [
        {
          provide: RoomsService,
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

    controller = moduleRef.get(RoomsController);
  });

  it('khởi tạo được controller với service giả lập', () => {
    expect(controller).toBeDefined();
  });
});