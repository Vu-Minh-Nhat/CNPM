
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.domain.models.agent import Agent, AgentNodeAccess
from src.domain.repositories.agent_repository import AgentRepository
from src.infrastructure.models.agent_model import (
    AgentModel,
    AgentNodeAccessModel,
)


class SqlAlchemyAgentRepository(AgentRepository):

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def create(self, agent: Agent) -> Agent:
        with self.session_factory() as session:
            model = AgentModel(
                id=agent.id,
                name=agent.name,
                certificate_fingerprint=agent.certificate_fingerprint,
                is_active=agent.is_active,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
            )

            try:
                session.add(model)
                session.commit()
                session.refresh(model)
                return self._to_domain(model)
            except IntegrityError:
                session.rollback()
                raise

    def get_by_id(self, agent_id: str) -> Agent | None:
        with self.session_factory() as session:
            model = session.get(AgentModel, agent_id)

            if model is None:
                return None

            return self._to_domain(model)

    def get_by_fingerprint(
        self,
        fingerprint: str,
    ) -> Agent | None:
        with self.session_factory() as session:
            statement = select(AgentModel).where(
                AgentModel.certificate_fingerprint == fingerprint
            )

            model = session.scalar(statement)

            if model is None:
                return None

            return self._to_domain(model)

    def update(self, agent: Agent) -> Agent:
        with self.session_factory() as session:
            model = session.get(AgentModel, agent.id)

            if model is None:
                raise ValueError("Agent not found")

            model.name = agent.name
            model.certificate_fingerprint = agent.certificate_fingerprint
            model.is_active = agent.is_active
            model.updated_at = agent.updated_at

            try:
                session.commit()
                session.refresh(model)
                return self._to_domain(model)
            except IntegrityError:
                session.rollback()
                raise

    def list_all(self) -> list[Agent]:
        with self.session_factory() as session:
            statement = select(AgentModel).order_by(
                AgentModel.created_at.desc()
            )

            models = session.scalars(statement).all()

            return [self._to_domain(model) for model in models]

    def assign_node(
        self,
        agent_id: str,
        node_id: str,
    ) -> AgentNodeAccess:
        with self.session_factory() as session:
            existing = session.get(
                AgentNodeAccessModel,
                (agent_id, node_id),
            )

            if existing is not None:
                return AgentNodeAccess(
                    agent_id=existing.agent_id,
                    node_id=existing.node_id,
                )

            access = AgentNodeAccessModel(
                agent_id=agent_id,
                node_id=node_id,
            )

            session.add(access)
            session.commit()

            return AgentNodeAccess(
                agent_id=access.agent_id,
                node_id=access.node_id,
            )

    def revoke_node(
        self,
        agent_id: str,
        node_id: str,
    ) -> bool:
        with self.session_factory() as session:
            access = session.get(
                AgentNodeAccessModel,
                (agent_id, node_id),
            )

            if access is None:
                return False

            session.delete(access)
            session.commit()

            return True

    def has_node_access(
        self,
        agent_id: str,
        node_id: str,
    ) -> bool:
        with self.session_factory() as session:
            statement = select(AgentNodeAccessModel.agent_id).where(
                AgentNodeAccessModel.agent_id == agent_id,
                AgentNodeAccessModel.node_id == node_id,
            )

            return session.scalar(statement) is not None

    def list_node_access(
        self,
        agent_id: str,
    ) -> list[str]:
        with self.session_factory() as session:
            statement = select(
                AgentNodeAccessModel.node_id
            ).where(
                AgentNodeAccessModel.agent_id == agent_id
            )

            return list(session.scalars(statement).all())

    @staticmethod
    def _to_domain(model: AgentModel) -> Agent:
        return Agent(
            id=str(model.id),
            name=model.name,
            certificate_fingerprint=model.certificate_fingerprint,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
