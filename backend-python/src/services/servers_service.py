from uuid import UUID, uuid4

from src.domain.exceptions import (
    ResourceNotFoundError,
    ValidationError,
)
from src.domain.models.asset import Node
from src.domain.repositories.rack_repository import RackRepository
from src.domain.repositories.server_repository import ServerRepository


class ServersService:
    def __init__(
        self,
        servers: ServerRepository,
        racks: RackRepository,
    ):
        self._servers = servers
        self._racks = racks

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
    ) -> dict[str, str | None]:
        if not isinstance(data, dict):
            raise ValidationError("Dữ liệu phải là JSON object.")

        allowed_fields = {"rackId", "code", "name", "serialNumber"}
        required_fields = {"rackId", "code", "name"}

        if set(data) - allowed_fields:
            raise ValidationError(
                "Dữ liệu chứa trường không được hỗ trợ."
            )

        if not data:
            raise ValidationError("Cần cung cấp dữ liệu.")

        if not partial and not required_fields.issubset(data):
            raise ValidationError(
                "rackId, mã và tên Server là bắt buộc."
            )

        result: dict[str, str | None] = {}

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

        if "rackId" in data:
            result["rack_id"] = cls._validate_id(
                data["rackId"],
                "rackId",
            )

        if "serialNumber" in data:
            serial = data["serialNumber"]

            if serial is None:
                result["serial_number"] = None
            else:
                if not isinstance(serial, str) or not serial.strip():
                    raise ValidationError(
                        "serialNumber phải là chuỗi không rỗng hoặc null."
                    )

                serial = serial.strip()

                if len(serial) > 128:
                    raise ValidationError(
                        "serialNumber không được vượt quá 128 ký tự."
                    )

                result["serial_number"] = serial

        return result

    def list_servers(self) -> list[Node]:
        return self._servers.list_servers()

    def get_server(self, server_id: str) -> Node:
        normalized_id = self._validate_id(server_id, "ID Server")
        server = self._servers.find_by_id(normalized_id)

        if server is None:
            raise ResourceNotFoundError("Không tìm thấy Server.")

        return server

    def create(self, data: object) -> Node:
        values = self._validate_payload(data)

        rack = self._racks.find_by_id(
            str(values["rack_id"])
        )

        if rack is None:
            raise ValidationError("Rack không tồn tại.")

        server = Node(
            id=str(uuid4()),
            rack_id=rack.id,
            code=str(values["code"]),
            name=str(values["name"]),
            serial_number=values.get("serial_number"),
            rack=rack,
            workloads=(),
        )

        return self._servers.add(server)

    def update(self, server_id: str, data: object) -> Node:
        normalized_id = self._validate_id(server_id, "ID Server")
        values = self._validate_payload(data, partial=True)

        if self._servers.find_by_id(normalized_id) is None:
            raise ResourceNotFoundError("Không tìm thấy Server.")

        if "rack_id" in values:
            rack = self._racks.find_by_id(
                str(values["rack_id"])
            )

            if rack is None:
                raise ValidationError("Rack không tồn tại.")

        server = self._servers.update(normalized_id, values)

        if server is None:
            raise ResourceNotFoundError("Không tìm thấy Server.")

        return server

    def delete(self, server_id: str) -> None:
        normalized_id = self._validate_id(server_id, "ID Server")
        deleted = self._servers.delete(normalized_id)

        if not deleted:
            raise ResourceNotFoundError("Không tìm thấy Server.")