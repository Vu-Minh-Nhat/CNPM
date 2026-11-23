
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Agent:
    id: str
    name: str
    certificate_fingerprint: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AgentNodeAccess:
    agent_id: str
    node_id: str
