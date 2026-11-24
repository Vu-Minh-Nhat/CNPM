
import math
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.exceptions import (
    ResourceConflictError,
    ResourceNotFoundError,
    ValidationError,
)
from src.domain.models.alert_rule import AlertRule
from src.domain.repositories.alert_repository import AlertRepository


class AlertService:
    SUPPORTED_METRICS = {
        "cpu_percent",
        "memory_percent",
        "disk_percent",
        "node_offline_seconds",
    }

    SUPPORTED_OPERATORS = {
        ">",
        ">=",
        "<",
        "<=",
    }

    SUPPORTED_SEVERITIES = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
    }

    SUPPORTED_STATUSES = {
        "FIRING",
        "ACKNOWLEDGED",
        "RECOVERED",
    }

    PERCENT_METRICS = {
        "cpu_percent",
        "memory_percent",
        "disk_percent",
    }

    DEFAULT_PAGE = 1
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    def __init__(self, repository: AlertRepository):
        self._repository = repository

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    @staticmethod
    def _validate_number(value, field_name: str) -> float:
        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            raise ValidationError(
                f"{field_name} phải là số."
            )

        number = float(value)

        if not math.isfinite(number):
            raise ValidationError(
                f"{field_name} phải là số hữu hạn."
            )

        if number < 0:
            raise ValidationError(
                f"{field_name} không được nhỏ hơn 0."
            )

        return number

    @classmethod
    def _validate_rule_data(cls, data: dict) -> dict:
        if not isinstance(data, dict):
            raise ValidationError(
                "Dữ liệu Alert Rule phải là object."
            )

        allowed_fields = {
            "metric",
            "operator",
            "threshold",
            "severity",
            "recovery_operator",
            "recovery_threshold",
        }

        unknown_fields = set(data) - allowed_fields

        if unknown_fields:
            raise ValidationError(
                "Alert Rule chứa trường không được hỗ trợ: "
                + ", ".join(sorted(unknown_fields))
            )

        required_fields = {
            "metric",
            "operator",
            "threshold",
            "severity",
            "recovery_operator",
            "recovery_threshold",
        }

        missing_fields = required_fields - set(data)

        if missing_fields:
            raise ValidationError(
                "Thiếu trường Alert Rule: "
                + ", ".join(sorted(missing_fields))
            )

        metric = data["metric"]

        if (
            not isinstance(metric, str)
            or metric not in cls.SUPPORTED_METRICS
        ):
            raise ValidationError(
                "Metric không được hỗ trợ."
            )

        operator = data["operator"]

        if (
            not isinstance(operator, str)
            or operator not in cls.SUPPORTED_OPERATORS
        ):
            raise ValidationError(
                "Operator không hợp lệ."
            )

        severity = data["severity"]

        if (
            not isinstance(severity, str)
            or severity not in cls.SUPPORTED_SEVERITIES
        ):
            raise ValidationError(
                "Severity phải là LOW, MEDIUM, HIGH hoặc CRITICAL."
            )

        threshold = cls._validate_number(
            data["threshold"],
            "threshold",
        )

        recovery_operator = data["recovery_operator"]
        recovery_threshold = data["recovery_threshold"]

        if (
            recovery_operator is None
            or recovery_threshold is None
        ):
            raise ValidationError(
                "Cần cấu hình recovery_operator và "
                "recovery_threshold."
            )

        if (
            not isinstance(recovery_operator, str)
            or recovery_operator not in cls.SUPPORTED_OPERATORS
        ):
            raise ValidationError(
                "recovery_operator không hợp lệ."
            )

        recovery_threshold = cls._validate_number(
            recovery_threshold,
            "recovery_threshold",
        )

        if metric in cls.PERCENT_METRICS:
            if threshold > 100:
                raise ValidationError(
                    "Threshold của metric phần trăm phải từ 0 đến 100."
                )

            if recovery_threshold > 100:
                raise ValidationError(
                    "Recovery threshold phải từ 0 đến 100."
                )

        return {
            "metric": metric,
            "operator": operator,
            "threshold": threshold,
            "severity": severity,
            "recovery_operator": recovery_operator,
            "recovery_threshold": recovery_threshold,
        }

    @staticmethod
    def _validate_pagination(
        page: int,
        page_size: int,
    ) -> None:
        if (
            isinstance(page, bool)
            or not isinstance(page, int)
            or page < 1
        ):
            raise ValidationError(
                "page phải là số nguyên lớn hơn hoặc bằng 1."
            )

        if (
            isinstance(page_size, bool)
            or not isinstance(page_size, int)
            or not 1 <= page_size <= 100
        ):
            raise ValidationError(
                "page_size phải nằm trong khoảng từ 1 đến 100."
            )

    # ---------------------------------------------------------
    # Rule operations
    # ---------------------------------------------------------

    def create_rule(self, data: dict) -> dict:
        values = self._validate_rule_data(data)

        now = datetime.now(timezone.utc)

        rule = AlertRule(
            id=str(uuid4()),
            metric=values["metric"],
            operator=values["operator"],
            threshold=values["threshold"],
            severity=values["severity"],
            recovery_operator=values["recovery_operator"],
            recovery_threshold=values["recovery_threshold"],
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        saved = self._repository.save_rule(rule)

        return self._rule_response(saved)

    def update_rule(
        self,
        rule_id: str,
        changes: dict,
    ) -> dict:
        current = self._repository.find_rule_by_id(rule_id)

        if current is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert Rule."
            )

        if not isinstance(changes, dict) or not changes:
            raise ValidationError(
                "Cần cung cấp dữ liệu cập nhật."
            )

        merged = {
            "metric": current.metric,
            "operator": current.operator,
            "threshold": current.threshold,
            "severity": current.severity,
            "recovery_operator": current.recovery_operator,
            "recovery_threshold": current.recovery_threshold,
        }

        merged.update(changes)

        values = self._validate_rule_data(merged)

        updated = self._repository.update_rule(
            rule_id,
            values,
        )

        if updated is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert Rule."
            )

        return self._rule_response(updated)

    def get_rule(self, rule_id: str) -> dict:
        rule = self._repository.find_rule_by_id(rule_id)

        if rule is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert Rule."
            )

        return self._rule_response(rule)

    def list_rules(self) -> list[dict]:
        return [
            self._rule_response(rule)
            for rule in self._repository.list_rules()
        ]

    def list_active_rules(self) -> list[AlertRule]:
        return self._repository.list_active_rules()

    def enable_rule(self, rule_id: str) -> dict:
        rule = self._repository.set_rule_active(
            rule_id,
            True,
        )

        if rule is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert Rule."
            )

        return self._rule_response(rule)

    def disable_rule(self, rule_id: str) -> dict:
        current = self._repository.find_rule_by_id(rule_id)

        if current is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert Rule."
            )

        rule = self._repository.set_rule_active(
            rule_id,
            False,
        )

        if rule is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert Rule."
            )

        active_alerts = self._repository.list_active_by_rule(
            rule_id
        )

        recovered_at = datetime.now(timezone.utc)

        for alert in active_alerts:
            self._repository.recover(
                alert.id,
                recovered_at,
            )

        return self._rule_response(rule)

    # ---------------------------------------------------------
    # Alert queries
    # ---------------------------------------------------------

    def get_alert(self, alert_id: str) -> dict:
        alert = self._repository.find_by_id(alert_id)

        if alert is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert."
            )

        return self._alert_response(alert)

    def list_alerts(
        self,
        node_id: str | None = None,
        metric: str | None = None,
        severity: str | None = None,
        status: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        page: int = DEFAULT_PAGE,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> dict:
        """
        Tra cứu Alert có lọc và phân trang.

        Thời gian lọc dựa trên triggered_at.
        """

        self._validate_pagination(page, page_size)

        alerts, total = self._repository.query_alerts(
            node_id=node_id,
            metric=metric,
            severity=severity,
            status=status,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size,
        )

        total_pages = math.ceil(total / page_size)

        return {
            "items": [
                self._alert_response(alert)
                for alert in alerts
            ],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
            },
        }

    def list_node_alerts(
        self,
        node_id: str,
        status: str | None = None,
    ) -> list[dict]:
        if status is not None and status not in self.SUPPORTED_STATUSES:
            raise ValidationError(
                "Trạng thái Alert không hợp lệ."
            )

        alerts = self._repository.list_by_node(
            node_id=node_id,
            status=status,
        )

        return [
            self._alert_response(alert)
            for alert in alerts
        ]

    def list_active_node_alerts(
        self,
        node_id: str,
    ) -> list[dict]:
        alerts = self._repository.list_active_by_node(
            node_id
        )

        return [
            self._alert_response(alert)
            for alert in alerts
        ]

    # ---------------------------------------------------------
    # Alert acknowledgement
    # ---------------------------------------------------------

    def acknowledge_alert(
        self,
        alert_id: str,
        actor_id: str,
    ) -> dict:
        """
        Xác nhận một Alert đang FIRING.

        Quyền Administrator/Operator được kiểm tra tại Controller.
        Repository chịu trách nhiệm khóa bản ghi, cập nhật trạng thái
        và ghi lịch sử trong cùng transaction.
        """

        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValidationError(
                "Không xác định được tài khoản xác nhận Alert."
            )

        acknowledged = self._repository.acknowledge(
            alert_id=alert_id,
            actor_id=actor_id,
            acknowledged_at=datetime.now(timezone.utc),
        )

        if acknowledged is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert."
            )

        return self._alert_response(acknowledged)

    # ---------------------------------------------------------
    # Response mapping
    # ---------------------------------------------------------

    @staticmethod
    def _rule_response(rule: AlertRule) -> dict:
        return {
            "id": rule.id,
            "metric": rule.metric,
            "operator": rule.operator,
            "threshold": rule.threshold,
            "severity": rule.severity,
            "recovery_operator": rule.recovery_operator,
            "recovery_threshold": rule.recovery_threshold,
            "is_active": rule.is_active,
            "created_at": rule.created_at.isoformat(),
            "updated_at": rule.updated_at.isoformat(),
        }

    @staticmethod
    def _alert_response(alert) -> dict:
        return {
            "id": alert.id,
            "node_id": alert.node_id,
            "rule_id": alert.rule_id,
            "metric": alert.metric,
            "operator": alert.operator,
            "threshold": alert.threshold,
            "triggered_value": alert.triggered_value,
            "severity": alert.severity,
            "status": alert.status,
            "message": alert.message,
            "triggered_at": alert.triggered_at.isoformat(),
            "acknowledged_by": alert.acknowledged_by,
            "acknowledged_at": (
                alert.acknowledged_at.isoformat()
                if alert.acknowledged_at is not None
                else None
            ),
            "recovered_at": (
                alert.recovered_at.isoformat()
                if alert.recovered_at is not None
                else None
            ),
        }
