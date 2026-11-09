from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from src.domain.models.asset import Node, Rack, Room, Site, Workload
from src.domain.repositories.asset_repository import AssetRepository
from src.infrastructure.models import NodeModel, RackModel, RoomModel


class SqlAlchemyAssetRepository(AssetRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

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

        workloads = tuple(
            Workload(
                id=workload.id,
                node_id=workload.node_id,
                code=workload.code,
                name=workload.name,
                runtime_id=workload.runtime_id,
            )
            for workload in model.workloads
        )

        return Node(
            id=model.id,
            rack_id=model.rack_id,
            code=model.code,
            name=model.name,
            serial_number=model.serial_number,
            rack=rack,
            workloads=workloads,
        )

    def list_nodes(self) -> list[Node]:
        with self._session_factory() as session:
            statement = (
                select(NodeModel)
                .options(
                    joinedload(NodeModel.rack)
                    .joinedload(RackModel.room)
                    .joinedload(RoomModel.site),
                    selectinload(NodeModel.workloads),
                )
                .order_by(NodeModel.code)
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]