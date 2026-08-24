"""
Base repository with common CRUD operations.
Generic repository pattern using SQLAlchemy async sessions.
"""
from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository with common database operations.

    Provides standard CRUD methods that can be inherited by specific repositories.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db

    async def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record.

        Args:
            obj: Model instance to create

        Returns:
            Created model instance
        """
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """
        Get a record by ID.

        Args:
            id: Record UUID

        Returns:
            Model instance or None if not found
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, obj: ModelType) -> ModelType:
        """
        Update an existing record.

        Args:
            obj: Model instance with updated values

        Returns:
            Updated model instance
        """
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """
        Delete a record.

        Args:
            obj: Model instance to delete
        """
        await self.db.delete(obj)
        await self.db.commit()

    async def count(self) -> int:
        """
        Count total records.

        Returns:
            Total number of records
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
