import { Body, Controller, Get, HttpCode, Inject, Post, Req } from "@nestjs/common";
import { Public } from "../common/decorators/public.decorator.js";
import { Roles } from "../common/decorators/roles.decorator.js";
import { ALL_ROLES } from "../common/enums/role.enum.js";
import { AuthService } from "./auth.service.js";

@Controller("auth")
export class AuthController {
  constructor(@Inject(AuthService) private readonly auth: AuthService) {}

  /** Endpoint duy nhất không cần JWT. */
  @Public()
  @HttpCode(200)
  @Post("login")
  async login(@Body() body: { email: string; password: string }) {
    return this.auth.login(body?.email, body?.password);
  }

  /** Xem thông tin người đang đăng nhập (mọi vai trò). */
  @Roles(...ALL_ROLES)
  @Get("me")
  me(@Req() req: any) {
    return req.user;
  }
}
