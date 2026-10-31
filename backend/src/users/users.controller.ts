import {
  BadRequestException,
  Body,
  ConflictException,
  Controller,
  Get,
  Inject,
  NotFoundException,
  Param,
  Patch,
  Post,
} from '@nestjs/common';
import { Roles } from '../common/decorators/roles.decorator.js';
import { ALL_ROLES, Role } from '../common/enums/role.enum.js';
import { UsersService } from './users.service.js';
import { ApiBearerAuth } from '@nestjs/swagger';

@ApiBearerAuth()
@Controller('users')
@Roles(Role.ADMINISTRATOR)
export class UsersController {
  constructor(
    @Inject(UsersService)
    private readonly users: UsersService,
  ) {}
  @Get()
  async list() {
    return this.users.list();
  }
  @Post()
  async create(
    @Body() body: {
      email: string;
      password: string;
      role: Role;
    },
  ) {
    if (
      typeof body?.email !== 'string' ||
      !body.email.trim() ||
      typeof body?.password !== 'string' ||
      body.password.length < 8 ||
      Buffer.byteLength(body.password, 'utf8') > 72
    ) {
      throw new BadRequestException(
        'Email là bắt buộc; mật khẩu từ 8 ký tự, tối đa 72 byte',
      );
    }
    if (!ALL_ROLES.includes(body.role)) {
      throw new BadRequestException('Vai trò không hợp lệ');
    }
    const existingUser = await this.users.findByEmail(body.email);
    if (existingUser) {
      throw new ConflictException('Email đã tồn tại');
    }

    return this.users.create(
      body.email,
      body.password,
      body.role,
    );
  }
  @Patch(':id/role')
  async changeRole(
    @Param('id') id: string,
    @Body() body: { role: Role },
  ) {
    if (!ALL_ROLES.includes(body?.role)) {
      throw new BadRequestException('Vai trò không hợp lệ');
    }
    const updated = await this.users.changeRole(id, body.role);
    if (!updated) {
      throw new NotFoundException('Không tìm thấy tài khoản');
    }
    return updated;
  }
}