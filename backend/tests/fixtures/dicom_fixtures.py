# backend/tests/fixtures/dicom_fixtures.py
"""
Synthetic DICOM file generator for testing.

Generates minimal valid DICOM files with synthetic data.
NO REAL PATIENT DATA.
"""

# Re-export everything from the parent tests directory for backward compatibility
# The actual implementation lives in tests/dicom_fixtures.py
from tests.dicom_fixtures import (
    create_synthetic_dicom,
    save_dicom_to_file,
    create_dicom_bytes,
    create_test_ct_chest,
    create_test_mr_brain,
    create_test_xray_chest,
    create_minimal_dicom,
    create_dicom_missing_optional_fields,
)

__all__ = [
    "create_synthetic_dicom",
    "save_dicom_to_file",
    "create_dicom_bytes",
    "create_test_ct_chest",
    "create_test_mr_brain",
    "create_test_xray_chest",
    "create_minimal_dicom",
    "create_dicom_missing_optional_fields",
]
