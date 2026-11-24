from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from incidentops_lab_api.api.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from incidentops_lab_api.core.database import get_db
from incidentops_lab_api.core.dependencies import get_current_user
from incidentops_lab_api.core.security import (
    create_access_token,
)
from incidentops_lab_api.models.user import User
from incidentops_lab_api.services.auth_service import (
    authenticate_user,
    create_user,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegister,
    db: DatabaseSession,
):
    try:
        user = await create_user(
            db=db,
            email=str(user_data.email),
            full_name=user_data.full_name,
            password=user_data.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: DatabaseSession,
):
    user = await authenticate_user(
        db=db,
        email=str(credentials.email),
        password=credentials.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    token = create_access_token(user.id)

    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
