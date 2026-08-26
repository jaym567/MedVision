# backend/tests/test_dicom_upload_flow.py
"""
Integration tests for DICOM upload workflow.

Tests the complete end-to-end flow:
1. User authentication
2. DICOM file upload
3. Patient creation/matching
4. Study creation/update
5. Metadata extraction
6. File storage
"""
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from pathlib import Path
import tempfile
import shutil

from app.models.user import User
from app.models.patient import Patient
from app.models.study import Study
from app.services.storage_service import StorageService
from tests.fixtures.dicom_fixtures import (
    create_test_ct_chest,
    create_test_mr_brain,
    create_test_xray_chest,
    save_dicom_to_file,
    create_dicom_bytes
)


@pytest.fixture
def temp_storage(monkeypatch):
    """Create temporary storage directory for tests."""
    temp_dir = tempfile.mkdtemp()
    from app.core import config
    monkeypatch.setattr(config.settings, 'LOCAL_STORAGE_ROOT', temp_dir)
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestDicomUploadFlow:
    """Integration tests for DICOM upload workflow."""

    @pytest.mark.asyncio
    async def test_upload_valid_ct_creates_patient_and_study(
        self,
        client: AsyncClient,
        test_user: dict,
        temp_storage: Path
    ):
        """Test uploading valid CT DICOM creates patient and study."""
        # Create synthetic CT DICOM
        ds = create_test_ct_chest()
        dicom_bytes = create_dicom_bytes(ds)

        # Upload DICOM
        response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct_chest.dcm", dicom_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "study" in data
        assert "dicom_metadata" in data
        assert "message" in data
        assert data["message"] == "DICOM uploaded successfully"

        # Verify study data
        study = data["study"]
        assert study["source"] == "dicom_upload"
        assert study["status"] == "ready"
        assert study["modality"] == "CT"
        assert study["body_part"] == "CHEST"
        assert study["storage_path"] is not None

        # Verify metadata
        metadata = data["dicom_metadata"]
        assert metadata["modality"] == "CT"
        assert metadata["body_part_examined"] == "CHEST"
        assert metadata["patient_id"] == "TEST_CT001"
        assert metadata["study_instance_uid"] is not None
        assert metadata["series_instance_uid"] is not None
        assert metadata["sop_instance_uid"] is not None

        # Verify file was saved
        storage_service = StorageService()
        assert storage_service.file_exists(study["storage_path"])

    @pytest.mark.asyncio
    async def test_upload_creates_new_patient(
        self,
        client: AsyncClient,
        test_user: dict,
        db_session,
        temp_storage: Path
    ):
        """Test that upload creates new patient from DICOM metadata."""
        ds = create_test_ct_chest()
        dicom_bytes = create_dicom_bytes(ds)

        # Verify patient doesn't exist yet
        result = await db_session.execute(
            select(Patient).where(Patient.mrn == "TEST_CT001")
        )
        assert result.scalar_one_or_none() is None

        # Upload DICOM
        response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct_chest.dcm", dicom_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )

        assert response.status_code == 200

        # Verify patient was created
        result = await db_session.execute(
            select(Patient).where(Patient.mrn == "TEST_CT001")
        )
        patient = result.scalar_one_or_none()
        assert patient is not None
        assert patient.first_name == "Test"
        assert patient.last_name == "CT Patient"
        assert patient.sex in ["M", "F", "O"]

    @pytest.mark.asyncio
    async def test_upload_reuses_existing_patient(
        self,
        client: AsyncClient,
        test_user: dict,
        db_session,
        temp_storage: Path
    ):
        """Test that upload reuses existing patient with same MRN."""
        from datetime import date
        # Create patient manually
        existing_patient = Patient(
            mrn="TEST_CT001",
            first_name="Existing",
            last_name="Patient",
            date_of_birth=date(1980, 1, 1),
            sex="M"
        )
        db_session.add(existing_patient)
        await db_session.commit()
        await db_session.refresh(existing_patient)

        # Upload DICOM with same patient ID
        ds = create_test_ct_chest()
        dicom_bytes = create_dicom_bytes(ds)

        response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct_chest.dcm", dicom_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )

        assert response.status_code == 200
        data = response.json()

        # Verify same patient was used
        assert data["study"]["patient"]["id"] == str(existing_patient.id)

        # Verify only one patient exists
        result = await db_session.execute(
            select(Patient).where(Patient.mrn == "TEST_CT001")
        )
        patients = result.scalars().all()
        assert len(patients) == 1

    @pytest.mark.asyncio
    async def test_upload_duplicate_study_updates_existing(
        self,
        client: AsyncClient,
        test_user: dict,
        db_session,
        temp_storage: Path
    ):
        """Test that uploading same StudyInstanceUID updates existing study."""
        ds = create_test_ct_chest()
        dicom_bytes = create_dicom_bytes(ds)

        # First upload
        response1 = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct_chest.dcm", dicom_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response1.status_code == 200
        study_id_1 = response1.json()["study"]["id"]

        # Second upload of same study
        response2 = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct_chest.dcm", dicom_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert response2.status_code == 200
        study_id_2 = response2.json()["study"]["id"]

        # Should be same study
        assert study_id_1 == study_id_2

        # Verify only one study exists
        study_uid = ds.StudyInstanceUID
        result = await db_session.execute(
            select(Study).where(Study.study_instance_uid == study_uid)
        )
        studies = result.scalars().all()
        assert len(studies) == 1

    @pytest.mark.asyncio
    async def test_upload_different_modalities(
        self,
        client: AsyncClient,
        test_user: dict,
        temp_storage: Path
    ):
        """Test uploading different modalities creates separate studies."""
        # Upload CT
        ct_ds = create_test_ct_chest()
        ct_bytes = create_dicom_bytes(ct_ds)
        ct_response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct.dcm", ct_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert ct_response.status_code == 200
        assert ct_response.json()["study"]["modality"] == "CT"

        # Upload MR
        mr_ds = create_test_mr_brain()
        mr_bytes = create_dicom_bytes(mr_ds)
        mr_response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("mr.dcm", mr_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert mr_response.status_code == 200
        assert mr_response.json()["study"]["modality"] == "MR"

        # Upload X-Ray
        xr_ds = create_test_xray_chest()
        xr_bytes = create_dicom_bytes(xr_ds)
        xr_response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("xr.dcm", xr_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert xr_response.status_code == 200
        assert xr_response.json()["study"]["modality"] == "CR"

    @pytest.mark.asyncio
    async def test_upload_without_authentication_fails(
        self,
        client: AsyncClient,
        temp_storage: Path
    ):
        """Test that upload without auth returns 401."""
        ds = create_test_ct_chest()
        dicom_bytes = create_dicom_bytes(ds)

        response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct.dcm", dicom_bytes, "application/dicom")}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_upload_invalid_file_fails(
        self,
        client: AsyncClient,
        test_user: dict,
        temp_storage: Path
    ):
        """Test that uploading non-DICOM file returns 422."""
        invalid_content = b"This is not a DICOM file"

        response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("fake.dcm", invalid_content, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )

        assert response.status_code == 422
        assert "not a valid DICOM file" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_oversized_file_fails(
        self,
        client: AsyncClient,
        test_user: dict,
        temp_storage: Path,
        monkeypatch
    ):
        """Test that oversized file returns 413."""
        # Set very small limit
        from app.core import config
        monkeypatch.setattr(config.settings, 'MAX_UPLOAD_SIZE_MB', 0.001)  # 1KB

        # Create file larger than limit
        large_content = b"x" * 2000  # 2KB

        response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("large.dcm", large_content, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )

        assert response.status_code == 413
        assert "exceeds maximum" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_upload_extracts_complete_metadata(
        self,
        client: AsyncClient,
        test_user: dict,
        temp_storage: Path
    ):
        """Test that all metadata fields are extracted correctly."""
        ds = create_test_ct_chest()
        dicom_bytes = create_dicom_bytes(ds)

        response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct.dcm", dicom_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )

        assert response.status_code == 200
        metadata = response.json()["dicom_metadata"]

        # Verify all key fields present
        assert metadata["patient_id"] is not None
        assert metadata["study_instance_uid"] is not None
        assert metadata["series_instance_uid"] is not None
        assert metadata["sop_instance_uid"] is not None
        assert metadata["modality"] is not None
        assert metadata["rows"] == 512
        assert metadata["columns"] == 512
        assert metadata["manufacturer"] == "Test Manufacturer"

        # Verify study has metadata in JSON
        study = response.json()["study"]
        assert study["metadata_json"] is not None
        assert "study_instance_uid" in study["metadata_json"]
        assert "modality" in study["metadata_json"]

    @pytest.mark.asyncio
    async def test_uploaded_study_appears_in_list(
        self,
        client: AsyncClient,
        test_user: dict,
        temp_storage: Path
    ):
        """Test that uploaded study appears in studies list."""
        # Upload DICOM
        ds = create_test_ct_chest()
        dicom_bytes = create_dicom_bytes(ds)

        upload_response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct.dcm", dicom_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert upload_response.status_code == 200
        study_id = upload_response.json()["study"]["id"]

        # Get studies list
        list_response = await client.get(
            "/api/v1/studies",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert list_response.status_code == 200

        # Verify uploaded study is in list
        studies = list_response.json()["items"]
        study_ids = [s["id"] for s in studies]
        assert study_id in study_ids

        # Verify study has correct source
        uploaded_study = next(s for s in studies if s["id"] == study_id)
        assert uploaded_study["modality"] == "CT"

    @pytest.mark.asyncio
    async def test_uploaded_study_detail_endpoint(
        self,
        client: AsyncClient,
        test_user: dict,
        temp_storage: Path
    ):
        """Test that uploaded study can be retrieved via detail endpoint."""
        # Upload DICOM
        ds = create_test_ct_chest()
        dicom_bytes = create_dicom_bytes(ds)

        upload_response = await client.post(
            "/api/v1/studies/upload-dicom",
            files={"file": ("ct.dcm", dicom_bytes, "application/dicom")},
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert upload_response.status_code == 200
        study_id = upload_response.json()["study"]["id"]

        # Get study detail
        detail_response = await client.get(
            f"/api/v1/studies/{study_id}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        assert detail_response.status_code == 200

        study = detail_response.json()
        assert study["id"] == study_id
        assert study["source"] == "dicom_upload"
        assert study["status"] == "ready"
        assert study["storage_path"] is not None
        assert study["metadata_json"] is not None
