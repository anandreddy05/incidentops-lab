from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from incidentops_lab_api.api.schemas.cart import (
    CartItemResponse,
    CartProductResponse,
    CartResponse,
)
from incidentops_lab_api.models.cart import Cart
from incidentops_lab_api.models.cart_item import CartItem
from incidentops_lab_api.models.product import Product


async def get_or_create_cart(
    db: AsyncSession,
    user_id: UUID,
) -> Cart:
    """Retrieve a user's cart or create one if it doesn't exist."""

    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    cart = result.scalar_one_or_none()

    if cart is not None:
        return cart

    cart = Cart(user_id=user_id)
    db.add(cart)
    await db.commit()
    await db.refresh(cart)

    return cart


async def add_item_to_cart(
    db: AsyncSession,
    cart: Cart,
    product_id: UUID,
    quantity: int,
) -> CartItem:
    """Add a product or increase its existing cart quantity."""

    product = await db.get(Product, product_id)

    if product is None or not product.is_active:
        raise LookupError("Product not found or unavailable")

    if quantity > product.stock_quantity:
        raise ValueError("Requested quantity exceeds available stock")

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
    )
    cart_item = result.scalar_one_or_none()

    if cart_item is not None:
        new_quantity = cart_item.quantity + quantity

        if new_quantity > product.stock_quantity:
            raise ValueError("Requested quantity exceeds available stock")

        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
        )
        db.add(cart_item)

    await db.commit()
    await db.refresh(cart_item)

    return cart_item


async def update_cart_item_quantity(
    db: AsyncSession,
    cart: Cart,
    item_id: UUID,
    quantity: int,
) -> CartItem | None:
    """Update the quantity of an existing cart item."""

    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
    )
    cart_item = result.scalar_one_or_none()

    if cart_item is None:
        return None

    product = await db.get(Product, cart_item.product_id)

    if product is None or not product.is_active:
        raise ValueError("Product is no longer available")

    if quantity > product.stock_quantity:
        raise ValueError("Requested quantity exceeds available stock")

    cart_item.quantity = quantity

    await db.commit()
    await db.refresh(cart_item)

    return cart_item


async def remove_cart_item(
    db: AsyncSession,
    cart: Cart,
    item_id: UUID,
) -> bool:
    """Remove an item from the user's cart."""

    result = await db.execute(
        select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id,
        )
    )
    cart_item = result.scalar_one_or_none()

    if cart_item is None:
        return False

    await db.delete(cart_item)
    await db.commit()

    return True


async def get_cart_response(
    db: AsyncSession,
    user_id: UUID,
) -> CartResponse:
    """Retrieve a cart with product details and calculated totals."""

    cart = await get_or_create_cart(db, user_id)

    result = await db.execute(
        select(Cart)
        .where(Cart.id == cart.id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
    )

    cart = result.scalar_one()

    items = [
        CartItemResponse(
            id=item.id,
            product=CartProductResponse.model_validate(item.product),
            quantity=item.quantity,
            subtotal=item.product.price * item.quantity,
        )
        for item in cart.items
    ]

    total_items = sum(item.quantity for item in cart.items)

    total_price = sum(
        (item.subtotal for item in items),
        start=Decimal("0.00"),
    )

    return CartResponse(
        id=cart.id,
        items=items,
        total_items=total_items,
        total_price=total_price,
        created_at=cart.created_at,
        updated_at=cart.updated_at,
    )
