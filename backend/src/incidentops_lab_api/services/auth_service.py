from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from incidentops_lab_api.core.security import hash_password, verify_password
from incidentops_lab_api.models.user import User


async def create_user(
    db: AsyncSession,
    email: str,
    full_name: str,
    password: str,
) -> User:
    """Create a user with a securely hashed password."""

    user = User(
        email=email.lower(),
        full_name=full_name,
        password_hash=hash_password(password),
    )

    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("An account with this email already exists")

    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """Authenticate a user using their email and password."""

    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user
