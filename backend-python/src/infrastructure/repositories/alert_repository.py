from collections.abc import Callable
from typing import NoReturn
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DataError, DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from src.domain.exceptions import (
    ResourceConflictError,
    ValidationError,
)
from src.domain.models.alert import Alert
from src.domain.models.alert_rule import AlertRule
from src.domain.repositories.alert_repository import AlertRepository
from src.infrastructure.models import AlertModel, AlertRuleModel


class SqlAlchemyAlertRepository(AlertRepository):
    def __init__(self, session_factory: Callable[[], Session]):
        self._session_factory = session_factory

    @staticmethod
    def _to_rule_domain(model: AlertRuleModel) -> AlertRule:
        return AlertRule(
            id=str(model.id),
            metric=model.metric,
            operator=model.operator,
            threshold=model.threshold,
            severity=model.severity,
            recovery_operator=model.recovery_operator,
            recovery_threshold=model.recovery_threshold,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_domain(model: AlertModel) -> Alert:
        return Alert(
            id=str(model.id),
            node_id=str(model.node_id),
            rule_id=str(model.rule_id) if model.rule_id else None,
            metric=model.metric,
            operator=model.operator,
            threshold=model.threshold,
            severity=model.severity,
            status=model.status,
            message=model.message,
            triggered_at=model.triggered_at,
            acknowledged_at=model.acknowledged_at,
            recovered_at=model.recovered_at,
        )

    @staticmethod
    def _handle_write_error(error: DBAPIError) -> NoReturn:
        code = getattr(error.orig, "sqlstate", None)

        if code == "23505":
            raise ResourceConflictError(
                "Cảnh báo đang hoạt động đã tồn tại."
            ) from error

        if code == "23503":
            raise ValidationError(
                "Node hoặc alert rule không tồn tại."
            ) from error

        if code in {"23502", "23514", "22001", "22P02"}:
            raise ValidationError(
                "Dữ liệu cảnh báo không hợp lệ."
            ) from error

        raise error

    @staticmethod
    def _normalize_uuid(value: str) -> str | None:
        try:
            return str(UUID(value))
        except (ValueError, TypeError, AttributeError):
            return None

    def save_rule(self, rule: AlertRule) -> AlertRule:
        try:
            with self._session_factory() as session:
                model = AlertRuleModel(
                    id=rule.id,
                    metric=rule.metric,
                    operator=rule.operator,
                    threshold=rule.threshold,
                    severity=rule.severity,
                    recovery_operator=rule.recovery_operator,
                    recovery_threshold=rule.recovery_threshold,
                    is_active=rule.is_active,
                    created_at=rule.created_at,
                    updated_at=rule.updated_at,
                )

                session.add(model)
                session.commit()

                return self._to_rule_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def find_rule_by_id(self, rule_id: str) -> AlertRule | None:
        normalized_id = self._normalize_uuid(rule_id)

        if normalized_id is None:
            return None

        with self._session_factory() as session:
            model = session.get(AlertRuleModel, normalized_id)

            if model is None:
                return None

            return self._to_rule_domain(model)

    def list_active_rules(self) -> list[AlertRule]:
        with self._session_factory() as session:
            statement = (
                select(AlertRuleModel)
                .where(AlertRuleModel.is_active.is_(True))
                .order_by(AlertRuleModel.metric, AlertRuleModel.id)
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_rule_domain(model)
                for model in models
            ]

    def save(self, alert: Alert) -> Alert:
        try:
            with self._session_factory() as session:
                model = AlertModel(
                    id=alert.id,
                    node_id=alert.node_id,
                    rule_id=alert.rule_id,
                    metric=alert.metric,
                    operator=alert.operator,
                    threshold=alert.threshold,
                    severity=alert.severity,
                    status=alert.status,
                    message=alert.message,
                    triggered_at=alert.triggered_at,
                    acknowledged_at=alert.acknowledged_at,
                    recovered_at=alert.recovered_at,
                )

                session.add(model)
                session.commit()

                return self._to_domain(model)
        except (IntegrityError, DataError) as error:
            self._handle_write_error(error)

    def find_by_id(self, alert_id: str) -> Alert | None:
        normalized_id = self._normalize_uuid(alert_id)

        if normalized_id is None:
            return None

        with self._session_factory() as session:
            model = session.get(AlertModel, normalized_id)

            if model is None:
                return None

            return self._to_domain(model)

    def list_by_node(
        self,
        node_id: str,
        status: str | None = None,
    ) -> list[Alert]:
        normalized_id = self._normalize_uuid(node_id)

        if normalized_id is None:
            return []

        with self._session_factory() as session:
            statement = select(AlertModel).where(
                AlertModel.node_id == normalized_id
            )

            if status is not None:
                statement = statement.where(
                    AlertModel.status == status
                )

            statement = statement.order_by(
                AlertModel.triggered_at.desc(),
                AlertModel.id,
            )

            models = session.execute(statement).scalars().all()

            return [
                self._to_domain(model)
                for model in models
            ]

    def list_active_by_node(self, node_id: str) -> list[Alert]:
        return self.list_by_node(
            node_id=node_id,
            status="FIRING",
        ) + self.list_by_node(
            node_id=node_id,
            status="ACKNOWLEDGED",
        )