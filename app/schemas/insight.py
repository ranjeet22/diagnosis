from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class Insight(BaseModel):
    """
    Base natural language observation/insight referencing deterministic source metrics.
    """
    id: str = Field(..., description="Unique alphanumeric identifier of the insight.")
    title: str = Field(..., description="A short punchy title for the insight.")
    summary: str = Field(..., description="One-sentence high level summary.")
    detailed_explanation: str = Field(..., description="Deep explanation of what this clinical metric means.")
    evidence: str = Field(..., description="Concrete data points/metrics serving as evidence.")
    source_metrics: List[str] = Field(..., description="List of source metric names or task IDs.")
    importance: str = Field("medium", description="Importance rating: high, medium, low.")
    confidence: float = Field(1.0, description="Confidence score representing data support (0.0 to 1.0).")
    category: str = Field(..., description="Insight category: demographics, clinical, outcomes, quality, general, etc.")


class TrendInsight(Insight):
    """Insight focusing on timeline workloads and intervals growth/seasonality patterns."""
    category: str = "trend_analysis"


class RiskInsight(Insight):
    """Insight highlighting clinical risks, outcomes anomalies, or mortality patterns."""
    category: str = "risk_detection"


class OpportunityInsight(Insight):
    """Insight identifying clinical opportunities or improvements in hospital operations."""
    category: str = "opportunity"


class DataQualityInsight(Insight):
    """Insight focusing on dataset completeness, cleaning scores, and outliers."""
    category: str = "data_quality"


class ExecutiveSummary(BaseModel):
    """
    C-level summary capturing overall cohort status, key findings, and medical indicators.
    """
    title: str = Field("Executive Health Cohort Summary", description="Title label.")
    summary: str = Field(..., description="High-level narrative explaining the findings.")
    key_takeaways: List[str] = Field(default_factory=list, description="Top bullet observations.")


class InsightMetadata(BaseModel):
    """Technical metadata for logging, auditing, and debugging generated insights."""
    prompt_version: str = Field("1.0.0", description="Version of prompt template used.")
    generation_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Generation time.")
    confidence_score: float = Field(1.0, description="Confidence of prompt generation context.")
    gemini_metadata: Dict[str, Any] = Field(default_factory=dict, description="LLM settings used (model name, tokens count).")


class InsightCollection(BaseModel):
    """
    Root JSON document containing summaries, observations, and generation metadata.
    """
    dataset_id: str = Field(..., description="The profiled dataset UUID.")
    executive_summary: ExecutiveSummary = Field(..., description="Top summary takeaways.")
    insights: List[Insight] = Field(default_factory=list, description="Categorized clinical findings.")
    metadata: InsightMetadata = Field(..., description="Audit metadata.")


class InsightContext(BaseModel):
    """
    Summarized, token-efficient payload representing analytical results
    designed to feed into PromptBuilder.
    """
    kpis: Dict[str, Any] = Field(default_factory=dict, description="Overview KPIs name and value.")
    distributions: Dict[str, Any] = Field(default_factory=dict, description="Categorical distributions splits.")
    trends: Dict[str, Any] = Field(default_factory=dict, description="Timeline trend values.")
    comparisons: Dict[str, Any] = Field(default_factory=dict, description="Cross-tab comparisons data.")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Quality scores and outlier ratios.")


class PromptPayload(BaseModel):
    """Structured instruction/prompt package sent to Gemini."""
    system_instruction: str = Field(..., description="Guiding persona instruction.")
    prompt: str = Field(..., description="User prompt context containing aggregated health data.")


class GeminiResponse(BaseModel):
    """Raw wrapper response returned from LLM client wrapper."""
    text: str = Field(..., description="JSON-formatted string response.")
    status: str = Field("success", description="Response status (success, error).")


class InsightResponse(BaseModel):
    """API Response wrapper returning computed insights."""
    dataset_id: str = Field(..., description="Dataset UUID.")
    insights: InsightCollection = Field(..., description="Unified natural language insights document.")
    recalculated: bool = Field(False, description="Flag indicating if the insights were regenerated or retrieved from cache.")
