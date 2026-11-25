from enum import StrEnum


class IncidentSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(StrEnum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"


class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class PaymentStatus(StrEnum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
