"""
Base Repository

Provides common CRUD operations for all repositories.
"""

from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import BaseModel


ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common database operations.

    Implements the Repository pattern for data access abstraction.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get record by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Get all records with pagination."""
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(
        self,
        id: UUID,
        **kwargs,
    ) -> Optional[ModelType]:
        """Update record by ID."""
        await self.db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.db.flush()
        return await self.get_by_id(id)

    async def delete(self, id: UUID) -> bool:
        """Delete record by ID."""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.flush()
        return result.rowcount > 0

    async def count(self) -> int:
        """Count total records."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
