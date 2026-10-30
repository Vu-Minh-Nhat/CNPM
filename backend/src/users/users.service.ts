import {
  BadRequestException,
  ConflictException,
  Inject,
  Injectable,
  ServiceUnavailableException,
} from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import { hash } from 'bcryptjs';
import { QueryFailedError } from 'typeorm';
import { Role } from '../common/enums/role.enum.js';
import { DatabaseService } from '../database/database.service.js';
import { AccountSchema } from '../database/entities.js';

@Injectable()
export class UsersService {
  constructor(
    @Inject(DatabaseService)
    private readonly database: DatabaseService,
  ) {}

  private repository() {
    const source = this.database.source;

    if (!source?.isInitialized) {
      throw new ServiceUnavailableException(
        'Database chưa được kết nối',
      );
    }

    return source.getRepository(AccountSchema);
  }

  async findByEmail(email: string) {
    return this.repository().findOne({
      where: { email: email.trim().toLowerCase() },
      select: {
        id: true,
        email: true,
        passwordHash: true,
        role: true,
        isActive: true,
      },
    });
  }

  async findById(id: string) {
    // Token cũ hoặc ID không hợp lệ không được gửi vào cột UUID.
    const uuidPattern =
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

    if (!uuidPattern.test(id)) return null;

    return this.repository().findOneBy({ id });
  }

  async list() {
    // passwordHash bị loại theo cấu hình select: false của entity.
    return this.repository().find({
      order: { email: 'ASC' },
    });
  }

  async create(email: string, password: string, role: Role) {
    if (
      typeof email !== 'string' ||
      typeof password !== 'string' ||
      password.length < 8 ||
      Buffer.byteLength(password, 'utf8') > 72
    ) {
      throw new BadRequestException(
        'Email và mật khẩu hợp lệ là bắt buộc; mật khẩu từ 8 ký tự, tối đa 72 byte',
      );
    }

    const normalizedEmail = email.trim().toLowerCase();

    if (
      normalizedEmail.length > 254 ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)
    ) {
      throw new BadRequestException('Email không hợp lệ');
    }

    const repository = this.repository();

    try {
      const user = await repository.save(
        repository.create({
          id: randomUUID(),
          email: normalizedEmail,
          passwordHash: await hash(password, 10),
          role,
          isActive: true,
        }),
      );

      const { passwordHash, ...safeUser } = user;
      return safeUser;
    } catch (error) {
      if (
        error instanceof QueryFailedError &&
        (error.driverError as { code?: string }).code === '23505'
      ) {
        throw new ConflictException('Email đã tồn tại');
      }

      throw error;
    }
  }

  async changeRole(id: string, role: Role) {
    const user = await this.findById(id);
    if (!user) return null;

    await this.repository().update({ id }, { role });

    return this.findById(id);
  }
}