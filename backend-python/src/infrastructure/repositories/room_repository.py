from collections.abc import Callable
from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.exc import DataError, DBAPIError, IntegrityError
from sqlalchemy.orm import Session, joinedload

from src.domain.exceptions import (
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.asset import Rack, Room, Site
from src.domain.repositories.room_repository import RoomRepository
from src.infrastructure.models import RackModel, RoomModel


class SqlAlchemyRoomRepository(RoomRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _to_domain(model: RoomModel) -> Room:
        site_model = model.site

        site = None

        if site_model is not None:
            site = Site(
                id=site_model.id,
                code=site_model.code,
                name=site_model.name,
            )

        return Room(
            id=model.id,
            site_id=model.site_id,
            code=model.code,
            name=model.name,
            site=site,
        )

    @staticmethod
    def _handle_write_error(
        error: DBAPIError,
        deleting: bool = False,
    ) -> NoReturn:
        code = getattr(error.orig, "sqlstate", None)

        if code == "23505":
            raise ResourceConflictError(
                "Mã Room đã tồn tại trong Site."
            ) from error

        if code == "23503":
            if deleting:
                raise ResourceConflictError(
                    "Không thể xóa Room còn dữ liệu liên quan."
                ) from error

            raise ValidationError("Site không tồn tại.") from error

        if code in {"23502", "23514", "22001"}:
            raise ValidationError(
                "Dữ liệu Room không hợp lệ."
            ) from error

        raise error

    def list_rooms(self) -> list[Room]:
        with self._session_factory() as session:
            statement = (
                select(RoomModel)
                .options(joinedload(RoomModel.site))
                .order_by(RoomModel.name, RoomModel.id)
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def find_by_id(self, room_id: str) -> Room | None:
        with self._session_factory() as session:
            statement = (
                select(RoomModel)
                .where(RoomModel.id == room_id)
                .options(joinedload(RoomModel.site))
            )

            model = session.execute(statement).scalar_one_or_none()

            if model is None:
                return None

            return self._to_domain(model)

    def list_racks(self, room_id: str) -> list[Rack]:
        with self._session_factory() as session:
            statement = (
                select(RackModel)
                .where(RackModel.room_id == room_id)
                .order_by(RackModel.code)
            )

            models = session.execute(statement).scalars().all()

            return [
                Rack(
                    id=model.id,
                    room_id=model.room_id,
                    code=model.code,
                    name=model.name,
                    capacity_u=model.capacity_u,
                    room=None,
                )
                for model in models
            ]

    def add(self, room: Room) -> Room:
        try:
            with self._session_factory() as session:
                model = RoomModel(
                    id=room.id,
                    site_id=room.site_id,
                    code=room.code,
                    name=room.name,
                )

                session.add(model)
                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def update(
        self,
        room_id: str,
        changes: dict[str, str],
    ) -> Room | None:
        try:
            with self._session_factory() as session:
                model = session.get(RoomModel, room_id)

                if model is None:
                    return None

                if "site_id" in changes:
                    model.site_id = changes["site_id"]

                if "code" in changes:
                    model.code = changes["code"]

                if "name" in changes:
                    model.name = changes["name"]

                session.commit()

                # Đọc lại quan hệ theo site_id hiện tại.
                session.expire(model, ["site"])

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def delete(self, room_id: str) -> bool:
        try:
            with self._session_factory() as session:
                model = session.get(RoomModel, room_id)

                if model is None:
                    return False

                session.delete(model)
                session.commit()

                return True
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error, deleting=True)