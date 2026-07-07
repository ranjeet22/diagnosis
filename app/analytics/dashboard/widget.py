from typing import Dict, Any, List
from app.schemas.visualization import VisualizationRecommendation
from app.schemas.dashboard import DashboardWidget, WidgetConfiguration, GridLayout


class WidgetFactory:
    """
    Factory creating complete DashboardWidget objects from visualization recommendations,
    defining configuration schemas, ECharts options, filters, and customizable properties.
    """

    @staticmethod
    def create_widget(
        dataset_id: str,
        rec: VisualizationRecommendation,
        grid_layout: GridLayout
    ) -> DashboardWidget:
        """
        Builds a DashboardWidget object.
        """
        chart_id = rec.chart_id
        c_type = rec.chart_config.chart_type

        # 1. Determine widget class
        if c_type == "card":
            widget_type = "KPI Card"
        elif c_type == "table":
            widget_type = "Table Widget"
        else:
            widget_type = "Chart Widget"

        # 2. Build configuration schema
        config = WidgetConfiguration(
            chart_id=chart_id,
            chart_type=c_type,
            chart_config=rec.chart_config.model_dump(),
            data_source=f"/api/v1/datasets/{dataset_id}/analytics",
            refresh_policy="on_demand",
            dependencies=[],
            visibility_rules={},
            loading_state="idle",
            error_state=None,
            export_support=["PNG", "PDF", "CSV", "JSON", "Excel"],
            customizable_properties={
                "chartType": c_type,
                "palette": rec.chart_config.legend.labels if rec.chart_config.legend else [],
                "legendPosition": rec.chart_config.legend.position if rec.chart_config.legend else "bottom",
                "enableAnimation": True,
                "sorting": False,
                "renameTitle": rec.name
            }
        )

        # 3. Configure filters
        # Supported filters are all recommended dataset filters
        supported_filters = rec.filters
        ignored_filters = []
        if rec.chart_config.x_axis and rec.chart_config.x_axis.labels:
            # Avoid self-filtering on the primary categorical axis
            ignored_filters = rec.chart_config.x_axis.labels

        prefix = "kpi" if c_type == "card" else "chart"
        widget_id = f"widget_{prefix}_{chart_id.lower().replace(' ', '_')}"

        return DashboardWidget(
            id=widget_id,
            title=rec.name,
            description=rec.description,
            widget_type=widget_type,
            layout=grid_layout,
            config=config,
            supported_filters=supported_filters,
            ignored_filters=ignored_filters,
            linked_filters=[],
            cross_filter_support=rec.interaction.cross_filter
        )
