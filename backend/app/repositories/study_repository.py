"""
Study repository for database operations on Study model.
"""
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import date
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study import Study
from app.repositories.base_repository import BaseRepository


class StudyRepository(BaseRepository[Study]):
    """Repository for Study model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Study, db)

    async def get_by_id_with_relations(self, study_id: UUID) -> Optional[Study]:
        """
        Get study by ID with patient and user relationships loaded.

        Args:
            study_id: Study UUID

        Returns:
            Study instance with relations or None
        """
        result = await self.db.execute(
            select(Study)
            .options(
                selectinload(Study.patient),
                selectinload(Study.created_by_user)
            )
            .where(Study.id == study_id)
        )
        return result.scalar_one_or_none()

    async def list_studies(
        self,
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[UUID] = None,
        modality: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        patient_name: Optional[str] = None
    ) -> List[Study]:
        """
        List studies with filtering and pagination.

        Args:
            skip: Records to skip
            limit: Max records to return
            patient_id: Filter by patient ID
            modality: Filter by modality
            status: Filter by status
            date_from: Filter by study date from
            date_to: Filter by study date to
            patient_name: Filter by patient name

        Returns:
            List of studies with relations loaded
        """
        query = select(Study).options(
            selectinload(Study.patient),
            selectinload(Study.created_by_user)
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

        # Apply filters
        if filters:
            query = query.where(and_(*filters))

        # Patient name search requires join
        if patient_name:
            from app.models.patient import Patient
            search = f"%{patient_name}%"
            query = query.join(Study.patient).where(
                (Patient.first_name.ilike(search)) |
                (Patient.last_name.ilike(search))
            )

        # Add pagination and ordering
        query = query.order_by(Study.study_date.desc(), Study.created_at.desc())
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
        patient_name: Optional[str] = None
    ) -> int:
        """
        Count studies matching filters.

        Args:
            Same as list_studies

        Returns:
            Total count of matching studies
        """
        query = select(func.count()).select_from(Study)

        # Build filters (same as list_studies)
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

        if patient_name:
            from app.models.patient import Patient
            search = f"%{patient_name}%"
            query = query.join(Study.patient).where(
                (Patient.first_name.ilike(search)) |
                (Patient.last_name.ilike(search))
            )

        result = await self.db.execute(query)
        return result.scalar_one()

    async def create_study(
        self,
        patient_id: UUID,
        created_by_user_id: UUID,
        accession_number: str,
        modality: str,
        study_date: date,
        body_part: Optional[str] = None,
        study_description: Optional[str] = None,
        study_instance_uid: Optional[str] = None,
        status: str = "created",
        source: str = "manual",
        metadata_json: Optional[dict] = None,
        storage_path: Optional[str] = None
    ) -> Study:
        """
        Create a new study.

        Args:
            patient_id: Patient UUID
            created_by_user_id: User UUID who created the study
            accession_number: Study accession number
            modality: Study modality (CT, MR, etc.)
            study_date: Date of study
            body_part: Body part examined
            study_description: Study description
            study_instance_uid: DICOM Study Instance UID
            status: Study status
            source: Study source
            metadata_json: Additional metadata as JSON
            storage_path: Path to stored images

        Returns:
            Created study instance
        """
        study = Study(
            patient_id=patient_id,
            created_by_user_id=created_by_user_id,
            accession_number=accession_number,
            modality=modality.upper(),
            study_date=study_date,
            body_part=body_part,
            study_description=study_description,
            study_instance_uid=study_instance_uid,
            status=status,
            source=source,
            metadata_json=metadata_json,
            storage_path=storage_path
        )
        return await self.create(study)
