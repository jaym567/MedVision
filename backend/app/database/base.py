from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.database.session import Base


class BaseModel(Base):
    """
    Base model class with common fields for all tables.
    Provides UUID primary key and timestamp tracking.
    """
    __abstract__ = True

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        nullable=False,
        index=True
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
