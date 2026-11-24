from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class TicketHistory:
    id: str
    ticket_id: str
    actor_id: str
    action: str
    from_status: str | None
    to_status: str | None
    note: str | None
    created_at: datetime
    details: dict[str, Any] | None = None
