import {
  ConflictException,
  Inject,
  Injectable,
  NotFoundException,
  ServiceUnavailableException,
} from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import { DatabaseService } from '../database/database.service.js';
import { SiteSchema } from '../database/entities.js';
import { CreateSiteDto } from './dto/create-site.dto.js';
import { UpdateSiteDto } from './dto/update-site.dto.js';

@Injectable()
export class SitesService {
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

    return source.getRepository(SiteSchema);
  }

  async create(createSiteDto: CreateSiteDto) {
    try {
      const site = this.repository.create({
        id: randomUUID(),
        code: createSiteDto.code,
        name: createSiteDto.name,
      });

      return await this.repository.save(site);
    } catch (error) {
      if ((error as { code?: string }).code === '23505') {
        throw new ConflictException('Mã Site đã tồn tại');
      }

      throw error;
    }
  }

  async findAll() {
    return this.repository.find({
      order: { name: 'ASC' },
    });
  }

  async findOne(id: string) {
    const site = await this.repository.findOneBy({ id });

    if (!site) {
      throw new NotFoundException(
        `Không tìm thấy Site: ${id}`,
      );
    }

    return site;
  }

  async update(id: string, updateSiteDto: UpdateSiteDto) {
    const site = await this.findOne(id);
    this.repository.merge(site, updateSiteDto);

    try {
      return await this.repository.save(site);
    } catch (error) {
      if ((error as { code?: string }).code === '23505') {
        throw new ConflictException('Mã Site đã tồn tại');
      }

      throw error;
    }
  }

  async remove(id: string) {
    const site = await this.findOne(id);

    try {
      await this.repository.remove(site);

      return {
        message: 'Xóa Site thành công',
      };
    } catch (error) {
      if ((error as { code?: string }).code === '23503') {
        throw new ConflictException(
          'Không thể xóa Site đang chứa Room',
        );
      }

      throw error;
    }
  }
}