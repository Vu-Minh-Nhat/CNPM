import {
  BadRequestException,
  ConflictException,
  Inject,
  Injectable,
  NotFoundException,
  ServiceUnavailableException,
} from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import { DatabaseService } from '../database/database.service.js';
import { NodeSchema } from '../database/entities.js';
import { CreateServerDto } from './dto/create-server.dto.js';
import { UpdateServerDto } from './dto/update-server.dto.js';

@Injectable()
export class ServersService {
  constructor(
    @Inject(DatabaseService)
    private readonly database: DatabaseService,
  ) {}

  private get repository() {
    const source = this.database.source;

    if (!source?.isInitialized) {
      throw new ServiceUnavailableException(
        'Database chưa được kết nối',
      );
    }

    return source.getRepository(NodeSchema);
  }

  private databaseErrorCode(error: unknown): string | undefined {
    const databaseError = error as {
      code?: string;
      driverError?: { code?: string };
    } | null;

    return databaseError?.driverError?.code
      ?? databaseError?.code;
  }

  private handleWriteError(error: unknown): never {
    const code = this.databaseErrorCode(error);

    if (code === '23505') {
      throw new ConflictException(
        'Mã hoặc serial Server đã tồn tại',
      );
    }

    if (code === '23503') {
      throw new BadRequestException('Rack không tồn tại');
    }

    if (
      code === '23502' ||
      code === '23514' ||
      code === '22001'
    ) {
      throw new BadRequestException(
        'Dữ liệu Server không hợp lệ',
      );
    }

    throw error;
  }

  async create(createServerDto: CreateServerDto) {
    try {
      const server = this.repository.create({
        id: randomUUID(),
        rackId: createServerDto.rackId,
        code: createServerDto.code,
        name: createServerDto.name,
        serialNumber: createServerDto.serialNumber ?? null,
      });

      return await this.repository.save(server);
    } catch (error) {
      this.handleWriteError(error);
    }
  }

  async findAll() {
    return this.repository.find({
      relations: { rack: true },
      order: { name: 'ASC' },
    });
  }

  async findOne(id: string) {
    const server = await this.repository.findOne({
      where: { id },
      relations: {
        rack: true,
        workloads: true,
      },
    });

    if (!server) {
      throw new NotFoundException(
        `Không tìm thấy Server: ${id}`,
      );
    }

    return server;
  }

  async update(id: string, updateServerDto: UpdateServerDto) {
    if (
      !updateServerDto ||
      Object.keys(updateServerDto).length === 0
    ) {
      throw new BadRequestException(
        'Cần cung cấp ít nhất một trường để cập nhật',
      );
    }

    await this.findOne(id);

    try {
      await this.repository.update(
        { id },
        updateServerDto,
      );
    } catch (error) {
      this.handleWriteError(error);
    }

    return this.findOne(id);
  }

  async remove(id: string) {
    const server = await this.findOne(id);

    try {
      await this.repository.remove(server);

      return {
        message: 'Xóa Server thành công',
      };
    } catch (error) {
      if (this.databaseErrorCode(error) === '23503') {
        throw new ConflictException(
          'Không thể xóa Server đang được dữ liệu khác tham chiếu',
        );
      }

      throw error;
    }
  }
}