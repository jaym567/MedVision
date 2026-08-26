# backend/app/services/storage_service.py
import os
import uuid
from pathlib import Path
from typing import BinaryIO, Optional
from datetime import datetime

from app.core.config import settings


class StorageService:
    """
    Service for secure file storage.

    Handles file uploads with:
    - Safe path generation (prevents path traversal)
    - Unique filename generation
    - Configurable storage backend (currently local only)
    - Original filename preserved as metadata only
    """

    def __init__(self):
        self.storage_root = Path(settings.LOCAL_STORAGE_ROOT)
        self.dicom_path = Path(settings.DICOM_STORAGE_PATH)
        self._ensure_storage_directories()

    def _ensure_storage_directories(self) -> None:
        """Create storage directories if they don't exist."""
        dicom_dir = self.storage_root / self.dicom_path
        dicom_dir.mkdir(parents=True, exist_ok=True)

    def _generate_safe_filename(self, original_filename: str) -> str:
        """
        Generate a safe unique filename.

        Original filename is NOT used in path construction to prevent
        path traversal attacks. It's preserved for display purposes only.

        Args:
            original_filename: Original uploaded filename (untrusted)

        Returns:
            Safe unique filename with UUID
        """
        # Extract extension if present, but validate it
        _, ext = os.path.splitext(original_filename)
        # Only allow alphanumeric extensions up to 10 chars
        if ext and ext.startswith('.') and len(ext) <= 11:
            safe_ext = ''.join(c for c in ext if c.isalnum() or c == '.')
        else:
            safe_ext = ''

        # Generate UUID-based filename
        unique_id = uuid.uuid4().hex
        timestamp = datetime.utcnow().strftime('%Y%m%d')

        return f"{timestamp}_{unique_id}{safe_ext}"

    def _get_relative_path(self, filename: str) -> Path:
        """Get relative path within storage root."""
        return self.dicom_path / filename

    def save_dicom_file(
        self,
        file_content: BinaryIO,
        original_filename: str,
        file_size: int
    ) -> tuple[str, str]:
        """
        Save uploaded DICOM file securely.

        Args:
            file_content: File binary content
            original_filename: Original filename (preserved as metadata only)
            file_size: File size in bytes

        Returns:
            Tuple of (relative_storage_path, safe_filename)

        Raises:
            ValueError: If file size exceeds limit
        """
        # Validate file size
        max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise ValueError(
                f"File size {file_size} bytes exceeds maximum "
                f"{settings.MAX_UPLOAD_SIZE_MB}MB"
            )

        # Generate safe filename
        safe_filename = self._generate_safe_filename(original_filename)
        relative_path = self._get_relative_path(safe_filename)
        absolute_path = self.storage_root / relative_path

        # Write file
        with open(absolute_path, 'wb') as f:
            f.write(file_content.read())

        # Return relative path as string for database storage
        return str(relative_path), safe_filename

    def get_absolute_path(self, relative_path: str) -> Path:
        """
        Convert relative storage path to absolute filesystem path.

        Args:
            relative_path: Relative path from database

        Returns:
            Absolute filesystem path
        """
        absolute_path = self.storage_root / relative_path

        # Verify path is within storage root (prevent path traversal)
        try:
            absolute_path = absolute_path.resolve()
            storage_root_resolved = self.storage_root.resolve()
            if not str(absolute_path).startswith(str(storage_root_resolved)):
                raise ValueError("Invalid storage path - outside storage root")
        except Exception as e:
            raise ValueError(f"Invalid storage path: {e}")

        return absolute_path

    def file_exists(self, relative_path: str) -> bool:
        """Check if file exists at relative path."""
        try:
            absolute_path = self.get_absolute_path(relative_path)
            return absolute_path.exists()
        except ValueError:
            return False

    def get_file_size(self, relative_path: str) -> Optional[int]:
        """Get file size in bytes, or None if file doesn't exist."""
        try:
            absolute_path = self.get_absolute_path(relative_path)
            if absolute_path.exists():
                return absolute_path.stat().st_size
        except ValueError:
            pass
        return None
