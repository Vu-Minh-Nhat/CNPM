
import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
  InternalServerErrorException,
} from '@nestjs/common';
import { randomUUID } from 'node:crypto';

import { DatabaseService } from '../database/database.service.js';
import { RackSchema } from '../database/entities.js';
import { CreateRackDto } from './dto/create-rack.dto.js';
import { UpdateRackDto } from './dto/update-rack.dto.js';

@Injectable()
export class RacksService {
  constructor(private readonly database: DatabaseService) {}

  private get repository() {
    if (!this.database.source?.isInitialized) {
      throw new InternalServerErrorException('Database chưa được kết nối');
    }
    return this.database.source.getRepository(RackSchema);
  }

  async create(createRackDto: CreateRackDto) {
    try {
      const rack = this.repository.create({
        id: randomUUID(),
        ...createRackDto,
      });
      return await this.repository.save(rack);
    } catch (error) {
      const code = (error as { code?: string }).code;

      if (code === '23505') {
        throw new ConflictException('Mã Rack đã tồn tại');
      }
      if (code === '23503') {
        throw new BadRequestException('Room không tồn tại');
      }
      throw error;
    }
  }

  async findAll() {
    return this.repository.find({
      relations: { room: true },
      order: { name: 'ASC' },
    });
  }

  async findOne(id: string) {
    const rack = await this.repository.findOne({
      where: { id },
      relations: { room: true, nodes: true },
    });

    if (!rack) {
      throw new NotFoundException(`Không tìm thấy Rack: ${id}`);
    }

    return rack;
  }

async update(id: string, updateRackDto: UpdateRackDto) {
  if (
    !updateRackDto ||
    Object.keys(updateRackDto).length === 0
  ) {
    throw new BadRequestException(
      'Cần cung cấp ít nhất một trường để cập nhật',
    );
  }

  await this.findOne(id);

  try {
    await this.repository.update(
      { id },
      updateRackDto,
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
        'Mã Rack đã tồn tại trong Room',
      );
    }

    if (code === '23503') {
      throw new BadRequestException(
        'Room không tồn tại',
      );
    }

    if (
      code === '23502' ||
      code === '23514' ||
      code === '22001'
    ) {
      throw new BadRequestException(
        'Dữ liệu Rack không hợp lệ',
      );
    }

    throw error;
  }

  return this.findOne(id);
}

  async remove(id: string) {
    const rack = await this.findOne(id);

    try {
      await this.repository.remove(rack);
      return { message: 'Xóa Rack thành công' };
    } catch (error) {
      if ((error as { code?: string }).code === '23503') {
        throw new ConflictException('Không thể xóa Rack đang chứa Server');
      }
      throw error;
    }
  }
}
