from collections.abc import Callable
from datetime import datetime, timezone
from uuid import UUID

from src.domain.exceptions import (
    ResourceNotFoundError,
    ValidationError,
)
from src.domain.models.node_monitoring import (
    evaluate_node_monitoring,
)
from src.domain.models.telemetry import TelemetryRecord
from src.domain.repositories.server_repository import ServerRepository
from src.domain.repositories.telemetry_repository import (
    TelemetryRepository,
)


class TelemetryQueryService:
    def __init__(
        self,
        telemetry_repository: TelemetryRepository,
        server_repository: ServerRepository,
        *,
        stale_after_seconds: int = 30,
        offline_after_seconds: int = 90,
        poll_interval_seconds: int = 5,
        clock: Callable[[], datetime] | None = None,
    ):
        for label, value in (
            ("stale_after_seconds", stale_after_seconds),
            ("offline_after_seconds", offline_after_seconds),
            ("poll_interval_seconds", poll_interval_seconds),
        ):
            if type(value) is not int or value <= 0:
                raise ValidationError(
                    f"{label} phải là số nguyên lớn hơn 0."
                )

        self._telemetry = telemetry_repository
        self._servers = server_repository
        self._stale_after = stale_after_seconds
        self._offline_after = offline_after_seconds
        self._poll_interval = poll_interval_seconds
        self._clock = clock or (
            lambda: datetime.now(timezone.utc)
        )

    @staticmethod
    def _utc(value: datetime, label: str) -> datetime:
        if (
            not isinstance(value, datetime)
            or value.utcoffset() is None
        ):
            raise ValidationError(
                f"{label} phải là datetime có múi giờ."
            )

        return value.astimezone(timezone.utc)

    def _require_node(self, node_id: str) -> str:
        try:
            normalized_id = str(UUID(node_id))
        except (ValueError, TypeError, AttributeError) as error:
            raise ValidationError(
                "node_id phải là UUID hợp lệ."
            ) from error

        if self._servers.find_by_id(normalized_id) is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Node."
            )

        return normalized_id

    @staticmethod
    def _record_response(record: TelemetryRecord) -> dict:
        return {
            "id": record.id,
            "message_id": record.message_id,
            "node_id": record.node_id,
            "measured_at": record.measured_at.isoformat(),
            "received_at": record.received_at.isoformat(),
            "cpu_percent": record.cpu_percent,
            "memory_percent": record.memory_percent,
            "disk_percent": record.disk_percent,
        }

    def get_latest(self, node_id: str) -> dict:
        normalized_id = self._require_node(node_id)

        latest = self._telemetry.get_latest(normalized_id)
        last_received = self._telemetry.get_last_received_at(
            normalized_id
        )

        # Tính tại thời điểm đọc, không phụ thuộc có bản tin mới.
        now = self._utc(self._clock(), "server_time")

        state = evaluate_node_monitoring(
            now=now,
            last_received_at=last_received,
            last_measured_at=(
                latest.measured_at if latest else None
            ),
            stale_after_seconds=self._stale_after,
            offline_after_seconds=self._offline_after,
        )

        return {
            "node_id": normalized_id,
            "server_time": now.isoformat(),
            "latest": (
                self._record_response(latest)
                if latest is not None
                else None
            ),
            "monitoring": {
                "connection_status": state.connection_status,
                "data_status": state.data_status,
                "last_received_at": (
                    self._utc(
                        last_received, "last_received_at"
                    ).isoformat()
                    if last_received is not None
                    else None
                ),
                "last_measured_at": (
                    latest.measured_at.isoformat()
                    if latest is not None
                    else None
                ),
                "seconds_since_received": (
                    state.seconds_since_received
                ),
                "seconds_since_measured": (
                    state.seconds_since_measured
                ),
                "stale_after_seconds": self._stale_after,
                "offline_after_seconds": self._offline_after,
            },
            "poll_interval_seconds": self._poll_interval,
        }

    def get_history(
        self,
        node_id: str,
        *,
        start: datetime,
        end: datetime,
        limit: int = 1000,
    ) -> dict:
        normalized_id = self._require_node(node_id)

        start = self._utc(start, "start")
        end = self._utc(end, "end")

        if start >= end:
            raise ValidationError(
                "start phải nhỏ hơn end."
            )

        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValidationError(
                "limit phải là số nguyên từ 1 đến 1000."
            )

        records = self._telemetry.list_history(
            normalized_id,
            start=start,
            end=end,
            limit=limit,
        )

        return {
            "node_id": normalized_id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": limit,
            "count": len(records),
            "limit_reached": len(records) == limit,
            "items": [
                self._record_response(record)
                for record in records
            ],
        }