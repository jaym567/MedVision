"""
Authentication Schemas

Request/response models for authentication endpoints.
"""

from typing import Optional, TYPE_CHECKING
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.user import UserRead


class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=1, max_length=255, description="Full name")
    role: str = Field(default="physician", description="User role")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is one of allowed values."""
        allowed_roles = {"physician", "researcher", "admin"}
        if v.lower() not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")
        return v.lower()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.lower()


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        return v.lower()


class TokenResponse(BaseModel):
    """Response schema for successful authentication."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: UserRead = Field(..., description="Authenticated user information")


class TokenPayload(BaseModel):
    """JWT token payload structure."""

    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    role: str = Field(..., description="User role")
    exp: Optional[int] = Field(None, description="Expiration timestamp")
    iat: Optional[int] = Field(None, description="Issued at timestamp")
