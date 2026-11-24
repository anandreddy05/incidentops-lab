from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from incidentops_lab_api.core.config import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password using the recommended password algorithm."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its stored hash."""
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: UUID) -> str:
    """Create a signed JWT access token for a user."""
    settings = get_settings()

    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> UUID:
    """Decode a JWT and return its user ID."""
    settings = get_settings()

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    subject = payload.get("sub")
    if not subject:
        raise ValueError("Token does not contain a subject")

    return UUID(subject)
