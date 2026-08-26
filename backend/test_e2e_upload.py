"""
End-to-end test of DICOM upload workflow.
"""
import requests
import sys
sys.path.insert(0, '.')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')
from tests.fixtures.dicom_fixtures import create_test_ct_chest, create_dicom_bytes
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("MedVision AI - DICOM Upload E2E Test")
print("=" * 60)

# Step 1: Register user
print("\n1️⃣  Registering test user...")
register_response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": "dicom_test@example.com",
        "password": "test123456",
        "full_name": "DICOM Test User",
        "role": "physician"
    }
)

if register_response.status_code == 201:
    print("✅ User registered successfully")
elif register_response.status_code == 400 and "already registered" in register_response.text.lower():
    print("ℹ️  User already exists, proceeding...")
else:
    print(f"❌ Registration failed: {register_response.status_code}")
    print(register_response.json())
    sys.exit(1)

# Step 2: Login
print("\n2️⃣  Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "dicom_test@example.com",
        "password": "test123456"
    }
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.json())
    sys.exit(1)

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Login successful, token: {token[:30]}...")

# Step 3: Create synthetic DICOM
print("\n3️⃣  Creating synthetic DICOM file...")
ds = create_test_ct_chest()
dicom_bytes = create_dicom_bytes(ds)
print(f"✅ Created synthetic CT scan ({len(dicom_bytes)} bytes)")
print(f"   Patient ID: {ds.PatientID}")
print(f"   Study UID: {ds.StudyInstanceUID[:40]}...")
print(f"   Modality: {ds.Modality}")

# Step 4: Upload DICOM
print("\n4️⃣  Uploading DICOM file...")
upload_response = requests.post(
    f"{BASE_URL}/studies/upload-dicom",
    headers=headers,
    files={"file": ("test_ct.dcm", dicom_bytes, "application/dicom")}
)

if upload_response.status_code != 200:
    print(f"❌ Upload failed: {upload_response.status_code}")
    print(upload_response.json())
    sys.exit(1)

upload_data = upload_response.json()
print("✅ Upload successful!")

# Step 5: Display results
study = upload_data["study"]
metadata = upload_data["dicom_metadata"]

print("\n" + "=" * 60)
print("📊 Upload Results")
print("=" * 60)

print(f"\n🏥 Study Information:")
print(f"   Study ID: {study['id']}")
print(f"   Status: {study['status']}")
print(f"   Source: {study['source']}")
print(f"   Modality: {study['modality']}")
print(f"   Body Part: {study['body_part']}")
print(f"   Study Date: {study['study_date']}")
print(f"   Storage Path: {study['storage_path']}")

print(f"\n👤 Patient Information:")
patient = study['patient']
print(f"   Patient ID: {patient['id']}")
print(f"   MRN: {patient['mrn']}")
print(f"   Name: {patient['first_name']} {patient['last_name']}")
print(f"   Sex: {patient['sex']}")

print(f"\n📋 DICOM Metadata:")
print(f"   Study UID: {metadata['study_instance_uid'][:40]}...")
print(f"   Series UID: {metadata['series_instance_uid'][:40]}...")
print(f"   SOP UID: {metadata['sop_instance_uid'][:40]}...")
print(f"   Rows x Columns: {metadata['rows']} x {metadata['columns']}")
print(f"   Manufacturer: {metadata['manufacturer']}")

# Step 6: Verify study in list
print("\n5️⃣  Verifying study appears in list...")
list_response = requests.get(
    f"{BASE_URL}/studies",
    headers=headers
)

if list_response.status_code != 200:
    print(f"❌ Failed to get studies list")
else:
    studies_list = list_response.json()
    uploaded_study = next((s for s in studies_list["items"] if s["id"] == study["id"]), None)
    if uploaded_study:
        print(f"✅ Study found in list (total: {studies_list['total']} studies)")
    else:
        print(f"❌ Study not found in list")

# Step 7: Get study detail
print("\n6️⃣  Fetching study detail...")
detail_response = requests.get(
    f"{BASE_URL}/studies/{study['id']}",
    headers=headers
)

if detail_response.status_code != 200:
    print(f"❌ Failed to get study detail")
else:
    detail = detail_response.json()
    print(f"✅ Study detail retrieved")
    print(f"   Has metadata: {detail['metadata_json'] is not None}")
    print(f"   Metadata keys: {list(detail['metadata_json'].keys())[:5]}...")

# Step 8: Verify file storage
print("\n7️⃣  Verifying file storage...")
storage_path = Path("storage") / study['storage_path']
if storage_path.exists():
    file_size = storage_path.stat().st_size
    print(f"✅ File exists on disk ({file_size} bytes)")
    print(f"   Path: {storage_path}")
else:
    print(f"❌ File not found at {storage_path}")

print("\n" + "=" * 60)
print("✨ End-to-End Test Complete!")
print("=" * 60)
