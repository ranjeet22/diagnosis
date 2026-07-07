import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Union, Optional
from app.core.logging import logger


class DatasetStatisticsCollector:
    """
    Computes mathematical metrics, summary descriptive statistics,
    and detects outliers over DataFrame columns.
    """

    @staticmethod
    def collect_numeric_stats(series: pd.Series) -> Dict[str, Any]:
        """
        Computes descriptive statistics for a numeric column.
        """
        non_nulls = series.dropna()
        if len(non_nulls) == 0:
            return {}

        # Convert elements to float/int and calculate
        min_val = non_nulls.min()
        max_val = non_nulls.max()
        mean_val = non_nulls.mean()
        median_val = non_nulls.median()
        std_val = non_nulls.std()

        # Calculate Mode
        mode_val = None
        mode_series = non_nulls.mode()
        if not mode_series.empty:
            mode_val = mode_series.iloc[0]

        # Calculate IQR and detect outliers
        q1 = non_nulls.quantile(0.25)
        q3 = non_nulls.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # Outliers check
        outliers_mask = (non_nulls < lower_bound) | (non_nulls > upper_bound)
        outliers_series = non_nulls[outliers_mask]
        outlier_count = len(outliers_series)
        outlier_percentage = float((outlier_count / len(series)) * 100.0)
        
        # Take up to 10 unique outlier samples
        outlier_samples = [
            DatasetStatisticsCollector._sanitize_value(x)
            for x in outliers_series.unique()[:10]
        ]

        return {
            "min_value": DatasetStatisticsCollector._sanitize_value(min_val),
            "max_value": DatasetStatisticsCollector._sanitize_value(max_val),
            "mean": float(mean_val) if not pd.isna(mean_val) else None,
            "median": float(median_val) if not pd.isna(median_val) else None,
            "std_dev": float(std_val) if not pd.isna(std_val) else None,
            "mode": DatasetStatisticsCollector._sanitize_value(mode_val),
            "outlier_count": outlier_count,
            "outlier_percentage": outlier_percentage,
            "outliers_samples": outlier_samples,
        }

    @staticmethod
    def collect_categorical_stats(series: pd.Series) -> Dict[str, Any]:
        """
        Computes mode, min, max, unique values for text/categorical columns.
        """
        non_nulls = series.dropna()
        if len(non_nulls) == 0:
            return {}

        mode_val = None
        mode_series = non_nulls.mode()
        if not mode_series.empty:
            mode_val = mode_series.iloc[0]

        # String bounds (lexicographical)
        try:
            min_val = non_nulls.min()
            max_val = non_nulls.max()
        except Exception:
            min_val = None
            max_val = None

        return {
            "min_value": DatasetStatisticsCollector._sanitize_value(min_val),
            "max_value": DatasetStatisticsCollector._sanitize_value(max_val),
            "mean": None,
            "median": None,
            "std_dev": None,
            "mode": DatasetStatisticsCollector._sanitize_value(mode_val),
            "outlier_count": 0,
            "outlier_percentage": 0.0,
            "outliers_samples": [],
        }

    @staticmethod
    def _sanitize_value(val: Any) -> Optional[Union[int, float, str]]:
        """
        Converts numpy, pandas, or CuPy values to basic Python types for JSON compatibility.
        """
        if val is None or pd.isna(val):
            return None
            
        # If float or integer, check types
        if hasattr(val, "item"):
            # Numpy scalar extraction
            val = val.item()
            
        if isinstance(val, (int, np.integer)):
            return int(val)
        if isinstance(val, (float, np.floating)):
            return float(val)
            
        # Stringify anything else (e.g. Timestamp, string)
        return str(val)
