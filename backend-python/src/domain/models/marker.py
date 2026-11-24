from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Marker:
    id: str
    marker_type: str
    identifier: str
    node_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime