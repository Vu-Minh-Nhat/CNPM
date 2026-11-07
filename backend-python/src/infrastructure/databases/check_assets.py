from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.create_app import create_app
from src.infrastructure.models import (
    NodeModel,
    RackModel,
    RoomModel,
)


def check_assets() -> None:
    app = create_app()
    database = app.extensions["database"]

    try:
        with database.create_session() as session:
            statement = (
                select(NodeModel)
                .where(NodeModel.code == "DEMO-NODE-01")
                .options(
                    joinedload(NodeModel.rack)
                    .joinedload(RackModel.room)
                    .joinedload(RoomModel.site),
                    selectinload(NodeModel.workloads),
                )
            )

            node = session.execute(statement).scalar_one_or_none()

            if node is None:
                print("Không tìm thấy DEMO-NODE-01.")
                return

            rack = node.rack
            room = rack.room if rack else None
            site = room.site if room else None

            print(f"Node: {node.code} — {node.name}")
            print(f"Serial: {node.serial_number or 'Chưa có'}")
            print(f"Rack: {rack.code if rack else 'Chưa có'}")
            print(f"Room: {room.code if room else 'Chưa có'}")
            print(f"Site: {site.code if site else 'Chưa có'}")

            if not node.workloads:
                print("Workload: Chưa có")
            else:
                for workload in node.workloads:
                    print(
                        f"Workload: {workload.code} — {workload.name}"
                    )
    finally:
        database.dispose()


if __name__ == "__main__":
    check_assets()