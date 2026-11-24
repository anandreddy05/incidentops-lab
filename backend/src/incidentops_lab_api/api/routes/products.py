
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from incidentops_lab_api.api.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
)
from incidentops_lab_api.core.database import get_db
from incidentops_lab_api.core.dependencies import require_admin
from incidentops_lab_api.models.user import User
from incidentops_lab_api.services.product_service import (
    create_product,
    get_product,
    list_products,
    update_product,
)

router = APIRouter(prefix="/products", tags=["Products"])

DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
AdminUser = Annotated[User, Depends(require_admin)]


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_endpoint(
    product_data: ProductCreate,
    db: DatabaseSession,
    admin: AdminUser,
):
    try:
        return await create_product(db, product_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get("", response_model=ProductListResponse)
async def list_products_endpoint(
    db: DatabaseSession,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    category: str | None = None,
    search: str | None = Query(default=None, max_length=100),
):
    products, total = await list_products(
        db,
        skip=skip,
        limit=limit,
        category=category,
        search=search,
    )

    return ProductListResponse(
        items=products,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_endpoint(
    product_id: UUID,
    db: DatabaseSession,
):
    product = await get_product(db, product_id)

    if product is None or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product_endpoint(
    product_id: UUID,
    product_data: ProductUpdate,
    db: DatabaseSession,
    admin: AdminUser,
):
    product = await get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    try:
        return await update_product(db, product, product_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
