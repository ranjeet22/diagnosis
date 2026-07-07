import os
import re
import math
from typing import Dict, Any, List, Tuple
import pandas as pd

from app.core.logging import logger
from app.core.exceptions import DatasetNotFound, AnalyticsError
from app.core.config import settings
from app.schemas.profile import DatasetProfile, ColumnProfile, DataQualityIssue
from app.schemas.dataset import DatasetMetadata
from app.storage.interface import StorageInterface
from app.analytics.dataframe_provider import load_dataset_df
from app.analytics.data_type_detector import DataTypeDetector
from app.analytics.statistics_collector import DatasetStatisticsCollector


def normalize_column_name(name: str) -> str:
    """
    Normalizes raw column names to a unified snake_case format,
    removing measurement units, parenthesis, and special characters.
    E.g., "Patient Age (years)" -> "patient_age"
          "Blood Pressure (mmHg)" -> "blood_pressure"
    """
    # Remove parentheses, brackets, curly braces and anything inside them
    name_clean = re.sub(r'[\(\[\{].*?[\)\]\}]', '', name)
    # Replace all non-alphanumeric chars with underscores
    name_clean = re.sub(r'[^a-zA-Z0-9]', '_', name_clean)
    # Replace multiple consecutive underscores with a single underscore
    name_clean = re.sub(r'_+', '_', name_clean)
    # Convert to lowercase and strip leading/trailing underscores
    return name_clean.strip('_').lower()


