from enum import StrEnum


class Role(StrEnum):
    ADMINISTRATOR = "Administrator"
    OPERATOR = "Operator"
    TECHNICIAN = "Technician"