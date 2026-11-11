from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.models.telemetry import (
    TelemetryRecord,
    TelemetrySample,
)


class TelemetryRepository(ABC):
    @abstractmethod
    def save(self, sample: TelemetrySample) -> TelemetryRecord:
        """
        Lưu mẫu mới.

        Cùng Node và message_id, cùng nội dung:
        trả bản ghi đã có, không tạo thêm.

        Cùng Node và message_id nhưng khác nội dung:
        báo xung đột, không ghi đè.
        """
        raise NotImplementedError

    @abstractmethod
    def get_latest(self, node_id: str) -> TelemetryRecord | None:
        """
        Lấy mẫu có measured_at mới nhất.

        Nếu cùng thời điểm đo, sắp tiếp theo
        received_at và id để kết quả ổn định.
        """
        raise NotImplementedError

    @abstractmethod
    def list_history(
        self,
        node_id: str,
        *,
        start: datetime,
        end: datetime,
        limit: int = 100,
    ) -> list[TelemetryRecord]:
        """
        Lấy lịch sử trong khoảng start <= measured_at < end.

        Kết quả tăng dần theo measured_at, received_at, id.
        Timestamp phải có múi giờ.
        Limit hợp lệ từ 1 đến 1000.
        """
        raise NotImplementedError