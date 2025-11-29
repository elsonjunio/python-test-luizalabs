
from sqlalchemy import Column, String, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.models.control_column import TimestampMixin, SoftDeleteMixin
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Customer(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = 'customers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String, nullable=False)
    email = Column(String, nullable=False)

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index(
            'uq_customer_active',
            'email',
            unique=True,
            postgresql_where=(deleted_at.is_(None)),
        ),
    )