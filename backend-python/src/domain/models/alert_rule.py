from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AlertRule:
    id: str
    metric: str
    operator: str
    threshold: float
    severity: str
    recovery_operator: str | None
    recovery_threshold: float | None
    is_active: bool
    created_at: datetime
    updated_at: datetime