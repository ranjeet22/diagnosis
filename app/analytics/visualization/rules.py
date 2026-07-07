from typing import Dict, List, Any, Optional
from app.schemas.profile import ColumnProfile
from app.core.logging import logger


class VisualizationRuleEngine:
    """
    Evaluates clinical variables and shapes (cardinality, data types) to choose
    the optimal ECharts visualization type deterministically.
    """

    @staticmethod
    def recommend_chart_type(
        task_id: str, 
        cols: List[str], 
        cols_profiles: Dict[str, ColumnProfile],
        unique_count: int = 0,
        planned_family: Optional[str] = None
    ) -> str:
        """
        Selects ECharts type: 'bar', 'line', 'pie', 'scatter', 'heatmap', 'boxplot', 'treemap'.
        """
        # 0. Planned family overrides
        if planned_family:
            pf = planned_family.lower().strip()
            if pf in {"bar", "pie", "line", "scatter", "heatmap", "boxplot", "treemap"}:
                return pf
            if pf == "histogram":
                return "bar"
            if pf == "area":
                return "line"
            if pf == "box plot":
                return "boxplot"

        # 1. Direct Pattern Matches from task IDs
        if "correlation" in task_id or "heatmap" in task_id:
            return "heatmap"
        if "boxplot" in task_id:
            return "boxplot"
        if "scatter" in task_id:
            return "scatter"
        if "treemap" in task_id:
            return "treemap"
        if "trend" in task_id or "moving_average" in task_id or "growth_rate" in task_id:
            return "line"

        # 2. Variable-count checks
        if len(cols) == 1:
            col = cols[0]
            prof = cols_profiles.get(col)
            
            if prof:
                dtype = prof.detected_data_type
                c_cnt = unique_count or prof.unique_count
                
                # Numeric distribution -> Boxplot or Histogram (Bar)
                if dtype in {"INTEGER", "FLOAT"}:
                    if "age" in col:
                        # Age binned histograms can use bar chart
                        return "bar"
                    return "boxplot"
                
                # Category splits
                if dtype in {"STRING", "CATEGORY", "BOOLEAN"}:
                    if 1 < c_cnt <= 6:
                        return "pie"
                    else:
                        return "bar" # horizontal/vertical bar

        elif len(cols) >= 2:
            col_a, col_b = cols[0], cols[1]
            prof_a = cols_profiles.get(col_a)
            prof_b = cols_profiles.get(col_b)

            if prof_a and prof_b:
                dtype_a = prof_a.detected_data_type
                dtype_b = prof_b.detected_data_type
                
                # Numeric vs Categorical -> Boxplot
                if (dtype_a in {"INTEGER", "FLOAT"} and dtype_b in {"STRING", "CATEGORY"}) or \
                   (dtype_b in {"INTEGER", "FLOAT"} and dtype_a in {"STRING", "CATEGORY"}):
                    return "boxplot"
                
                # Numeric vs Numeric -> Scatter
                if dtype_a in {"INTEGER", "FLOAT"} and dtype_b in {"INTEGER", "FLOAT"}:
                    return "scatter"
                
                # Categorical vs Categorical -> Stacked Bar / Heatmap / Bar
                if dtype_a in {"STRING", "CATEGORY"} and dtype_b in {"STRING", "CATEGORY"}:
                    return "bar" # Stacked bar represented as bar with series groups
                    
        return "bar"
