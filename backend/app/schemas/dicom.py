# backend/app/schemas/dicom.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date

from app.schemas.study import StudyRead


class DicomMetadataSchema(BaseModel):
    """DICOM metadata extracted from file."""

    # Patient identifiers
    patient_id: Optional[str] = Field(None, description="Patient ID (MRN)")
    patient_name: Optional[str] = Field(None, description="Patient name")
    patient_birth_date: Optional[str] = Field(None, description="Patient birth date (ISO format)")
    patient_sex: Optional[str] = Field(None, description="Patient sex (M/F/O)")

    # Study identifiers
    study_instance_uid: str = Field(..., description="Unique study identifier")
    series_instance_uid: str = Field(..., description="Unique series identifier")
    sop_instance_uid: str = Field(..., description="Unique instance identifier")
    accession_number: Optional[str] = Field(None, description="Accession number")

    # Study information
    modality: Optional[str] = Field(None, description="Imaging modality")
    study_date: Optional[str] = Field(None, description="Study date (ISO format)")
    study_description: Optional[str] = Field(None, description="Study description")
    body_part_examined: Optional[str] = Field(None, description="Body part examined")

    # Equipment information
    manufacturer: Optional[str] = Field(None, description="Equipment manufacturer")

    # Image properties
    rows: Optional[int] = Field(None, description="Image rows (height)")
    columns: Optional[int] = Field(None, description="Image columns (width)")
    pixel_spacing: Optional[list] = Field(None, description="Pixel spacing [row, col] in mm")
    slice_thickness: Optional[float] = Field(None, description="Slice thickness in mm")

    # Display parameters
    window_center: Optional[float] = Field(None, description="Window center for display")
    window_width: Optional[float] = Field(None, description="Window width for display")
    photometric_interpretation: Optional[str] = Field(None, description="Photometric interpretation")

    class Config:
        from_attributes = True


class DicomUploadResponse(BaseModel):
    """Response from DICOM upload."""

    study: StudyRead = Field(..., description="Created or updated study")
    dicom_metadata: DicomMetadataSchema = Field(..., description="Extracted DICOM metadata")
    message: str = Field(..., description="Success message")

    class Config:
        from_attributes = True
