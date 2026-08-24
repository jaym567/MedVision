"""
Study Service

Business logic for study management operations.
"""

from typing import Optional
from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFoundError
from app.core.logging import logger
from app.models.study import Study
from app.repositories.patient_repository import PatientRepository
from app.repositories.study_repository import StudyRepository
from app.schemas.study import (
    StudyCreateRequest,
    StudyRead,
    StudySummary,
    StudyListResponse,
    StudyUpdate,
)
from app.schemas.patient import PatientSummary


class StudyService:
    """Service for study management operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.study_repo = StudyRepository(db)
        self.patient_repo = PatientRepository(db)

    async def create_study(
        self,
        request: StudyCreateRequest,
        user_id: UUID,
    ) -> StudyRead:
        """
        Create a new study with patient information.

        Args:
            request: Study creation request with patient data
            user_id: ID of user creating the study

        Returns:
            Created study with full details

        WARNING: Use mock/de-identified patient data only.
        """
        # Get or create patient
        patient = None

        if request.patient.mrn:
            # Try to find existing patient by MRN
            patient = await self.patient_repo.get_by_mrn(request.patient.mrn)

        if not patient:
            # Create new patient with sensible defaults for optional fields
            patient = await self.patient_repo.create_patient(
                mrn=request.patient.mrn or f"MRN-{user_id}-AUTO",
                first_name=request.patient.first_name or "Unknown",
                last_name=request.patient.last_name or "Unknown",
                date_of_birth=request.patient.date_of_birth or date.today(),
                sex=request.patient.sex or "O",
                medical_history=request.patient.medical_history,
            )
            logger.info("Created new patient", patient_id=str(patient.id), mrn=patient.mrn)
        else:
            logger.info("Reusing existing patient", patient_id=str(patient.id), mrn=patient.mrn)

        # Create study
        study = await self.study_repo.create_study(
            patient_id=patient.id,
            created_by_user_id=user_id,
            modality=request.study.modality or "OT",
            body_part=request.study.body_part,
            study_description=request.study.study_description,
            study_date=request.study.study_date or date.today(),
            accession_number=request.study.accession_number or f"ACC-{user_id}",
            metadata_json=request.study.metadata_json,
            status="created",
            source="manual",
        )

        logger.info(
            "Study created",
            study_id=str(study.id),
            patient_id=str(patient.id),
            user_id=str(user_id),
            modality=study.modality,
        )

        # Fetch with relationships
        study_with_relations = await self.study_repo.get_by_id_with_relations(study.id)

        return StudyRead.model_validate(study_with_relations)

    async def list_studies(
        self,
        page: int = 1,
        page_size: int = 20,
        modality: Optional[str] = None,
        status: Optional[str] = None,
        patient_name: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        patient_id: Optional[UUID] = None,
    ) -> StudyListResponse:
        """
        List studies with filtering and pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            modality: Filter by modality
            status: Filter by status
            patient_name: Filter by patient name
            date_from: Filter studies from date
            date_to: Filter studies to date
            patient_id: Filter by patient UUID

        Returns:
            Paginated list of studies
        """
        skip = (page - 1) * page_size

        studies = await self.study_repo.list_studies(
            skip=skip,
            limit=page_size,
            modality=modality,
            status=status,
            patient_name=patient_name,
            date_from=date_from,
            date_to=date_to,
            patient_id=patient_id,
        )

        total = await self.study_repo.count_studies(
            modality=modality,
            status=status,
            date_from=date_from,
            date_to=date_to,
            patient_id=patient_id,
            patient_name=patient_name,
        )

        # Convert to summary schemas with patient display names
        items = []
        for study in studies:
            items.append(
                StudySummary(
                    id=study.id,
                    patient=PatientSummary(
                        id=study.patient.id,
                        display_name=study.patient.display_name,
                        mrn=study.patient.mrn,
                    ),
                    modality=study.modality,
                    body_part=study.body_part,
                    study_description=study.study_description,
                    study_date=study.study_date,
                    status=study.status,
                    source=study.source,
                    created_at=study.created_at,
                )
            )

        return StudyListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get_study_detail(self, study_id: UUID) -> StudyRead:
        """
        Get study detail with all relationships.

        Args:
            study_id: Study UUID

        Returns:
            Complete study information

        Raises:
            ResourceNotFoundError: Study not found
        """
        study = await self.study_repo.get_by_id_with_relations(study_id)

        if not study:
            raise ResourceNotFoundError("Study", study_id)

        return StudyRead.model_validate(study)

    async def update_study(
        self,
        study_id: UUID,
        update_data: StudyUpdate,
    ) -> StudyRead:
        """
        Update study information.

        Args:
            study_id: Study UUID
            update_data: Fields to update

        Returns:
            Updated study

        Raises:
            ResourceNotFoundError: Study not found
        """
        # Verify study exists
        study = await self.study_repo.get_by_id(study_id)
        if not study:
            raise ResourceNotFoundError("Study", study_id)

        # Update only provided fields
        update_dict = update_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(study, field, value)

        # Persist update using base repository update method
        updated_study = await self.study_repo.update(study)

        logger.info("Study updated", study_id=str(study_id), fields=list(update_dict.keys()))

        # Fetch with relationships
        study_with_relations = await self.study_repo.get_by_id_with_relations(study_id)

        return StudyRead.model_validate(study_with_relations)
