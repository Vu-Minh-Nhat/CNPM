import { type INestApplication } from "@nestjs/common";
import { Test } from "@nestjs/testing";
import request from "supertest";
import { AppModule } from "../src/app.module.js";

describe("RBAC (e2e)", () => {
  let app: INestApplication;
  const token: Record<string, string> = {};

  const login = async (email: string, password: string) => {
    const res = await request(app.getHttpServer()).post("/auth/login").send({ email, password });
    return res.body.accessToken as string;
  };

  const call = (method: "get" | "post" | "put" | "delete", url: string, t?: string) => {
    const r = request(app.getHttpServer())[method](url);
    return t ? r.set("Authorization", `Bearer ${t}`) : r;
  };

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({ imports: [AppModule] }).compile();
    app = moduleRef.createNestApplication();
    await app.init();
    token.admin = await login("admin@arimms.local", "Admin@123");
    token.op = await login("operator@arimms.local", "Operator@123");
    token.tech = await login("tech@arimms.local", "Tech@123");
  });

  afterAll(async () => {
    await app.close();
  });

  it("TC01 không có token -> 401", () => call("get", "/assets").expect(401));
  it("TC02 token sai -> 401", () => call("get", "/assets", "abc.def.ghi").expect(401));
  it("TC03 sai mật khẩu -> 401", async () => {
    const res = await request(app.getHttpServer()).post("/auth/login").send({ email: "admin@arimms.local", password: "sai" });
    expect(res.status).toBe(401);
  });
  it("TC04 Administrator xem danh sách tài khoản -> 200", () => call("get", "/users", token.admin).expect(200));
  it("TC05 Operator xem danh sách tài khoản -> 403", () => call("get", "/users", token.op).expect(403));
  it("TC06 Technician xem danh sách tài khoản -> 403", () => call("get", "/users", token.tech).expect(403));
  it("TC07 Technician xem tài sản -> 200", () => call("get", "/assets", token.tech).expect(200));
  it("TC08 Technician tạo tài sản -> 403", () => call("post", "/assets", token.tech).expect(403));
  it("TC09 Operator tạo tài sản -> 201", () => call("post", "/assets", token.op).expect(201));
  it("TC10 Operator xóa tài sản -> 403", () => call("delete", "/assets/1", token.op).expect(403));
  it("TC11 Administrator xóa tài sản -> 200", () => call("delete", "/assets/1", token.admin).expect(200));
});
