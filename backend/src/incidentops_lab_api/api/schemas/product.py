
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    description: str | None = None
    sku: str = Field(min_length=2, max_length=50)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    category: str = Field(min_length=2, max_length=100)
    image_url: HttpUrl | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    sku: str | None = Field(default=None, min_length=2, max_length=50)
    price: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=10,
        decimal_places=2,
    )
    stock_quantity: int | None = Field(default=None, ge=0)
    category: str | None = Field(default=None, min_length=2, max_length=100)
    image_url: HttpUrl | None = None
    is_active: bool | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        for field in (
            "name",
            "sku",
            "price",
            "stock_quantity",
            "category",
            "is_active",
        ):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    sku: str
    price: Decimal
    stock_quantity: int
    category: str
    image_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    skip: int
    limit: int
