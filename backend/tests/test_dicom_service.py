# backend/tests/test_dicom_service.py
import pytest
import tempfile
from pathlib import Path
import shutil

from app.services.dicom_service import DicomService, DicomMetadata
from pydicom.errors import InvalidDicomError
from tests.fixtures.dicom_fixtures import (
    create_test_ct_chest,
    create_test_mr_brain,
    create_minimal_dicom,
    create_dicom_missing_optional_fields,
    save_dicom_to_file
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for DICOM files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def ct_chest_file(temp_dir):
    """Create temporary CT chest DICOM file."""
    ds = create_test_ct_chest()
    filepath = temp_dir / "ct_chest.dcm"
    save_dicom_to_file(ds, filepath)
    return filepath


@pytest.fixture
def mr_brain_file(temp_dir):
    """Create temporary MR brain DICOM file."""
    ds = create_test_mr_brain()
    filepath = temp_dir / "mr_brain.dcm"
    save_dicom_to_file(ds, filepath)
    return filepath


@pytest.fixture
def minimal_dicom_file(temp_dir):
    """Create minimal DICOM file."""
    ds = create_minimal_dicom()
    filepath = temp_dir / "minimal.dcm"
    save_dicom_to_file(ds, filepath)
    return filepath


class TestDicomService:
    """Test suite for DicomService."""

    def test_validate_valid_dicom(self, ct_chest_file):
        """Test validation of valid DICOM file."""
        assert DicomService.validate_dicom_file(ct_chest_file) is True

    def test_validate_invalid_file(self, temp_dir):
        """Test validation of non-DICOM file."""
        invalid_file = temp_dir / "not_dicom.txt"
        invalid_file.write_text("This is not a DICOM file")

        assert DicomService.validate_dicom_file(invalid_file) is False

    def test_validate_nonexistent_file(self, temp_dir):
        """Test validation of non-existent file."""
        nonexistent = temp_dir / "does_not_exist.dcm"
        assert DicomService.validate_dicom_file(nonexistent) is False

    def test_extract_metadata_ct_chest(self, ct_chest_file):
        """Test metadata extraction from CT chest scan."""
        metadata = DicomService.extract_metadata(ct_chest_file)

        assert metadata is not None
        assert metadata.patient_id == "TEST_CT001"
        assert metadata.patient_name == "Test CT Patient"
        assert metadata.patient_sex in ["M", "F", "O"]
        assert metadata.modality == "CT"
        assert metadata.body_part_examined == "CHEST"
        assert metadata.study_instance_uid is not None
        assert metadata.series_instance_uid is not None
        assert metadata.sop_instance_uid is not None
        assert metadata.rows == 512
        assert metadata.columns == 512
        assert metadata.manufacturer == "Test Manufacturer"

    def test_extract_metadata_mr_brain(self, mr_brain_file):
        """Test metadata extraction from MR brain scan."""
        metadata = DicomService.extract_metadata(mr_brain_file)

        assert metadata is not None
        assert metadata.patient_id == "TEST_MR001"
        assert metadata.patient_sex == "F"
        assert metadata.modality == "MR"
        assert metadata.body_part_examined == "BRAIN"

    def test_extract_metadata_to_dict(self, ct_chest_file):
        """Test metadata conversion to dictionary."""
        metadata = DicomService.extract_metadata(ct_chest_file)
        data = metadata.to_dict()

        assert isinstance(data, dict)
        assert 'study_instance_uid' in data
        assert 'modality' in data
        assert 'patient_id' in data
        assert None not in data.values()  # No None values

    def test_extract_metadata_missing_optional_fields(self, temp_dir):
        """Test metadata extraction with missing optional fields."""
        ds = create_dicom_missing_optional_fields()
        filepath = temp_dir / "missing_fields.dcm"
        save_dicom_to_file(ds, filepath)

        metadata = DicomService.extract_metadata(filepath)

        # Required fields still present
        assert metadata.study_instance_uid is not None
        assert metadata.sop_instance_uid is not None

        # Optional fields gracefully None
        data = metadata.to_dict()
        assert 'study_description' not in data  # None values removed
        assert 'body_part_examined' not in data

    def test_extract_metadata_invalid_dicom(self, temp_dir):
        """Test metadata extraction from invalid DICOM."""
        invalid_file = temp_dir / "invalid.dcm"
        invalid_file.write_text("Not a DICOM file")

        with pytest.raises(InvalidDicomError):
            DicomService.extract_metadata(invalid_file)

    def test_extract_metadata_missing_required_field(self, temp_dir):
        """Test metadata extraction with missing required field."""
        ds = create_minimal_dicom()
        # Remove required field
        del ds.StudyInstanceUID

        filepath = temp_dir / "no_study_uid.dcm"
        save_dicom_to_file(ds, filepath)

        with pytest.raises(ValueError, match="Missing required field"):
            DicomService.extract_metadata(filepath)

    def test_parse_patient_name_standard_format(self):
        """Test patient name parsing from standard format."""
        first, last = DicomService.parse_patient_name("John Doe")
        assert first == "John"
        assert last == "Doe"

    def test_parse_patient_name_multiple_names(self):
        """Test patient name parsing with multiple names."""
        first, last = DicomService.parse_patient_name("John Michael Doe Smith")
        assert first == "John"
        assert last == "Michael Doe Smith"

    def test_parse_patient_name_single_name(self):
        """Test patient name parsing with single name."""
        first, last = DicomService.parse_patient_name("Doe")
        assert first is None
        assert last == "Doe"

    def test_parse_patient_name_none(self):
        """Test patient name parsing with None."""
        first, last = DicomService.parse_patient_name(None)
        assert first is None
        assert last is None

    def test_parse_patient_name_empty(self):
        """Test patient name parsing with empty string."""
        first, last = DicomService.parse_patient_name("")
        assert first is None
        assert last is None


class TestDicomMetadata:
    """Test suite for DicomMetadata class."""

    def test_metadata_properties(self, ct_chest_file):
        """Test that all metadata properties are accessible."""
        import pydicom
        ds = pydicom.dcmread(ct_chest_file)
        metadata = DicomMetadata(ds)

        # Test all properties don't raise exceptions
        _ = metadata.patient_id
        _ = metadata.patient_name
        _ = metadata.patient_birth_date
        _ = metadata.patient_sex
        _ = metadata.study_instance_uid
        _ = metadata.series_instance_uid
        _ = metadata.sop_instance_uid
        _ = metadata.accession_number
        _ = metadata.modality
        _ = metadata.study_date
        _ = metadata.study_description
        _ = metadata.body_part_examined
        _ = metadata.manufacturer
        _ = metadata.rows
        _ = metadata.columns
        _ = metadata.pixel_spacing
        _ = metadata.slice_thickness
        _ = metadata.window_center
        _ = metadata.window_width
        _ = metadata.photometric_interpretation

    def test_date_conversion(self, ct_chest_file):
        """Test DICOM date format conversion."""
        import pydicom
        ds = pydicom.dcmread(ct_chest_file)
        metadata = DicomMetadata(ds)

        study_date = metadata.study_date
        if study_date:
            # Should be in ISO format YYYY-MM-DD
            assert len(study_date) == 10
            assert study_date[4] == '-'
            assert study_date[7] == '-'

    def test_safe_get_with_missing_tag(self, ct_chest_file):
        """Test safe tag access with missing tag."""
        import pydicom
        ds = pydicom.dcmread(ct_chest_file)
        # Remove a tag
        if hasattr(ds, 'StudyDescription'):
            del ds.StudyDescription

        metadata = DicomMetadata(ds)
        # Should return None gracefully
        assert metadata.study_description is None
