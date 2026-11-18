from enum import StrEnum


class Role(StrEnum):
    ADMINISTRATOR = "Administrator"
    OPERATOR = "Operator"
    TECHNICIAN = "Technician"


class AlertStatus(StrEnum):
    FIRING = "FIRING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RECOVERED = "RECOVERED"


class TicketStatus(StrEnum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    CLOSED = "CLOSED"