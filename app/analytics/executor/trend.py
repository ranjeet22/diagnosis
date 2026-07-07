import time
from typing import List, Dict, Any, Tuple
import pandas as pd
from app.schemas.results import TrendResult
from app.core.logging import logger


class TrendEngine:
    """
    Computes daily, weekly, monthly, and yearly admission trends, along with
    moving averages, growth rates, running totals, and seasonality metadata.
    """

    @staticmethod
    def calculate_trend(df: Any, task_id: str, col: str) -> TrendResult:
        """
        Executes temporal trend calculations.
        """
        timestamps: List[str] = []
        counts: List[int] = []
        moving_avg: List[float] = []
        running_tot: List[float] = []
        growth_rate: List[float] = []
        seasonality: Dict[str, Any] = {}

        if col not in df.columns:
            logger.warning(f"TrendEngine: Column '{col}' not found in DataFrame.")
            return TrendResult(task_id=task_id, timestamps=[], counts=[], seasonality_metadata={})

        try:
            # 1. Parse date series (cuDF/Pandas safe)
            date_series = _to_datetime_series(df[col])
            
            # Filter NaNs
            valid_mask = date_series.notnull()
            dates_valid = date_series[valid_mask]
            
            if len(dates_valid) == 0:
                return TrendResult(task_id=task_id, timestamps=[], counts=[], seasonality_metadata={})

            # Create components df for calculations
            # To be 100% safe with complex aggregations, convert dates to pandas
            if hasattr(dates_valid, "to_pandas"):
                dates_pd = dates_valid.to_pandas()
            else:
                dates_pd = dates_valid

            # 2. Extract Interval Groups
            if "daily" in task_id:
                group_col = dates_pd.dt.strftime("%Y-%m-%d")
            elif "weekly" in task_id:
                group_col = dates_pd.dt.strftime("%Y-W%U")
            elif "monthly" in task_id:
                group_col = dates_pd.dt.strftime("%Y-%m")
            elif "quarterly" in task_id:
                group_col = dates_pd.dt.year.astype(str) + "-Q" + ((dates_pd.dt.month - 1) // 3 + 1).astype(str)
            elif "yearly" in task_id:
                group_col = dates_pd.dt.year.astype(str)
            else:
                group_col = dates_pd.dt.strftime("%Y-%m-%d")

            # Value counts sorted chronologically by date string index
            counts_series = group_col.value_counts().sort_index()

            # 3. Populate timestamps and counts lists
            timestamps = [str(idx) for idx in counts_series.index]
            counts = [int(c) for c in counts_series.tolist()]

            # 4. Compute Vectorized Metrics
            if len(counts_series) > 0:
                # Rolling 7-period moving average
                roll_mean = counts_series.rolling(window=7, min_periods=1).mean()
                moving_avg = [round(float(x), 2) for x in roll_mean.tolist()]

                # Cumulative Sum (Running Total)
                cum_sum = counts_series.cumsum()
                running_tot = [float(x) for x in cum_sum.tolist()]

                # Growth Rate (Percent change)
                pct_change = counts_series.pct_change().fillna(0.0) * 100.0
                growth_rate = [round(float(x), 2) for x in pct_change.tolist()]

            # 5. Evaluate Seasonality Metadata
            if len(dates_pd) > 0:
                # Weekday distribution
                days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                wd_counts = dates_pd.dt.weekday.value_counts().sort_index()
                wd_dict = {days[int(k)]: int(v) for k, v in wd_counts.items() if int(k) < 7}

                # Month distribution
                months = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]
                m_counts = dates_pd.dt.month.value_counts().sort_index()
                m_dict = {months[int(k) - 1]: int(v) for k, v in m_counts.items() if 1 <= int(k) <= 12}

                peak_day = max(wd_dict, key=wd_dict.get) if wd_dict else None
                peak_month = max(m_dict, key=m_dict.get) if m_dict else None

                seasonality = {
                    "day_of_week_distribution": wd_dict,
                    "month_of_year_distribution": m_dict,
                    "peak_day_of_week": peak_day,
                    "peak_month_of_year": peak_month
                }

        except Exception as e:
            logger.error(f"TrendEngine: Failed to calculate trend for '{task_id}': {e}", exc_info=True)

        return TrendResult(
            task_id=task_id,
            timestamps=timestamps,
            counts=counts,
            moving_average=moving_avg if moving_avg else None,
            growth_rate=growth_rate if growth_rate else None,
            running_total=running_tot if running_tot else None,
            seasonality_metadata=seasonality
        )


def _to_datetime_series(series: Any) -> Any:
    """Helper converting series to pandas/cuDF DatetimeSeries."""
    try:
        import cudf
        if isinstance(series, cudf.Series):
            return cudf.to_datetime(series, errors="coerce")
    except ImportError:
        pass
    return pd.to_datetime(series, errors="coerce")
