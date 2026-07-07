from typing import List, Dict, Any, Optional
from app.schemas.visualization import (
    ChartConfiguration,
    AxisConfiguration,
    LegendConfiguration,
    TooltipConfiguration
)
from app.core.logging import logger


class ChartRecommendationEngine:
    """
    Constructs axis types, sorting, legend positions, units, and tooltip triggers
    for planned ECharts specifications.
    """

    @staticmethod
    def build_chart_configuration(
        chart_type: str,
        task_id: str,
        cols: List[str],
        result_data: Any
    ) -> ChartConfiguration:
        """
        Populates complete ChartConfiguration (axes, legends, tooltips) based on results structure.
        """
        x_axis = None
        y_axis = None
        legend_labels = []
        legend_visible = False
        legend_position = "bottom"
        tooltip_trigger = "axis"
        tooltip_metrics = cols

        # Extract labels from result data for legend/axes if present
        labels = []
        if isinstance(result_data, dict):
            if "labels" in result_data:
                labels = result_data["labels"]
            elif "timestamps" in result_data:
                labels = result_data["timestamps"]
            else:
                labels = list(result_data.keys())

        # 1. Line trends
        if chart_type == "line":
            # X-axis is chronological date category
            x_axis = AxisConfiguration(
                type="category",
                labels=labels,
                rotation=45,  # rotate to avoid collisions
                sorted=True
            )
            y_axis = AxisConfiguration(
                type="value",
                units="admissions" if "admission" in task_id else "records"
            )
            # If moving average or rolling total, we have multiple series
            legend_labels = ["Cases"]
            if "moving_average" in task_id:
                legend_labels.append("7-day Moving Avg")
                legend_visible = True
            elif "running_total" in task_id:
                legend_labels.append("Running Total")
                legend_visible = True
                
            tooltip_trigger = "axis"

        # 2. Pie charts
        elif chart_type == "pie":
            # No axes for Pie
            x_axis = None
            y_axis = None
            legend_labels = labels
            legend_visible = len(labels) <= 10
            legend_position = "right"
            tooltip_trigger = "item"

        # 3. Bar charts (Vertical vs Horizontal)
        elif chart_type == "bar":
            legend_labels = []
            
            # Check if horizontal bar is preferred (> 6 categories)
            if len(labels) > 6:
                # Horizontal Bar: Value on X, Category on Y
                x_axis = AxisConfiguration(
                    type="value",
                    units="records"
                )
                y_axis = AxisConfiguration(
                    type="category",
                    labels=labels,
                    rotation=0,
                    sorted=False
                )
                tooltip_trigger = "axis"
            else:
                # Vertical Bar: Category on X, Value on Y
                x_axis = AxisConfiguration(
                    type="category",
                    labels=labels,
                    rotation=0 if len(labels) <= 4 else 30,
                    sorted=False
                )
                y_axis = AxisConfiguration(
                    type="value",
                    units="records"
                )
                tooltip_trigger = "axis"

            # Check if comparison stacked bars (multiple inner series)
            if isinstance(result_data, dict) and len(result_data) > 0:
                first_val = list(result_data.values())[0]
                if isinstance(first_val, dict):
                    # Category vs Category (e.g. Disease vs Gender)
                    # Slices of Gender (e.g., M, F) are the legend labels
                    legend_labels = list(first_val.keys())
                    legend_visible = True

        # 4. Boxplots
        elif chart_type == "boxplot":
            x_axis = AxisConfiguration(
                type="category",
                labels=labels,
                rotation=30 if len(labels) > 4 else 0
            )
            y_axis = AxisConfiguration(
                type="value",
                units="age" if "age" in task_id.lower() or "age" in cols else "value"
            )
            legend_visible = False
            tooltip_trigger = "item"

        # 5. Heatmaps
        elif chart_type == "heatmap":
            x_axis = AxisConfiguration(
                type="category",
                labels=labels
            )
            y_axis = AxisConfiguration(
                type="category",
                labels=labels
            )
            legend_visible = True
            legend_position = "right"
            tooltip_trigger = "item"

        return ChartConfiguration(
            chart_type=chart_type,
            x_axis=x_axis,
            y_axis=y_axis,
            legend=LegendConfiguration(
                position=legend_position,
                visible=legend_visible,
                labels=legend_labels
            ),
            tooltip=TooltipConfiguration(
                trigger=tooltip_trigger,
                format="",
                displayed_metrics=tooltip_metrics,
                precision=2
            )
        )
