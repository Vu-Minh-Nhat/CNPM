import bcrypt

from src.domain.exceptions import ValidationError
from src.domain.security.password_hasher import PasswordHasher
from src.domain.security.password_verifier import PasswordVerifier


class BcryptPasswordVerifier(PasswordVerifier, PasswordHasher):
    def verify(self, password: str, password_hash: str) -> bool:
        password_bytes = password.encode("utf-8")

        if not password_bytes or len(password_bytes) > 72:
            return False

        try:
            return bcrypt.checkpw(
                password_bytes,
                password_hash.encode("utf-8"),
            )
        except ValueError:
            return False

    def hash_password(self, password: str) -> str:
        if not isinstance(password, str):
            raise ValidationError("Mật khẩu phải là chuỗi.")

        password_bytes = password.encode("utf-8")

        if not password_bytes or len(password_bytes) > 72:
            raise ValidationError(
                "Mật khẩu không được rỗng hoặc vượt quá 72 byte UTF-8."
            )

        hashed = bcrypt.hashpw(
            password_bytes,
            bcrypt.gensalt(rounds=10),
        )

        return hashed.decode("ascii")