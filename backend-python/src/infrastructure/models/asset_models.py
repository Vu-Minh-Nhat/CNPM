from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.databases.base import Base


class SiteModel(Base):
    __tablename__ = "sites"

    __table_args__ = (
        UniqueConstraint("code", name="uq_sites_code"),
        CheckConstraint(
            "btrim(code) <> ''",
            name="ck_sites_code_not_blank",
        ),
        CheckConstraint(
            "btrim(name) <> ''",
            name="ck_sites_name_not_blank",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)


class RoomModel(Base):
    __tablename__ = "rooms"

    __table_args__ = (
        UniqueConstraint(
            "site_id", "code",
            name="uq_rooms_site_code",
        ),
        CheckConstraint(
            "btrim(code) <> ''",
            name="ck_rooms_code_not_blank",
        ),
        CheckConstraint(
            "btrim(name) <> ''",
            name="ck_rooms_name_not_blank",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    site_id: Mapped[str] = mapped_column(
        ForeignKey("sites.id", ondelete="RESTRICT"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    site: Mapped[SiteModel] = relationship("SiteModel")


class RackModel(Base):
    __tablename__ = "racks"

    __table_args__ = (
        UniqueConstraint(
            "room_id", "code",
            name="uq_racks_room_code",
        ),
        CheckConstraint(
            "btrim(code) <> ''",
            name="ck_racks_code_not_blank",
        ),
        CheckConstraint(
            "btrim(name) <> ''",
            name="ck_racks_name_not_blank",
        ),
        CheckConstraint(
            "capacity_u > 0 AND capacity_u <= 100",
            name="ck_racks_capacity_u",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    room_id: Mapped[str] = mapped_column(
        ForeignKey("rooms.id", ondelete="RESTRICT"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    capacity_u: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("42"),
    )

    room: Mapped[RoomModel] = relationship("RoomModel")


class NodeModel(Base):
    __tablename__ = "nodes"

    __table_args__ = (
        UniqueConstraint("code", name="uq_nodes_code"),
        UniqueConstraint(
            "serial_number",
            name="uq_nodes_serial_number",
        ),
        CheckConstraint(
            "btrim(code) <> ''",
            name="ck_nodes_code_not_blank",
        ),
        CheckConstraint(
            "btrim(name) <> ''",
            name="ck_nodes_name_not_blank",
        ),
        CheckConstraint(
            "serial_number IS NULL OR btrim(serial_number) <> ''",
            name="ck_nodes_serial_number_not_blank",
        ),
        Index("nodes_rack_idx", "rack_id"),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    rack_id: Mapped[str] = mapped_column(
        ForeignKey("racks.id", ondelete="RESTRICT"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )

    rack: Mapped[RackModel] = relationship("RackModel")

    workloads: Mapped[list["WorkloadModel"]] = relationship(
        "WorkloadModel",
        back_populates="node",
        passive_deletes="all",
    )


class WorkloadModel(Base):
    __tablename__ = "workloads"

    __table_args__ = (
        UniqueConstraint(
            "node_id", "code",
            name="uq_workloads_node_code",
        ),
        UniqueConstraint(
            "node_id", "runtime_id",
            name="uq_workloads_node_runtime",
        ),
        CheckConstraint(
            "btrim(code) <> ''",
            name="ck_workloads_code_not_blank",
        ),
        CheckConstraint(
            "btrim(name) <> ''",
            name="ck_workloads_name_not_blank",
        ),
        CheckConstraint(
            "runtime_id IS NULL OR btrim(runtime_id) <> ''",
            name="ck_workloads_runtime_id_not_blank",
        ),
    )

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    node_id: Mapped[str] = mapped_column(
        ForeignKey("nodes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    runtime_id: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )

    node: Mapped[NodeModel] = relationship(
        "NodeModel",
        back_populates="workloads",
    )