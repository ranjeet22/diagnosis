from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field


class KPIResult(BaseModel):
    """Execution results for a specific Key Performance Indicator."""
    name: str = Field(..., description="KPI name identifier.")
    value: Any = Field(..., description="Computed value (numeric, string, percent).")
    formula: str = Field(..., description="The mathematical formula used for calculations.")
    execution_time_ms: float = Field(..., description="Execution duration in milliseconds.")
    confidence: float = Field(..., description="Mapping confidence score (0.0 to 1.0).")
    source_columns: List[str] = Field(..., description="Source columns consumed.")


class MetricResult(BaseModel):
    """General metric output value."""
    name: str = Field(..., description="Metric key name.")
    value: Any = Field(..., description="Computed metric value.")
    description: str = Field(..., description="Definition summary.")


class DistributionResult(BaseModel):
    """Categorical count/percentage splits across labels."""
    task_id: str = Field(..., description="Associated planning task ID.")
    labels: List[str] = Field(..., description="Category group names/labels.")
    counts: List[int] = Field(..., description="Absolute count of records per label.")
    percentages: List[float] = Field(..., description="Percent ratio representation of counts.")


class TrendResult(BaseModel):
    """Chronological time-series counts, metrics, seasonality, and moving averages."""
    task_id: str = Field(..., description="Associated planning task ID.")
    timestamps: List[str] = Field(..., description="ISO 8601 date strings representing intervals.")
    counts: List[int] = Field(..., description="Admissions/records count per interval.")
    values: Optional[List[float]] = Field(None, description="Continuous value aggregates per interval if relevant.")
    moving_average: Optional[List[float]] = Field(None, description="Rolling average outputs.")
    growth_rate: Optional[List[float]] = Field(None, description="Interval growth rate ratios.")
    running_total: Optional[List[float]] = Field(None, description="Cumulative sum outputs.")
    seasonality_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata describing seasonal peaks/days.")


class ComparisonResult(BaseModel):
    """Cross-tab comparisons or binned box-plot numeric ranges."""
    name: str = Field(..., description="Comparison plan name (e.g. 'Disease vs Gender').")
    columns: List[str] = Field(..., description="Normalized columns compared.")
    comparison_type: str = Field(..., description="Comparison structure format.")
    data: Dict[str, Any] = Field(..., description="Computed cross-tab matrix or box-plot series statistics.")


class AggregationResult(BaseModel):
    """Standalone math aggregation metrics."""
    column: str = Field(..., description="Target normalized column name.")
    operation: str = Field(..., description="Operation executed (e.g. mean, std_dev, variance).")
    value: Any = Field(..., description="Calculated aggregate number.")


class CorrelationResult(BaseModel):
    """Pearson/Spearman matrices and identified strong relationships."""
    matrix: Dict[str, Dict[str, float]] = Field(..., description="Complete correlation coefficient mapping grid.")
    strong_positive: List[Tuple[str, str, float]] = Field(..., description="Variables pairs with high positive correlation (> 0.70).")
    strong_negative: List[Tuple[str, str, float]] = Field(..., description="Variables pairs with high negative correlation (< -0.70).")
    weak_correlations: List[Tuple[str, str, float]] = Field(..., description="Variables pairs with correlation coefficients near zero.")


class ExecutionSummary(BaseModel):
    """Aggregated stats summarizing task runs."""
    dataset_id: str = Field(..., description="The profiled dataset UUID.")
    total_tasks_planned: int = Field(..., description="Tasks specified in the execution plan.")
    total_tasks_executed: int = Field(..., description="Tasks actively calculated by the engine.")
    cached_tasks_reused: int = Field(..., description="Tasks loaded from intermediate memory caches.")
    overall_runtime_ms: float = Field(..., description="Cumulative engine runtime duration.")


class ExecutionStatistics(BaseModel):
    """Detailed micro-durations mapping performance profiles."""
    tasks_durations_ms: Dict[str, float] = Field(..., description="Execution duration per task key.")
    memory_usage_bytes: Optional[int] = Field(None, description="Approximated memory overhead size.")


class AnalyticsResult(BaseModel):
    """
    Unified computed analytics results wrapping KPIs, distributions, trends, comparisons,
    aggregations, correlations, and execution logs.
    """
    dataset_id: str = Field(..., description="The profiled dataset UUID.")
    kpis: Dict[str, KPIResult] = Field(default_factory=dict, description="Calculated dashboard KPIs.")
    distributions: Dict[str, DistributionResult] = Field(default_factory=dict, description="Computed distributions.")
    trends: Dict[str, TrendResult] = Field(default_factory=dict, description="Time-series trend outcomes.")
    comparisons: Dict[str, ComparisonResult] = Field(default_factory=dict, description="Cross-tab comparisons.")
    aggregations: List[AggregationResult] = Field(default_factory=list, description="Aggregations summary list.")
    correlations: Optional[CorrelationResult] = Field(None, description="Numeric correlation parameters.")
    summary: ExecutionSummary = Field(..., description="Execution logs details summary.")
    statistics: ExecutionStatistics = Field(..., description="Micro-performance statistics.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Analytics results creation timestamp.")


class AnalyticsResultResponse(BaseModel):
    """API Response model wrapper returning computed analytics."""
    dataset_id: str = Field(..., description="The analyzed dataset UUID.")
    analytics_results: AnalyticsResult = Field(..., description="The complete generated analytics results.")
    recalculated: bool = Field(False, description="Flag indicating if the results were recalculated or fetched from cache.")
