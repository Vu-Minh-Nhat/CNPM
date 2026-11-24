
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Alert:
    id: str
    node_id: str
    rule_id: str | None
    metric: str
    operator: str
    threshold: float | None
    severity: str
    status: str
    message: str
    triggered_at: datetime
    acknowledged_at: datetime | None
    recovered_at: datetime | None
    triggered_value: float | None = None
    acknowledged_by: str | None = None
