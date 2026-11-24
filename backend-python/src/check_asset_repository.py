from src.create_app import create_app
from src.infrastructure.repositories.asset_repository import (
    SqlAlchemyAssetRepository,
)


def check_repository() -> None:
    app = create_app()
    database = app.extensions["database"]

    repository = SqlAlchemyAssetRepository(
        session_factory=database.create_session,
    )

    try:
        nodes = repository.list_nodes()
        print(f"Số Node: {len(nodes)}")

        node = next(
            (item for item in nodes if item.code == "DEMO-NODE-01"),
            None,
        )

        if node is None:
            raise RuntimeError("Không tìm thấy Node demo.")

        print(f"Node: {node.code}")

        rack = node.rack
        room = rack.room if rack else None
        site = room.site if room else None

        print(f"Rack: {rack.code if rack else 'Chưa có'}")
        print(f"Room: {room.code if room else 'Chưa có'}")
        print(f"Site: {site.code if site else 'Chưa có'}")

        for workload in node.workloads:
            print(f"Workload: {workload.code}")

        print("Asset Repository: OK")
    finally:
        database.dispose()


if __name__ == "__main__":
    check_repository()