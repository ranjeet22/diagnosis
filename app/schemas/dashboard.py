from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class WidgetPosition(BaseModel):
    """Grid layout position coordinates and sizes details."""
    row: int = Field(..., description="Starting grid row index (0-indexed).")
    col: int = Field(..., description="Starting grid column index (0 to 11).")
    width: int = Field(..., description="Grid span width (1 to 12).")
    height: int = Field(..., description="Grid span height rows count.")
    min_width: int = Field(2, description="Minimum allowed grid span width.")
    min_height: int = Field(2, description="Minimum allowed grid span height.")
    max_width: Optional[int] = Field(None, description="Maximum allowed grid span width.")
    max_height: Optional[int] = Field(None, description="Maximum allowed grid span height.")


class GridLayout(BaseModel):
    """Responsive coordinates detailing layouts on Desktop, Tablet, and Mobile screens."""
    desktop: WidgetPosition = Field(..., description="Desktop grid positions coordinates.")
    tablet: WidgetPosition = Field(..., description="Tablet grid positions coordinates.")
    mobile: WidgetPosition = Field(..., description="Mobile grid positions coordinates.")
    priority: int = Field(50, description="Display priorities value (0 to 100).")


class WidgetConfiguration(BaseModel):
    """Widget-specific execution dependencies and properties settings."""
    chart_id: Optional[str] = Field(None, description="Task ID this widget represents.")
    chart_type: str = Field(..., description="Render type: bar, line, pie, boxplot, heatmap, card, table.")
    chart_config: Optional[Dict[str, Any]] = Field(None, description="Generic visual chart configuration properties.")
    data_source: str = Field(..., description="Backend results REST endpoint URL.")
    refresh_policy: str = Field("on_demand", description="Refresh triggers policy: real_time, on_demand.")
    dependencies: List[str] = Field(default_factory=list, description="IDs of parent calculation tasks.")
    visibility_rules: Dict[str, Any] = Field(default_factory=dict, description="Custom layout visibility triggers.")
    loading_state: str = Field("idle", description="Loading state: idle, loading, ready, error.")
    error_state: Optional[str] = Field(None, description="Detailed error log descriptions.")
    export_support: List[str] = Field(default_factory=lambda: ["PNG", "PDF", "CSV", "JSON", "Excel"], description="Supported export file formats.")
    customizable_properties: Dict[str, Any] = Field(default_factory=dict, description="Editable configuration parameters for the frontend.")


class DashboardWidget(BaseModel):
    """Interactive component card widget containing details, config schemas, and layouts."""
    id: str = Field(..., description="Unique widget identifier string.")
    title: str = Field(..., description="Header text label.")
    description: str = Field(..., description="Descriptive helper caption.")
    widget_type: str = Field(..., description="Widget type: KPI Card, Chart Widget, Table Widget, Summary Widget, Insight Widget, Recommendation Widget, Filter Widget, Metric Card, Divider, Markdown Block.")
    layout: GridLayout = Field(..., description="Grid coordinate configurations.")
    config: WidgetConfiguration = Field(..., description="Inner properties parameters.")
    supported_filters: List[str] = Field(default_factory=list, description="Dropdown filter column keys this widget responds to.")
    ignored_filters: List[str] = Field(default_factory=list, description="Dropdown filters that do not affect this widget.")
    linked_filters: List[str] = Field(default_factory=list, description="Cascading filter links.")
    cross_filter_support: bool = Field(True, description="Flag allowing widget selection to filter other page items.")


class DashboardSection(BaseModel):
    """Sub-layout section folder organizing a list of related cards."""
    id: str = Field(..., description="Section identifier.")
    title: str = Field(..., description="Header title labels.")
    description: str = Field(..., description="Sub-caption summary.")
    widgets: List[DashboardWidget] = Field(default_factory=list, description="Child cards sequence.")
    display_order: int = Field(0, description="Display rendering rank order.")


class DashboardPage(BaseModel):
    """Top-level tab folders classifying pages."""
    id: str = Field(..., description="Unique page ID.")
    title: str = Field(..., description="Label shown on page tabs.")
    sections: List[DashboardSection] = Field(default_factory=list, description="Page section layout containers.")
    display_order: int = Field(0, description="Tab display order.")


