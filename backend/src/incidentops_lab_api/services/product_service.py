from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from incidentops_lab_api.api.schemas.product import ProductCreate, ProductUpdate
from incidentops_lab_api.models.product import Product


async def create_product(
    db: AsyncSession,
    product_data: ProductCreate,
) -> Product:
    """Create a product in the database."""

    product = Product(**product_data.model_dump(mode="json"))

    db.add(product)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("A product with this SKU already exists")

    await db.refresh(product)
    return product


async def get_product(
    db: AsyncSession,
    product_id: UUID,
) -> Product | None:
    """Retrieve a product by its ID."""

    return await db.get(Product, product_id)


async def list_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
    category: str | None = None,
    search: str | None = None,
) -> tuple[list[Product], int]:
    """Retrieve products with filtering, search and pagination."""

    query = select(Product).where(Product.is_active.is_(True))

    if category:
        query = query.where(Product.category.ilike(category))

    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    result = await db.execute(
        query.order_by(Product.created_at.desc()).offset(skip).limit(limit)
    )

    return list(result.scalars().all()), total or 0


async def update_product(
    db: AsyncSession,
    product: Product,
    product_data: ProductUpdate,
) -> Product:
    """Update selected product fields."""

    updates = product_data.model_dump(
        exclude_unset=True,
        mode="json",
    )

    for field, value in updates.items():
        setattr(product, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ValueError("A product with this SKU already exists")

    await db.refresh(product)
    return product
