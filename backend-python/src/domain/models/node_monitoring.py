from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.exceptions import ValidationError


@dataclass(frozen=True, slots=True)
class NodeMonitoringState:
    connection_status: str
    data_status: str
    seconds_since_received: float | None
    seconds_since_measured: float | None


def evaluate_node_monitoring(
    *,
    now: datetime,
    last_received_at: datetime | None,
    last_measured_at: datetime | None,
    stale_after_seconds: int = 30,
    offline_after_seconds: int = 90,
) -> NodeMonitoringState:
    """Tính trạng thái tại thời điểm được cung cấp, không truy vấn DB."""

    for label, value in (
        ("stale_after_seconds", stale_after_seconds),
        ("offline_after_seconds", offline_after_seconds),
    ):
        if type(value) is not int or value <= 0:
            raise ValidationError(
                f"{label} phải là số nguyên lớn hơn 0."
            )

    def to_utc(value: datetime, label: str) -> datetime:
        if (
            not isinstance(value, datetime)
            or value.utcoffset() is None
        ):
            raise ValidationError(
                f"{label} phải là datetime có múi giờ."
            )

        return value.astimezone(timezone.utc)

    checked_at = to_utc(now, "now")

    received_age = None
    measured_age = None

    if last_received_at is None:
        connection_status = "never_seen"
    else:
        received_at = to_utc(last_received_at, "last_received_at")
        received_age = (checked_at - received_at).total_seconds()

        if received_age < 0:
            connection_status = "unknown"
        elif received_age > offline_after_seconds:
            connection_status = "offline"
        else:
            connection_status = "online"

    if last_measured_at is None:
        data_status = "no_data"
    else:
        measured_at = to_utc(last_measured_at, "last_measured_at")
        measured_age = (checked_at - measured_at).total_seconds()

        if measured_age < 0:
            data_status = "invalid_time"
        elif measured_age > stale_after_seconds:
            data_status = "stale"
        else:
            data_status = "fresh"

    return NodeMonitoringState(
        connection_status=connection_status,
        data_status=data_status,
        seconds_since_received=received_age,
        seconds_since_measured=measured_age,
    )