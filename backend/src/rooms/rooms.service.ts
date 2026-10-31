
import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
  InternalServerErrorException,
} from '@nestjs/common';
import { randomUUID } from 'node:crypto';

import { DatabaseService } from '../database/database.service.js';
import { RoomSchema } from '../database/entities.js';
import { CreateRoomDto } from './dto/create-room.dto.js';
import { UpdateRoomDto } from './dto/update-room.dto.js';

@Injectable()
export class RoomsService {
  constructor(private readonly database: DatabaseService) {}

  private get repository() {
    if (!this.database.source?.isInitialized) {
      throw new InternalServerErrorException('Database chưa được kết nối');
    }
    return this.database.source.getRepository(RoomSchema);
  }

  async create(createRoomDto: CreateRoomDto) {
    try {
      const room = this.repository.create({
        id: randomUUID(),
        ...createRoomDto,
      });
      return await this.repository.save(room);
    } catch (error) {
      const code = (error as { code?: string }).code;

      if (code === '23505') {
        throw new ConflictException('Mã Room đã tồn tại');
      }
      if (code === '23503') {
        throw new BadRequestException('Site không tồn tại');
      }
      throw error;
    }
  }

  async findAll() {
    return this.repository.find({
      relations: { site: true },
      order: { name: 'ASC' },
    });
  }

  async findOne(id: string) {
    const room = await this.repository.findOne({
      where: { id },
      relations: { site: true, racks: true },
    });

    if (!room) {
      throw new NotFoundException(`Không tìm thấy Room: ${id}`);
    }

    return room;
  }

async update(id: string, updateRoomDto: UpdateRoomDto) {
  if (
    !updateRoomDto ||
    Object.keys(updateRoomDto).length === 0
  ) {
    throw new BadRequestException(
      'Cần cung cấp ít nhất một trường để cập nhật',
    );
  }

  await this.findOne(id);

  try {
    await this.repository.update(
      { id },
      updateRoomDto,
    );
  } catch (error) {
    const databaseError = error as {
      code?: string;
      driverError?: { code?: string };
    } | null;

    const code =
      databaseError?.driverError?.code ??
      databaseError?.code;

    if (code === '23505') {
      throw new ConflictException(
        'Mã Room đã tồn tại trong Site',
      );
    }

    if (code === '23503') {
      throw new BadRequestException(
        'Site không tồn tại',
      );
    }

    if (
      code === '23502' ||
      code === '23514' ||
      code === '22001'
    ) {
      throw new BadRequestException(
        'Dữ liệu Room không hợp lệ',
      );
    }

    throw error;
  }

  return this.findOne(id);
}

  async remove(id: string) {
    const room = await this.findOne(id);

    try {
      await this.repository.remove(room);
      return { message: 'Xóa Room thành công' };
    } catch (error) {
      if ((error as { code?: string }).code === '23503') {
        throw new ConflictException('Không thể xóa Room đang chứa Rack');
      }
      throw error;
    }
  }
}
