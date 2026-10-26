
import { Module } from "@nestjs/common";
import { APP_GUARD } from "@nestjs/core";
import { AssetsModule } from "./assets/assets.module.js";         
import { AuthModule } from "./auth/auth.module.js";                 
import { JwtAuthGuard } from "./auth/jwt-auth.guard.js";             
import { RolesGuard } from "./auth/roles.guard.js";                 
import { UsersModule } from "./users/users.module.js";               

@Module({
  imports: [
    
    AuthModule, UsersModule, AssetsModule,                          
  providers: [
   
    { provide: APP_GUARD, useClass: JwtAuthGuard },                
    { provide: APP_GUARD, useClass: RolesGuard },                    
})
export class AppModule {}
