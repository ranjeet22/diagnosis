import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Standard full clinical CSV
CLINICAL_CSV = (
    "Patient_ID,Age,Gender,Admission_Date,Discharge_Time,Diagnosis,Outcome,Hospital,Zipcode\n"
    "ID1,45,M,2026-01-01,2026-01-02 14:30:00,Flu,recovered,City Clinic,90210\n"
    "ID2,60,F,2026-01-02,2026-01-05 09:15:00,COVID-19,stable,General Hospital,10001\n"
    "ID3,30,F,2026-01-03,2026-01-03 18:00:00,Flu,stable,City Clinic,30303\n"
    "ID4,15,M,2026-01-04,2026-01-04 12:00:00,Cold,recovered,General Hospital,75001\n"
    "ID5,95,M,2026-01-05,2026-01-10 11:30:00,Flu,mortality,General Hospital,99501\n"
)


def test_analytics_planning_pipeline():
    """
    Tests the full end-to-end planning engine pipeline:
    1. Ingest clinical records CSV.
    2. Profile dataset.
    3. Generate Semantic Model.
    4. Generate Analytics Execution Plan and assert:
       - KPIs mapping formulas & dashboard placements.
       - Correct AnalysisTasks planning and ECharts visualization planner.
       - Execution graph edges representing computational dependencies.
       - Logical comparison tabs and filter recommendations.
       - Cache mechanisms and forced rebuild endpoints.
    """
    # 1. Ingestion
    files = {"file": ("clinical.csv", CLINICAL_CSV, "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    # 2. Profile
    profile_res = client.get(f"/api/v1/datasets/{dataset_id}/profile")
    assert profile_res.status_code == 200

    # 3. Semantic Mapping
    sem_res = client.get(f"/api/v1/datasets/{dataset_id}/semantic-model")
    assert sem_res.status_code == 200

    # 4. GET Analytics Plan (cache miss: builds and caches)
    plan_res = client.get(f"/api/v1/datasets/{dataset_id}/analytics-plan")
    assert plan_res.status_code == 200
    
    data = plan_res.json()
    assert data["dataset_id"] == dataset_id
    assert data["recalculated"] is True  # Cache miss

    plan = data["analytics_plan"]
    
    # Assert KPIs details
    kpis = plan["kpis"]
    kpi_names = {k["name"] for k in kpis}
    assert "Total Patients" in kpi_names
    assert "Average Patient Age" in kpi_names
    assert "Recovery Rate" in kpi_names
    assert "Mortality Rate" in kpi_names
    assert "Unique Diagnoses" in kpi_names
    assert "Dataset Completeness" in kpi_names
    assert "Data Quality Score" in kpi_names

    recovery_kpi = next(k for k in kpis if k["name"] == "Recovery Rate")
    assert recovery_kpi["aggregation_type"] == "percentage"
    assert recovery_kpi["dashboard_placement"] == "Overview"
    assert "recovered" in recovery_kpi["formula"]

    # Assert Analysis Tasks
    tasks = plan["analysis_tasks"]
    task_ids = {t["task_id"] for t in tasks}
    assert "disease_distribution" in task_ids
    assert "age_histogram" in task_ids
    assert "monthly_admission_trend" in task_ids
    assert "gender_distribution" in task_ids
    assert "recovery_rate" in task_ids
    
    # Assert specific visualization recommendations
    dis_task = next(t for t in tasks if t["task_id"] == "disease_distribution")
    assert dis_task["visualization"]["chart_family"] == "Bar"
    assert dis_task["visualization"]["recommended_size"] == "half"
    assert dis_task["priority_score"] > 50.0  # High business value & confidence

    trend_task = next(t for t in tasks if t["task_id"] == "monthly_admission_trend")
    assert trend_task["visualization"]["chart_family"] in {"Line", "Area"}
    assert trend_task["visualization"]["recommended_size"] == "full"

    # Assert comparison plans
    comparisons = plan["comparison_plans"]
    comp_names = {c["name"] for c in comparisons}
    assert "Disease vs Age" in comp_names
    assert "Disease vs Gender" in comp_names
    assert "Disease vs Outcome" in comp_names

    # Assert Filter Recommendations
    filters = plan["filter_recommendations"]
    filter_labels = {f["label"] for f in filters}
    assert "Age Range" in filter_labels
    assert "Gender" in filter_labels
    assert "Diagnosis" in filter_labels
    assert "Outcome" in filter_labels

    # Assert Dashboard Layout Sections
    sections = plan["dashboard_sections"]
    sec_names = {s["section_name"] for s in sections}
    assert "Overview" in sec_names
    assert "Demographics" in sec_names
    assert "Temporal Trends" in sec_names
    assert "Disease Analytics" in sec_names

    # Assert Execution dependency Graph
    graph = plan["execution_graph"]
    assert "disease_distribution" in graph["nodes"]
    assert "Average Patient Age" in graph["nodes"]
    
    edges = [tuple(edge) for edge in graph["edges"]]
    # Age histogram should depend on age_distribution task
    assert ("age_distribution", "age_histogram") in edges
    # Average Patient Age KPI should depend on average_age task
    assert ("average_age", "Average Patient Age") in edges

    # 5. GET Plan again (cache hit)
    cache_res = client.get(f"/api/v1/datasets/{dataset_id}/analytics-plan")
    assert cache_res.status_code == 200
    assert cache_res.json()["recalculated"] is False  # cache hit!

    # 6. Force rebuild
    rebuild_res = client.post(f"/api/v1/datasets/{dataset_id}/analytics-plan/rebuild")
    assert rebuild_res.status_code == 200
    assert rebuild_res.json()["recalculated"] is True  # forced refresh
