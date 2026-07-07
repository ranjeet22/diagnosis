import os
import json
from typing import List, Dict, Any, Optional
from app.schemas.plan import VisualizationPlan
from app.core.logging import logger


class VisualizationPlanner:
    """
    Recommends details for chart renderings (chart family, size, position, interaction rules)
    by loading specifications dynamically from visualization_rules.json.
    """
    def __init__(self, rules_path: str = None) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_rules = os.path.abspath(
            os.path.join(current_dir, "..", "..", "config", "semantic", "visualization_rules.json")
        )
        self.rules_path = rules_path or default_rules
        self.vis_rules: Dict[str, Any] = {}
        self._load_rules()

    def _load_rules(self) -> None:
        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    self.vis_rules = json.load(f)
                logger.debug(f"VisualizationPlanner: Loaded rules from {self.rules_path}")
            else:
                logger.warning(f"VisualizationPlanner rules file missing at: {self.rules_path}")
        except Exception as e:
            logger.error(f"Failed to load visualization rules config file: {e}")

    def plan_task_visualization(self, task_id: str, name: str, required_cols: List[str]) -> Optional[VisualizationPlan]:
        """
        Plans visualization details for a given task ID using the rules config.
        """
        tasks_rules = self.vis_rules.get("tasks", {})
        
        # 1. Direct task ID match
        if task_id in tasks_rules:
            rule = tasks_rules[task_id]
            return VisualizationPlan(
                chart_family=rule["chart_family"],
                purpose=rule["purpose"],
                required_columns=required_cols,
                aggregation=rule["aggregation"],
                priority=rule["priority"],
                recommended_size=rule["recommended_size"],
                recommended_position=rule["recommended_position"],
                interaction_type=rule["interaction_type"]
            )

        # 2. Pattern-based fallback (Temporal Trend default)
        if "trend" in task_id or "moving_average" in task_id or "growth_rate" in task_id:
            rule = self.vis_rules.get("trend_default", {})
            if rule:
                chart = "Area" if "admission_trend" in task_id else rule.get("chart_family", "Line")
                return VisualizationPlan(
                    chart_family=chart,
                    purpose=rule["purpose"],
                    required_columns=required_cols,
                    aggregation=rule["aggregation"],
                    priority=rule["priority"],
                    recommended_size=rule["recommended_size"],
                    recommended_position=rule["recommended_position"],
                    interaction_type=rule["interaction_type"]
                )

        return None

    def plan_comparison_visualization(self, name: str, cols: List[str], comp_type: str) -> Optional[VisualizationPlan]:
        """
        Plans chart types for cross-column comparison dashboards.
        """
        comp_rules = self.vis_rules.get("comparisons", {})
        if comp_type in comp_rules:
            rule = comp_rules[comp_type]
            
            # Formulate cross-tab purpose description dynamically
            purpose = f"Analyze numerical statistics of {cols[1]} grouped by categories of {cols[0]}."
            if comp_type == "categorical_vs_categorical":
                purpose = f"Cross-tabulate category count ratios between {cols[0]} and {cols[1]}."
            elif comp_type == "temporal_vs_categorical":
                purpose = f"Examine daily counts of {cols[1]} categories over time."

            return VisualizationPlan(
                chart_family=rule["chart_family"],
                purpose=purpose,
                required_columns=cols,
                aggregation=rule["aggregation"],
                priority=rule["priority"],
                recommended_size=rule["recommended_size"],
                recommended_position=rule["recommended_position"],
                interaction_type=rule["interaction_type"]
            )

        return None
