from uuid import uuid4

from src.create_app import create_app
from src.domain.exceptions import ValidationError
from src.infrastructure.repositories.room_repository import (
    SqlAlchemyRoomRepository,
)
from src.infrastructure.repositories.site_repository import (
    SqlAlchemySiteRepository,
)
from src.services.rooms_service import RoomsService


def check_rooms() -> None:
    app = create_app()
    database = app.extensions["database"]

    service = RoomsService(
        rooms=SqlAlchemyRoomRepository(
            session_factory=database.create_session,
        ),
        sites=SqlAlchemySiteRepository(
            session_factory=database.create_session,
        ),
    )

    try:
        rooms = service.list_rooms()
        print(f"Số Room: {len(rooms)}")

        if not rooms:
            raise RuntimeError("Chưa có Room để kiểm tra.")

        room, racks = service.get_details(rooms[0].id)

        print(f"Room: {room.code}")
        print(f"Site: {room.site.code if room.site else 'Chưa có'}")
        print(f"Số Rack: {len(racks)}")

        original_site_id = room.site_id

        try:
            service.update(
                room.id,
                {"siteId": str(uuid4())},
            )
        except ValidationError:
            print("Site không tồn tại bị từ chối: OK")
        else:
            raise RuntimeError("Chưa từ chối Site không tồn tại.")

        after = service.get_room(room.id)

        if after.site_id != original_site_id:
            raise RuntimeError("Quan hệ Site đã bị thay đổi sai.")

        print("Quan hệ Site được giữ nguyên: OK")
        print("Room Repository và Service: OK")
    finally:
        database.dispose()


if __name__ == "__main__":
    check_rooms()