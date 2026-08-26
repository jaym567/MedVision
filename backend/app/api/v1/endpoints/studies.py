# backend/app/api/v1/endpoints/studies.py
from typing import Optional
from datetime import date
from uuid import UUID
import tempfile
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydicom.errors import InvalidDicomError

from app.database.session import get_db
from app.core.config import settings
from app.services.study_service import StudyService
from app.services.storage_service import StorageService
from app.services.dicom_service import DicomService
from app.schemas.study import (
    StudyCreateRequest,
    StudyRead,
    StudyListResponse,
    StudyUpdate,
)
from app.schemas.dicom import DicomUploadResponse, DicomMetadataSchema
from app.core.exceptions import ResourceNotFoundError, ValidationError
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("", response_model=StudyRead, status_code=status.HTTP_201_CREATED)
async def create_study(
    study_data: StudyCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new study with patient information.

    **WARNING**: Use mock/de-identified data only. Do not submit real PHI.

    - If patient with given MRN exists, study will be associated with existing patient
    - If patient does not exist, a new patient record will be created
    - Study status will be set to 'created' and source to 'manual'
    """
    try:
        study_service = StudyService(db)
        study = await study_service.create_study(
            request=study_data,
            user_id=current_user.id
        )
        return study
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )


@router.post("/upload-dicom", response_model=DicomUploadResponse)
async def upload_dicom(
    file: UploadFile = File(..., description="DICOM file to upload"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload DICOM file and create/update study.

    Workflow:
    1. Validate file size
    2. Save to temporary location
    3. Validate DICOM format
    4. Extract metadata
    5. Store file permanently
    6. Create or update patient and study
    7. Return study with metadata

    **IMPORTANT**: Use only synthetic or de-identified DICOM files.
    This system is for research and demonstration purposes only.
    """
    # Validate file size
    content = await file.read()
    file_size = len(content)

    max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {file_size} bytes exceeds maximum {settings.MAX_UPLOAD_SIZE_MB}MB"
        )

    # Save to temporary file for DICOM validation
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dcm') as temp_file:
        temp_path = Path(temp_file.name)
        temp_file.write(content)

    try:
        # Validate DICOM format
        if not DicomService.validate_dicom_file(temp_path):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="File is not a valid DICOM file"
            )

        # Extract metadata
        try:
            dicom_metadata = DicomService.extract_metadata(temp_path)
        except InvalidDicomError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid DICOM file format"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"DICOM validation error: {str(e)}"
            )

        # Store file permanently
        storage_service = StorageService()
        storage_path, safe_filename = storage_service.save_dicom_file(
            file_content=BytesIO(content),
            original_filename=file.filename or "upload.dcm",
            file_size=file_size
        )

        # Create or update study from DICOM metadata
        study = await StudyService.create_study_from_dicom(
            db=db,
            dicom_metadata=dicom_metadata,
            storage_path=storage_path,
            created_by_user_id=current_user.id
        )

        # Load relationships for response
        await db.refresh(study, ['patient', 'created_by_user'])

        # Convert to response schema
        study_read = StudyRead.model_validate(study)
        metadata_schema = DicomMetadataSchema(**dicom_metadata.to_dict())

        return DicomUploadResponse(
            study=study_read,
            dicom_metadata=metadata_schema,
            message="DICOM uploaded successfully"
        )

    finally:
        # Clean up temporary file
        if temp_path.exists():
            temp_path.unlink()

@router.get("", response_model=StudyListResponse)
async def list_studies(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    modality: Optional[str] = Query(None, description="Filter by modality (CT, MR, etc.)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    patient_name: Optional[str] = Query(None, description="Search by patient name"),
    date_from: Optional[date] = Query(None, description="Filter studies from date (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Filter studies to date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List studies with filtering and pagination.

    Supports filtering by:
    - Patient ID
    - Modality (CT, MR, US, XR, etc.)
    - Status (created, uploaded, processing, ready, failed, archived)
    - Patient name (partial match)
    - Date range

    Returns paginated list with total count and page metadata.
    """
    study_service = StudyService(db)

    result = await study_service.list_studies(
        page=page,
        page_size=page_size,
        patient_id=patient_id,
        modality=modality,
        status=status,
        patient_name=patient_name,
        date_from=date_from,
        date_to=date_to,
    )

    return result


@router.get("/{study_id}", response_model=StudyRead)
async def get_study(
    study_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific study.

    Includes full patient and creator user information.
    """
    try:
        study_service = StudyService(db)
        return await study_service.get_study_detail(study_id)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.patch("/{study_id}", response_model=StudyRead)
async def update_study(
    study_id: UUID,
    study_update: StudyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update study information.

    All fields are optional. Only provided fields will be updated.
    """
    try:
        study_service = StudyService(db)
        return await study_service.update_study(study_id, study_update)
    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
