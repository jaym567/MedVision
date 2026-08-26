# test_create_dicom.py (run this in backend directory)
import sys
sys.path.insert(0, '.')
from tests.fixtures.dicom_fixtures import create_test_ct_chest, create_dicom_bytes
import os

# Create synthetic CT chest DICOM
dicom = create_test_ct_chest()
dicom_bytes = create_dicom_bytes(dicom)

# Save to a file you can upload
output_path = "test_upload.dcm"
with open(output_path, 'wb') as f:
    f.write(dicom_bytes)

print(f"Created test DICOM file: {output_path}")
print(f"Size: {len(dicom_bytes)} bytes")
print(f"Patient MRN: {dicom.PatientID}")
print(f"Study UID: {dicom.StudyInstanceUID}")
