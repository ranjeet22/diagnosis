import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

CLINICAL_VIS_CSV = (
    "Patient_ID,Age,Gender,Admission_Date,Discharge_Time,Diagnosis,Outcome,Hospital,Zipcode\n"
    "ID1,45,M,2026-01-01,2026-01-02 14:30:00,Flu,recovered,City Clinic,90210\n"
    "ID2,60,F,2026-01-02,2026-01-05 09:15:00,COVID-19,stable,General Hospital,10001\n"
    "ID3,30,F,2026-01-03,2026-01-03 18:00:00,Flu,stable,City Clinic,30303\n"
    "ID4,15,M,2026-01-04,2026-01-04 12:00:00,Cold,recovered,General Hospital,75001\n"
    "ID5,95,M,2026-01-05,2026-01-10 11:30:00,Flu,mortality,General Hospital,99501\n"
)


def test_visualization_recommendation_pipeline():
    """
    Integration test verifying the visualization recommendation pipeline:
    1. Upload CSV, profile, map, plan, execute results.
    2. Request visualization plan via API.
    3. Assert ECharts chart configurations, dynamic accessibility alt-text summaries,
       interaction plans, grid layouts, and color palettes.
    4. Assert theme override flags (Dark Mode and Color Blind parameters).
    5. Assert API caching and forced rebuilds.
    """
    # 1. Pipeline Prerequisites Ingestion
    files = {"file": ("clinical_vis.csv", CLINICAL_VIS_CSV, "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    # Ingest profile, semantic, plan, and run analytics
    client.get(f"/api/v1/datasets/{dataset_id}/profile")
    client.get(f"/api/v1/datasets/{dataset_id}/semantic-model")
    client.get(f"/api/v1/datasets/{dataset_id}/analytics-plan")
    client.get(f"/api/v1/datasets/{dataset_id}/analytics")

    # 2. GET Visualization Plan (cache miss: executes and caches)
    vis_res = client.get(f"/api/v1/datasets/{dataset_id}/visualization-plan")
    assert vis_res.status_code == 200
    
    data = vis_res.json()
    assert data["dataset_id"] == dataset_id
    assert data["recalculated"] is True  # Cache miss

    plan = data["visualization_plan"]
    
    # Assert theme configurations (default light)
    theme = plan["theme"]
    assert theme["theme_name"] == "light"
    assert theme["palette"]["name"] == "Color Blind Friendly (Okabe-Ito)"
    assert theme["palette"]["background"] == "#ffffff"
    assert theme["contrast_ratio"] == 4.5

    # Assert Recommendations exist
    recs = plan["recommendations"]
    assert "Total Patients" in recs
    assert "gender_distribution" in recs
    assert "disease_distribution" in recs
    assert "daily_admission_trend" in recs

    # Assert KPI Recommendation details
    kpi_card = recs["Total Patients"]
    assert kpi_card["chart_config"]["chart_type"] == "card"
    assert kpi_card["layout"]["card_size"] == "small"
    assert kpi_card["accessibility"]["alt_text"] == "Key Performance Indicator card for Total Patients with calculated value of 5."

    # Assert Categorical Recommendation details (Pie chart since gender has 2 classes <= 6)
    gender_rec = recs["gender_distribution"]
    assert gender_rec["chart_config"]["chart_type"] == "pie"
    assert gender_rec["layout"]["card_size"] == "medium"
    assert "M" in gender_rec["chart_config"]["legend"]["labels"]
    assert "F" in gender_rec["chart_config"]["legend"]["labels"]
    assert gender_rec["chart_config"]["tooltip"]["trigger"] == "item"
    assert gender_rec["interaction"]["cross_filter"] is True
    # Accessibility alt text verification: M is highest with 3 records (60.0%)
    alt_gender = gender_rec["accessibility"]["alt_text"]
    assert "highest volume with 3 records" in alt_gender

    # Assert Disease Distribution (Vertical bar since disease has 3 classes <= 6)
    disease_rec = recs["disease_distribution"]
    assert disease_rec["chart_config"]["chart_type"] == "bar"
    assert disease_rec["chart_config"]["x_axis"]["type"] == "category"
    assert "Flu" in disease_rec["chart_config"]["x_axis"]["labels"]
    assert disease_rec["chart_config"]["y_axis"]["type"] == "value"
    assert disease_rec["chart_config"]["y_axis"]["units"] == "records"
    alt_disease = disease_rec["accessibility"]["alt_text"]
    assert "Flu has the highest volume with 3 records" in alt_disease

    # Assert Trend Recommendations (Line plot with zoom enabled)
    trend_rec = recs["daily_admission_trend"]
    assert trend_rec["chart_config"]["chart_type"] == "line"
    assert trend_rec["chart_config"]["x_axis"]["type"] == "category"
    assert trend_rec["chart_config"]["x_axis"]["rotation"] == 45
    assert trend_rec["interaction"]["zoom"] is True
    assert trend_rec["interaction"]["pan"] is True
    alt_trend = trend_rec["accessibility"]["alt_text"]
    assert "Line chart representing the temporal trend" in alt_trend

    # Assert filter recommendations (linked filter options excluding the chart column itself)
    # E.g. gender_distribution should suggest filters like hospital, outcome, disease, region
    assert "hospital" in gender_rec["filters"]
    assert "outcome" in gender_rec["filters"]
    assert "gender" not in gender_rec["filters"]

    # 3. GET Visualization Plan again (cache hit)
    cache_res = client.get(f"/api/v1/datasets/{dataset_id}/visualization-plan")
    assert cache_res.status_code == 200
    assert cache_res.json()["recalculated"] is False  # Cache hit

    # 4. POST Force rebuild with theme=dark override
    rebuild_res = client.post(f"/api/v1/datasets/{dataset_id}/visualization-plan/rebuild?theme=dark")
    assert rebuild_res.status_code == 200
    assert rebuild_res.json()["recalculated"] is True
    
    plan_dark = rebuild_res.json()["visualization_plan"]
    assert plan_dark["theme"]["theme_name"] == "dark"
    assert plan_dark["theme"]["palette"]["name"] == "Dark Blue Theme"
    assert plan_dark["theme"]["palette"]["background"] == "#1e293b"

    # 5. POST Rebuild with accessibility=high_contrast override
    contrast_res = client.post(f"/api/v1/datasets/{dataset_id}/visualization-plan/rebuild?accessibility=high_contrast")
    assert contrast_res.status_code == 200
    plan_contrast = contrast_res.json()["visualization_plan"]
    assert plan_contrast["theme"]["palette"]["name"] == "High Contrast"
    assert plan_contrast["theme"]["palette"]["background"] == "#000000"
    assert plan_contrast["theme"]["contrast_ratio"] == 7.0
