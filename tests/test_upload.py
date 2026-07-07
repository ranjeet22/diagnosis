import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

# Sample valid CSV content
VALID_CSV = (
    "PatientID,Age,AdmissionDate,Diagnosis\n"
    "1,45,2026-01-01,Flu\n"
    "2,60,2026-01-02,COVID-19\n"
    "3,30,2026-01-03,Cold\n"
)

# Sample invalid CSV content (mismatched columns)
INVALID_CSV = (
    "PatientID,Age,AdmissionDate,Diagnosis\n"
    "1,45,2026-01-01,Flu,ExtraCol\n"
    "2,60\n"
)


def test_successful_upload():
    """
    Tests uploading a valid CSV dataset. Verifies status, UUID generation,
    dimensions, and subsequent metadata query.
    """
    files = {"file": ("patients.csv", VALID_CSV, "text/csv")}
    response = client.post("/api/v1/datasets/upload", files=files)
    
    assert response.status_code == 201
    res_data = response.json()
    assert "dataset_id" in res_data
    assert res_data["filename"] == "patients.csv"
    assert res_data["status"] == "VALIDATED"
    assert res_data["rows"] == 3
    assert res_data["columns"] == 4

    # Query metadata using the returned dataset ID
    dataset_id = res_data["dataset_id"]
    meta_response = client.get(f"/api/v1/datasets/{dataset_id}")
    
    assert meta_response.status_code == 200
    meta_data = meta_response.json()
    assert meta_data["dataset_id"] == dataset_id
    assert meta_data["original_filename"] == "patients.csv"
    assert meta_data["column_names"] == ["PatientID", "Age", "AdmissionDate", "Diagnosis"]
    assert meta_data["delimiter"] == ","
    assert meta_data["rows"] == 3
    assert meta_data["columns"] == 4
    assert meta_data["encoding"] in ("utf-8", "ascii")


def test_upload_empty_file():
    """
    Tests that an empty file upload is rejected.
    """
    files = {"file": ("empty.csv", "", "text/csv")}
    response = client.post("/api/v1/datasets/upload", files=files)
    
    assert response.status_code == 422
    assert "EmptyDataset" in response.json()["error"]


def test_upload_invalid_extension():
    """
    Tests that files with unsupported extensions are rejected.
    """
    files = {"file": ("report.pdf", "Some random pdf bytes", "application/pdf")}
    response = client.post("/api/v1/datasets/upload", files=files)
    
    assert response.status_code == 422
    assert "UnsupportedFormat" in response.json()["error"]


def test_upload_invalid_csv_structure():
    """
    Tests that malformed CSV files (e.g. columns mismatched) are rejected.
    """
    files = {"file": ("corrupted.csv", INVALID_CSV, "text/csv")}
    response = client.post("/api/v1/datasets/upload", files=files)
    
    assert response.status_code == 422
    assert "InvalidCSV" in response.json()["error"]


def test_upload_file_too_large():
    """
    Temporarily overrides configuration size limits to test that file size
    enforcement functions correctly.
    """
    original_limit = settings.STORAGE_MAX_FILE_SIZE_MB
    # Set limit to 0MB (rejects everything)
    settings.STORAGE_MAX_FILE_SIZE_MB = 0
    
    try:
        files = {"file": ("large.csv", VALID_CSV, "text/csv")}
        response = client.post("/api/v1/datasets/upload", files=files)
        assert response.status_code == 413
        assert "DatasetTooLarge" in response.json()["error"]
    finally:
        # Reset configuration
        settings.STORAGE_MAX_FILE_SIZE_MB = original_limit


def test_duplicate_filenames_no_overwrite():
    """
    Verifies that uploading two different files with the same name generates
    unique IDs and both metadata copies are stored safely without conflicts.
    """
    files1 = {"file": ("data.csv", VALID_CSV, "text/csv")}
    response1 = client.post("/api/v1/datasets/upload", files=files1)
    assert response1.status_code == 201
    id1 = response1.json()["dataset_id"]

    files2 = {"file": ("data.csv", VALID_CSV, "text/csv")}
    response2 = client.post("/api/v1/datasets/upload", files=files2)
    assert response2.status_code == 201
    id2 = response2.json()["dataset_id"]

    assert id1 != id2

    # Verify both exist separately
    meta1 = client.get(f"/api/v1/datasets/{id1}").json()
    meta2 = client.get(f"/api/v1/datasets/{id2}").json()
    
    assert meta1["dataset_id"] == id1
    assert meta2["dataset_id"] == id2
