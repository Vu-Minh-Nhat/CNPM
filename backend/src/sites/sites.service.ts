import {
  Injectable,
  NotFoundException,
  ConflictException,
  InternalServerErrorException,
} from '@nestjs/common';

import { DatabaseService } from '../database/database.service.js';
import { SiteSchema } from '../database/entities.js';
import { CreateSiteDto } from './dto/create-site.dto.js';
import { UpdateSiteDto } from './dto/update-site.dto.js';

@Injectable()
export class SitesService {
  constructor(private readonly database: DatabaseService) {}

  private get repository() {
    if (!this.database.source?.isInitialized) {
      throw new InternalServerErrorException('Database chưa được kết nối');
    }
    return this.database.source.getRepository(SiteSchema);
  }

  async create(createSiteDto: CreateSiteDto) {
    try {
      const site = this.repository.create(createSiteDto);
      return await this.repository.save(site);
    } catch (error) {
      if ((error as { code?: string }).code === '23505') {
        throw new ConflictException('Mã Site đã tồn tại');
      }
      throw error;
    }
  }

  async findAll() {
    return this.repository.find({ order: { name: 'ASC' } });
  }

  async findOne(id: string) {
    const site = await this.repository.findOneBy({ id });
    if (!site) {
      throw new NotFoundException(`Không tìm thấy Site: ${id}`);
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
    await this.repository.remove(site);
    return { message: 'Xóa Site thành công' };
  }
}
