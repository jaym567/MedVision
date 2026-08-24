"""
User Repository

Data access layer for User model.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user data access."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User's email address (case-insensitive)

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        Check if email is already registered.

        Args:
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        user = await self.get_by_email(email)
        return user is not None

    async def create_user(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        role: str = "physician",
    ) -> User:
        """
        Create a new user.

        Args:
            email: User's email (will be lowercased)
            password_hash: Hashed password
            full_name: User's full name
            role: User role (physician, researcher, admin)

        Returns:
            Created user instance
        """
        return await self.create(
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
            is_verified=False,
        )
