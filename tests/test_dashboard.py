import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

CLINICAL_DASH_CSV = (
    "Patient_ID,Age,Gender,Admission_Date,Discharge_Time,Diagnosis,Outcome,Hospital,Zipcode\n"
    "ID1,45,M,2026-01-01,2026-01-02 14:30:00,Flu,recovered,City Clinic,90210\n"
    "ID2,60,F,2026-01-02,2026-01-05 09:15:00,COVID-19,stable,General Hospital,10001\n"
    "ID3,30,F,2026-01-03,2026-01-03 18:00:00,Flu,stable,City Clinic,30303\n"
    "ID4,15,M,2026-01-04,2026-01-04 12:00:00,Cold,recovered,General Hospital,75001\n"
    "ID5,95,M,2026-01-05,2026-01-10 11:30:00,Flu,mortality,General Hospital,99501\n"
)


def test_dashboard_composition_pipeline():
    """
    Integration test verifying the dashboard composition pipeline:
    1. Upload CSV, profile, map, plan, execute results, and generate visualization plan.
    2. Request composed dashboard configuration via API.
    3. Assert global filters, theme attributes, and multi-page layouts.
    4. Assert widget definitions, ECharts configurations, responsive layouts,
       customizable properties, and export support.
    5. Assert layout validation outputs (is_valid flag).
    6. Assert API caching and page metadata endpoints.
    """
    # 1. Pipeline Prerequisites Ingestion
    files = {"file": ("clinical_dash.csv", CLINICAL_DASH_CSV, "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    # Ingest dependencies
    client.get(f"/api/v1/datasets/{dataset_id}/profile")
    client.get(f"/api/v1/datasets/{dataset_id}/semantic-model")
    client.get(f"/api/v1/datasets/{dataset_id}/analytics-plan")
    client.get(f"/api/v1/datasets/{dataset_id}/analytics")
    client.get(f"/api/v1/datasets/{dataset_id}/visualization-plan")

    # 2. GET Dashboard Config (cache miss)
    dash_res = client.get(f"/api/v1/datasets/{dataset_id}/dashboard")
    assert dash_res.status_code == 200
    
    data = dash_res.json()
    assert data["dataset_id"] == dataset_id
    assert data["recalculated"] is True  # Cache miss

    config = data["dashboard_config"]
    assert config["is_valid"] is True
    assert "validation completed successfully" in config["validation_logs"][-1]

    dashboard = config["dashboard"]
    
    # Assert theme configuration mappings
    theme = dashboard["theme"]
    assert theme["theme_name"] == "light"
    assert theme["border_radius"] == "8px"
    assert "shadow" in theme
    assert "typography" in theme
    assert "spacing" in theme

    # Assert Global filters list
    filters = dashboard["global_filters"]
    filter_ids = [f["filter_id"] for f in filters]
    assert "filter_gender" in filter_ids
    assert "filter_age" in filter_ids
    assert "filter_hospital" in filter_ids
    assert "filter_dates" in filter_ids

    # Assert Page structures
    pages = dashboard["pages"]
    page_ids = [p["id"] for p in pages]
    assert "overview" in page_ids
    assert "demographics" in page_ids
    assert "disease_analytics" in page_ids
    assert "trend_analysis" in page_ids

    # Assert Widget details on Overview Page
    overview_page = next(p for p in pages if p["id"] == "overview")
    sec = overview_page["sections"][0]
    assert sec["id"] == "sec_overview"
    widgets = sec["widgets"]
    assert len(widgets) > 0

    # Assert KPI Card properties
    kpi_widget = next(w for w in widgets if w["config"]["chart_type"] == "card")
    assert kpi_widget["widget_type"] == "KPI Card"
    assert kpi_widget["layout"]["desktop"]["width"] == 3
    assert kpi_widget["layout"]["desktop"]["height"] == 2
    assert kpi_widget["layout"]["mobile"]["width"] == 12  # Responsive mobile stacking
    assert kpi_widget["config"]["refresh_policy"] == "on_demand"
    assert kpi_widget["config"]["export_support"] == ["PNG", "PDF", "CSV", "JSON", "Excel"]
    assert kpi_widget["config"]["customizable_properties"]["renameTitle"] == kpi_widget["title"]

    # Assert Chart Widget on Demographics Page
    demo_page = next(p for p in pages if p["id"] == "demographics")
    demo_widgets = demo_page["sections"][0]["widgets"]
    pie_widget = next(w for w in demo_widgets if w["config"]["chart_type"] == "pie")
    assert pie_widget["widget_type"] == "Chart Widget"
    assert pie_widget["layout"]["desktop"]["width"] == 6  # Medium visual size
    assert pie_widget["cross_filter_support"] is True
    assert "outcome" in pie_widget["supported_filters"]

    # 3. GET Dashboard Config again (cache hit)
    cache_res = client.get(f"/api/v1/datasets/{dataset_id}/dashboard")
    assert cache_res.status_code == 200
    assert cache_res.json()["recalculated"] is False  # Cache hit

    # 4. POST Force Rebuild Dashboard Configuration
    rebuild_res = client.post(f"/api/v1/datasets/{dataset_id}/dashboard/rebuild")
    assert rebuild_res.status_code == 200
    assert rebuild_res.json()["recalculated"] is True

    # 5. GET Dashboard Page Metadata list
    pages_res = client.get(f"/api/v1/datasets/{dataset_id}/dashboard/pages")
    assert pages_res.status_code == 200
    pages_meta = pages_res.json()
    assert len(pages_meta) > 0
    assert pages_meta[0]["id"] == "overview"
    assert "widget_count" in pages_meta[0]
