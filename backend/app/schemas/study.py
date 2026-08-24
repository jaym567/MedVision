"""
Study Schemas

Request/response models for study data.
"""

from datetime import date, datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.schemas.patient import PatientCreate, PatientRead, PatientSummary
from app.schemas.user import UserSummary


class StudyCreate(BaseModel):
    """Schema for creating a study."""

    modality: Optional[str] = Field(None, max_length=32, description="Modality (CT, MR, etc.)")
    body_part: Optional[str] = Field(None, max_length=128, description="Body part examined")
    study_description: Optional[str] = Field(None, description="Study description")
    study_date: Optional[date] = Field(None, description="Study date")
    accession_number: Optional[str] = Field(None, max_length=128, description="Accession number")
    metadata_json: Optional[dict[str, Any]] = Field(None, description="Additional metadata")


class StudyCreateRequest(BaseModel):
    """Complete request for creating a study with patient info."""

    patient: PatientCreate = Field(..., description="Patient information")
    study: StudyCreate = Field(..., description="Study information")


class StudyUpdate(BaseModel):
    """Schema for updating a study."""

    body_part: Optional[str] = None
    study_description: Optional[str] = None
    status: Optional[str] = None
    metadata_json: Optional[dict[str, Any]] = None


class StudyRead(BaseModel):
    """Complete study schema for detail views."""

    id: UUID
    patient: PatientRead
    created_by_user: Optional[UserSummary]
    study_instance_uid: Optional[str]
    accession_number: Optional[str]
    modality: Optional[str]
    body_part: Optional[str]
    study_description: Optional[str]
    study_date: Optional[date]
    status: str
    source: str
    metadata_json: Optional[dict[str, Any]]
    storage_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StudySummary(BaseModel):
    """Minimal study information for list views."""

    id: UUID
    patient: PatientSummary
    modality: Optional[str]
    body_part: Optional[str]
    study_description: Optional[str]
    study_date: Optional[date]
    status: str
    source: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StudyListResponse(BaseModel):
    """Paginated study list response."""

    items: list[StudySummary]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Calculate total pages."""
        return (self.total + self.page_size - 1) // self.page_size


class StudyFilters(BaseModel):
    """Query parameters for filtering studies."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    modality: Optional[str] = Field(None, description="Filter by modality")
    status: Optional[str] = Field(None, description="Filter by status")
    patient_name: Optional[str] = Field(None, description="Filter by patient name")
    date_from: Optional[date] = Field(None, description="Filter studies from date")
    date_to: Optional[date] = Field(None, description="Filter studies to date")
