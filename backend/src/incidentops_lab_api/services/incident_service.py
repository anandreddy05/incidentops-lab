from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from incidentops_lab_api.api.schemas.incident import IncidentCreate
from incidentops_lab_api.models.incident import Incident


async def create_incident(
    db: AsyncSession,
    incident_data: IncidentCreate,
) -> Incident:
    incident = Incident(**incident_data.model_dump())

    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    return incident


async def get_incident(
    db: AsyncSession,
    incident_id: UUID,
) -> Incident | None:
    result = await db.execute(select(Incident).where(Incident.id == incident_id))

    return result.scalar_one_or_none()


async def list_incidents(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> list[Incident]:
    result = await db.execute(
        select(Incident).order_by(Incident.created_at.desc()).offset(skip).limit(limit)
    )

    return list(result.scalars().all())
