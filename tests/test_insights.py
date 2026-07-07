import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.results import AnalyticsResult, KPIResult, DistributionResult, TrendResult, ExecutionSummary, ExecutionStatistics
from app.schemas.insight import InsightContext
from app.analytics.insight.context import InsightContextBuilder
from app.analytics.insight.prompt import PromptBuilder
from app.analytics.insight.validation import InsightValidationService
from app.gemini import GeminiClientWrapper, GeminiClientError
from app.gemini.retry import RetryManager
from app.services.insight_generation import InsightGenerationService

client = TestClient(app)

CLINICAL_CSV_DATA = (
    "Patient_ID,Age,Gender,Admission_Date,Discharge_Time,Diagnosis,Outcome,Hospital,Zipcode\n"
    "ID1,45,M,2026-01-01,2026-01-02 14:30:00,Flu,recovered,City Clinic,90210\n"
    "ID2,60,F,2026-01-02,2026-01-05 09:15:00,COVID-19,stable,General Hospital,10001\n"
)


def test_insight_context_builder_compression():
    """
    Verifies that InsightContextBuilder compresses raw statistical data
    without raw patient lists or row-level entries.
    """
    mock_result = AnalyticsResult(
        dataset_id="test-uuid",
        kpis={
            "kpi1": KPIResult(name="Total Records", value=50, formula="COUNT(*)", execution_time_ms=1.5, confidence=1.0, source_columns=["Patient_ID"]),
            "kpi2": KPIResult(name="Dataset Completeness", value="100.0%", formula="1 - nulls/total", execution_time_ms=1.0, confidence=1.0, source_columns=[])
        },
        distributions={
            "dist1": DistributionResult(task_id="gender_distribution", labels=["M", "F"], counts=[30, 20], percentages=[60.0, 40.0])
        },
        trends={
            "trend1": TrendResult(task_id="daily_admission_trend", timestamps=["2026-01-01", "2026-01-02"], counts=[10, 15], seasonality_metadata={"peak_day": "Friday"})
        },
        comparisons={},
        aggregations=[],
        correlations=None,
        summary=ExecutionSummary(dataset_id="test-uuid", total_tasks_planned=5, total_tasks_executed=5, cached_tasks_reused=0, overall_runtime_ms=15.0),
        statistics=ExecutionStatistics(tasks_durations_ms={})
    )

    context = InsightContextBuilder.build_context(mock_result)
    assert isinstance(context, InsightContext)
    
    # Assert KPIs are simplified
    assert "Total Records" in context.kpis
    assert context.kpis["Total Records"] == 50
    assert "formula" not in context.kpis

    # Assert distributions are simplified
    assert "gender_distribution" in context.distributions
    assert context.distributions["gender_distribution"]["M"] == (30, 60.0)

    # Assert trends are summarized
    assert "daily_admission_trend" in context.trends
    assert context.trends["daily_admission_trend"]["overall_sum"] == 25
    assert context.trends["daily_admission_trend"]["average_per_interval"] == 12.5


def test_prompt_builder_rendering():
    """
    Verifies that PromptBuilder loads templates and replaces placeholders correctly.
    """
    context = InsightContext(
        kpis={"Total Patients": 100},
        distributions={},
        trends={},
        comparisons={},
        quality_metrics={}
    )
    builder = PromptBuilder()
    payload = builder.build_prompt_payload(context)
    
    assert "Total Patients" in payload.prompt
    assert "senior medical statistician" in payload.system_instruction


@pytest.mark.anyio
async def test_retry_manager_exponential_backoff():
    """
    Tests that RetryManager implements backoff and successfully retries on rate limit errors.
    """
    mock_func = AsyncMock()
    # Attempt 1: Rate limit 429
    # Attempt 2: Success
    mock_func.side_effect = [GeminiClientError("Rate Limit exceeded (429)"), "Success text"]

    with patch("asyncio.sleep", AsyncMock()) as mock_sleep:
        res = await RetryManager.execute_with_retry(mock_func, max_retries=2, initial_delay=0.1, backoff_factor=2.0)
        assert res == "Success text"
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once_with(0.1)


@pytest.mark.anyio
async def test_insight_generation_fallback_graceful_handling():
    """
    Verifies that the service falls back gracefully to pre-compiled deterministic insights
    on Gemini client errors.
    """
    mock_repo = AsyncMock()
    mock_result_repo = AsyncMock()
    mock_client = AsyncMock()

    # Stub dependencies
    mock_result = AnalyticsResult(
        dataset_id="test-uuid",
        kpis={"kpi_comp": KPIResult(name="Dataset Completeness", value="98%", formula="", execution_time_ms=0.1, confidence=1.0, source_columns=[])},
        distributions={},
        trends={},
        comparisons={},
        aggregations=[],
        summary=ExecutionSummary(dataset_id="test-uuid", total_tasks_planned=1, total_tasks_executed=1, cached_tasks_reused=0, overall_runtime_ms=1.0),
        statistics=ExecutionStatistics(tasks_durations_ms={})
    )
    mock_result_repo.get_results.return_return = mock_result
    mock_result_repo.get_results = AsyncMock(return_value=mock_result)

    # Gemini client throws error (e.g. timeout)
    mock_client.default_model = "gemini-1.5-pro"
    mock_client.generate_explanation.side_effect = GeminiClientError("Request Timed Out")

    service = InsightGenerationService(
        repository=mock_repo,
        result_repository=mock_result_repo,
        client_wrapper=mock_client
    )

    # Trigger generation
    collection = await service.generate_insights(dataset_id="test-uuid", force=True)
    
    # Assert it completed successfully despite Gemini failure, using fallback mode
    assert collection.dataset_id == "test-uuid"
    assert "Fallback Mode" in collection.executive_summary.title
    assert collection.metadata.gemini_metadata["status"] == "fallback"
    assert len(collection.insights) > 0
    assert collection.insights[0].id == "fallback_kpi_overview"
    
    # Verify save was called
    mock_repo.save_insights.assert_called_once()


def test_insight_pipeline_integration():
    """
    Executes full pipeline integration test: upload -> profiles -> mappings -> plan -> execute -> viz -> compose -> insights.
    """
    # 1. Ingest dataset
    files = {"file": ("clinical_test.csv", CLINICAL_CSV_DATA, "text/csv")}
    upload_res = client.post("/api/v1/datasets/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    # Ingest pipeline steps
    client.get(f"/api/v1/datasets/{dataset_id}/profile")
    client.get(f"/api/v1/datasets/{dataset_id}/semantic-model")
    client.get(f"/api/v1/datasets/{dataset_id}/analytics-plan")
    client.get(f"/api/v1/datasets/{dataset_id}/analytics")

    # 2. Get Insights (cache miss -> triggers fallback because API key is empty/mocked in tests)
    insights_res = client.get(f"/api/v1/datasets/{dataset_id}/insights")
    assert insights_res.status_code == 200
    
    data = insights_res.json()
    assert data["dataset_id"] == dataset_id
    assert data["recalculated"] is True

    insights = data["insights"]
    assert "Deterministic Cohort Summary" in insights["executive_summary"]["title"]
    assert len(insights["insights"]) > 0

    # 3. Get Insights again (cache hit)
    cache_res = client.get(f"/api/v1/datasets/{dataset_id}/insights")
    assert cache_res.status_code == 200
    assert cache_res.json()["recalculated"] is False

    # 4. POST Force Refresh Insights
    refresh_res = client.post(f"/api/v1/datasets/{dataset_id}/insights/refresh")
    assert refresh_res.status_code == 200
    assert refresh_res.json()["recalculated"] is True
