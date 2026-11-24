from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TelemetrySample:
    """Dữ liệu cần lưu, chưa có metadata do database tạo."""

    message_id: str
    node_id: str
    measured_at: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float


@dataclass(frozen=True, slots=True)
class TelemetryRecord(TelemetrySample):
    """Bản ghi đã được lưu trong database."""

    id: str
    received_at: datetime