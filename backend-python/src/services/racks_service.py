from uuid import UUID, uuid4

from src.domain.exceptions import (
    ResourceNotFoundError,
    ValidationError,
)
from src.domain.models.asset import Node, Rack
from src.domain.repositories.rack_repository import RackRepository
from src.domain.repositories.room_repository import RoomRepository


class RacksService:
    def __init__(
        self,
        racks: RackRepository,
        rooms: RoomRepository,
    ):
        self._racks = racks
        self._rooms = rooms

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
    ) -> dict[str, str | int]:
        if not isinstance(data, dict):
            raise ValidationError("Dữ liệu phải là JSON object.")

        allowed_fields = {"roomId", "code", "name", "capacityU"}

        if set(data) - allowed_fields:
            raise ValidationError(
                "Dữ liệu chứa trường không được hỗ trợ."
            )

        if not data:
            raise ValidationError("Cần cung cấp dữ liệu.")

        if not partial and not allowed_fields.issubset(data):
            raise ValidationError(
                "roomId, mã, tên và capacityU là bắt buộc."
            )

        result: dict[str, str | int] = {}

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

        if "roomId" in data:
            result["room_id"] = cls._validate_id(
                data["roomId"],
                "roomId",
            )

        if "capacityU" in data:
            capacity = data["capacityU"]

            if type(capacity) is not int or not 1 <= capacity <= 100:
                raise ValidationError(
                    "capacityU phải là số nguyên từ 1 đến 100."
                )

            result["capacity_u"] = capacity

        return result

    def list_racks(self) -> list[Rack]:
        return self._racks.list_racks()

    def get_rack(self, rack_id: str) -> Rack:
        normalized_id = self._validate_id(rack_id, "ID Rack")
        rack = self._racks.find_by_id(normalized_id)

        if rack is None:
            raise ResourceNotFoundError("Không tìm thấy Rack.")

        return rack

    def get_details(self, rack_id: str) -> tuple[Rack, list[Node]]:
        rack = self.get_rack(rack_id)
        nodes = self._racks.list_nodes(rack.id)

        return rack, nodes

    def create(self, data: object) -> Rack:
        values = self._validate_payload(data)

        room = self._rooms.find_by_id(
            str(values["room_id"])
        )

        if room is None:
            raise ValidationError("Room không tồn tại.")

        rack = Rack(
            id=str(uuid4()),
            room_id=room.id,
            code=str(values["code"]),
            name=str(values["name"]),
            capacity_u=int(values["capacity_u"]),
            room=room,
        )

        return self._racks.add(rack)

    def update(self, rack_id: str, data: object) -> Rack:
        normalized_id = self._validate_id(rack_id, "ID Rack")
        values = self._validate_payload(data, partial=True)

        if self._racks.find_by_id(normalized_id) is None:
            raise ResourceNotFoundError("Không tìm thấy Rack.")

        if "room_id" in values:
            room = self._rooms.find_by_id(
                str(values["room_id"])
            )

            if room is None:
                raise ValidationError("Room không tồn tại.")

        rack = self._racks.update(normalized_id, values)

        if rack is None:
            raise ResourceNotFoundError("Không tìm thấy Rack.")

        return rack

    def delete(self, rack_id: str) -> None:
        normalized_id = self._validate_id(rack_id, "ID Rack")
        deleted = self._racks.delete(normalized_id)

        if not deleted:
            raise ResourceNotFoundError("Không tìm thấy Rack.")