class DashboardTheme(BaseModel):
    """Typography styles, border bounds, spacing ratios, shadow offsets, and hex colors."""
    theme_name: str = Field("light", description="Theme classification: light, dark, high_contrast.")
    palette: List[str] = Field(default_factory=list, description="Hex color values.")
    background: str = Field("#ffffff", description="Background hex code.")
    text_color: str = Field("#1f2937", description="Text color hex code.")
    typography: Dict[str, Any] = Field(default_factory=dict, description="Font properties (size, weight).")
    spacing: Dict[str, Any] = Field(default_factory=dict, description="Grid margins spacing settings.")
    border_radius: str = Field("8px", description="CSS corner radius border styles.")
    shadow: str = Field("0 4px 6px -1px rgb(0 0 0 / 0.1)", description="CSS box shadow variables.")
    animation_settings: Dict[str, Any] = Field(default_factory=dict, description="Chart animation settings parameters.")


class DashboardFilter(BaseModel):
    """Global sidebar filter parameters definitions."""
    filter_id: str = Field(..., description="Unique filter ID.")
    column: str = Field(..., description="Dataset column name mapping.")
    filter_type: str = Field("select", description="Triage filter type: select, range, multiselect, date-range.")
    label: str = Field(..., description="UI header label.")
    default_value: Optional[Any] = Field(None, description="Initial values.")


class DashboardState(BaseModel):
    """Client-side state schema for automatic dashboard restorings."""
    collapsed_widgets: List[str] = Field(default_factory=list, description="Collapsed widget IDs.")
    expanded_widgets: List[str] = Field(default_factory=list, description="Expanded widget IDs.")
    selected_filters: Dict[str, Any] = Field(default_factory=dict, description="Active dropdown filter variables.")
    theme: str = Field("light", description="Active theme state.")
    user_layout: Dict[str, Any] = Field(default_factory=dict, description="Modified user coordinate layout overrides.")
    hidden_widgets: List[str] = Field(default_factory=list, description="Hidden widget IDs.")
    pinned_widgets: List[str] = Field(default_factory=list, description="Pinned widgets.")
    last_refresh: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Refresh timestamp.")


class UserPreferences(BaseModel):
    """Personalized user setting parameters."""
    theme: str = Field("light", description="Preferred active theme mode.")
    layout_density: str = Field("comfortable", description="Layout sizing densities: comfortable, compact.")
    pinned_widgets: List[str] = Field(default_factory=list, description="Home-page pinned card widgets.")


class DashboardMetadata(BaseModel):
    """System revision metadata indices."""
    dataset_id: str = Field(..., description="Source dataset UUID.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp.")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last modified timestamp.")
    version: str = Field("1.0.0", description="Dashboard configuration structure versions.")


class Dashboard(BaseModel):
    """Unified layout containing pages, themes, filters, states, and preferences."""
    metadata: DashboardMetadata = Field(..., description="System revision logs.")
    theme: DashboardTheme = Field(..., description="Active color templates and borders.")
    global_filters: List[DashboardFilter] = Field(default_factory=list, description="Global sidebar filter lists.")
    pages: List[DashboardPage] = Field(default_factory=list, description="Multi-page layout containers.")
    state: DashboardState = Field(..., description="State restoring schema.")
    user_preferences: UserPreferences = Field(..., description="User configuration overrides.")


class DashboardConfiguration(BaseModel):
    """The root Dashboard configuration document containing validation markers."""
    dashboard: Dashboard = Field(..., description="Dashboard schema.")
    validation_logs: List[str] = Field(default_factory=list, description="Integrity audit reports.")
    is_valid: bool = Field(True, description="Flag indicating if the layout is verified.")


class DashboardResponse(BaseModel):
    """API Response wrapper returning computed dashboard configuration."""
    dataset_id: str = Field(..., description="Dataset UUID.")
    dashboard_config: DashboardConfiguration = Field(..., description="The complete dashboard configuration.")
    recalculated: bool = Field(False, description="Flag indicating if the layout was regenerated or fetched from cache.")
