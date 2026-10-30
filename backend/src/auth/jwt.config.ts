/** Khóa ký JWT. Production bắt buộc đặt biến môi trường JWT_SECRET. */
export function getJwtSecret(): string {
  const secret = process.env.JWT_SECRET;
  if (secret) return secret;
  if (process.env.NODE_ENV === "production") {
    throw new Error("Thiếu biến môi trường JWT_SECRET");
  }
  return "dev-only-secret-change-me";
}

export interface JwtPayload {
  sub: string;
  email: string;
  role: string;
}
