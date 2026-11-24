
import math
from datetime import datetime, timezone
from uuid import uuid4

from src.domain.exceptions import (
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

    PERCENT_METRICS = {
        "cpu_percent",
        "memory_percent",
        "disk_percent",
    }

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
        # Bước 1: Kiểm tra Rule tồn tại.
        current = self._repository.find_rule_by_id(rule_id)

        if current is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert Rule."
            )

        # Bước 2: Vô hiệu hóa Rule.
        rule = self._repository.set_rule_active(
            rule_id,
            False,
        )

        if rule is None:
            raise ResourceNotFoundError(
                "Không tìm thấy Alert Rule."
            )

        # Bước 3: Lấy tất cả Alert đang hoạt động thuộc Rule.
        active_alerts = self._repository.list_active_by_rule(
            rule_id
        )

        # Bước 4: Phục hồi các Alert khi Rule bị vô hiệu hóa.
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

    def list_node_alerts(
        self,
        node_id: str,
        status: str | None = None,
    ) -> list[dict]:
        allowed_statuses = {
            "FIRING",
            "ACKNOWLEDGED",
            "RECOVERED",
        }

        if status is not None and status not in allowed_statuses:
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
            "severity": alert.severity,
            "status": alert.status,
            "message": alert.message,
            "triggered_at": alert.triggered_at.isoformat(),
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
