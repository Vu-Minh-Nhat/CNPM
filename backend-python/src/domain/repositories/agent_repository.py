
from abc import ABC, abstractmethod

from src.domain.models.agent import Agent, AgentNodeAccess


class AgentRepository(ABC):

    @abstractmethod
    def create(self, agent: Agent) -> Agent:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, agent_id: str) -> Agent | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_fingerprint(
        self,
        fingerprint: str,
    ) -> Agent | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, agent: Agent) -> Agent:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Agent]:
        raise NotImplementedError

    @abstractmethod
    def assign_node(
        self,
        agent_id: str,
        node_id: str,
    ) -> AgentNodeAccess:
        raise NotImplementedError

    @abstractmethod
    def revoke_node(
        self,
        agent_id: str,
        node_id: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def has_node_access(
        self,
        agent_id: str,
        node_id: str,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_node_access(
        self,
        agent_id: str,
    ) -> list[str]:
        raise NotImplementedError
