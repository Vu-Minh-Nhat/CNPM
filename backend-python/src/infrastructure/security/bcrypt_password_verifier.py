import bcrypt

from src.domain.security.password_verifier import PasswordVerifier


class BcryptPasswordVerifier(PasswordVerifier):
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