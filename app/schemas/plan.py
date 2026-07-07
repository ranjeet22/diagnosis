from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field


class MetricDefinition(BaseModel):
    """General definition representing a numeric or aggregated metric formula."""
    name: str = Field(..., description="Name of the metric.")
    description: str = Field(..., description="Descriptive summary of what the metric represents.")
    formula: str = Field(..., description="A clean, human-readable formula or mathematical syntax.")
    required_columns: List[str] = Field(..., description="Normalized column names required to calculate this metric.")
    aggregation_type: str = Field(..., description="Aggregation operation (e.g. SUM, AVG, COUNT).")


class FilterDefinition(BaseModel):
    """Recommended dashboard filter configuration."""
    column: str = Field(..., description="Normalized column name that this filter operates on.")
    filter_type: str = Field(..., description="Interface filter display type (select, range, multiselect, date-range).")
    label: str = Field(..., description="Human-readable label for the filter UI element.")


class AggregationPlan(BaseModel):
    """Lists requested math aggregation operations for a specific column."""
    column: str = Field(..., description="Normalized column name.")
    operations: List[str] = Field(..., description="List of aggregations needed (e.g. ['mean', 'median', 'sum']).")


class ComparisonPlan(BaseModel):
    """Lists comparison configurations (e.g. cross-tabulating columns)."""
    name: str = Field(..., description="Name of the comparison task.")
    columns: List[str] = Field(..., description="Normalized columns to compare (usually two, e.g. ['age', 'gender']).")
    comparison_type: str = Field(..., description="Comparison category (e.g. numeric_vs_categorical, categorical_vs_categorical).")


class VisualizationPlan(BaseModel):
    """Visual rendering hints for a particular analysis task."""
    chart_family: str = Field(..., description="ECharts visual type (Bar, Pie, Line, Area, Histogram, Box Plot, Scatter, Heatmap, Map).")
    purpose: str = Field(..., description="Description of the visualization objective.")
    required_columns: List[str] = Field(..., description="Normalized columns needed for the chart.")
    aggregation: str = Field(..., description="Aggregation mapping required for the axis (e.g. count, sum).")
    priority: str = Field(..., description="Visual visibility tier: high, medium, low.")
    recommended_size: str = Field(..., description="Dashboard space indicator: full, half, third.")
    recommended_position: str = Field(..., description="Suggested coordinates or placement sorting index.")
    interaction_type: str = Field(..., description="Chart event interaction: interactive, static, drill-down.")


class KPIPlan(BaseModel):
    """Dashboard Key Performance Indicator metric model."""
    name: str = Field(..., description="The name of the KPI.")
    description: str = Field(..., description="The explanation of what this KPI measures.")
    formula: str = Field(..., description="Formula/rule to compute this KPI.")
    required_columns: List[str] = Field(..., description="Normalized columns used to evaluate this KPI.")
    aggregation_type: str = Field(..., description="Math aggregation: count, sum, average, distinct_count, etc.")
    priority: str = Field(..., description="Display priority: high, medium, low.")
    dashboard_placement: str = Field(..., description="Dashboard section where this KPI belongs.")


class AnalysisTask(BaseModel):
    """Unit analysis task containing clinical heuristics and prioritizations."""
    task_id: str = Field(..., description="Unique alphanumeric identifier of the task.")
    name: str = Field(..., description="The name of the analysis task.")
    description: str = Field(..., description="Summary of the questions answered by this analysis.")
    required_columns: List[str] = Field(..., description="Normalized columns needed for execution.")
    
    # Priority Engine metadata
    priority_score: float = Field(..., description="Calculated priority score (0.0 to 100.0).")
    business_value: str = Field(..., description="Business significance value: high, medium, low.")
    visualization_importance: str = Field(..., description="Importance of the chart output: high, medium, low.")
    computation_cost: str = Field(..., description="Expected memory/processor complexity cost: low, medium, high.")
    expected_runtime_ms: int = Field(..., description="Estimated runtime in milliseconds.")
    confidence: float = Field(..., description="Derived confidence of mapping sources (0.0 to 1.0).")
    
    # Visualization
    visualization: Optional[VisualizationPlan] = Field(None, description="Recommended chart guidelines.")


class DashboardSection(BaseModel):
    """Layout structure defining dashboard organization."""
    section_name: str = Field(..., description="Section title (Overview, Demographics, Outcomes, etc.).")
    description: str = Field(..., description="Descriptive context of the section.")
    kpis: List[str] = Field(default_factory=list, description="List of KPI names inside this section.")
    tasks: List[str] = Field(default_factory=list, description="List of AnalysisTask IDs inside this section.")


class ExecutionGraph(BaseModel):
    """Directed dependency graph resolving analytical dependencies."""
    nodes: List[str] = Field(..., description="List of all unique task IDs and KPI names in the plan.")
    edges: List[Tuple[str, str]] = Field(..., description="List of directed dependency lines (Parent Task ID, Dependent Task ID).")


class AnalyticsPlan(BaseModel):
    """
    Unified Analytics Execution Plan resolving tasks, layouts, graphs, and filters.
    """
    dataset_id: str = Field(..., description="The profiled dataset UUID.")
    kpis: List[KPIPlan] = Field(default_factory=list, description="Recommended dashboard KPIs.")
    dashboard_sections: List[DashboardSection] = Field(default_factory=list, description="Dynamic dashboard sections layout.")
    analysis_tasks: List[AnalysisTask] = Field(default_factory=list, description="Calculations and analysis tasks execution list.")
    aggregation_plans: List[AggregationPlan] = Field(default_factory=list, description="Unique column-level aggregations mapped.")
    comparison_plans: List[ComparisonPlan] = Field(default_factory=list, description="Cross-tab comparisons planned.")
    filter_recommendations: List[FilterDefinition] = Field(default_factory=list, description="Dashboard filtering panels.")
    execution_graph: ExecutionGraph = Field(..., description="Aggregated dependency calculations graph.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Plan creation timestamp.")


class AnalyticsPlanResponse(BaseModel):
    """API Response model wrapper returning the analytics plan."""
    dataset_id: str = Field(..., description="The analyzed dataset UUID.")
    analytics_plan: AnalyticsPlan = Field(..., description="The complete generated analytics plan.")
    recalculated: bool = Field(False, description="Flag indicating if the plan was rebuilt or fetched from cache.")
