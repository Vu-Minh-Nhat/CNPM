from uuid import uuid4

from src.create_app import create_app
from src.domain.exceptions import ValidationError
from src.infrastructure.repositories.rack_repository import (
    SqlAlchemyRackRepository,
)
from src.infrastructure.repositories.server_repository import (
    SqlAlchemyServerRepository,
)
from src.services.servers_service import ServersService


def check_servers() -> None:
    app = create_app()
    database = app.extensions["database"]

    service = ServersService(
        servers=SqlAlchemyServerRepository(
            session_factory=database.create_session,
        ),
        racks=SqlAlchemyRackRepository(
            session_factory=database.create_session,
        ),
    )

    try:
        servers = service.list_servers()
        print(f"Số Server: {len(servers)}")

        server = next(
            (item for item in servers if item.code == "DEMO-NODE-01"),
            None,
        )

        if server is None:
            raise RuntimeError("Không tìm thấy Server demo.")

        detail = service.get_server(server.id)

        print(f"Server: {detail.code}")
        print(f"Rack: {detail.rack.code if detail.rack else 'Chưa có'}")

        for workload in detail.workloads:
            print(f"Workload: {workload.code}")

        try:
            service.update(
                server.id,
                {"rackId": str(uuid4())},
            )
        except ValidationError:
            print("Rack không tồn tại bị từ chối: OK")
        else:
            raise RuntimeError("Chưa từ chối Rack không tồn tại.")

        after = service.get_server(server.id)

        if after.rack_id != detail.rack_id:
            raise RuntimeError("Quan hệ Rack đã thay đổi sai.")

        print("Quan hệ Rack được giữ nguyên: OK")
        print("Server Repository và Service: OK")
    finally:
        database.dispose()


if __name__ == "__main__":
    check_servers()