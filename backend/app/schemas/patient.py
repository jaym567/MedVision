"""
Patient Schemas

Request/response models for patient data.
"""

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    """Schema for creating a patient."""

    mrn: Optional[str] = Field(None, max_length=128, description="Medical Record Number")
    first_name: Optional[str] = Field(None, max_length=128, description="First name")
    last_name: Optional[str] = Field(None, max_length=128, description="Last name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    sex: Optional[str] = Field(None, description="Patient sex")
    medical_history: Optional[str] = Field(None, description="Medical history")


class PatientRead(BaseModel):
    """Patient schema for API responses."""

    id: UUID
    mrn: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[date]
    sex: Optional[str]
    medical_history: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PatientSummary(BaseModel):
    """Minimal patient information for study lists."""

    id: UUID
    display_name: str
    mrn: Optional[str]

    model_config = {"from_attributes": True}
