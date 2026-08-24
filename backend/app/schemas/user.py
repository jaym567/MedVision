"""
User Schemas

Request/response models for user data.
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    full_name: str


class UserRead(BaseModel):
    """User schema for API responses."""

    id: UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    """Minimal user information for related entities."""

    id: UUID
    email: EmailStr
    full_name: str

    model_config = {"from_attributes": True}


class CurrentUser(BaseModel):
    """Current authenticated user information."""

    id: UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
