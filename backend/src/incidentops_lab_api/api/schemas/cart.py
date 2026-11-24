from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CartProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    sku: str
    price: Decimal
    image_url: str | None


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product: CartProductResponse
    quantity: int
    subtotal: Decimal


class CartResponse(BaseModel):
    id: UUID
    items: list[CartItemResponse]
    total_items: int
    total_price: Decimal
    created_at: datetime
    updated_at: datetime


class CartItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)
