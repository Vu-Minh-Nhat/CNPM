from datetime import datetime, timezone
from uuid import uuid4

from src.domain.models.asset import Node
from src.domain.models.marker import Marker
from src.infrastructure.repositories.asset_repository import (
    SqlAlchemyAssetRepository,
)
from src.infrastructure.repositories.marker_repository import (
    SqlAlchemyMarkerRepository,
)


class MarkerService:
    def __init__(
        self,
        repository: SqlAlchemyMarkerRepository,
        assets: SqlAlchemyAssetRepository,
    ):
        self.repository = repository
        self.assets = assets

    def register_marker(
        self,
        marker_type: str,
        identifier: str,
        node_id: str,
    ) -> Marker:
        marker_type = marker_type.strip().upper()
        identifier = identifier.strip()
        node_id = node_id.strip()

        if not marker_type:
            raise ValueError("Marker type is required")

        if not identifier:
            raise ValueError("Marker identifier is required")

        if not node_id:
            raise ValueError("Node ID is required")

        node = self.assets.get_by_id(node_id)

        if node is None:
            raise ValueError("Node not found")

        existing = self.repository.get_by_identifier(
            marker_type,
            identifier,
        )

        if existing is not None and existing.is_active:
            raise ValueError("Active marker identifier already exists")

        now = datetime.now(timezone.utc)

        marker = Marker(
            id=str(uuid4()),
            marker_type=marker_type,
            identifier=identifier,
            node_id=node.id,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        return self.repository.create(marker)

    def lookup_marker(
        self,
        marker_type: str,
        identifier: str,
    ) -> tuple[Marker, Node] | None:
        marker_type = marker_type.strip().upper()
        identifier = identifier.strip()

        marker = self.repository.get_by_identifier(
            marker_type,
            identifier,
        )

        if marker is None or not marker.is_active:
            return None

        node = self.assets.get_by_id(marker.node_id)

        if node is None:
            return None

        return marker, node

    def deactivate_marker(self, marker_id: str) -> Marker:
        marker = self.repository.get_by_id(marker_id)

        if marker is None:
            raise ValueError("Marker not found")

        if not marker.is_active:
            return marker

        updated_marker = Marker(
            id=marker.id,
            marker_type=marker.marker_type,
            identifier=marker.identifier,
            node_id=marker.node_id,
            is_active=False,
            created_at=marker.created_at,
            updated_at=datetime.now(timezone.utc),
        )

        return self.repository.update(updated_marker)

    def list_markers(self) -> list[Marker]:
        return list(self.repository.list_all())