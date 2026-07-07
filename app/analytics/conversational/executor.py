import pandas as pd
from typing import Dict, Any, List
from app.core.logging import logger
from app.schemas.results import AnalyticsResult
from app.schemas.conversation import IntentResponse, QueryResult, IntentExecution


class IntentExecutor:
    """
    Executes a parsed structured query intent (IntentResponse) deterministically
    on a pandas DataFrame, resolving filters, groupings, and aggregations.
    """

    @staticmethod
    def execute_intent(
        intent: IntentResponse,
        df: pd.DataFrame,
        results: AnalyticsResult
    ) -> IntentExecution:
        import time
        start_time = time.perf_counter()
        logger.info(f"IntentExecutor: Executing action: {intent.action}")

        # 1. Handle KPI lookup
        if intent.action == "KPI_QUERY":
            kpi_name = intent.kpi_name or "Total Records"
            matching_kpi = None
            for key, kpi in results.kpis.items():
                if kpi.name.lower() == kpi_name.lower():
                    matching_kpi = kpi
                    break
            
            execution_time = (time.perf_counter() - start_time) * 1000.0
            if matching_kpi:
                summary = f"The KPI '{matching_kpi.name}' is calculated as {matching_kpi.value}."
                data = [{"KPI": matching_kpi.name, "Value": matching_kpi.value}]
                query_result = QueryResult(data=data, summary=summary, columns=["KPI", "Value"])
                return IntentExecution(
                    intent=intent,
                    query_result=query_result,
                    execution_time_ms=round(execution_time, 2),
                    success=True
                )
            else:
                return IntentExecution(
                    intent=intent,
                    query_result=QueryResult(data=[], summary=f"KPI '{kpi_name}' not found.", columns=[]),
                    execution_time_ms=round(execution_time, 2),
                    success=False,
                    error_message=f"KPI '{kpi_name}' was not found in planned results."
                )

        # 2. Handle explanation requests
        if intent.action in ["GENERAL_EXPLANATION", "UNKNOWN"]:
            execution_time = (time.perf_counter() - start_time) * 1000.0
            summary = "Query maps to general explanation or non-dataset request."
            query_result = QueryResult(data=[], summary=summary, columns=[])
            return IntentExecution(
                intent=intent,
                query_result=query_result,
                execution_time_ms=round(execution_time, 2),
                success=True
            )

        # 3. Handle data filtering & ranking operations (FILTER, GROUP, SORT, LIMIT, etc.)
        try:
            working_df = df.copy()

            # Apply filters
            for filt in intent.filters:
                col = filt.get("column")
                op = filt.get("operator", "equals")
                val = filt.get("value")
                
                if col not in working_df.columns:
                    continue
                working_df = IntentExecutor._apply_filter(working_df, col, op, val)

            total_filtered = len(working_df)

            # Apply grouping and aggregations
            if intent.group_by:
                if intent.group_by not in working_df.columns:
                    execution_time = (time.perf_counter() - start_time) * 1000.0
                    return IntentExecution(
                        intent=intent,
                        query_result=QueryResult(data=[], summary="Missing grouping column.", columns=[]),
                        execution_time_ms=round(execution_time, 2),
                        success=False,
                        error_message=f"Grouping column '{intent.group_by}' does not exist."
                    )

                agg_op = intent.aggregation or "count"
                
                # We aggregate by counting rows, or performing sum/average on target numeric columns
                # Let's find a valid numeric column if none is specified but metric requires numbers
                numeric_cols = working_df.select_dtypes(include=["number"]).columns
                target_col = numeric_cols[0] if len(numeric_cols) > 0 else working_df.columns[0]

                if agg_op == "count":
                    grouped = working_df.groupby(intent.group_by).size().reset_index(name="count")
                    metric_name = "count"
                elif agg_op == "average":
                    grouped = working_df.groupby(intent.group_by)[target_col].mean().reset_index(name="average")
                    metric_name = "average"
                elif agg_op == "sum":
                    grouped = working_df.groupby(intent.group_by)[target_col].sum().reset_index(name="sum")
                    metric_name = "sum"
                elif agg_op == "median":
                    grouped = working_df.groupby(intent.group_by)[target_col].median().reset_index(name="median")
                    metric_name = "median"
                elif agg_op == "min":
                    grouped = working_df.groupby(intent.group_by)[target_col].min().reset_index(name="min")
                    metric_name = "min"
                elif agg_op == "max":
                    grouped = working_df.groupby(intent.group_by)[target_col].max().reset_index(name="max")
                    metric_name = "max"
                elif agg_op == "distinct_count":
                    grouped = working_df.groupby(intent.group_by)[target_col].nunique().reset_index(name="distinct_count")
                    metric_name = "distinct_count"
                else:
                    grouped = working_df.groupby(intent.group_by).size().reset_index(name="count")
                    metric_name = "count"

                # Round float metric values
                grouped[metric_name] = grouped[metric_name].round(2)

                # Sorting
                ascending = (intent.sort == "ascending")
                grouped = grouped.sort_values(by=metric_name, ascending=ascending)

                # Limit
                if intent.limit:
                    grouped = grouped.head(intent.limit)

                data = grouped.to_dict(orient="records")
                columns = list(grouped.columns)
                summary = f"Grouped by '{intent.group_by}' returning {len(data)} groups out of {total_filtered} filtered records."
            else:
                # No grouping, return filtered rows (with limit and sort if applicable)
                if intent.limit:
                    working_df = working_df.head(intent.limit)

                # Convert datetime columns to strings
                for c in working_df.select_dtypes(include=["datetime64", "datetimetz"]).columns:
                    working_df[c] = working_df[c].dt.strftime("%Y-%m-%d %H:%M:%S")

                data = working_df.to_dict(orient="records")
                columns = list(working_df.columns)
                summary = f"Filtered dataset returning {len(data)} records."

            execution_time = (time.perf_counter() - start_time) * 1000.0
            query_result = QueryResult(data=data, summary=summary, columns=columns)
            
            return IntentExecution(
                intent=intent,
                query_result=query_result,
                execution_time_ms=round(execution_time, 2),
                success=True
            )

        except Exception as e:
            logger.error(f"IntentExecutor: Failure executing intent query: {e}")
            execution_time = (time.perf_counter() - start_time) * 1000.0
            return IntentExecution(
                intent=intent,
                query_result=QueryResult(data=[], summary="Failed to execute query.", columns=[]),
                execution_time_ms=round(execution_time, 2),
                success=False,
                error_message=str(e)
            )

    @staticmethod
    def _apply_filter(df: pd.DataFrame, col: str, op: str, val: Any) -> pd.DataFrame:
        """Parses and applies filters matching operators equals, greater_than, less_than, etc."""
        # Convert val to int/float if col is numeric and val is string
        if pd.api.types.is_numeric_dtype(df[col]) and isinstance(val, str):
            try:
                val = float(val) if '.' in val else int(val)
            except ValueError:
                pass

        if op == "greater_than":
            return df[df[col] > val]
        elif op == "less_than":
            return df[df[col] < val]
        elif op == "greater_than_or_equal":
            return df[df[col] >= val]
        elif op == "less_than_or_equal":
            return df[df[col] <= val]
        else:  # equals
            return df[df[col] == val]
