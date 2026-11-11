from datetime import datetime

from src.domain.models.telemetry import TelemetryRecord, TelemetrySample
from src.domain.repositories.telemetry_repository import TelemetryRepository


class TelemetryService:
    def __init__(self, telemetry_repository: TelemetryRepository):
        self._telemetry_repository = telemetry_repository

    def ingest(
        self,
        *,
        message_id: str,
        node_id: str,
        measured_at: datetime,
        cpu_percent: float,
        memory_percent: float,
        disk_percent: float,
    ) -> TelemetryRecord:
        sample = TelemetrySample(
            message_id=message_id,
            node_id=node_id,
            measured_at=measured_at,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_percent=disk_percent,
        )

        return self._telemetry_repository.save(sample)

    def get_latest(self, node_id: str) -> TelemetryRecord | None:
        return self._telemetry_repository.get_latest(node_id)