
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from src.domain.models.agent import Agent
from src.domain.repositories.agent_repository import AgentRepository
from src.domain.repositories.asset_repository import AssetRepository


class AgentService:

    def __init__(
        self,
        repository: AgentRepository,
        assets: AssetRepository,
    ):
        self.repository = repository
        self.assets = assets

    def register_agent(
        self,
        name: str,
        certificate_fingerprint: str,
    ) -> Agent:
        name = name.strip()
        certificate_fingerprint = (
            certificate_fingerprint.strip().lower()
        )

        if not name:
            raise ValueError("Agent name is required")

        if len(name) > 128:
            raise ValueError("Agent name must not exceed 128 characters")

        if (
            len(certificate_fingerprint) != 64
            or any(
                char not in "0123456789abcdef"
                for char in certificate_fingerprint
            )
        ):
            raise ValueError("Invalid certificate fingerprint")

        existing = self.repository.get_by_fingerprint(
            certificate_fingerprint
        )

        if existing is not None:
            raise ValueError("Agent certificate already registered")

        now = datetime.now(timezone.utc)

        agent = Agent(
            id=str(uuid4()),
            name=name,
            certificate_fingerprint=certificate_fingerprint,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        try:
            return self.repository.create(agent)
        except IntegrityError as exc:
            raise ValueError(
                "Agent certificate already registered"
            ) from exc

    def get_agent(self, agent_id: str) -> Agent | None:
        return self.repository.get_by_id(agent_id.strip())

    def authenticate_agent(
        self,
        certificate_fingerprint: str,
    ) -> Agent | None:
        fingerprint = certificate_fingerprint.strip().lower()

        if (
            len(fingerprint) != 64
            or any(
                char not in "0123456789abcdef"
                for char in fingerprint
            )
        ):
            return None

        agent = self.repository.get_by_fingerprint(fingerprint)

        if agent is None or not agent.is_active:
            return None

        return agent

    def assign_node(
        self,
        agent_id: str,
        node_id: str,
    ):
        agent_id = agent_id.strip()
        node_id = node_id.strip()

        agent = self.repository.get_by_id(agent_id)

        if agent is None:
            raise ValueError("Agent not found")

        if not agent.is_active:
            raise ValueError("Cannot assign Node to inactive Agent")

        node = self.assets.get_by_id(node_id)

        if node is None:
            raise ValueError("Node not found")

        return self.repository.assign_node(agent_id, node_id)

    def revoke_node(
        self,
        agent_id: str,
        node_id: str,
    ) -> bool:
        agent = self.repository.get_by_id(agent_id.strip())

        if agent is None:
            raise ValueError("Agent not found")

        return self.repository.revoke_node(
            agent.id,
            node_id.strip(),
        )

    def has_node_access(
        self,
        agent_id: str,
        node_id: str,
    ) -> bool:
        agent = self.repository.get_by_id(agent_id)

        if agent is None or not agent.is_active:
            return False

        return self.repository.has_node_access(agent_id, node_id)

    def deactivate_agent(self, agent_id: str) -> Agent:
        agent = self.repository.get_by_id(agent_id.strip())

        if agent is None:
            raise ValueError("Agent not found")

        if not agent.is_active:
            return agent

        updated_agent = Agent(
            id=agent.id,
            name=agent.name,
            certificate_fingerprint=agent.certificate_fingerprint,
            is_active=False,
            created_at=agent.created_at,
            updated_at=datetime.now(timezone.utc),
        )

        return self.repository.update(updated_agent)

    def activate_agent(self, agent_id: str) -> Agent:
        agent = self.repository.get_by_id(agent_id.strip())

        if agent is None:
            raise ValueError("Agent not found")

        if agent.is_active:
            return agent

        updated_agent = Agent(
            id=agent.id,
            name=agent.name,
            certificate_fingerprint=agent.certificate_fingerprint,
            is_active=True,
            created_at=agent.created_at,
            updated_at=datetime.now(timezone.utc),
        )

        return self.repository.update(updated_agent)

    def list_agents(self) -> list[Agent]:
        return self.repository.list_all()

    def list_agent_nodes(self, agent_id: str) -> list[str]:
        agent = self.repository.get_by_id(agent_id.strip())

        if agent is None:
            raise ValueError("Agent not found")

        return self.repository.list_node_access(agent.id)
