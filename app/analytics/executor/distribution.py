import os
import json
from typing import List, Dict, Any
import pandas as pd
from app.schemas.results import DistributionResult
from app.core.logging import logger


class DistributionEngine:
    """
    Computes value distributions, counts, and percentages for categorical
    and binned numerical variables (e.g., patient age groups).
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
                logger.debug(f"DistributionEngine: Loaded age groups from {self.age_groups_path}")
            else:
                logger.warning(f"DistributionEngine age groups file missing: {self.age_groups_path}")
                raise FileNotFoundError()
        except Exception:
            # Standard fallback brackets
            self.age_groups = [
                {"label": "0-18", "min": 0, "max": 18},
                {"label": "19-35", "min": 19, "max": 35},
                {"label": "36-50", "min": 36, "max": 50},
                {"label": "51-65", "min": 51, "max": 65},
                {"label": "65+", "min": 66, "max": 150}
            ]

    def calculate_distribution(self, df: Any, task_id: str, col: str, is_age: bool = False) -> DistributionResult:
        """
        Computes frequency and percentage distributions.
        """
        labels: List[str] = []
        counts: List[int] = []
        percentages: List[float] = []

        if col not in df.columns:
            logger.warning(f"DistributionEngine: Column '{col}' not found in DataFrame.")
            return DistributionResult(task_id=task_id, labels=[], counts=[], percentages=[])

        series = df[col]
        total_rows = len(series)

        if total_rows == 0:
            return DistributionResult(task_id=task_id, labels=[], counts=[], percentages=[])

        try:
            if is_age:
                # 1. Age Cohorts Bins - Boolean masks (cuDF + Pandas compatible)
                for group in self.age_groups:
                    lbl = group["label"]
                    min_val = group["min"]
                    max_val = group["max"]
                    
                    mask = (series >= min_val) & (series <= max_val)
                    c = int(mask.sum())
                    pct = round((c / total_rows) * 100.0, 2)
                    
                    labels.append(lbl)
                    counts.append(c)
                    percentages.append(pct)
            else:
                # 2. Categorical distribution
                # Convert values to string representation to avoid serialization errors
                val_counts = series.astype(str).value_counts()
                
                # Convert cuDF Series to pandas for easy iteration if needed
                if hasattr(val_counts, "to_pandas"):
                    val_counts = val_counts.to_pandas()
                
                # Fetch top 30 values to prevent bloated JSON files
                val_counts_top = val_counts.head(30)
                
                for lbl, c in val_counts_top.items():
                    lbl_str = str(lbl).strip()
                    if lbl_str == "nan" or not lbl_str:
                        lbl_str = "Missing"
                    
                    pct = round((int(c) / total_rows) * 100.0, 2)
                    labels.append(lbl_str)
                    counts.append(int(c))
                    percentages.append(pct)

        except Exception as e:
            logger.error(f"DistributionEngine: Failed to calculate distribution for '{task_id}': {e}", exc_info=True)

        return DistributionResult(
            task_id=task_id,
            labels=labels,
            counts=counts,
            percentages=percentages
        )
