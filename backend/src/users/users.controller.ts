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
} from "@nestjs/common";
import { Roles } from "../common/decorators/roles.decorator.js";
import { ALL_ROLES, Role } from "../common/enums/role.enum.js";
import { UsersService } from "./users.service.js";

/** Quản lý tài khoản & gán vai trò: chỉ Administrator. */
@Controller("users")
@Roles(Role.ADMINISTRATOR)
export class UsersController {
  constructor(@Inject(UsersService) private readonly users: UsersService) {}

  @Get()
  list() {
    return this.users.list();
  }

  @Post()
  create(@Body() body: { email: string; password: string; role: Role }) {
    if (!body?.email || !body?.password || body.password.length < 8) {
      throw new BadRequestException("Email và mật khẩu (>= 8 ký tự) là bắt buộc");
    }
    if (!ALL_ROLES.includes(body.role)) throw new BadRequestException("Vai trò không hợp lệ");
    if (this.users.findByEmail(body.email)) throw new ConflictException("Email đã tồn tại");
    return this.users.create(body.email, body.password, body.role);
  }

  @Patch(":id/role")
  changeRole(@Param("id") id: string, @Body() body: { role: Role }) {
    if (!ALL_ROLES.includes(body?.role)) throw new BadRequestException("Vai trò không hợp lệ");
    const updated = this.users.changeRole(id, body.role);
    if (!updated) throw new NotFoundException();
    return updated;
  }
}
