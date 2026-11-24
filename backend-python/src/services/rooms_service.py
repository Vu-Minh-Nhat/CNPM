from uuid import UUID, uuid4

from src.domain.exceptions import (
    ResourceNotFoundError,
    ValidationError,
)
from src.domain.models.asset import Rack, Room
from src.domain.repositories.room_repository import RoomRepository
from src.domain.repositories.site_repository import SiteRepository


class RoomsService:
    def __init__(
        self,
        rooms: RoomRepository,
        sites: SiteRepository,
    ):
        self._rooms = rooms
        self._sites = sites

    @staticmethod
    def _validate_id(value: str, label: str) -> str:
        try:
            return str(UUID(value))
        except (ValueError, TypeError, AttributeError) as error:
            raise ValidationError(
                f"{label} phải là UUID hợp lệ."
            ) from error

    @classmethod
    def _validate_payload(
        cls,
        data: object,
        partial: bool = False,
    ) -> dict[str, str]:
        if not isinstance(data, dict):
            raise ValidationError("Dữ liệu phải là JSON object.")

        allowed_fields = {"siteId", "code", "name"}

        if set(data) - allowed_fields:
            raise ValidationError("Dữ liệu chứa trường không được hỗ trợ.")

        if not data:
            raise ValidationError("Cần cung cấp dữ liệu.")

        if not partial and not allowed_fields.issubset(data):
            raise ValidationError(
                "siteId, mã và tên Room là bắt buộc."
            )

        result = {}

        for field, maximum in (("code", 64), ("name", 200)):
            if field not in data:
                continue

            value = data[field]

            if not isinstance(value, str) or not value.strip():
                raise ValidationError(
                    f"{field} phải là chuỗi không rỗng."
                )

            value = value.strip()

            if len(value) > maximum:
                raise ValidationError(
                    f"{field} không được vượt quá {maximum} ký tự."
                )

            result[field] = value

        if "siteId" in data:
            result["site_id"] = cls._validate_id(
                data["siteId"],
                "siteId",
            )

        return result

    def list_rooms(self) -> list[Room]:
        return self._rooms.list_rooms()

    def get_room(self, room_id: str) -> Room:
        normalized_id = self._validate_id(room_id, "ID Room")
        room = self._rooms.find_by_id(normalized_id)

        if room is None:
            raise ResourceNotFoundError("Không tìm thấy Room.")

        return room

    def get_details(self, room_id: str) -> tuple[Room, list[Rack]]:
        room = self.get_room(room_id)
        racks = self._rooms.list_racks(room.id)

        return room, racks

    def create(self, data: object) -> Room:
        values = self._validate_payload(data)
        site = self._sites.find_by_id(values["site_id"])

        if site is None:
            raise ValidationError("Site không tồn tại.")

        room = Room(
            id=str(uuid4()),
            site_id=site.id,
            code=values["code"],
            name=values["name"],
            site=site,
        )

        return self._rooms.add(room)

    def update(self, room_id: str, data: object) -> Room:
        normalized_id = self._validate_id(room_id, "ID Room")
        values = self._validate_payload(data, partial=True)

        if self._rooms.find_by_id(normalized_id) is None:
            raise ResourceNotFoundError("Không tìm thấy Room.")

        if "site_id" in values:
            site = self._sites.find_by_id(values["site_id"])

            if site is None:
                raise ValidationError("Site không tồn tại.")

        room = self._rooms.update(normalized_id, values)

        if room is None:
            raise ResourceNotFoundError("Không tìm thấy Room.")

        return room

    def delete(self, room_id: str) -> None:
        normalized_id = self._validate_id(room_id, "ID Room")
        deleted = self._rooms.delete(normalized_id)

        if not deleted:
            raise ResourceNotFoundError("Không tìm thấy Room.")