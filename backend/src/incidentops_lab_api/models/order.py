from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from incidentops_lab_api.api.schemas.enums import (
    OrderStatus,
    PaymentStatus,
)
from incidentops_lab_api.core.base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus,
            name="order_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(
            PaymentStatus,
            name="payment_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=PaymentStatus.PENDING,
        server_default=PaymentStatus.PENDING.value,
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
