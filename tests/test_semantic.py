import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Clean clinical CSV with standard columns mapping to all major concepts
CLINICAL_CSV = (
    "Patient_ID,Age,Gender,Admission_Date,Discharge_Time,Diagnosis,Outcome,Hospital,Zipcode\n"
    "ID1,45,M,2026-01-01,2026-01-02 14:30:00,Flu,readmitted,City Clinic,90210\n"
    "ID2,60,F,2026-01-02,2026-01-05 09:15:00,COVID-19,stable,General Hospital,10001\n"
    "ID3,30,F,2026-01-03,2026-01-03 18:00:00,Flu,stable,City Clinic,30303\n"
    "ID4,15,M,2026-01-04,2026-01-04 12:00:00,Cold,stable,General Hospital,75001\n"
    "ID5,95,M,2026-01-05,2026-01-10 11:30:00,Flu,readmitted,General Hospital,99501\n"
)


def test_healthcare_semantic_mapping_pipeline():
    """
    Tests that:
    1. A clinical dataset is uploaded and profiled.
    2. A semantic model is generated from the profile, identifying:
       - Synonym concepts (AGE, GENDER, DISEASE, ADMISSION_DATE, etc.)
       - Correct entity groups (Patient, Encounter, Clinical Outcome)
       - Analysis recommendations and chart suggestions.
    3. Multiple cross-column clinical relationships are correctly identified.
    4. Caching and rebuild API endpoints perform properly.
    """
    # 1. Upload CSV
    files = {"file": ("clinical_records.csv", CLINICAL_CSV, "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    # 2. Trigger profile first (semantic mapping depends on profile existence)
    profile_res = client.get(f"/api/v1/datasets/{dataset_id}/profile")
    assert profile_res.status_code == 200

    # 3. GET semantic model (cache miss: builds and saves)
    sem_res = client.get(f"/api/v1/datasets/{dataset_id}/semantic-model")
    assert sem_res.status_code == 200
    
    data = sem_res.json()
    assert data["dataset_id"] == dataset_id
    assert data["recalculated"] is True  # Cache miss
    
    model = data["semantic_model"]
    assert model["metadata"]["mapped_columns_count"] == 9
    assert model["metadata"]["unmapped_columns_count"] == 0
    assert model["metadata"]["completeness_score"] == 100.0  # Mapped all key concepts!
    assert model["metadata"]["mean_confidence_score"] == 1.0  # All columns matched exactly

    # Verify column mappings
    columns = model["columns"]
    assert columns["age"]["semantic_type"] == "AGE"
    assert columns["age"]["entity_group"] == "Patient"
    assert columns["age"]["expected_units"] == "years"
    assert "Histogram" in columns["age"]["suggested_visualizations"]

    assert columns["gender"]["semantic_type"] == "GENDER"
    assert columns["gender"]["entity_group"] == "Patient"
    assert "Pie" in columns["gender"]["suggested_visualizations"]

    assert columns["admission_date"]["semantic_type"] == "ADMISSION_DATE"
    assert columns["admission_date"]["entity_group"] == "Encounter"
    assert columns["discharge_time"]["semantic_type"] == "DISCHARGE_DATE"

    assert columns["diagnosis"]["semantic_type"] == "DISEASE"
    assert columns["diagnosis"]["entity_group"] == "Clinical Outcome"
    assert "Bar" in columns["diagnosis"]["suggested_visualizations"]
    assert "Pie" in columns["diagnosis"]["suggested_visualizations"]

    assert columns["outcome"]["semantic_type"] == "OUTCOME"
    assert columns["outcome"]["entity_group"] == "Clinical Outcome"

    assert columns["hospital"]["semantic_type"] == "HOSPITAL"
    assert columns["zipcode"]["semantic_type"] == "LOCATION"

    # Verify relationship detection
    relationships = model["relationships"]
    rel_names = {r["name"] for r in relationships}
    
    assert "admission_to_discharge_duration" in rel_names
    assert "age_vs_disease_prevalence" in rel_names
    assert "gender_vs_disease_prevalence" in rel_names
    assert "disease_vs_outcome_association" in rel_names
    assert "hospital_vs_disease_incidence" in rel_names
    assert "location_vs_disease_distribution" in rel_names

    # Check details of stay duration
    duration_rel = next(r for r in relationships if r["name"] == "admission_to_discharge_duration")
    assert duration_rel["relationship_type"] == "temporal"
    assert duration_rel["source_column"] == "admission_date"
    assert duration_rel["target_column"] == "discharge_time"

    # Verify entities structure
    entities = model["entities"]
    assert "Patient" in entities
    assert "age" in entities["Patient"]["columns"]
    assert "gender" in entities["Patient"]["columns"]
    assert "zipcode" in entities["Patient"]["columns"]
    assert "Encounter" in entities
    assert "admission_date" in entities["Encounter"]["columns"]
    assert "discharge_time" in entities["Encounter"]["columns"]

    # 4. Fetch model again (cache hit)
    cache_res = client.get(f"/api/v1/datasets/{dataset_id}/semantic-model")
    assert cache_res.status_code == 200
    assert cache_res.json()["recalculated"] is False  # cache hit!

    # 5. Force rebuild
    rebuild_res = client.post(f"/api/v1/datasets/{dataset_id}/semantic-model/rebuild")
    assert rebuild_res.status_code == 200
    assert rebuild_res.json()["recalculated"] is True  # forced refresh
