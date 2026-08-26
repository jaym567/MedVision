"""
Study Service

Business logic for study management operations.
"""

from typing import Optional
from datetime import datetime, date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import ResourceNotFoundError
from app.core.logging import logger
from app.models.study import Study
from app.models.patient import Patient
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
        """
        # Get or create patient
        patient = None

        if request.patient.mrn:
            # Try to find existing patient by MRN
            patient = await self.patient_repo.get_by_mrn(request.patient.mrn)

        if not patient:
            # Create new patient
            patient = await self.patient_repo.create_patient(
                mrn=request.patient.mrn,
                first_name=request.patient.first_name,
                last_name=request.patient.last_name,
                date_of_birth=request.patient.date_of_birth,
                sex=request.patient.sex,
                medical_history=request.patient.medical_history,
            )
            logger.info("Created new patient", patient_id=str(patient.id), mrn=patient.mrn)
        else:
            logger.info("Reusing existing patient", patient_id=str(patient.id), mrn=patient.mrn)

        # Create study
        study = await self.study_repo.create_study(
            patient_id=patient.id,
            created_by_user_id=user_id,
            modality=request.study.modality,
            body_part=request.study.body_part,
            study_description=request.study.study_description,
            study_date=request.study.study_date,
            accession_number=request.study.accession_number,
            metadata_json=request.study.metadata_json,
            status="created",
            source="manual",
        )

        await self.db.commit()

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
        patient_id: Optional[UUID] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> StudyListResponse:
        """
        List studies with filtering and pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            modality: Filter by modality
            status: Filter by status
            patient_name: Filter by patient name
            patient_id: Filter by patient ID
            date_from: Filter studies from date
            date_to: Filter studies to date

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
            patient_id=patient_id,
            date_from=date_from,
            date_to=date_to,
        )

        total = await self.study_repo.count_studies(
            modality=modality,
            status=status,
            patient_name=patient_name,
            patient_id=patient_id,
            date_from=date_from,
            date_to=date_to,
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

        updated_study = await self.study_repo.update(study_id, **update_dict)
        await self.db.commit()

        logger.info("Study updated", study_id=str(study_id), fields=list(update_dict.keys()))

        # Fetch with relationships
        study_with_relations = await self.study_repo.get_by_id_with_relations(study_id)

        return StudyRead.model_validate(study_with_relations)

    # ─── DICOM Upload ─────────────────────────────────────────────────────────

    @staticmethod
    async def create_study_from_dicom(
        db: AsyncSession,
        dicom_metadata,  # DicomMetadata from dicom_service
        storage_path: str,
        created_by_user_id,
    ) -> Study:
        """
        Create or update study from DICOM metadata.

        Workflow:
        1. Get or create patient from DICOM PatientID
        2. Check if study exists by StudyInstanceUID
        3. Create new study or update existing

        Args:
            db: Database session
            dicom_metadata: Extracted DICOM metadata
            storage_path: Relative path to stored file
            created_by_user_id: ID of user who uploaded

        Returns:
            Created or updated Study
        """
        from app.services.dicom_service import DicomService

        # Extract patient data from DICOM
        patient_id = dicom_metadata.patient_id or "UNKNOWN"
        patient_name = dicom_metadata.patient_name

        # Parse patient name
        first_name, last_name = DicomService.parse_patient_name(patient_name)

        # Parse birth date
        birth_date = None
        if dicom_metadata.patient_birth_date:
            try:
                birth_date = datetime.strptime(
                    dicom_metadata.patient_birth_date, '%Y-%m-%d'
                ).date()
            except ValueError:
                pass

        # Get or create patient
        patient = await StudyService._get_or_create_patient(
            db=db,
            mrn=patient_id,
            first_name=first_name or "Unknown",
            last_name=last_name or "Unknown",
            date_of_birth=birth_date,
            sex=dicom_metadata.patient_sex
        )

        # Check if study exists by StudyInstanceUID
        study_instance_uid = dicom_metadata.study_instance_uid
        result = await db.execute(
            select(Study).where(Study.study_instance_uid == study_instance_uid)
        )
        existing_study = result.scalar_one_or_none()

        if existing_study:
            # Update existing study with new file
            existing_study.storage_path = storage_path
            existing_study.metadata_json = dicom_metadata.to_dict()
            existing_study.status = "ready"
            existing_study.updated_at = datetime.utcnow()

            # Update fields if not already set
            if not existing_study.modality and dicom_metadata.modality:
                existing_study.modality = dicom_metadata.modality
            if not existing_study.body_part and dicom_metadata.body_part_examined:
                existing_study.body_part = dicom_metadata.body_part_examined
            if not existing_study.study_description and dicom_metadata.study_description:
                existing_study.study_description = dicom_metadata.study_description

            await db.commit()
            await db.refresh(existing_study)
            return existing_study

        # Parse study date
        study_date = None
        if dicom_metadata.study_date:
            try:
                study_date = datetime.strptime(
                    dicom_metadata.study_date, '%Y-%m-%d'
                ).date()
            except ValueError:
                pass

        # Create new study
        study = Study(
            patient_id=patient.id,
            created_by_user_id=created_by_user_id,
            study_instance_uid=study_instance_uid,
            accession_number=dicom_metadata.accession_number,
            modality=dicom_metadata.modality,
            body_part=dicom_metadata.body_part_examined,
            study_description=dicom_metadata.study_description,
            study_date=study_date or date.today(),
            status="ready",
            source="dicom_upload",
            metadata_json=dicom_metadata.to_dict(),
            storage_path=storage_path
        )

        db.add(study)
        await db.commit()
        await db.refresh(study)

        return study

    @staticmethod
    async def _get_or_create_patient(
        db: AsyncSession,
        mrn: str,
        first_name: str,
        last_name: str,
        date_of_birth: Optional[date],
        sex: Optional[str]
    ) -> Patient:
        """
        Get existing patient by MRN or create new one.

        Args:
            db: Database session
            mrn: Medical record number
            first_name: Patient first name
            last_name: Patient last name
            date_of_birth: Patient birth date
            sex: Patient sex (M/F/O)

        Returns:
            Patient (existing or newly created)
        """
        result = await db.execute(
            select(Patient).where(Patient.mrn == mrn)
        )
        patient = result.scalar_one_or_none()

        if patient:
            return patient

        # Create new patient
        patient = Patient(
            mrn=mrn,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            sex=sex or "O"
        )

        db.add(patient)
        await db.flush()  # Get patient ID without committing

        return patient
