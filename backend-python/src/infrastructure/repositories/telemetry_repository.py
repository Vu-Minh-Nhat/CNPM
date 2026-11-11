from collections.abc import Callable
from datetime import datetime, timezone
from typing import NoReturn
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DataError, DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from src.domain.exceptions import (
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.telemetry import (
    TelemetryRecord,
    TelemetrySample,
)
from src.domain.repositories.telemetry_repository import (
    TelemetryRepository,
)
from src.infrastructure.models import TelemetryModel


class SqlAlchemyTelemetryRepository(TelemetryRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _normalize_id(value: str, label: str) -> str:
        if not isinstance(value, str):
            raise ValidationError(f"{label} phải là UUID hợp lệ.")

        try:
            return str(UUID(value))
        except (ValueError, TypeError, AttributeError) as error:
            raise ValidationError(
                f"{label} phải là UUID hợp lệ."
            ) from error

    @staticmethod
    def _normalize_time(value: datetime, label: str) -> datetime:
        if not isinstance(value, datetime) or value.utcoffset() is None:
            raise ValidationError(
                f"{label} phải là datetime có múi giờ."
            )

        return value.astimezone(timezone.utc)

    @staticmethod
    def _normalize_percent(value: float, label: str) -> float:
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not 0 <= value <= 100
        ):
            raise ValidationError(
                f"{label} phải là số hữu hạn từ 0 đến 100."
            )

        return float(value)

    @staticmethod
    def _to_domain(model: TelemetryModel) -> TelemetryRecord:
        return TelemetryRecord(
            id=model.id,
            message_id=model.message_id,
            node_id=model.node_id,
            measured_at=model.measured_at.astimezone(timezone.utc),
            received_at=model.received_at.astimezone(timezone.utc),
            cpu_percent=model.cpu_percent,
            memory_percent=model.memory_percent,
            disk_percent=model.disk_percent,
        )

    @staticmethod
    def _same_payload(model: TelemetryModel, values: dict) -> bool:
        return (
            model.measured_at.astimezone(timezone.utc)
            == values["measured_at"]
            and model.cpu_percent == values["cpu_percent"]
            and model.memory_percent == values["memory_percent"]
            and model.disk_percent == values["disk_percent"]
        )

    @staticmethod
    def _raise_write_error(error: DBAPIError) -> NoReturn:
        code = getattr(error.orig, "sqlstate", None)

        if code == "23503":
            raise ValidationError(
                "Node không tồn tại."
            ) from error

        if code == "23505":
            raise ResourceConflictError(
                "Định danh telemetry đã tồn tại."
            ) from error

        if code in {"23502", "23514", "22001", "22P02"}:
            raise ValidationError(
                "Dữ liệu telemetry không hợp lệ."
            ) from error

        raise error

    def save(self, sample: TelemetrySample) -> TelemetryRecord:
        if not isinstance(sample, TelemetrySample):
            raise ValidationError(
                "Dữ liệu phải là TelemetrySample."
            )

        values = {
            "message_id": self._normalize_id(
                sample.message_id, "message_id"
            ),
            "node_id": self._normalize_id(
                sample.node_id, "node_id"
            ),
            "measured_at": self._normalize_time(
                sample.measured_at, "measured_at"
            ),
            "cpu_percent": self._normalize_percent(
                sample.cpu_percent, "cpu_percent"
            ),
            "memory_percent": self._normalize_percent(
                sample.memory_percent, "memory_percent"
            ),
            "disk_percent": self._normalize_percent(
                sample.disk_percent, "disk_percent"
            ),
        }

        with self._session_factory() as session:
            try:
                with session.begin():
                    statement = (
                        insert(TelemetryModel)
                        .values(id=str(uuid4()), **values)
                        .on_conflict_do_nothing(
                            constraint="uq_node_telemetry_node_message"
                        )
                        .returning(TelemetryModel)
                    )

                    model = session.scalar(statement)

                    if model is None:
                        # Bản tin đã tồn tại: đọc lại, không ghi đè.
                        model = session.scalar(
                            select(TelemetryModel).where(
                                TelemetryModel.node_id
                                == values["node_id"],
                                TelemetryModel.message_id
                                == values["message_id"],
                            )
                        )

                        if model is None:
                            raise RuntimeError(
                                "Không đọc được bản tin sau khi phát hiện trùng."
                            )

                        if not self._same_payload(model, values):
                            raise ResourceConflictError(
                                "Cùng node_id và message_id "
                                "nhưng nội dung telemetry khác nhau."
                            )

                    result = self._to_domain(model)

                return result

            except (IntegrityError, DataError) as error:
                self._raise_write_error(error)

    def get_latest(self, node_id: str) -> TelemetryRecord | None:
        normalized_id = self._normalize_id(node_id, "node_id")

        statement = (
            select(TelemetryModel)
            .where(TelemetryModel.node_id == normalized_id)
            .order_by(
                TelemetryModel.measured_at.desc(),
                TelemetryModel.received_at.desc(),
                TelemetryModel.id.desc(),
            )
            .limit(1)
        )

        with self._session_factory() as session:
            model = session.scalar(statement)

            if model is None:
                return None

            return self._to_domain(model)

    def list_history(
        self,
        node_id: str,
        *,
        start: datetime,
        end: datetime,
        limit: int = 100,
    ) -> list[TelemetryRecord]:
        normalized_id = self._normalize_id(node_id, "node_id")
        normalized_start = self._normalize_time(start, "start")
        normalized_end = self._normalize_time(end, "end")

        if normalized_start >= normalized_end:
            raise ValidationError(
                "start phải nhỏ hơn end."
            )

        if type(limit) is not int or not 1 <= limit <= 1000:
            raise ValidationError(
                "limit phải là số nguyên từ 1 đến 1000."
            )

        statement = (
            select(TelemetryModel)
            .where(
                TelemetryModel.node_id == normalized_id,
                TelemetryModel.measured_at >= normalized_start,
                TelemetryModel.measured_at < normalized_end,
            )
            .order_by(
                TelemetryModel.measured_at.asc(),
                TelemetryModel.received_at.asc(),
                TelemetryModel.id.asc(),
            )
            .limit(limit)
        )

        with self._session_factory() as session:
            models = session.scalars(statement).all()

            return [
                self._to_domain(model)
                for model in models
            ]