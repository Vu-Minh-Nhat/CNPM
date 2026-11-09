from uuid import uuid4

from src.create_app import create_app
from src.domain.exceptions import ValidationError
from src.infrastructure.repositories.rack_repository import (
    SqlAlchemyRackRepository,
)
from src.infrastructure.repositories.room_repository import (
    SqlAlchemyRoomRepository,
)
from src.services.racks_service import RacksService


def check_racks() -> None:
    app = create_app()
    database = app.extensions["database"]

    service = RacksService(
        racks=SqlAlchemyRackRepository(
            session_factory=database.create_session,
        ),
        rooms=SqlAlchemyRoomRepository(
            session_factory=database.create_session,
        ),
    )

    try:
        racks = service.list_racks()
        print(f"Số Rack: {len(racks)}")

        if not racks:
            raise RuntimeError("Chưa có Rack để kiểm tra.")

        rack, nodes = service.get_details(racks[0].id)

        print(f"Rack: {rack.code}")
        print(f"Room: {rack.room.code if rack.room else 'Chưa có'}")
        print(f"Capacity U: {rack.capacity_u}")
        print(f"Số Node: {len(nodes)}")

        for value in (0, 101, True, "42", 1.5, None):
            try:
                service.update(
                    rack.id,
                    {"capacityU": value},
                )
            except ValidationError:
                print(f"capacityU={value!r} bị từ chối: OK")
            else:
                raise RuntimeError(
                    f"Chưa từ chối capacityU={value!r}."
                )

        try:
            service.update(
                rack.id,
                {"roomId": str(uuid4())},
            )
        except ValidationError:
            print("Room không tồn tại bị từ chối: OK")
        else:
            raise RuntimeError("Chưa từ chối Room không tồn tại.")

        after = service.get_rack(rack.id)

        if (
            after.room_id != rack.room_id
            or after.capacity_u != rack.capacity_u
        ):
            raise RuntimeError("Dữ liệu Rack đã thay đổi sai.")

        print("Dữ liệu Rack được giữ nguyên: OK")
        print("Rack Repository và Service: OK")
    finally:
        database.dispose()


if __name__ == "__main__":
    check_racks()