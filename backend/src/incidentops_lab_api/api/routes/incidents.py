from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from incidentops_lab_api.api.schemas.incident import (
    IncidentCreate,
    IncidentResponse,
)
from incidentops_lab_api.core.database import get_db
from incidentops_lab_api.services.incident_service import (
    create_incident,
    get_incident,
    list_incidents,
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident_endpoint(
    incident_data: IncidentCreate,
    db: DatabaseSession,
):
    return await create_incident(db, incident_data)


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def get_incident_endpoint(
    incident_id: UUID,
    db: DatabaseSession,
):
    incident = await get_incident(db, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found",
        )

    return incident


@router.get(
    "",
    response_model=list[IncidentResponse],
)
async def list_incidents_endpoint(
    db: DatabaseSession,
    skip: int = 0,
    limit: int = 20,
):
    return await list_incidents(db, skip=skip, limit=limit)
