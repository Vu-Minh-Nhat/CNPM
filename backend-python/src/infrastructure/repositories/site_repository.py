from collections.abc import Callable
from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.exc import DataError, DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from src.domain.exceptions import (
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.asset import Site
from src.domain.repositories.site_repository import SiteRepository
from src.infrastructure.models import SiteModel


class SqlAlchemySiteRepository(SiteRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _to_domain(model: SiteModel) -> Site:
        return Site(
            id=model.id,
            code=model.code,
            name=model.name,
        )

    @staticmethod
    def _handle_write_error(error: DBAPIError) -> NoReturn:
        code = getattr(error.orig, "sqlstate", None)

        if code == "23505":
            raise ResourceConflictError(
                "Mã Site đã tồn tại."
            ) from error

        if code == "23503":
            raise ResourceConflictError(
                "Không thể xóa Site còn dữ liệu liên quan."
            ) from error

        if code in {"23502", "23514", "22001"}:
            raise ValidationError(
                "Dữ liệu Site không hợp lệ."
            ) from error

        raise error

    def list_sites(self) -> list[Site]:
        with self._session_factory() as session:
            statement = select(SiteModel).order_by(
                SiteModel.name,
                SiteModel.id,
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def find_by_id(self, site_id: str) -> Site | None:
        with self._session_factory() as session:
            model = session.get(SiteModel, site_id)

            if model is None:
                return None

            return self._to_domain(model)

    def add(self, site: Site) -> Site:
        try:
            with self._session_factory() as session:
                model = SiteModel(
                    id=site.id,
                    code=site.code,
                    name=site.name,
                )

                session.add(model)
                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def update(
        self,
        site_id: str,
        changes: dict[str, str],
    ) -> Site | None:
        try:
            with self._session_factory() as session:
                model = session.get(SiteModel, site_id)

                if model is None:
                    return None

                if "code" in changes:
                    model.code = changes["code"]

                if "name" in changes:
                    model.name = changes["name"]

                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def delete(self, site_id: str) -> bool:
        try:
            with self._session_factory() as session:
                model = session.get(SiteModel, site_id)

                if model is None:
                    return False

                session.delete(model)
                session.commit()

                return True
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)