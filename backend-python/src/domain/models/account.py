from dataclasses import dataclass, field

from src.domain.constants import Role


@dataclass(frozen=True, slots=True)
class Account:
    id: str
    email: str
    role: Role
    is_active: bool
    password_hash: str = field(repr=False)