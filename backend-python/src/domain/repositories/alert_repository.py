from abc import ABC, abstractmethod

from src.domain.models.alert import Alert
from src.domain.models.alert_rule import AlertRule


class AlertRepository(ABC):
    @abstractmethod
    def save_rule(self, rule: AlertRule) -> AlertRule:
        raise NotImplementedError

    @abstractmethod
    def find_rule_by_id(self, rule_id: str) -> AlertRule | None:
        raise NotImplementedError

    @abstractmethod
    def list_active_rules(self) -> list[AlertRule]:
        raise NotImplementedError

    @abstractmethod
    def save(self, alert: Alert) -> Alert:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, alert_id: str) -> Alert | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_node(
        self,
        node_id: str,
        status: str | None = None,
    ) -> list[Alert]:
        raise NotImplementedError

    @abstractmethod
    def list_active_by_node(self, node_id: str) -> list[Alert]:
        raise NotImplementedError
    
    @abstractmethod
    def list_all(self) -> list[Alert]:
        raise NotImplementedError

    @abstractmethod
    def update(self, alert: Alert) -> Alert:
        raise NotImplementedError