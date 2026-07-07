from typing import List, Dict
from app.schemas.visualization import VisualizationPlan
from app.schemas.dashboard import Dashboard


class DashboardValidationService:
    """
    Validates structural integrity of dashboard configurations, auditing widget IDs,
    broken visual layout maps, circular dependencies, and missing ECharts targets.
    """

    @staticmethod
    def validate_dashboard(
        dashboard: Dashboard,
        vis_plan: VisualizationPlan
    ) -> tuple[List[str], bool]:
        """
        Runs validation checks. Returns logs list and is_valid flag.
        """
        logs: List[str] = []
        is_valid = True

        widget_ids = set()
        widget_configs = {}

        # 1. Audit pages, sections, and widgets
        for page in dashboard.pages:
            for section in page.sections:
                for widget in section.widgets:
                    wid = widget.id
                    
                    # Duplicate Widget IDs check
                    if wid in widget_ids:
                        logs.append(f"Validation Error: Duplicate Widget ID '{wid}' found on page '{page.title}'.")
                        is_valid = False
                    widget_ids.add(wid)
                    widget_configs[wid] = widget

                    # Position coordinates validation
                    layout = widget.layout
                    for env, pos in [("desktop", layout.desktop), ("tablet", layout.tablet), ("mobile", layout.mobile)]:
                        if pos.col + pos.width > 12:
                            logs.append(f"Validation Warning: Widget '{wid}' bounds exceed 12 columns in environment '{env}' ({pos.col} + {pos.width}).")
                            is_valid = False
                        if pos.width <= 0 or pos.height <= 0:
                            logs.append(f"Validation Error: Widget '{wid}' has invalid sizes in environment '{env}' (width {pos.width}, height {pos.height}).")
                            is_valid = False

                    # Check broken ECharts visual reference links
                    v_ref = widget.config.chart_id
                    if v_ref and v_ref not in vis_plan.recommendations:
                        logs.append(f"Validation Warning: Widget '{wid}' references a missing visualization plan recommendation ID '{v_ref}'.")
                        # Do not mark is_valid=False for soft warnings if fallback exists

        # 2. Check for missing widgets from visualization recommendations
        for v_id in vis_plan.recommendations.keys():
            # Check if any ECharts recommendation has no mapped widget
            has_widget = any(w.config.chart_id == v_id for page in dashboard.pages for sec in page.sections for w in sec.widgets)
            if not has_widget:
                logs.append(f"Validation Notice: Recommended visualization ID '{v_id}' is not mapped to any dashboard widget.")

        # 3. Check for circular dependency links (if any)
        # Simply checks if dependencies lists contain the widget's own ID
        for wid, widget in widget_configs.items():
            if wid in widget.config.dependencies:
                logs.append(f"Validation Error: Widget '{wid}' lists a circular self-dependency.")
                is_valid = False

        if is_valid:
            logs.append("Dashboard configuration validation completed successfully. Structural integrity verified.")

        return logs, is_valid
