"""
User repository for database operations on User model.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email (case-insensitive)

        Returns:
            User instance or None
        """
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email to check

        Returns:
            True if email exists
        """
        user = await self.get_by_email(email)
        return user is not None

    async def create_user(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        role: str
    ) -> User:
        """
        Create a new user.

        Args:
            email: User email
            password_hash: Hashed password
            full_name: User full name
            role: User role

        Returns:
            Created user instance
        """
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
            is_verified=False
        )
        return await self.create(user)
