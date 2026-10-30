import { Module } from "@nestjs/common";
import { JwtModule } from "@nestjs/jwt";
import { UsersModule } from "../users/users.module.js";
import { AuthController } from "./auth.controller.js";
import { AuthService } from "./auth.service.js";
import { getJwtSecret } from "./jwt.config.js";

@Module({
  imports: [
    UsersModule,
    JwtModule.register({ secret: getJwtSecret(), signOptions: { expiresIn: 3600 } }), // 1 giờ
  ],
  controllers: [AuthController],
  providers: [AuthService],
  exports: [JwtModule, AuthService],
})
export class AuthModule {}
