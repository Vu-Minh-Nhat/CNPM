import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Inject,
  Injectable,
} from "@nestjs/common";
import { Reflector } from "@nestjs/core";
import { IS_PUBLIC_KEY } from "../common/decorators/public.decorator.js";
import { ROLES_KEY } from "../common/decorators/roles.decorator.js";
import { Role } from "../common/enums/role.enum.js";

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(@Inject(Reflector) private readonly reflector: Reflector) {}

  canActivate(context: ExecutionContext): boolean {
    // 1. Nếu là API Public (không cần đăng nhập), cho phép truy cập luôn
    const isPublic = this.reflector.getAllAndOverride<boolean>(IS_PUBLIC_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    if (isPublic) return true;

    // 2. Lấy danh sách Roles yêu cầu từ decorator @Roles()
    const requiredRoles = this.reflector.getAllAndOverride<Role[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);
    
    // Nếu endpoint không yêu cầu Role cụ thể -> Chỉ cần đăng nhập (Token hợp lệ) là được vào
    if (!requiredRoles || requiredRoles.length === 0) {
     throw new ForbiddenException(
     'Endpoint chưa được cấu hình quyền truy cập',
    );
    }

    // 3. Lấy thông tin user từ request (đã được JwtStrategy giải mã và gắn vào req.user)
    const { user } = context.switchToHttp().getRequest();
    if (!user) {
      throw new ForbiddenException("Không tìm thấy thông tin người dùng");
    }

    // 4. Kiểm tra quyền của người dùng
    // Trường hợp A: user.role là 1 chuỗi đơn (VD: 'ADMIN')
    const hasRole = requiredRoles.includes(user.role);

    // Trường hợp B: Nếu user.roles trong DB/JWT là một MẢNG (VD: ['ADMIN', 'USER']), dùng dòng dưới:
    // const hasRole = requiredRoles.some((role) => user.roles?.includes(role));

    if (!hasRole) {
      throw new ForbiddenException("Bạn không có quyền thực hiện thao tác này");
    }

    return true;
  }
}