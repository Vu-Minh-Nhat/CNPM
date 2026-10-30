import {
  CanActivate,
  ExecutionContext,
  Inject,
  Injectable,
  UnauthorizedException,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { JwtService } from "@nestjs/jwt";
import { IS_PUBLIC_KEY } from "../common/decorators/public.decorator.js";
import { UsersService } from "../users/users.service.js";
import type { JwtPayload } from "./jwt.config.js";


@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(
    @Inject(Reflector) private readonly reflector: Reflector,
    @Inject(JwtService) private readonly jwt: JwtService,
    @Inject(UsersService) private readonly users: UsersService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

    const request = context.switchToHttp().getRequest();
    const header: string = request.headers["authorization"] ?? "";
    const [type, token] = header.split(" ");
    if (type !== "Bearer" || !token) {
      throw new UnauthorizedException("Thiếu access token");
    }

    let payload: JwtPayload;
    try {
      payload = await this.jwt.verifyAsync<JwtPayload>(token);
    } catch {
      throw new UnauthorizedException("Token không hợp lệ hoặc đã hết hạn");
    }

    // Lấy vai trò từ nguồn dữ liệu tin cậy để đổi quyền / khóa tài khoản có hiệu lực ngay.
 const user = await this.users.findById(payload.sub);
    if (!user || !user.isActive) {
      throw new UnauthorizedException("Tài khoản không tồn tại hoặc đã bị khóa");
    }

    request.user = { userId: user.id, email: user.email, role: user.role };
    return true;
  }
}
