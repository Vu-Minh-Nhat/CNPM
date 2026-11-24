from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.databases.base import Base


class RoleModel(Base):
    __tablename__ = "roles"

    __table_args__ = (
        CheckConstraint(
            "code IN ('Administrator', 'Operator', 'Technician')",
            name="ck_roles_code",
        ),
        CheckConstraint(
            "btrim(name) <> ''",
            name="ck_roles_name_not_blank",
        ),
    )

    code: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )