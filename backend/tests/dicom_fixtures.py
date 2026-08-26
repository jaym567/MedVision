# backend/tests/fixtures/dicom_fixtures.py
"""
Synthetic DICOM file generator for testing.

Generates minimal valid DICOM files with synthetic data.
NO REAL PATIENT DATA.
"""

import io
from datetime import datetime, date
from pathlib import Path
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
import numpy as np


def create_synthetic_dicom(
    patient_id: str = "TEST001",
    patient_name: str = "Doe^John",
    patient_birth_date: str = "19800101",
    patient_sex: str = "M",
    study_instance_uid: str = None,
    series_instance_uid: str = None,
    sop_instance_uid: str = None,
    accession_number: str = "ACC001",
    modality: str = "CT",
    study_date: str = None,
    study_description: str = "Test Study",
    body_part: str = "CHEST",
    rows: int = 512,
    columns: int = 512,
    manufacturer: str = "Test Manufacturer",
    include_pixel_data: bool = False
) -> FileDataset:
    """
    Create synthetic DICOM dataset for testing.

    Args:
        patient_id: Patient ID (MRN)
        patient_name: Patient name in format LastName^FirstName
        patient_birth_date: Birth date YYYYMMDD
        patient_sex: M/F/O
        study_instance_uid: Study UID (generated if None)
        series_instance_uid: Series UID (generated if None)
        sop_instance_uid: Instance UID (generated if None)
        accession_number: Accession number
        modality: Modality (CT, MR, etc)
        study_date: Study date YYYYMMDD (today if None)
        study_description: Study description
        body_part: Body part examined
        rows: Image rows
        columns: Image columns
        manufacturer: Equipment manufacturer
        include_pixel_data: Whether to include pixel data (slower)

    Returns:
        FileDataset ready for writing
    """
    # Generate UIDs if not provided
    if study_instance_uid is None:
        study_instance_uid = generate_uid()
    if series_instance_uid is None:
        series_instance_uid = generate_uid()
    if sop_instance_uid is None:
        sop_instance_uid = generate_uid()

    # Use today if no study date
    if study_date is None:
        study_date = datetime.now().strftime('%Y%m%d')

    # Create file meta information
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
    file_meta.MediaStorageSOPInstanceUID = sop_instance_uid
    file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'  # Implicit VR Little Endian
    file_meta.ImplementationClassUID = generate_uid()

    # Create dataset using pydicom 2.4.x compatible constructor
    ds = FileDataset(
        "",           # filename_or_obj — positional, not keyword in 2.4.x
        {},           # dataset
        file_meta=file_meta,
        preamble=b"\0" * 128
    )

    # Required for pydicom < 3.0 when writing
    ds.is_implicit_VR = True
    ds.is_little_endian = True

    # Patient module
    ds.PatientID = patient_id
    ds.PatientName = patient_name
    ds.PatientBirthDate = patient_birth_date
    ds.PatientSex = patient_sex

    # Study module
    ds.StudyInstanceUID = study_instance_uid
    ds.StudyDate = study_date
    ds.StudyTime = datetime.now().strftime('%H%M%S')
    ds.AccessionNumber = accession_number
    ds.StudyDescription = study_description
    ds.StudyID = "1"

    # Series module
    ds.SeriesInstanceUID = series_instance_uid
    ds.SeriesNumber = "1"
    ds.Modality = modality
    ds.BodyPartExamined = body_part

    # Instance module
    ds.SOPInstanceUID = sop_instance_uid
    ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    ds.InstanceNumber = "1"

    # Equipment module
    ds.Manufacturer = manufacturer
    ds.ManufacturerModelName = "Test Model"

    # Image module
    ds.Rows = rows
    ds.Columns = columns
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 1

    # Display parameters
    ds.WindowCenter = "40"
    ds.WindowWidth = "400"
    ds.RescaleIntercept = "-1024"
    ds.RescaleSlope = "1"

    # Optional pixel spacing
    ds.PixelSpacing = [0.5, 0.5]  # [row, col] in mm
    ds.SliceThickness = "5.0"

    # Add synthetic pixel data if requested
    if include_pixel_data:
        # Create simple gradient pattern
        pixel_array = np.linspace(0, 4095, rows * columns, dtype=np.uint16)
        pixel_array = pixel_array.reshape((rows, columns))
        ds.PixelData = pixel_array.tobytes()

    return ds


def save_dicom_to_file(ds: FileDataset, filepath: Path) -> None:
    """Save DICOM dataset to file."""
    ds.save_as(filepath, write_like_original=False)


def create_dicom_bytes(ds: FileDataset) -> bytes:
    """Convert DICOM dataset to bytes for upload testing."""
    buffer = io.BytesIO()
    ds.save_as(buffer, write_like_original=False)
    buffer.seek(0)
    return buffer.getvalue()


# Pre-defined test fixtures
def create_test_ct_chest() -> FileDataset:
    """Create test CT chest scan."""
    return create_synthetic_dicom(
        patient_id="TEST_CT001",
        patient_name="Test^CT^Patient",
        modality="CT",
        body_part="CHEST",
        study_description="Chest CT with contrast"
    )


def create_test_mr_brain() -> FileDataset:
    """Create test MR brain scan."""
    return create_synthetic_dicom(
        patient_id="TEST_MR001",
        patient_name="Test^MR^Patient",
        patient_sex="F",
        modality="MR",
        body_part="BRAIN",
        study_description="Brain MRI T1"
    )


def create_test_xray_chest() -> FileDataset:
    """Create test chest X-ray."""
    return create_synthetic_dicom(
        patient_id="TEST_XR001",
        patient_name="Test^XRay^Patient",
        modality="CR",
        body_part="CHEST",
        study_description="Chest X-ray PA",
        rows=2048,
        columns=2048
    )


def create_minimal_dicom() -> FileDataset:
    """Create minimal DICOM with only required fields."""
    return create_synthetic_dicom(
        patient_id="MIN001",
        patient_name="Minimal^Patient",
        study_description="Minimal test",
        body_part="CHEST"
    )


def create_dicom_missing_optional_fields() -> FileDataset:
    """Create DICOM with many optional fields missing."""
    ds = create_synthetic_dicom(
        patient_id="MISSING001",
        patient_name="Missing^Fields"
    )
    # Remove optional fields
    del ds.StudyDescription
    del ds.BodyPartExamined
    del ds.Manufacturer
    del ds.WindowCenter
    del ds.WindowWidth
    del ds.PixelSpacing
    del ds.SliceThickness
    return ds
