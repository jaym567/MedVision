"""
Patient Repository

Data access layer for Patient model.
"""

from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.repositories.base_repository import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Repository for patient data access."""

    def __init__(self, db: AsyncSession):
        super().__init__(Patient, db)

    async def get_by_mrn(self, mrn: str) -> Optional[Patient]:
        """
        Get patient by Medical Record Number.

        Args:
            mrn: Medical record number

        Returns:
            Patient if found, None otherwise
        """
        result = await self.db.execute(
            select(Patient).where(Patient.mrn == mrn)
        )
        return result.scalar_one_or_none()

    async def search_by_name(
        self,
        name: str,
        limit: int = 20,
    ) -> List[Patient]:
        """
        Search patients by name (first or last).

        Args:
            name: Name to search for
            limit: Maximum number of results

        Returns:
            List of matching patients
        """
        search_pattern = f"%{name.lower()}%"
        result = await self.db.execute(
            select(Patient)
            .where(
                or_(
                    Patient.first_name.ilike(search_pattern),
                    Patient.last_name.ilike(search_pattern),
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_patient(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        mrn: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        sex: Optional[str] = None,
        medical_history: Optional[str] = None,
    ) -> Patient:
        """
        Create a new patient record.

        Args:
            first_name: Patient's first name
            last_name: Patient's last name
            mrn: Medical record number
            date_of_birth: Date of birth
            sex: Patient sex
            medical_history: Medical history notes

        Returns:
            Created patient instance
        """
        return await self.create(
            first_name=first_name,
            last_name=last_name,
            mrn=mrn,
            date_of_birth=date_of_birth,
            sex=sex,
            medical_history=medical_history,
        )

    async def get_or_create_by_mrn(
        self,
        mrn: str,
        **defaults,
    ) -> tuple[Patient, bool]:
        """
        Get existing patient by MRN or create new one.

        Args:
            mrn: Medical record number
            **defaults: Default values if creating new patient

        Returns:
            Tuple of (patient, created) where created is True if new
        """
        patient = await self.get_by_mrn(mrn)

        if patient:
            return patient, False

        patient = await self.create_patient(mrn=mrn, **defaults)
        return patient, True