class DatasetProfiler:
    """
    Orchestration service that loads datasets, profiles columns,
    identifies datatypes/roles, detects data quality issues,
    calculates a quality score, and generates the final DatasetProfile.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def profile_dataset(self, dataset_id: str) -> DatasetProfile:
        """
        Builds a comprehensive profile for a dataset by ID.
        """
        logger.info(f"Generating profile for dataset: {dataset_id}")
        
        # 1. Fetch metadata to get file details (delimiter, encoding, original filename)
        try:
            metadata: DatasetMetadata = await self.storage.get_metadata(dataset_id)
        except DatasetNotFound:
            raise DatasetNotFound(f"Dataset '{dataset_id}' not found. Cannot profile.")
        except Exception as e:
            raise AnalyticsError(f"Failed to fetch metadata for profiling: {e}")

        # 2. Get local file path and load into DataFrame
        file_path = self.storage.get_file_path(dataset_id, "original.csv")
        if not os.path.exists(file_path):
            raise DatasetNotFound(f"Raw CSV file for dataset '{dataset_id}' is missing from storage.")

        try:
            df = load_dataset_df(
                file_path=file_path,
                delimiter=metadata.delimiter,
                encoding=metadata.encoding
            )
        except Exception as e:
            logger.error(f"Error loading dataframe for dataset {dataset_id}: {e}")
            raise AnalyticsError(f"Failed to read dataset file for profiling: {e}")

        total_rows = int(df.shape[0])
        total_cols = int(df.shape[1])
        
        if total_rows == 0:
            raise AnalyticsError("Dataset contains 0 rows. Cannot profile.")

        # 3. Collect Dataset-Level Base Metrics
        duplicate_rows_count = int(df.duplicated().sum())
        total_cells = total_rows * total_cols
        total_missing = int(df.isnull().sum().sum())
        
        # Calculate memory footprint
        total_memory_bytes = int(df.memory_usage(deep=True).sum())
        estimated_size_str = self._format_size(total_memory_bytes)

        # 4. Profile Columns
        columns_profile: Dict[str, ColumnProfile] = {}
        quality_issues: List[DataQualityIssue] = []
        
        numeric_count = 0
        categorical_count = 0
        date_count = 0
        text_count = 0
        boolean_count = 0
        
        potential_target_columns = []
        potential_identifier_columns = []
        potential_time_columns = []
        potential_measurement_columns = []

        # Deduplicate normalized names to avoid conflicts on duplicate columns
        seen_normalized_names: Dict[str, int] = {}

        for pos, col_name in enumerate(df.columns):
            series = df[col_name]
            
            # Normalize column name
            norm_name = normalize_column_name(col_name)
            if not norm_name:
                norm_name = f"column_{pos}"
                
            # Handle normalized collision
            if norm_name in seen_normalized_names:
                seen_normalized_names[norm_name] += 1
                norm_name = f"{norm_name}_{seen_normalized_names[norm_name]}"
            else:
                seen_normalized_names[norm_name] = 0

            # Missing and uniques
            missing_cnt = int(series.isnull().sum())
            missing_pct = float((missing_cnt / total_rows) * 100.0)
            
            non_nulls = series.dropna()
            unique_vals = [DatasetStatisticsCollector._sanitize_value(x) for x in non_nulls.unique()]
            unique_cnt = len(unique_vals)
            
            # Duplicate cells count in column
            dup_cnt = int(series.duplicated().sum()) - missing_cnt
            dup_cnt = max(0, dup_cnt)

            # Detect logical datatype
            logical_type = DataTypeDetector.detect_type(series)
            storage_type = str(series.dtype)

            # Update count metrics
            if logical_type in {"INTEGER", "FLOAT"}:
                numeric_count += 1
            elif logical_type in {"CATEGORY", "STRING", "EMAIL", "PHONE", "ZIPCODE"}:
                categorical_count += 1
            elif logical_type in {"DATE", "DATETIME"}:
                date_count += 1
            elif logical_type == "TEXT":
                text_count += 1
            elif logical_type == "BOOLEAN":
                boolean_count += 1

            # Infer semantic roles
            roles = DataTypeDetector.infer_roles(col_name, logical_type, unique_vals, total_rows, series)
            if "Target Variable" in roles:
                potential_target_columns.append(norm_name)
            if "Identifier" in roles:
                potential_identifier_columns.append(norm_name)
            if "Timestamp" in roles:
                potential_time_columns.append(norm_name)
            if "Measurement" in roles:
                potential_measurement_columns.append(norm_name)

            # Collect descriptive statistics
            if logical_type in {"INTEGER", "FLOAT"}:
                stats = DatasetStatisticsCollector.collect_numeric_stats(series)
            else:
                stats = DatasetStatisticsCollector.collect_categorical_stats(series)

            # Determine cardinality status
            if unique_cnt == 1:
                cardinality_label = "constant"
            elif unique_cnt == 2:
                cardinality_label = "binary"
            elif unique_cnt < 15:
                cardinality_label = "low"
            elif unique_cnt / total_rows > 0.4:
                cardinality_label = "high"
            else:
                cardinality_label = "medium"

            # Get sample values (first 10 unique values)
            samples = unique_vals[:10]

            col_profile = ColumnProfile(
                original_name=col_name,
                normalized_name=norm_name,
                column_position=pos,
                detected_data_type=logical_type,
                storage_type=storage_type,
                semantic_hint="",
                nullable=missing_cnt > 0,
                unique_count=unique_cnt,
                duplicate_count=dup_cnt,
                missing_count=missing_cnt,
                missing_percentage=missing_pct,
                min_value=stats.get("min_value"),
                max_value=stats.get("max_value"),
                mean=stats.get("mean"),
                median=stats.get("median"),
                std_dev=stats.get("std_dev"),
                mode=stats.get("mode"),
                sample_values=samples,
                memory_usage=int(series.memory_usage(deep=True)),
                cardinality=cardinality_label
            )

            columns_profile[norm_name] = col_profile

            # 5. Column-Level Quality Issues Detection
            # Empty column
            if unique_cnt == 0:
                quality_issues.append(DataQualityIssue(
                    column=norm_name,
                    issue_type="empty_column",
                    severity="critical",
                    message=f"Column '{col_name}' is entirely empty (100% missing values).",
                    affected_percentage=100.0
                ))
            # Missing values warning
            elif missing_pct > 0.0:
                severity = "critical" if missing_pct > 40.0 else "warning"
                quality_issues.append(DataQualityIssue(
                    column=norm_name,
                    issue_type="missing_values",
                    severity=severity,
                    message=f"Column '{col_name}' has {missing_cnt} missing values ({missing_pct:.2f}%).",
                    affected_percentage=missing_pct
                ))

            # Constant Column (excluding empty)
            if unique_cnt == 1 and missing_pct < 100.0:
                quality_issues.append(DataQualityIssue(
                    column=norm_name,
                    issue_type="constant_column",
                    severity="warning",
                    message=f"Column '{col_name}' is constant and contains only one unique value: {repr(unique_vals[0])}.",
                    affected_percentage=100.0
                ))

            # High Cardinality Categorical Column
            if cardinality_label == "high" and logical_type in {"CATEGORY", "STRING"} and "Identifier" not in roles:
                affected_pct = (unique_cnt / total_rows) * 100.0
                quality_issues.append(DataQualityIssue(
                    column=norm_name,
                    issue_type="high_cardinality",
                    severity="warning",
                    message=f"Categorical column '{col_name}' has high cardinality ({unique_cnt} unique values).",
                    affected_percentage=affected_pct
                ))

            # Outliers warning
            outliers_count = stats.get("outlier_count", 0)
            outliers_pct = stats.get("outlier_percentage", 0.0)
            if outliers_count > 0 and outliers_pct > 3.0:
                quality_issues.append(DataQualityIssue(
                    column=norm_name,
                    issue_type="outliers",
                    severity="warning",
                    message=f"Numeric column '{col_name}' contains {outliers_count} outliers ({outliers_pct:.2f}% of rows).",
                    affected_percentage=outliers_pct
                ))

            # Whitespace warning
            if logical_type in {"STRING", "TEXT", "CATEGORY"}:
                whitespace_rows = int(non_nulls.str.startswith(" ").sum() + non_nulls.str.endswith(" ").sum())
                if whitespace_rows > 0:
                    ws_pct = (whitespace_rows / total_rows) * 100.0
                    quality_issues.append(DataQualityIssue(
                        column=norm_name,
                        issue_type="whitespace_issues",
                        severity="info",
                        message=f"Column '{col_name}' has leading/trailing whitespaces in string values.",
                        affected_percentage=ws_pct
                    ))

            # Mixed Datatypes checking
            if logical_type in {"STRING", "CATEGORY"}:
                numeric_strings = 0
                sample_str = non_nulls.astype(str).str.strip()
                for v in sample_str:
                    try:
                        float(v)
                        numeric_strings += 1
                    except ValueError:
                        pass
                
                # If column has mixed text and digits
                if 0.05 < (numeric_strings / len(non_nulls)) < 0.95:
                    mix_pct = (numeric_strings / len(non_nulls)) * 100.0
                    quality_issues.append(DataQualityIssue(
                        column=norm_name,
                        issue_type="mixed_datatypes",
                        severity="warning",
                        message=f"Column '{col_name}' contains mixed datatypes (both text and numeric characters).",
                        affected_percentage=min(mix_pct, 100.0 - mix_pct)
                    ))

        # 6. Dataset-Level Quality Issues Detection
        if duplicate_rows_count > 0:
            dup_pct = (duplicate_rows_count / total_rows) * 100.0
            severity = "warning" if dup_pct > 5.0 else "info"
            quality_issues.append(DataQualityIssue(
                column=None,
                issue_type="duplicate_rows",
                severity=severity,
                message=f"Dataset contains {duplicate_rows_count} duplicate rows ({dup_pct:.2f}%).",
                affected_percentage=dup_pct
            ))

        # 7. Calculate Dataset Quality Score (0 - 100)
        quality_score = self._calculate_quality_score(
            total_cells=total_cells,
            total_missing=total_missing,
            duplicate_rows=duplicate_rows_count,
            total_rows=total_rows,
            quality_issues=quality_issues
        )

        # Assemble dataset profile
        dataset_profile = DatasetProfile(
            dataset_id=dataset_id,
            rows=total_rows,
            columns_count=total_cols,
            total_missing_values=total_missing,
            duplicate_rows=duplicate_rows_count,
            memory_usage=total_memory_bytes,
            estimated_dataset_size=estimated_size_str,
            delimiter=metadata.delimiter,
            encoding=metadata.encoding,
            numeric_column_count=numeric_count,
            categorical_column_count=categorical_count,
            date_column_count=date_count,
            text_column_count=text_count,
            boolean_column_count=boolean_count,
            potential_target_columns=potential_target_columns,
            potential_identifier_columns=potential_identifier_columns,
            potential_time_columns=potential_time_columns,
            potential_measurement_columns=potential_measurement_columns,
            dataset_quality_score=quality_score,
            quality_issues=quality_issues,
            columns=columns_profile
        )

        return dataset_profile

    def _calculate_quality_score(
        self,
        total_cells: int,
        total_missing: int,
        duplicate_rows: int,
        total_rows: int,
        quality_issues: List[DataQualityIssue]
    ) -> float:
        """
        Determines the dataset quality score on a scale of 0 to 100
        by applying mathematical penalties based on severity and metrics.
        """
        score = 100.0

        # Penalty 1: Missing values (subtract up to 30 points)
        if total_cells > 0:
            missing_ratio = total_missing / total_cells
            score -= (missing_ratio * 30.0)

        # Penalty 2: Duplicate rows (subtract up to 15 points)
        if total_rows > 0:
            dup_ratio = duplicate_rows / total_rows
            score -= (dup_ratio * 15.0)

        # Penalty 3: Deduct based on count and severity of individual column issues
        # Critical = -8 points, Warning = -3 points, Info = -1 point
        for issue in quality_issues:
            if issue.column is not None:  # Column level issues
                if issue.severity == "critical":
                    score -= 8.0
                elif issue.severity == "warning":
                    score -= 3.0
                elif issue.severity == "info":
                    score -= 0.5

        # Restrict bounds
        return float(max(0.0, min(100.0, round(score, 2))))

    def _format_size(self, size_bytes: int) -> str:
        """Formats raw byte counts into human-readable memory footprints."""
        if size_bytes == 0:
            return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"
