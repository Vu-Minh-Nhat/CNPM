from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infrastructure.databases.base import Base


class SiteModel(Base):
    __tablename__ = "sites"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)


class RoomModel(Base):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    site_id: Mapped[str] = mapped_column(
        ForeignKey("sites.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)

    site: Mapped[SiteModel] = relationship("SiteModel")


class RackModel(Base):
    __tablename__ = "racks"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    room_id: Mapped[str] = mapped_column(
        ForeignKey("rooms.id"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    capacity_u: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    room: Mapped[RoomModel] = relationship("RoomModel")


class NodeModel(Base):
    __tablename__ = "nodes"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    rack_id: Mapped[str] = mapped_column(
        ForeignKey("racks.id"), nullable=False
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

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True
    )
    node_id: Mapped[str] = mapped_column(
        ForeignKey("nodes.id"), nullable=False
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