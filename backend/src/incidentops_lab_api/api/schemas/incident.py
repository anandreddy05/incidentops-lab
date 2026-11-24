from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str | None = None
    severity: str = "medium"
    source: str = Field(min_length=1, max_length=50)
    fingerprint: str | None = Field(default=None, max_length=128)
    first_seen_at: datetime
    last_seen_at: datetime


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=255)
    description: str | None = None
    severity: str | None = None
    status: str | None = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    severity: str
    status: str
    source: str
    fingerprint: str | None
    first_seen_at: datetime
    last_seen_at: datetime
    created_at: datetime
    updated_at: datetime
