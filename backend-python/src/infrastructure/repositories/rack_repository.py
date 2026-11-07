from collections.abc import Callable
from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.exc import DataError, DBAPIError, IntegrityError
from sqlalchemy.orm import Session, joinedload

from src.domain.exceptions import (
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.asset import Node, Rack, Room, Site
from src.domain.repositories.rack_repository import RackRepository
from src.infrastructure.models import NodeModel, RackModel, RoomModel


class SqlAlchemyRackRepository(RackRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _to_domain(model: RackModel) -> Rack:
        room_model = model.room
        site_model = room_model.site if room_model else None

        site = None

        if site_model is not None:
            site = Site(
                id=site_model.id,
                code=site_model.code,
                name=site_model.name,
            )

        room = None

        if room_model is not None:
            room = Room(
                id=room_model.id,
                site_id=room_model.site_id,
                code=room_model.code,
                name=room_model.name,
                site=site,
            )

        return Rack(
            id=model.id,
            room_id=model.room_id,
            code=model.code,
            name=model.name,
            capacity_u=model.capacity_u,
            room=room,
        )

    @staticmethod
    def _handle_write_error(
        error: DBAPIError,
        deleting: bool = False,
    ) -> NoReturn:
        code = getattr(error.orig, "sqlstate", None)

        if code == "23505":
            raise ResourceConflictError(
                "Mã Rack đã tồn tại trong Room."
            ) from error

        if code == "23503":
            if deleting:
                raise ResourceConflictError(
                    "Không thể xóa Rack còn dữ liệu liên quan."
                ) from error

            raise ValidationError("Room không tồn tại.") from error

        if code in {"23502", "23514", "22001"}:
            raise ValidationError(
                "Dữ liệu Rack không hợp lệ."
            ) from error

        raise error

    def list_racks(self) -> list[Rack]:
        with self._session_factory() as session:
            statement = (
                select(RackModel)
                .options(
                    joinedload(RackModel.room)
                    .joinedload(RoomModel.site)
                )
                .order_by(RackModel.name, RackModel.id)
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def find_by_id(self, rack_id: str) -> Rack | None:
        with self._session_factory() as session:
            statement = (
                select(RackModel)
                .where(RackModel.id == rack_id)
                .options(
                    joinedload(RackModel.room)
                    .joinedload(RoomModel.site)
                )
            )

            model = session.execute(statement).scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    def list_nodes(self, rack_id: str) -> list[Node]:
        with self._session_factory() as session:
            statement = (
                select(NodeModel)
                .where(NodeModel.rack_id == rack_id)
                .order_by(NodeModel.code)
            )

            models = session.execute(statement).scalars().all()

            return [
                Node(
                    id=model.id,
                    rack_id=model.rack_id,
                    code=model.code,
                    name=model.name,
                    serial_number=model.serial_number,
                    rack=None,
                    workloads=(),
                )
                for model in models
            ]

    def add(self, rack: Rack) -> Rack:
        try:
            with self._session_factory() as session:
                model = RackModel(
                    id=rack.id,
                    room_id=rack.room_id,
                    code=rack.code,
                    name=rack.name,
                    capacity_u=rack.capacity_u,
                )

                session.add(model)
                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def update(
        self,
        rack_id: str,
        changes: dict[str, str | int],
    ) -> Rack | None:
        try:
            with self._session_factory() as session:
                model = session.get(RackModel, rack_id)

                if model is None:
                    return None

                for field in ("room_id", "code", "name", "capacity_u"):
                    if field in changes:
                        setattr(model, field, changes[field])

                session.commit()

                # Tải lại Room theo room_id sau cập nhật.
                session.expire(model, ["room"])

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def delete(self, rack_id: str) -> bool:
        try:
            with self._session_factory() as session:
                model = session.get(RackModel, rack_id)

                if model is None:
                    return False

                session.delete(model)
                session.commit()

                return True
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error, deleting=True)