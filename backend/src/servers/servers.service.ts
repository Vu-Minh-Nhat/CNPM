import {
  Injectable,
  NotFoundException,
  ConflictException,
  BadRequestException,
  InternalServerErrorException,
} from '@nestjs/common';
import { randomUUID } from 'node:crypto';

import { DatabaseService } from '../database/database.service.js';
import { NodeSchema } from '../database/entities.js';
import { CreateServerDto } from './dto/create-server.dto.js';
import { UpdateServerDto } from './dto/update-server.dto.js';

@Injectable()
export class ServersService {
  constructor(private readonly database: DatabaseService) {}

  private get repository() {
    if (!this.database.source?.isInitialized) {
      throw new InternalServerErrorException('Database chưa được kết nối');
    }
    return this.database.source.getRepository(NodeSchema);
  }

  async create(createServerDto: CreateServerDto) {
    try {
      const server = this.repository.create({
        id: randomUUID(),
        ...createServerDto,
      });
      return await this.repository.save(server);
    } catch (error) {
      const code = (error as { code?: string }).code;

      if (code === '23505') throw new ConflictException('Mã Server đã tồn tại');
      if (code === '23503') throw new BadRequestException('Rack không tồn tại');
      throw error;
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
      relations: { rack: true, workloads: true },
    });

    if (!server) throw new NotFoundException(`Không tìm thấy Server: ${id}`);

    return server;
  }

  async update(id: string, updateServerDto: UpdateServerDto) {
    const server = await this.findOne(id);
    this.repository.merge(server, updateServerDto);
    return this.repository.save(server);
  }

  async remove(id: string) {
    const server = await this.findOne(id);
    await this.repository.remove(server);
    return { message: 'Xóa Server thành công' };
  }
}