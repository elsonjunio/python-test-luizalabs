from sqlalchemy import Column, ForeignKey, Index, String
from app.core.database import Base
from app.models.control_column import TimestampMixin, SoftDeleteMixin
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID
import uuid


class WishlistItem(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'wishlist_item'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    customer_id = Column(
        UUID(as_uuid=True),
        ForeignKey('customers.id', ondelete='CASCADE'),
        nullable=False,
    )

    product_id = Column(String, nullable=False)

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index(
            'uq_customer_product_active',
            'customer_id',
            'product_id',
            unique=True,
            postgresql_where=(deleted_at.is_(None)),
        ),
    )
