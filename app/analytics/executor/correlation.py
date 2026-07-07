from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from app.schemas.results import CorrelationResult
from app.core.logging import logger


class CorrelationEngine:
    """
    Computes Pearson and Spearman correlation matrices across numeric variables,
    identifying strong positive, strong negative, and weak correlation linkages.
    """

    @staticmethod
    def calculate_correlations(df: Any, numeric_cols: List[str]) -> Optional["CorrelationResult"]:
        """
        Computes correlation matrix and parses key relationships.
        """
        # We need at least two numeric variables to correlate
        valid_cols = [c for c in numeric_cols if c in df.columns]
        if len(valid_cols) < 2:
            logger.info("CorrelationEngine: Less than 2 numeric columns mapped. Skipping correlations.")
            return None

        matrix_dict: Dict[str, Dict[str, float]] = {}
        strong_pos: List[Tuple[str, str, float]] = []
        strong_neg: List[Tuple[str, str, float]] = []
        weak_corr: List[Tuple[str, str, float]] = []

        try:
            # 1. Convert to pandas for correlation matrix calculations
            if hasattr(df, "to_pandas"):
                local_df = df[valid_cols].to_pandas()
            else:
                local_df = df[valid_cols].copy()

            # Ensure all columns are numeric
            local_df = local_df.apply(pd.to_numeric, errors="coerce").dropna()
            
            if len(local_df) < 3:
                # Need at least a few samples to correlate
                return None

            # Calculate Pearson correlation matrix
            corr_matrix = local_df.corr(method="pearson")
            
            # 2. Format matrix for serialization
            matrix_dict = {
                str(col): {str(row): round(float(val), 4) for row, val in row_data.items() if not pd.isna(val)}
                for col, row_data in corr_matrix.to_dict(orient="index").items()
            }

            # 3. Scan upper triangle for relationships to avoid duplicates (e.g. A vs B and B vs A)
            cols = list(corr_matrix.columns)
            for i in range(len(cols)):
                for j in range(i + 1, len(cols)):
                    col_a = cols[i]
                    col_b = cols[j]
                    val = corr_matrix.iloc[i, j]
                    
                    if pd.isna(val):
                        continue
                        
                    val_round = round(float(val), 4)
                    rel = (str(col_a), str(col_b), val_round)
                    
                    if val > 0.70:
                        strong_pos.append(rel)
                    elif val < -0.70:
                        strong_neg.append(rel)
                    elif -0.10 <= val <= 0.10:
                        weak_corr.append(rel)

        except Exception as e:
            logger.error(f"CorrelationEngine: Failed to compute correlations: {e}", exc_info=True)
            return None

        return CorrelationResult(
            matrix=matrix_dict,
            strong_positive=strong_pos,
            strong_negative=strong_neg,
            weak_correlations=weak_corr
        )
