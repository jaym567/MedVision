# create_sprint2_files.ps1
# Run from: C:\AppDev\personal\medvision\backend
# Usage: .\create_sprint2_files.ps1

Write-Host "Creating Sprint 2 Backend Files..." -ForegroundColor Green

# =============================================================================
# CORE - EXCEPTIONS
# =============================================================================
$exceptionsContent = @'
"""
Custom exception classes for MedVision AI.
Provides specific exception types for different error scenarios.
"""


class MedVisionException(Exception):
    """Base exception for all MedVision errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(MedVisionException):
    """Raised when authentication fails (401)."""
    pass


class AuthorizationError(MedVisionException):
    """Raised when user lacks permissions (403)."""
    pass


class ResourceNotFoundError(MedVisionException):
    """Raised when a requested resource doesn't exist (404)."""
    pass


class DuplicateResourceError(MedVisionException):
    """Raised when attempting to create a duplicate resource (409)."""
    pass


class ValidationError(MedVisionException):
    """Raised when input validation fails (422)."""
    pass


class InactiveUserError(MedVisionException):
    """Raised when user account is inactive (403)."""
    pass
'@

Set-Content -Path "app\core\exceptions.py" -Value $exceptionsContent
Write-Host "✓ Created app/core/exceptions.py" -ForegroundColor Cyan

# =============================================================================
# CORE - SECURITY
# =============================================================================
$securityContent = @'
"""
Security utilities for authentication and password management.
Handles password hashing, JWT token creation/validation.
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in token
        expires_delta: Optional token expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Dictionary of token claims

    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


def validate_password_strength(password: str) -> None:
    """
    Validate password meets minimum security requirements.

    Args:
        password: Password to validate

    Raises:
        ValidationError: If password doesn't meet requirements
    """
    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters")
'@

Set-Content -Path "app\core\security.py" -Value $securityContent
Write-Host "✓ Created app/core/security.py" -ForegroundColor Cyan

# =============================================================================
# REPOSITORIES - BASE
# =============================================================================
$baseRepoContent = @'
"""
Base repository with common CRUD operations.
Generic repository pattern using SQLAlchemy async sessions.
"""
from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic base repository with common database operations.

    Provides standard CRUD methods that can be inherited by specific repositories.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Async database session
        """
        self.model = model
        self.db = db

    async def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record.

        Args:
            obj: Model instance to create

        Returns:
            Created model instance
        """
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """
        Get a record by ID.

        Args:
            id: Record UUID

        Returns:
            Model instance or None if not found
        """
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        result = await self.db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def update(self, obj: ModelType) -> ModelType:
        """
        Update an existing record.

        Args:
            obj: Model instance with updated values

        Returns:
            Updated model instance
        """
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """
        Delete a record.

        Args:
            obj: Model instance to delete
        """
        await self.db.delete(obj)
        await self.db.commit()

    async def count(self) -> int:
        """
        Count total records.

        Returns:
            Total number of records
        """
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
'@

Set-Content -Path "app\repositories\base_repository.py" -Value $baseRepoContent
Write-Host "✓ Created app/repositories/base_repository.py" -ForegroundColor Cyan

# =============================================================================
# REPOSITORIES - USER
# =============================================================================
$userRepoContent = @'
"""
User repository for database operations on User model.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.

        Args:
            email: User email (case-insensitive)

        Returns:
            User instance or None
        """
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email to check

        Returns:
            True if email exists
        """
        user = await self.get_by_email(email)
        return user is not None

    async def create_user(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        role: str
    ) -> User:
        """
        Create a new user.

        Args:
            email: User email
            password_hash: Hashed password
            full_name: User full name
            role: User role

        Returns:
            Created user instance
        """
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            is_active=True,
            is_verified=False
        )
        return await self.create(user)
'@

Set-Content -Path "app\repositories\user_repository.py" -Value $userRepoContent
Write-Host "✓ Created app/repositories/user_repository.py" -ForegroundColor Cyan

# =============================================================================
# REPOSITORIES - PATIENT
# =============================================================================
$patientRepoContent = @'
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
'@

Set-Content -Path "app\repositories\patient_repository.py" -Value $patientRepoContent
Write-Host "✓ Created app/repositories/patient_repository.py" -ForegroundColor Cyan

# =============================================================================
# REPOSITORIES - STUDY
# =============================================================================
$studyRepoContent = @'
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
'@

Set-Content -Path "app\repositories\study_repository.py" -Value $studyRepoContent
Write-Host "✓ Created app/repositories/study_repository.py" -ForegroundColor Cyan

# =============================================================================
# REPOSITORIES - __init__.py
# =============================================================================
$repoInitContent = @'
from app.repositories.base_repository import BaseRepository
from app.repositories.user_repository import UserRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.study_repository import StudyRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "PatientRepository",
    "StudyRepository"
]
'@

Set-Content -Path "app\repositories\__init__.py" -Value $repoInitContent
Write-Host "✓ Updated app/repositories/__init__.py" -ForegroundColor Cyan

Write-Host "`nAll files created successfully!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: docker-compose restart backend" -ForegroundColor White
Write-Host "2. Check logs: docker-compose logs backend" -ForegroundColor White
Write-Host "3. The backend should now start without import errors" -ForegroundColor White
