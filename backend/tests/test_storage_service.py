# backend/tests/test_storage_service.py
import pytest
import io
from pathlib import Path
import tempfile
import shutil

from app.services.storage_service import StorageService
from app.core.config import settings


@pytest.fixture
def temp_storage_root(monkeypatch):
    """Create temporary storage root for testing."""
    temp_dir = tempfile.mkdtemp()
    monkeypatch.setattr(settings, 'LOCAL_STORAGE_ROOT', temp_dir)
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def storage_service(temp_storage_root):
    """Create StorageService with temporary storage."""
    return StorageService()


class TestStorageService:
    """Test suite for StorageService."""

    def test_storage_directories_created(self, storage_service, temp_storage_root):
        """Test that storage directories are created on initialization."""
        dicom_dir = temp_storage_root / settings.DICOM_STORAGE_PATH
        assert dicom_dir.exists()
        assert dicom_dir.is_dir()

    def test_generate_safe_filename(self, storage_service):
        """Test safe filename generation."""
        # Test with normal filename
        filename = storage_service._generate_safe_filename("test.dcm")
        assert filename.endswith(".dcm")
        assert len(filename) > 10  # Should have timestamp and UUID

        # Test with path traversal attempt
        filename = storage_service._generate_safe_filename("../../etc/passwd")
        assert ".." not in filename
        assert "/" not in filename
        assert "\\" not in filename

        # Test with no extension
        filename = storage_service._generate_safe_filename("testfile")
        assert not filename.endswith(".")

    def test_save_dicom_file_success(self, storage_service, temp_storage_root):
        """Test successful file save."""
        file_content = io.BytesIO(b"fake dicom content")
        original_filename = "test_scan.dcm"
        file_size = len(b"fake dicom content")

        relative_path, safe_filename = storage_service.save_dicom_file(
            file_content, original_filename, file_size
        )

        # Check return values
        assert relative_path.startswith(settings.DICOM_STORAGE_PATH)
        assert safe_filename.endswith(".dcm")

        # Check file exists
        absolute_path = temp_storage_root / relative_path
        assert absolute_path.exists()

        # Check content
        with open(absolute_path, 'rb') as f:
            assert f.read() == b"fake dicom content"

    def test_save_file_exceeds_size_limit(self, storage_service, monkeypatch):
        """Test that oversized files are rejected."""
        # Set very small limit
        monkeypatch.setattr(settings, 'MAX_UPLOAD_SIZE_MB', 0.001)  # 1KB

        # Create file larger than limit
        large_content = io.BytesIO(b"x" * 2000)  # 2KB

        with pytest.raises(ValueError, match="exceeds maximum"):
            storage_service.save_dicom_file(
                large_content, "large.dcm", 2000
            )

    def test_get_absolute_path(self, storage_service, temp_storage_root):
        """Test conversion of relative to absolute path."""
        relative_path = f"{settings.DICOM_STORAGE_PATH}/test_file.dcm"
        absolute_path = storage_service.get_absolute_path(relative_path)

        expected_path = temp_storage_root / settings.DICOM_STORAGE_PATH / "test_file.dcm"
        assert absolute_path == expected_path

    def test_get_absolute_path_prevents_traversal(self, storage_service):
        """Test that path traversal is prevented."""
        with pytest.raises(ValueError, match="outside storage root"):
            storage_service.get_absolute_path("../../etc/passwd")

    def test_file_exists(self, storage_service, temp_storage_root):
        """Test file existence check."""
        # Create a file
        file_content = io.BytesIO(b"test")
        relative_path, _ = storage_service.save_dicom_file(
            file_content, "test.dcm", 4
        )

        # Check it exists
        assert storage_service.file_exists(relative_path)

        # Check non-existent file
        assert not storage_service.file_exists("nonexistent/file.dcm")

    def test_get_file_size(self, storage_service):
        """Test file size retrieval."""
        content = b"test content with some length"
        file_content = io.BytesIO(content)
        relative_path, _ = storage_service.save_dicom_file(
            file_content, "test.dcm", len(content)
        )

        size = storage_service.get_file_size(relative_path)
        assert size == len(content)

        # Non-existent file
        assert storage_service.get_file_size("nonexistent.dcm") is None
