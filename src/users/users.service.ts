import { Injectable } from "@nestjs/common";
import * as bcrypt from "bcryptjs";
import { Role } from "../common/enums/role.enum.js";

export interface UserRecord {
  id: string;
  email: string;
  passwordHash: string;
  role: Role;
  isActive: boolean;
}


@Injectable()
export class UsersService {
  private readonly users: UserRecord[] = [
    { id: "u-admin", email: "admin@arimms.local", passwordHash: bcrypt.hashSync("Admin@123", 10), role: Role.ADMINISTRATOR, isActive: true },
    { id: "u-op", email: "operator@arimms.local", passwordHash: bcrypt.hashSync("Operator@123", 10), role: Role.OPERATOR, isActive: true },
    { id: "u-tech", email: "tech@arimms.local", passwordHash: bcrypt.hashSync("Tech@123", 10), role: Role.TECHNICIAN, isActive: true },
  ];

  findByEmail(email: string) {
    return this.users.find((u) => u.email === email);
  }

  findById(id: string) {
    return this.users.find((u) => u.id === id);
  }

  list() {
    return this.users.map(({ passwordHash, ...rest }) => rest);
  }

  create(email: string, password: string, role: Role) {
    const user: UserRecord = {
      id: `u-${this.users.length + 1}`,
      email,
      passwordHash: bcrypt.hashSync(password, 10),
      role,
      isActive: true,
    };
    this.users.push(user);
    const { passwordHash, ...safe } = user;
    return safe;
  }

  changeRole(id: string, role: Role) {
    const user = this.findById(id);
    if (!user) return undefined;
    user.role = role;
    const { passwordHash, ...safe } = user;
    return safe;
  }
}
