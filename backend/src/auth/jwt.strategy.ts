import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { UsersService } from '../users/users.service.js';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(private readonly usersService: UsersService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: process.env.JWT_SECRET || 'your_secret_key',
    });
  }

  async validate(payload: any) {
    // Kiểm tra xem user trong payload có tồn tại và còn hoạt động không
    const user = await this.usersService.findById(payload.sub); // hoặc findByEmail tùy service của bạn
    if (!user || !user.isActive) {
      throw new UnauthorizedException('Tài khoản không tồn tại hoặc đã bị khóa');
    }

    // Trả về thông tin gắn vào req.user
    return { userId: user.id, email: user.email, role: user.role };
  }
}