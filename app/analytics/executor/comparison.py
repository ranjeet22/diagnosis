import os
import json
from typing import List, Dict, Any
import pandas as pd
from app.schemas.plan import ComparisonPlan
from app.schemas.results import ComparisonResult
from app.core.logging import logger


class ComparisonEngine:
    """
    Executes cross-variable comparisons, generating cross-tabulation matrices
    or grouped numerical box-plot statistics.
    """
    def __init__(self, age_groups_path: str = None) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_age_groups = os.path.abspath(
            os.path.join(current_dir, "..", "..", "config", "semantic", "age_groups.json")
        )
        self.age_groups_path = age_groups_path or default_age_groups
        self.age_groups: List[Dict[str, Any]] = []
        self._load_age_groups()

    def _load_age_groups(self) -> None:
        try:
            if os.path.exists(self.age_groups_path):
                with open(self.age_groups_path, "r", encoding="utf-8") as f:
                    self.age_groups = json.load(f)
        except Exception:
            self.age_groups = [
                {"label": "0-18", "min": 0, "max": 18},
                {"label": "19-35", "min": 19, "max": 35},
                {"label": "36-50", "min": 36, "max": 50},
                {"label": "51-65", "min": 51, "max": 65},
                {"label": "65+", "min": 66, "max": 150}
            ]

    def calculate_comparison(
        self, 
        df: Any, 
        plan: ComparisonPlan,
        age_col: Optional[str] = None
    ) -> ComparisonResult:
        """
        Executes comparison calculations.
        """
        cols = plan.columns
        comp_type = plan.comparison_type
        name = plan.name
        
        computed_data: Dict[str, Any] = {}

        if not cols or len(cols) < 2:
            return ComparisonResult(name=name, columns=cols, comparison_type=comp_type, data={})

        col_a, col_b = cols[0], cols[1]

        # Verify columns exist
        if col_a not in df.columns or col_b not in df.columns:
            # Check if one of them is virtual "age_group"
            if "age_group" in col_a or "age_group" in col_b:
                if not age_col or age_col not in df.columns:
                    logger.warning(f"ComparisonEngine: age_col '{age_col}' not found. Cannot evaluate age comparisons.")
                    return ComparisonResult(name=name, columns=cols, comparison_type=comp_type, data={})
            else:
                logger.warning(f"ComparisonEngine: Columns '{col_a}' or '{col_b}' missing.")
                return ComparisonResult(name=name, columns=cols, comparison_type=comp_type, data={})

        try:
            # 1. Create a local temporary copy of dataframe with relevant columns
            # Convert to pandas for complex multi-variable crosstabs/box-plots to avoid cuDF unstack/quantile index issues
            if hasattr(df, "to_pandas"):
                local_df = df[[c for c in cols if c in df.columns]].to_pandas()
            else:
                local_df = df[[c for c in cols if c in df.columns]].copy()

            # 2. Inject virtual binned age groups if requested
            if "age_group" in col_a or "age_group" in col_b:
                # Bin age column
                ages = df[age_col].to_pandas() if hasattr(df[age_col], "to_pandas") else df[age_col]
                binned = _bin_ages(ages, self.age_groups)
                
                if "age_group" in col_a:
                    local_df[col_a] = binned
                if "age_group" in col_b:
                    local_df[col_b] = binned

            # 3. Compute calculations
            if comp_type == "categorical_vs_numeric":
                # E.g. Disease vs Age -> group by category (col_a) and get box plot stats of numeric (col_b)
                unique_cats = local_df[col_a].dropna().unique()
                for cat in unique_cats:
                    cat_str = str(cat).strip()
                    if cat_str == "nan" or not cat_str:
                        cat_str = "Missing"
                        
                    subset = local_df[local_df[col_a] == cat][col_b].dropna()
                    if len(subset) > 0:
                        # Box plot quantiles
                        q_min = float(subset.min())
                        q1 = float(subset.quantile(0.25))
                        q_med = float(subset.median())
                        q3 = float(subset.quantile(0.75))
                        q_max = float(subset.max())
                        
                        computed_data[cat_str] = {
                            "min": round(q_min, 2),
                            "q1": round(q1, 2),
                            "median": round(q_med, 2),
                            "q3": round(q3, 2),
                            "max": round(q_max, 2),
                            "count": len(subset)
                        }
            else:
                # categorical_vs_categorical / temporal_vs_categorical
                # E.g. Disease vs Gender -> group count
                grouped = local_df.groupby([col_a, col_b]).size()
                crosstab_df = grouped.unstack(fill_value=0)
                
                # Convert matrix to dictionary
                raw_dict = crosstab_df.to_dict(orient="index")
                
                # Format labels securely
                for row_lbl, col_vals in raw_dict.items():
                    row_str = str(row_lbl).strip()
                    if row_str == "nan" or not row_str:
                        row_str = "Missing"
                    
                    inner_dict = {}
                    for col_lbl, count in col_vals.items():
                        col_str = str(col_lbl).strip()
                        if col_str == "nan" or not col_str:
                            col_str = "Missing"
                        inner_dict[col_str] = int(count)
                        
                    computed_data[row_str] = inner_dict

        except Exception as e:
            logger.error(f"ComparisonEngine: Failed to compute comparison '{name}': {e}", exc_info=True)

        return ComparisonResult(
            name=name,
            columns=cols,
            comparison_type=comp_type,
            data=computed_data
        )


def _bin_ages(ages_series: pd.Series, age_groups: List[Dict[str, Any]]) -> pd.Series:
    """Bins ages series into labels."""
    labels = pd.Series(["Unknown"] * len(ages_series), index=ages_series.index)
    for gp in age_groups:
        lbl = gp["label"]
        min_v = gp["min"]
        max_v = gp["max"]
        mask = (ages_series >= min_v) & (ages_series <= max_v)
        labels[mask] = lbl
    return labels
