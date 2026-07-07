from typing import List, Any
import pandas as pd
from app.schemas.plan import AggregationPlan
from app.schemas.results import AggregationResult
from app.core.logging import logger


class AggregationEngine:
    """
    Executes standard mathematical and statistical aggregations (mean, standard deviation,
    rolling averages, running totals) over columns.
    """

    @staticmethod
    def calculate_aggregations(df: Any, plan: AggregationPlan) -> List[AggregationResult]:
        """
        Executes aggregations requested for a column.
        """
        results: List[AggregationResult] = []
        col = plan.column
        
        if col not in df.columns:
            logger.warning(f"AggregationEngine: Column '{col}' not found in DataFrame.")
            return results

        series = df[col]

        for op in plan.operations:
            val = None
            try:
                # 1. Scalar Aggregations
                if op == "Count":
                    val = int(series.count())
                elif op == "Sum":
                    val = float(series.sum())
                elif op == "Average":
                    val = float(series.mean())
                elif op == "Median":
                    val = float(series.median())
                elif op == "Minimum":
                    val = float(series.min())
                elif op == "Maximum":
                    val = float(series.max())
                elif op == "Distinct Count":
                    val = int(series.nunique())
                elif op == "Mode":
                    modes = series.mode()
                    # Handle pandas / cudf Series conversion
                    if hasattr(modes, "to_pandas"):
                        modes = modes.to_pandas()
                    val = str(modes.iloc[0]) if not modes.empty else None
                elif op == "Variance":
                    val = float(series.var())
                elif op == "Standard Deviation":
                    val = float(series.std())
                elif op == "Percentiles":
                    quantiles = series.quantile([0.25, 0.50, 0.75])
                    if hasattr(quantiles, "to_pandas"):
                        quantiles = quantiles.to_pandas()
                    # Return list [Q1, Median, Q3]
                    val = [float(quantiles.iloc[0]), float(quantiles.iloc[1]), float(quantiles.iloc[2])]

                # 2. Cumulative/Rolling Vector Aggregations
                elif op == "Running Total":
                    # Cumulative Sum (fill nulls to avoid breaking serialization)
                    cum_sum = series.fillna(0).cumsum()
                    if hasattr(cum_sum, "to_pandas"):
                        cum_sum = cum_sum.to_pandas()
                    val = [float(x) for x in cum_sum.tolist()]
                elif op == "Rolling Average":
                    # 7-day rolling window mean (fill NaNs with 0/prev values)
                    roll_mean = series.fillna(0).rolling(window=7, min_periods=1).mean()
                    if hasattr(roll_mean, "to_pandas"):
                        roll_mean = roll_mean.to_pandas()
                    val = [round(float(x), 2) for x in roll_mean.tolist()]

            except Exception as e:
                logger.error(f"AggregationEngine: Failed to compute '{op}' on column '{col}': {e}")
                val = None

            # Round float values for display
            if isinstance(val, float):
                val = round(val, 2)

            if val is not None:
                results.append(AggregationResult(
                    column=col,
                    operation=op,
                    value=val
                ))

        return results
