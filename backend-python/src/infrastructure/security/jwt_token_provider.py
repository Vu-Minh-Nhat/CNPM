from datetime import datetime, timedelta, timezone

import jwt

from src.domain.exceptions import AuthenticationError
from src.domain.models.account import Account
from src.domain.security.token_provider import TokenProvider


class JwtTokenProvider(TokenProvider):
    def __init__(self, secret: str, expires_in_seconds: int):
        if not secret or len(secret.encode("utf-8")) < 32:
            raise ValueError("JWT_SECRET phải có ít nhất 32 byte.")

        if expires_in_seconds <= 0:
            raise ValueError("Thời hạn JWT phải lớn hơn 0.")

        self._secret = secret
        self._expires_in_seconds = expires_in_seconds

    def issue(self, account: Account) -> str:
        now = datetime.now(timezone.utc)

        payload = {
            "sub": account.id,
            "email": account.email,
            "role": account.role.value,
            "iat": now,
            "exp": now + timedelta(
                seconds=self._expires_in_seconds,
            ),
        }

        return jwt.encode(
            payload,
            self._secret,
            algorithm="HS256",
        )

    def verify(self, token: str) -> str:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                options={
                    "require": ["sub", "iat", "exp"],
                },
            )
        except jwt.InvalidTokenError as error:
            raise AuthenticationError(
                "Token không hợp lệ hoặc đã hết hạn."
            ) from error

        account_id = payload.get("sub")

        if not isinstance(account_id, str) or not account_id:
            raise AuthenticationError("Token không hợp lệ.")

        return account_id