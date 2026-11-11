from collections.abc import Callable
from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.exc import DataError, DBAPIError, IntegrityError
from sqlalchemy.orm import Session, joinedload, selectinload

from src.domain.exceptions import (
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.asset import Node, Rack, Room, Site, Workload
from src.domain.repositories.server_repository import ServerRepository
from src.infrastructure.models import NodeModel, RackModel, RoomModel


class SqlAlchemyServerRepository(ServerRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _statement():
        return select(NodeModel).options(
            joinedload(NodeModel.rack)
            .joinedload(RackModel.room)
            .joinedload(RoomModel.site),
            selectinload(NodeModel.workloads),
        )

    @staticmethod
    def _to_domain(model: NodeModel) -> Node:
        rack_model = model.rack
        room_model = rack_model.room if rack_model else None
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

        rack = None

        if rack_model is not None:
            rack = Rack(
                id=rack_model.id,
                room_id=rack_model.room_id,
                code=rack_model.code,
                name=rack_model.name,
                capacity_u=rack_model.capacity_u,
                room=room,
            )

        return Node(
            id=model.id,
            rack_id=model.rack_id,
            code=model.code,
            name=model.name,
            serial_number=model.serial_number,
            rack=rack,
            workloads=tuple(
                Workload(
                    id=item.id,
                    node_id=item.node_id,
                    code=item.code,
                    name=item.name,
                    runtime_id=item.runtime_id,
                )
                for item in model.workloads
            ),
        )

    @staticmethod
    def _handle_write_error(
        error: DBAPIError,
        deleting: bool = False,
    ) -> NoReturn:
        code = getattr(error.orig, "sqlstate", None)

        if code == "23505":
            raise ResourceConflictError(
                "Mã hoặc serial Server đã tồn tại."
            ) from error

        if code == "23503":
            if deleting:
                raise ResourceConflictError(
                    "Không thể xóa Server còn dữ liệu liên quan."
                ) from error

            raise ValidationError("Rack không tồn tại.") from error

        if code in {"23502", "23514", "22001"}:
            raise ValidationError(
                "Dữ liệu Server không hợp lệ."
            ) from error

        raise error

    def list_servers(self) -> list[Node]:
        with self._session_factory() as session:
            statement = self._statement().order_by(
                NodeModel.name,
                NodeModel.id,
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def find_by_id(self, server_id: str) -> Node | None:
        with self._session_factory() as session:
            statement = self._statement().where(
                NodeModel.id == server_id
            )

            model = session.execute(statement).scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    def add(self, server: Node) -> Node:
        try:
            with self._session_factory() as session:
                model = NodeModel(
                    id=server.id,
                    rack_id=server.rack_id,
                    code=server.code,
                    name=server.name,
                    serial_number=server.serial_number,
                )

                session.add(model)
                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def update(
        self,
        server_id: str,
        changes: dict[str, str | None],
    ) -> Node | None:
        try:
            with self._session_factory() as session:
                model = session.get(NodeModel, server_id)

                if model is None:
                    return None

                for field in (
                    "rack_id",
                    "code",
                    "name",
                    "serial_number",
                ):
                    if field in changes:
                        setattr(model, field, changes[field])

                session.commit()

                # Đọc lại Rack theo rack_id sau cập nhật.
                session.expire(model, ["rack"])

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def delete(self, server_id: str) -> bool:
        try:
            with self._session_factory() as session:
                model = session.get(NodeModel, server_id)

                if model is None:
                    return False

                session.delete(model)
                session.commit()

                return True
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error, deleting=True)