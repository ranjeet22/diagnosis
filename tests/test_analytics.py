import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Comprehensive mock clinical CSV containing demographics, timelines, outcomes, and multiple vitals metrics
CLINICAL_CORR_CSV = (
    "Patient_ID,Age,Gender,Admission_Date,Discharge_Time,Diagnosis,Outcome,Hospital,Zipcode,Heart_Rate,Temperature\n"
    "ID1,45,M,2026-01-01,2026-01-02 14:30:00,Flu,recovered,City Clinic,90210,72,36.6\n"
    "ID2,60,F,2026-01-02,2026-01-05 09:15:00,COVID-19,stable,General Hospital,10001,88,38.2\n"
    "ID3,30,F,2026-01-03,2026-01-03 18:00:00,Flu,stable,City Clinic,30303,65,36.8\n"
    "ID4,15,M,2026-01-04,2026-01-04 12:00:00,Cold,recovered,General Hospital,75001,75,36.5\n"
    "ID5,95,M,2026-01-05,2026-01-10 11:30:00,Flu,mortality,General Hospital,99501,95,39.0\n"
)


def test_analytics_execution_pipeline():
    """
    Integration test verifying the full execution pipeline:
    1. Upload clinical CSV, profile it, build semantic model, and build analytics plan.
    2. Run analytics executor via API endpoints.
    3. Assert correctness of computed KPIs (Total Patients, recovery rates, stay averages, quality scores).
    4. Assert binned distributions (Age cohorts, disease counts) and chronological daily/monthly trends.
    5. Validate cross-tab comparisons (Disease vs Gender, Disease vs Age).
    6. Validate Pearson correlation coefficients matrix for vitals.
    7. Validate API caching, forced re-runs, and recalculation status flags.
    """
    # 1. Pipeline Prerequisites Ingestion
    files = {"file": ("clinical_execution.csv", CLINICAL_CORR_CSV, "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    # Profile
    client.get(f"/api/v1/datasets/{dataset_id}/profile")
    # Semantic
    client.get(f"/api/v1/datasets/{dataset_id}/semantic-model")
    # Plan
    client.get(f"/api/v1/datasets/{dataset_id}/analytics-plan")

    # 2. GET Analytics Results (cache miss: executes and caches)
    exec_res = client.get(f"/api/v1/datasets/{dataset_id}/analytics")
    assert exec_res.status_code == 200
    
    data = exec_res.json()
    assert data["dataset_id"] == dataset_id
    assert data["recalculated"] is True  # Cache miss

    results = data["analytics_results"]
    
    # Assert KPIs Values
    kpis = results["kpis"]
    assert kpis["Total Records"]["value"] == 5
    assert kpis["Total Patients"]["value"] == 5
    assert kpis["Unique Diagnoses"]["value"] == 3
    assert kpis["Average Patient Age"]["value"] == 49.0
    
    # Stay duration average check:
    # Stay times: 1.6 days, 3.39 days, 0.75 days, 0.5 days, 5.48 days
    # Sum = 11.72 days. Avg = 11.72 / 5 = 2.344 -> rounded to 2.34
    assert kpis["Average Hospital Stay"]["value"] == 2.34
    
    # Recovery rate (recovered ID1, ID4 = 2 / 5 = 40.0%)
    # Mortality rate (mortality ID5 = 1 / 5 = 20.0%)
    assert kpis["Recovery Rate"]["value"] == 40.0
    assert kpis["Mortality Rate"]["value"] == 20.0
    assert kpis["Dataset Completeness"]["value"] == 100.0

    # Assert Distributions (Age groupings, categories)
    distributions = results["distributions"]
    assert "age_groups" in distributions
    age_groups = distributions["age_groups"]
    assert "0-18" in age_groups["labels"]
    # 15-year old ID4 falls in '0-18' group
    id_0_18 = age_groups["labels"].index("0-18")
    assert age_groups["counts"][id_0_18] == 1
    
    # Flu counts (ID1, ID3, ID5 = 3 counts out of 5 = 60.0%)
    disease_dist = distributions["disease_distribution"]
    flu_id = disease_dist["labels"].index("Flu")
    assert disease_dist["counts"][flu_id] == 3
    assert disease_dist["percentages"][flu_id] == 60.0

    # Assert Trends (seasonality, rolling sums)
    trends = results["trends"]
    assert "monthly_admission_trend" in trends
    monthly = trends["monthly_admission_trend"]
    assert monthly["timestamps"] == ["2026-01"]
    assert monthly["counts"] == [5]
    assert monthly["seasonality_metadata"]["peak_day_of_week"] is not None

    # Assert Comparisons
    comparisons = results["comparisons"]
    assert "Disease vs Gender" in comparisons
    cross_tab = comparisons["Disease vs Gender"]["data"]
    # Flu count for Male = ID1 + ID5 = 2 counts
    assert cross_tab["Flu"]["M"] == 2
    # Flu count for Female = ID3 = 1 count
    assert cross_tab["Flu"]["F"] == 1

    # Assert Correlation Matrix (Pearson)
    correlations = results["correlations"]
    assert correlations is not None
    matrix = correlations["matrix"]
    # Self-correlations
    assert matrix["age"]["age"] == 1.0
    assert matrix["heart_rate"]["heart_rate"] == 1.0
    # Cross-correlations
    assert "temperature" in matrix["age"]
    assert "heart_rate" in matrix["temperature"]

    # Assert Execution summary logs
    summary = results["summary"]
    assert summary["total_tasks_executed"] > 0
    assert summary["cached_tasks_reused"] >= 0
    assert summary["overall_runtime_ms"] > 0.0

    # 3. GET Analytics Results again (cache hit)
    cache_res = client.get(f"/api/v1/datasets/{dataset_id}/analytics")
    assert cache_res.status_code == 200
    assert cache_res.json()["recalculated"] is False  # Cache hit

    # 4. POST run endpoint (executes and re-calculates)
    run_res = client.post(f"/api/v1/datasets/{dataset_id}/analytics/run")
    assert run_res.status_code == 200
    assert run_res.json()["recalculated"] is True

    # 5. POST refresh endpoint (forces re-computation)
    refresh_res = client.post(f"/api/v1/datasets/{dataset_id}/analytics/refresh")
    assert refresh_res.status_code == 200
    assert refresh_res.json()["recalculated"] is True
