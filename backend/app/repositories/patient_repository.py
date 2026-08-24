"""
Patient repository for database operations on Patient model.
"""
from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.repositories.base_repository import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Repository for Patient model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Patient, db)

    async def get_by_mrn(self, mrn: str) -> Optional[Patient]:
        """
        Get patient by MRN.

        Args:
            mrn: Medical Record Number

        Returns:
            Patient instance or None
        """
        result = await self.db.execute(
            select(Patient).where(Patient.mrn == mrn)
        )
        return result.scalar_one_or_none()

    async def search_by_name(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Patient]:
        """
        Search patients by name (first or last).

        Args:
            search_term: Name to search for (partial match)
            skip: Records to skip
            limit: Max records to return

        Returns:
            List of matching patients
        """
        search = f"%{search_term}%"
        result = await self.db.execute(
            select(Patient)
            .where(
                or_(
                    Patient.first_name.ilike(search),
                    Patient.last_name.ilike(search)
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create_patient(
        self,
        mrn: str,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        sex: str,
        medical_history: Optional[str] = None
    ) -> Patient:
        """
        Create a new patient.

        Args:
            mrn: Medical Record Number
            first_name: Patient first name
            last_name: Patient last name
            date_of_birth: Patient date of birth
            sex: Patient sex (M/F/O)
            medical_history: Optional medical history

        Returns:
            Created patient instance
        """
        patient = Patient(
            mrn=mrn,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            sex=sex,
            medical_history=medical_history
        )
        return await self.create(patient)

    async def get_or_create_by_mrn(
        self,
        mrn: str,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        sex: str,
        medical_history: Optional[str] = None
    ) -> Tuple[Patient, bool]:
        """
        Get existing patient by MRN or create new one.

        Args:
            mrn: Medical Record Number
            first_name: Patient first name
            last_name: Patient last name
            date_of_birth: Patient date of birth
            sex: Patient sex
            medical_history: Optional medical history

        Returns:
            Tuple of (Patient instance, created flag)
        """
        existing = await self.get_by_mrn(mrn)
        if existing:
            return (existing, False)

        new_patient = await self.create_patient(
            mrn=mrn,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            sex=sex,
            medical_history=medical_history
        )
        return (new_patient, True)
