"""
Authentication Service

Business logic for user registration, login, and token management.
"""

from datetime import timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    validate_password_strength,
)
from app.core.exceptions import (
    AuthenticationError,
    DuplicateResourceError,
    ValidationError,
    InactiveUserError,
)
from app.core.logging import logger
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserRead


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register_user(
        self,
        request: UserRegisterRequest,
    ) -> UserRead:
        """
        Register a new user.

        Args:
            request: User registration request

        Returns:
            Created user

        Raises:
            DuplicateResourceError: Email already registered
            ValidationError: Password validation failed
        """
        # Check if email already exists
        if await self.user_repo.email_exists(request.email):
            raise DuplicateResourceError("User", "email", request.email)

        # Validate password strength (raises ValidationError if invalid)
        validate_password_strength(request.password)

        # Hash password
        password_hash = hash_password(request.password)

        # Create user
        user = await self.user_repo.create_user(
            email=request.email,
            password_hash=password_hash,
            full_name=request.full_name,
            role=request.role,
        )

        logger.info(
            "User registered",
            user_id=str(user.id),
            email=user.email,
            role=user.role,
        )

        return UserRead.model_validate(user)

    async def authenticate_user(
        self,
        request: LoginRequest,
    ) -> TokenResponse:
        """
        Authenticate user and generate access token.

        Args:
            request: Login credentials

        Returns:
            Token response with user information

        Raises:
            AuthenticationError: Invalid credentials
            InactiveUserError: User account is inactive
        """
        # Get user by email
        user = await self.user_repo.get_by_email(request.email)

        if not user:
            logger.warning("Login failed: user not found", email=request.email)
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(request.password, user.password_hash):
            logger.warning("Login failed: invalid password", user_id=str(user.id))
            raise AuthenticationError("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            logger.warning("Login failed: inactive user", user_id=str(user.id))
            raise InactiveUserError()

        # Create access token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }

        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        logger.info("User logged in", user_id=str(user.id), email=user.email)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserRead.model_validate(user),
        )

    async def get_current_user(self, token: str) -> User:
        """
        Get current user from access token.

        Args:
            token: JWT access token

        Returns:
            Current user

        Raises:
            AuthenticationError: Invalid or expired token
        """
        payload = decode_access_token(token)

        if not payload:
            raise AuthenticationError("Invalid or expired token")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise AuthenticationError("Invalid token payload")

        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise AuthenticationError("Invalid user ID in token")

        user = await self.user_repo.get_by_id(user_id)

        if not user:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise InactiveUserError()

        return user
