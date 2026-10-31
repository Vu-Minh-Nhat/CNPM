import {
  Controller,
  Delete,
  Get,
  Inject,
  NotImplementedException,
  Post,
  Put,
  ServiceUnavailableException,
} from '@nestjs/common';
import { Roles } from '../common/decorators/roles.decorator.js';
import { ALL_ROLES, Role } from '../common/enums/role.enum.js';
import { DatabaseService } from '../database/database.service.js';
import { NodeSchema } from '../database/entities.js';
import { ApiBearerAuth } from '@nestjs/swagger';

@ApiBearerAuth()
@Controller('assets')
export class AssetsController {
  constructor(
    @Inject(DatabaseService)
    private readonly database: DatabaseService,
  ) {}

  @Get()
  @Roles(...ALL_ROLES)
  async findAll() {
    const source = this.database.source;

    if (!source?.isInitialized) {
      throw new ServiceUnavailableException(
        'Database chưa được kết nối',
      );
    }

    return source.getRepository(NodeSchema).find({
      relations: {
        rack: {
          room: {
            site: true,
          },
        },
        workloads: true,
      },
      order: {
        code: 'ASC',
      },
    });
  }

  @Post()
  @Roles(Role.ADMINISTRATOR, Role.OPERATOR)
  create() {
    throw new NotImplementedException(
      'Chức năng tạo tài sản chưa được triển khai',
    );
  }

  @Put(':id')
  @Roles(Role.ADMINISTRATOR, Role.OPERATOR)
  update() {
    throw new NotImplementedException(
      'Chức năng cập nhật tài sản chưa được triển khai',
    );
  }

  @Delete(':id')
  @Roles(Role.ADMINISTRATOR)
  remove() {
    throw new NotImplementedException(
      'Chức năng xóa tài sản chưa được triển khai',
    );
  }
}