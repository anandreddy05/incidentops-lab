from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from incidentops_lab_api.api.schemas.enums import (
    IncidentSeverity,
    IncidentStatus,
)


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = None
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    source: str = Field(min_length=1, max_length=50)
    fingerprint: str | None = Field(default=None, max_length=128)
    first_seen_at: datetime
    last_seen_at: datetime

    @model_validator(mode="after")
    def validate_seen_timestamps(self):
        if self.last_seen_at < self.first_seen_at:
            raise ValueError("last_seen_at cannot be earlier than first_seen_at")
        return self


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None

    @model_validator(mode="after")
    def validate_patch_fields(self):
        # Reject an empty PATCH request.
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        # These fields cannot explicitly be set to null.
        for field in ("title", "severity", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    severity: IncidentSeverity
    status: IncidentStatus
    source: str
    fingerprint: str | None
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime
