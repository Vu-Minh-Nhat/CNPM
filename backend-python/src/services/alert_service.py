from datetime import datetime, timezone
from uuid import UUID

from src.domain.constants import AlertStatus
from src.domain.exceptions import ResourceNotFoundError, ValidationError
from src.domain.models.alert import Alert
from src.domain.repositories.alert_repository import AlertRepository


class AlertService:
    def __init__(self, alerts: AlertRepository):
        self._alerts = alerts

    @staticmethod
    def _public_alert(alert: Alert) -> dict:
        return {
            "id": alert.id,
            "nodeId": alert.node_id,
            "ruleId": alert.rule_id,
            "metric": alert.metric,
            "operator": alert.operator,
            "threshold": alert.threshold,
            "severity": alert.severity,
            "status": alert.status,
            "message": alert.message,
            "triggeredAt": alert.triggered_at.isoformat(),
            "acknowledgedAt": (
                alert.acknowledged_at.isoformat()
                if alert.acknowledged_at else None
            ),
            "recoveredAt": (
                alert.recovered_at.isoformat()
                if alert.recovered_at else None
            ),
        }

    def list_alerts(self) -> list[dict]:
        return [
            self._public_alert(alert)
            for alert in self._alerts.list_all()
        ]

    def acknowledge(self, alert_id: str) -> dict:
        try:
            normalized_id = str(UUID(alert_id))
        except (ValueError, TypeError, AttributeError) as error:
            raise ValidationError("Alert ID không hợp lệ.") from error

        alert = self._alerts.find_by_id(normalized_id)

        if alert is None:
            raise ResourceNotFoundError("Không tìm thấy cảnh báo.")

        if alert.status != AlertStatus.FIRING:
            raise ValidationError(
                "Chỉ có thể xác nhận cảnh báo đang kích hoạt."
            )

        updated = Alert(
            id=alert.id,
            node_id=alert.node_id,
            rule_id=alert.rule_id,
            metric=alert.metric,
            operator=alert.operator,
            threshold=alert.threshold,
            severity=alert.severity,
            status=AlertStatus.ACKNOWLEDGED,
            message=alert.message,
            triggered_at=alert.triggered_at,
            acknowledged_at=datetime.now(timezone.utc),
            recovered_at=alert.recovered_at,
        )

        return self._public_alert(self._alerts.update(updated))
    