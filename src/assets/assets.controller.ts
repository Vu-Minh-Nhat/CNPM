import { Controller, Delete, Get, Post, Put } from "@nestjs/common";
import { Roles } from "../common/decorators/roles.decorator.js";
import { ALL_ROLES, Role } from "../common/enums/role.enum.js";


@Controller("assets")
export class AssetsController {
  @Get()
  @Roles(...ALL_ROLES)
  findAll() {
    return { message: "Danh sách tài sản (demo)" };
  }

  @Post()
  @Roles(Role.ADMINISTRATOR, Role.OPERATOR)
  create() {
    return { message: "Tạo tài sản (demo)" };
  }

  @Put(":id")
  @Roles(Role.ADMINISTRATOR, Role.OPERATOR)
  update() {
    return { message: "Cập nhật tài sản (demo)" };
  }

  @Delete(":id")
  @Roles(Role.ADMINISTRATOR)
  remove() {
    return { message: "Xóa tài sản (demo)" };
  }
}
