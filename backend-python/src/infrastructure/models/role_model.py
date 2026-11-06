from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.databases.base import Base


class RoleModel(Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )