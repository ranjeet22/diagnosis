from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ColorPalette(BaseModel):
    """Hex color codes matching a selected theme style."""
    name: str = Field(..., description="Palette name identifier.")
    colors: List[str] = Field(..., description="Hex code colors sequence.")
    background: str = Field(..., description="Recommended card/chart background hex code.")
    text_color: str = Field(..., description="Contrast text hex code.")


class ThemeConfiguration(BaseModel):
    """UI styles for ECharts widgets configurations."""
    theme_name: str = Field(..., description="Theme type name ('light', 'dark', 'high_contrast').")
    palette: ColorPalette = Field(..., description="Selected color palette.")
    font_family: str = Field("Inter, sans-serif", description="Font face family selection.")
    contrast_ratio: float = Field(..., description="Minimum palette color contrast rating.")


class AxisConfiguration(BaseModel):
    """Tick markings, units, sorting, and rotation configs."""
    type: str = Field(..., description="Axis type: 'category', 'value', 'time', 'log'.")
    labels: Optional[List[str]] = Field(None, description="Static axis category labels.")
    tick_format: Optional[str] = Field(None, description="Formatting template (e.g. date format or percent).")
    units: Optional[str] = Field(None, description="Suffix labels mapping measurement units.")
    rotation: int = Field(0, description="Angle rotation degree for label display.")
    sorted: bool = Field(False, description="Flag indicating if labels are ordered.")


class LegendConfiguration(BaseModel):
    """Legend positions and series labels visibility settings."""
    position: str = Field(..., description="Placement position: 'top', 'bottom', 'left', 'right'.")
    visible: bool = Field(True, description="Flag managing legend visibility.")
    labels: List[str] = Field(..., description="Series categories legend keys.")
    grouping: Optional[str] = Field(None, description="Optional legend group category.")


class TooltipConfiguration(BaseModel):
    """Hover values and metric formats recommendations."""
    trigger: str = Field("axis", description="Hover trigger: 'axis', 'item', 'none'.")
    format: str = Field("", description="HTML or template formatting rule.")
    displayed_metrics: List[str] = Field(..., description="Specific value column keys shown in tooltip.")
    precision: int = Field(2, description="Numerical decimal precision representation.")
    units: Optional[str] = Field(None, description="Suffix measurement units.")


class InteractionConfiguration(BaseModel):
    """Interaction capabilities supported by the visual element."""
    zoom: bool = Field(False, description="Enables zoom interactions.")
    pan: bool = Field(False, description="Enables pan/drag navigation.")
    brush: bool = Field(False, description="Enables visual selecting brush tool.")
    hover: bool = Field(True, description="Enables state hover highlighting.")
    click_action: Optional[str] = Field(None, description="Click event type ('filter', 'drilldown').")
    cross_filter: bool = Field(False, description="Clicking slices updates other charts in dashboard.")
    drill_down: bool = Field(False, description="Clicking traverses down hierarchical levels.")
    supported_interactions: List[str] = Field(default_factory=list, description="Explicit action methods.")


class AccessibilityConfiguration(BaseModel):
    """Contrast compliance, font scalings, alt text, and screen reader labels."""
    aria_label: str = Field(..., description="W3C accessibility ARIA label.")
    keyboard_navigation: bool = Field(True, description="Keyboard focusable navigation indicator.")
    color_contrast_compliant: bool = Field(True, description="Meets WCAG 2.1 AA color contrast compliance.")
    alt_text: str = Field(..., description="Text alternative summarizing trends or highest counts.")
    font_scaling_supported: bool = Field(True, description="Enables browser font resizings.")


class LayoutConfiguration(BaseModel):
    """Grid row/column positioning and responsive dimensions details."""
    width_percent: float = Field(100.0, description="Responsive card width ratio.")
    height_px: int = Field(400, description="Recommended height in pixels.")
    card_size: str = Field("medium", description="Card size dimensions classification ('small', 'medium', 'large', 'full').")
    grid_row: int = Field(0, description="Logical dashboard grid row index.")
    grid_col: int = Field(0, description="Logical dashboard grid column index.")
    priority_score: float = Field(..., description="Dashboard placement order rating.")
    responsive_behavior: str = Field("fluid", description="Responsive styling classes ('fluid', 'fixed').")
    section: str = Field("Overview", description="Parent dashboard layout section mapping.")
    display_order: int = Field(0, description="Display sequence order within the section.")


class ChartConfiguration(BaseModel):
    """Visual mapping options detailing charts, axis lines, tooltips, and legends."""
    chart_type: str = Field(..., description="Generic visual chart type: 'bar', 'line', 'pie', 'scatter', 'heatmap', 'boxplot', 'treemap'.")
    x_axis: Optional[AxisConfiguration] = Field(None, description="Horizontal axis detail.")
    y_axis: Optional[AxisConfiguration] = Field(None, description="Vertical axis detail.")
    legend: LegendConfiguration = Field(..., description="Legend visibility and positioning parameters.")
    tooltip: TooltipConfiguration = Field(..., description="Tooltip display rules.")


class VisualizationRecommendation(BaseModel):
    """Intelligent visualization recommendations wrapping configurations, layouts, and accessibility logs."""
    chart_id: str = Field(..., description="Unique chart ID matching the planner task key.")
    name: str = Field(..., description="Visual card header name.")
    description: str = Field(..., description="Metric description label.")
    chart_config: ChartConfiguration = Field(..., description="Generic visual chart configuration properties.")
    layout: LayoutConfiguration = Field(..., description="Dashboard positioning layout specifications.")
    interaction: InteractionConfiguration = Field(..., description="Supported interactions.")
    accessibility: AccessibilityConfiguration = Field(..., description="Accessibility compliance parameters.")
    filters: List[str] = Field(default_factory=list, description="Dropdown filter options linked to this widget.")
    confidence_score: float = Field(1.0, description="Visualization recommendation rating.")
    readability_score: float = Field(1.0, description="Readability rating (0.0 to 1.0).")
    business_value_score: float = Field(1.0, description="Business decision value rating (0.0 to 1.0).")
    complexity_score: float = Field(0.0, description="Visual complexity rating (0.0 to 1.0).")
    accessibility_score: float = Field(1.0, description="Accessibility score index (0.0 to 1.0).")


class VisualizationPlan(BaseModel):
    """
    Unified visualization plan document containing theme configuration and a mapped dictionary
    of chart recommendations for downstream dashboard builders.
    """
    dataset_id: str = Field(..., description="Profiled dataset UUID.")
    theme: ThemeConfiguration = Field(..., description="Recommended active theme styles.")
    recommendations: Dict[str, VisualizationRecommendation] = Field(default_factory=dict, description="Chart recommendations indexed by chart_id.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Generation timestamp.")


class VisualizationPlanResponse(BaseModel):
    """API Response wrapper returning computed visualization plan."""
    dataset_id: str = Field(..., description="Dataset UUID.")
    visualization_plan: VisualizationPlan = Field(..., description="The complete visualization recommendations plan.")
    recalculated: bool = Field(False, description="Flag indicating if the plan was regenerated or fetched from cache.")
