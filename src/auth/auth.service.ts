import { Inject, Injectable, UnauthorizedException } from "@nestjs/common";
import { JwtService } from "@nestjs/jwt";
import * as bcrypt from "bcryptjs";
import { UsersService } from "../users/users.service.js";

@Injectable()
export class AuthService {
  constructor(
    @Inject(UsersService) private readonly users: UsersService,
    @Inject(JwtService) private readonly jwt: JwtService,
  ) {}

  async login(email: string, password: string) {
    const user = email ? this.users.findByEmail(email) : undefined;
    const ok = !!user && user.isActive && (await bcrypt.compare(password ?? "", user.passwordHash));
    if (!user || !ok) throw new UnauthorizedException("Sai email hoặc mật khẩu");

    const accessToken = await this.jwt.signAsync({ sub: user.id, email: user.email, role: user.role });
    return { accessToken, role: user.role };
  }
}
