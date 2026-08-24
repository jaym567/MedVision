"""
Study Repository

Data access layer for Study model.
"""

from typing import Optional, List
from datetime import date
from uuid import UUID

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.study import Study
from app.repositories.base_repository import BaseRepository


class StudyRepository(BaseRepository[Study]):
    """Repository for study data access."""

    def __init__(self, db: AsyncSession):
        super().__init__(Study, db)

    async def get_by_id_with_relations(self, id: UUID) -> Optional[Study]:
        """
        Get study by ID with patient and user relationships loaded.

        Args:
            id: Study UUID

        Returns:
            Study with relationships or None
        """
        result = await self.db.execute(
            select(Study)
            .where(Study.id == id)
            .options(
                selectinload(Study.patient),
                selectinload(Study.created_by_user),
            )
        )
        return result.scalar_one_or_none()

    async def list_studies(
        self,
        skip: int = 0,
        limit: int = 20,
        patient_id: Optional[UUID] = None,
        modality: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        patient_name: Optional[str] = None,
    ) -> List[Study]:
        """
        List studies with filtering and pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            patient_id: Filter by patient ID
            modality: Filter by modality (e.g., 'CT', 'MR')
            status: Filter by status
            date_from: Filter studies on or after this date
            date_to: Filter studies on or before this date
            patient_name: Filter by patient name

        Returns:
            List of studies matching criteria
        """
        query = select(Study).options(
            selectinload(Study.patient),
            selectinload(Study.created_by_user),
        )

        # Build filters
        filters = []

        if patient_id:
            filters.append(Study.patient_id == patient_id)

        if modality:
            filters.append(Study.modality == modality.upper())

        if status:
            filters.append(Study.status == status)

        if date_from:
            filters.append(Study.study_date >= date_from)

        if date_to:
            filters.append(Study.study_date <= date_to)

        if patient_name:
            from app.models.patient import Patient
            search_pattern = f"%{patient_name.lower()}%"
            query = query.join(Study.patient)
            filters.append(
                or_(
                    Patient.first_name.ilike(search_pattern),
                    Patient.last_name.ilike(search_pattern),
                )
            )

        if filters:
            query = query.where(and_(*filters))

        # Add ordering and pagination
        query = query.order_by(Study.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_studies(
        self,
        patient_id: Optional[UUID] = None,
        modality: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> int:
        """
        Count studies matching filters.

        Args:
            Same as list_studies

        Returns:
            Total count of matching studies
        """
        query = select(func.count()).select_from(Study)

        filters = []

        if patient_id:
            filters.append(Study.patient_id == patient_id)

        if modality:
            filters.append(Study.modality == modality.upper())

        if status:
            filters.append(Study.status == status)

        if date_from:
            filters.append(Study.study_date >= date_from)

        if date_to:
            filters.append(Study.study_date <= date_to)

        if filters:
            query = query.where(and_(*filters))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def create_study(
        self,
        patient_id: UUID,
        created_by_user_id: UUID,
        modality: Optional[str] = None,
        body_part: Optional[str] = None,
        study_description: Optional[str] = None,
        study_date: Optional[date] = None,
        accession_number: Optional[str] = None,
        status: str = "created",
        source: str = "manual",
        metadata_json: Optional[dict] = None,
        storage_path: Optional[str] = None,
        study_instance_uid: Optional[str] = None,
    ) -> Study:
        """
        Create a new study.

        Args:
            patient_id: Patient UUID
            created_by_user_id: Creating user UUID
            modality: Imaging modality
            body_part: Body part examined
            study_description: Study description
            study_date: Date of study
            accession_number: Hospital accession number
            status: Study status
            source: Study source (manual, dicom_upload)
            metadata_json: Additional metadata
            storage_path: File storage path
            study_instance_uid: DICOM Study Instance UID

        Returns:
            Created study instance
        """
        return await self.create(
            patient_id=patient_id,
            created_by_user_id=created_by_user_id,
            modality=modality.upper() if modality else None,
            body_part=body_part,
            study_description=study_description,
            study_date=study_date,
            accession_number=accession_number,
            status=status,
            source=source,
            metadata_json=metadata_json,
            storage_path=storage_path,
            study_instance_uid=study_instance_uid,
        )
