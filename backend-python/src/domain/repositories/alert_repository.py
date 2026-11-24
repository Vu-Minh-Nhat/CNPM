
from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.models.alert import Alert
from src.domain.models.alert_rule import AlertRule


class AlertRepository(ABC):

    # ---------------------------------------------------------
    # Alert Rule
    # ---------------------------------------------------------

    @abstractmethod
    def save_rule(self, rule: AlertRule) -> AlertRule:
        raise NotImplementedError

    @abstractmethod
    def update_rule(
        self,
        rule_id: str,
        changes: dict,
    ) -> AlertRule | None:
        raise NotImplementedError

    @abstractmethod
    def find_rule_by_id(
        self,
        rule_id: str,
    ) -> AlertRule | None:
        raise NotImplementedError

    @abstractmethod
    def list_rules(self) -> list[AlertRule]:
        raise NotImplementedError

    @abstractmethod
    def list_active_rules(self) -> list[AlertRule]:
        raise NotImplementedError

    @abstractmethod
    def set_rule_active(
        self,
        rule_id: str,
        is_active: bool,
    ) -> AlertRule | None:
        raise NotImplementedError

    # ---------------------------------------------------------
    # Alert
    # ---------------------------------------------------------

    @abstractmethod
    def save(self, alert: Alert) -> Alert:
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        alert_id: str,
        changes: dict,
    ) -> Alert | None:
        raise NotImplementedError

    @abstractmethod
    def recover(
        self,
        alert_id: str,
        recovered_at: datetime,
    ) -> Alert | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(
        self,
        alert_id: str,
    ) -> Alert | None:
        raise NotImplementedError

    @abstractmethod
    def find_active_by_node_and_rule(
        self,
        node_id: str,
        rule_id: str,
    ) -> Alert | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_node(
        self,
        node_id: str,
        status: str | None = None,
    ) -> list[Alert]:
        raise NotImplementedError

    @abstractmethod
    def list_active_by_node(
        self,
        node_id: str,
    ) -> list[Alert]:
        raise NotImplementedError

    @abstractmethod
    def list_active_by_rule(
        self,
        rule_id: str,
    ) -> list[Alert]:
        raise NotImplementedError
