from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Ticket:
    id: str
    node_id: str
    alert_id: str | None
    created_by: str
    assigned_to: str | None
    status: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    progress: int = 0
    work_notes: str | None = None
    evidence: str | None = None
    result: str | None = None
    version: int = 1
