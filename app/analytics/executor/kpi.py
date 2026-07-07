import time
from typing import Dict, Any, List, Optional
import pandas as pd
from app.schemas.plan import KPIPlan
from app.schemas.results import KPIResult
from app.core.logging import logger


class KPIEngine:
    """
    Computes Key Performance Indicators (KPIs) over the active pandas/cuDF DataFrame
    deterministically using vectorized operations.
    """

    @staticmethod
    def calculate_kpi(
        df: Any, 
        kpi_plan: KPIPlan, 
        profile_completeness: float, 
        profile_quality_score: float,
        confidence: float = 1.0
    ) -> KPIResult:
        """
        Executes a planned KPI calculation.
        """
        start_time = time.perf_counter()
        name = kpi_plan.name
        agg_type = kpi_plan.aggregation_type
        req_cols = kpi_plan.required_columns
        
        val = None

        try:
            # 1. Total records / Patients distinct count
            if name == "Total Records" or agg_type == "count" and not req_cols:
                val = len(df)
            elif name == "Total Patients" or (agg_type == "distinct_count" and req_cols and name == "Total Patients"):
                col = req_cols[0]
                val = int(df[col].nunique())
            
            # 2. General Distinct Counts
            elif agg_type == "distinct_count" and req_cols:
                col = req_cols[0]
                val = int(df[col].nunique())
                
            # 3. Mode
            elif agg_type == "mode" and req_cols:
                col = req_cols[0]
                mode_res = df[col].mode()
                # Handle pandas / cudf Series conversion
                if hasattr(mode_res, "to_pandas"):
                    mode_res = mode_res.to_pandas()
                val = str(mode_res.iloc[0]) if not mode_res.empty else None

            # 4. Average Patient Age / Numeric averages
            elif agg_type == "average" and req_cols and name == "Average Patient Age":
                col = req_cols[0]
                val = float(df[col].mean())

            # 5. Recovery & Mortality Rates
            elif agg_type == "percentage" and req_cols and name in {"Recovery Rate", "Mortality Rate"}:
                col = req_cols[0]
                total = len(df)
                if total > 0:
                    series_str = df[col].astype(str).str.lower().str.strip()
                    if name == "Recovery Rate":
                        # Match 'recovered', 'recovery', 'discharged'
                        matches = series_str.isin(["recovered", "recovery", "discharged"])
                    else:
                        # Match 'mortality', 'died', 'expired', 'death'
                        matches = series_str.isin(["mortality", "died", "expired", "death", "deceased"])
                    
                    val = float((matches.sum() / total) * 100.0)
                else:
                    val = 0.0

            # 6. Average Hospital Stay Duration
            elif agg_type == "average" and len(req_cols) >= 2 and name == "Average Hospital Stay":
                adm_col = req_cols[1]  # Admission_Date
                dis_col = req_cols[0]  # Discharge_Date
                
                # Check Series types and convert
                adms = _to_datetime_series(df[adm_col])
                disch = _to_datetime_series(df[dis_col])
                
                # Vectorized timedelta calculation in days
                stay_deltas = (disch - adms).dt.total_seconds() / 86400.0
                # Filter out negative stays or errors
                stay_deltas = stay_deltas[stay_deltas >= 0]
                val = float(stay_deltas.mean()) if len(stay_deltas) > 0 else 0.0

            # 7. Generic averages (Average BMI, etc.)
            elif agg_type == "average" and req_cols:
                col = req_cols[0]
                val = float(df[col].mean())

            # 8. Completeness & Quality Score fallbacks
            elif name == "Dataset Completeness":
                val = float(profile_completeness)
            elif name == "Data Quality Score":
                val = float(profile_quality_score)
            
            else:
                # Catch-all general numeric aggregation
                if req_cols:
                    col = req_cols[0]
                    if agg_type == "sum":
                        val = float(df[col].sum())
                    elif agg_type == "average":
                        val = float(df[col].mean())
                    elif agg_type == "median":
                        val = float(df[col].median())
                    elif agg_type == "min":
                        val = float(df[col].min())
                    elif agg_type == "max":
                        val = float(df[col].max())

        except Exception as e:
            logger.error(f"KPIEngine: Failed to compute KPI '{name}': {e}", exc_info=True)
            val = None

        duration = (time.perf_counter() - start_time) * 1000.0
        
        # Round numeric values for display
        if isinstance(val, float):
            val = round(val, 2)

        return KPIResult(
            name=name,
            value=val,
            formula=kpi_plan.formula,
            execution_time_ms=round(duration, 2),
            confidence=confidence,
            source_columns=req_cols
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
