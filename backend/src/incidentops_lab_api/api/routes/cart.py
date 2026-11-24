from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from incidentops_lab_api.api.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
)
from incidentops_lab_api.core.dependencies import (
    DatabaseSession,
    get_current_user,
)
from incidentops_lab_api.models.user import User
from incidentops_lab_api.services.cart_service import (
    add_item_to_cart,
    get_cart_response,
    get_or_create_cart,
    remove_cart_item,
    update_cart_item_quantity,
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
async def get_cart(
    db: DatabaseSession,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Retrieve the current user's shopping cart."""

    return await get_cart_response(db, current_user.id)


@router.post("/items", response_model=CartResponse)
async def add_cart_item(
    item_data: CartItemCreate,
    db: DatabaseSession,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Add a product to the current user's cart."""

    cart = await get_or_create_cart(db, current_user.id)

    try:
        await add_item_to_cart(
            db,
            cart,
            item_data.product_id,
            item_data.quantity,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    return await get_cart_response(db, current_user.id)


@router.patch("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: UUID,
    item_data: CartItemUpdate,
    db: DatabaseSession,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Update the quantity of a cart item."""

    cart = await get_or_create_cart(db, current_user.id)

    try:
        updated_item = await update_cart_item_quantity(
            db,
            cart,
            item_id,
            item_data.quantity,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    return await get_cart_response(db, current_user.id)


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cart_item(
    item_id: UUID,
    db: DatabaseSession,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Remove an item from the current user's cart."""

    cart = await get_or_create_cart(db, current_user.id)

    removed = await remove_cart_item(db, cart, item_id)

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
