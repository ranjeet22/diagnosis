from typing import Any, Dict, List
from app.schemas.visualization import AccessibilityConfiguration
from app.core.logging import logger


class AccessibilityPlanner:
    """
    Formulates W3C ARIA descriptions, keyboard focus guidelines,
    and descriptive alt texts reflecting the actual computed values.
    """

    @staticmethod
    def plan_accessibility(
        chart_id: str,
        name: str,
        chart_type: str,
        result_data: Any
    ) -> AccessibilityConfiguration:
        """
        Builds AccessibilityConfiguration including screen-reader alt text
        computed dynamically from dataset metrics.
        """
        aria_label = f"Interactive {chart_type} chart visualization titled {name}."
        alt_text = f"Visual representation of {name}."

        try:
            # 1. KPI elements (single scalar value)
            if result_data is None:
                alt_text = f"Metric card for {name}."
            elif isinstance(result_data, (int, float, str)):
                alt_text = f"Key Performance Indicator card for {name} with calculated value of {result_data}."

            # 2. Categorical distributions (Pydantic objects or dicts with labels/counts)
            elif isinstance(result_data, dict) and "labels" in result_data and "counts" in result_data:
                labels = result_data["labels"]
                counts = result_data["counts"]
                pcts = result_data.get("percentages", [])
                
                if labels and counts:
                    # Find maximum and minimum caseloads
                    max_idx = counts.index(max(counts))
                    min_idx = counts.index(min(counts))
                    
                    max_lbl, max_val = labels[max_idx], counts[max_idx]
                    min_lbl, min_val = labels[min_idx], counts[min_idx]
                    
                    max_pct = f" ({pcts[max_idx]}%)" if pcts else ""
                    min_pct = f" ({pcts[min_idx]}%)" if pcts else ""
                    
                    alt_text = (
                        f"{chart_type.capitalize()} chart displaying caseload frequencies of {name} across "
                        f"{len(labels)} categories. {max_lbl} has the highest volume with {max_val} records{max_pct}, "
                        f"while {min_lbl} represents the minimum volume with {min_val} records{min_pct}."
                    )
                else:
                    alt_text = f"Empty {chart_type} chart representing {name}."

            # 3. Time Series Trends
            elif isinstance(result_data, dict) and "timestamps" in result_data and "counts" in result_data:
                ts = result_data["timestamps"]
                counts = result_data["counts"]
                
                if ts and counts:
                    max_idx = counts.index(max(counts))
                    min_idx = counts.index(min(counts))
                    
                    max_time, max_val = ts[max_idx], counts[max_idx]
                    min_time, min_val = ts[min_idx], counts[min_idx]
                    
                    alt_text = (
                        f"Line chart representing the temporal trend of {name} over {len(ts)} intervals. "
                        f"Caseload volume peaked on {max_time} with {max_val} records, "
                        f"and hit a minimum on {min_time} with {min_val} records."
                    )
                else:
                    alt_text = f"Line chart of temporal trends for {name} with no dates plotted."

            # 4. Cross-tab/Box-plot Comparisons
            elif isinstance(result_data, dict) and len(result_data) > 0:
                first_val = list(result_data.values())[0]
                if isinstance(first_val, dict) and "median" in first_val:
                    # Boxplot comparison (e.g. Disease vs Age)
                    medians = {k: v["median"] for k, v in result_data.items() if "median" in v}
                    if medians:
                        max_grp = max(medians, key=medians.get)
                        min_grp = min(medians, key=medians.get)
                        alt_text = (
                            f"Box plot chart comparing numeric ranges of {name} across categories. "
                            f"The highest median was observed in the {max_grp} group ({medians[max_grp]}), "
                            f"while the lowest median was in the {min_grp} group ({medians[min_grp]})."
                        )
                else:
                    # Cross-tab comparison (Disease vs Gender)
                    top_groups = list(result_data.keys())[:3]
                    alt_text = (
                        f"Comparative cross-tabulation table chart titled {name} showing grouped totals "
                        f"for categories including {', '.join(top_groups)}."
                    )

        except Exception as e:
            logger.warning(f"AccessibilityPlanner: Failed to compile dynamic alt text for {chart_id}: {e}")

        return AccessibilityConfiguration(
            aria_label=aria_label,
            keyboard_navigation=True,
            color_contrast_compliant=True,
            alt_text=alt_text,
            font_scaling_supported=True
        )
