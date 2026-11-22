from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.models.marker import Marker
from src.domain.repositories.marker_repository import MarkerRepository
from src.infrastructure.models.marker_model import MarkerModel


class SqlAlchemyMarkerRepository(MarkerRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    def create(self, marker: Marker) -> Marker:
        with self._session_factory() as session:
            model = MarkerModel(
                id=marker.id,
                marker_type=marker.marker_type,
                identifier=marker.identifier,
                node_id=marker.node_id,
                is_active=marker.is_active,
                created_at=marker.created_at,
                updated_at=marker.updated_at,
            )

            session.add(model)
            session.commit()
            session.refresh(model)

            return self._to_domain(model)

    def get_by_id(self, marker_id: str) -> Marker | None:
        with self._session_factory() as session:
            model = session.get(MarkerModel, marker_id)

            if model is None:
                return None

            return self._to_domain(model)

    def get_by_identifier(
        self,
        marker_type: str,
        identifier: str,
    ) -> Marker | None:
        with self._session_factory() as session:
            statement = select(MarkerModel).where(
                MarkerModel.marker_type == marker_type,
                MarkerModel.identifier == identifier,
            )

            model = session.scalar(statement)

            if model is None:
                return None

            return self._to_domain(model)

    def list_all(self) -> list[Marker]:
        with self._session_factory() as session:
            statement = select(MarkerModel).order_by(
                MarkerModel.created_at.desc()
            )

            models = session.scalars(statement).all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def update(self, marker: Marker) -> Marker:
        with self._session_factory() as session:
            model = session.get(MarkerModel, marker.id)

            if model is None:
                raise ValueError(f"Marker not found: {marker.id}")

            model.marker_type = marker.marker_type
            model.identifier = marker.identifier
            model.node_id = marker.node_id
            model.is_active = marker.is_active
            model.updated_at = marker.updated_at

            session.commit()
            session.refresh(model)

            return self._to_domain(model)

    @staticmethod
    def _to_domain(model: MarkerModel) -> Marker:
        return Marker(
            id=model.id,
            marker_type=model.marker_type,
            identifier=model.identifier,
            node_id=model.node_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )