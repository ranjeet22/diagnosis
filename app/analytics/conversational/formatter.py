from typing import Dict, Any, List
from app.schemas.conversation import IntentResponse, QueryResult


class ResponseFormatter:
    """
    Translates deterministic execution QueryResult structures into clean,
    frontend-ready UI layout definitions (tables, metric cards, chart configurations).
    """

    @staticmethod
    def format_response(
        intent: IntentResponse,
        result: QueryResult,
        execution_time_ms: float
    ) -> Dict[str, Any]:
        """
        Builds the formatted_response dictionary.
        """
        # Determine render type
        if intent.action == "KPI_QUERY":
            kpi_name = intent.kpi_name or "Total Records"
            kpi_value = result.data[0]["Value"] if result.data else 0
            return {
                "render_type": "metric_card",
                "title": kpi_name,
                "value": kpi_value,
                "subtext": result.summary,
                "metadata": {
                    "execution_time_ms": execution_time_ms,
                    "columns": result.columns
                }
            }

        if intent.group_by and result.data:
            # Format as chart dataset configuration
            labels = [str(row[intent.group_by]) for row in result.data]
            
            # Find the numeric/count metric key
            metric_key = None
            for key in result.data[0].keys():
                if key != intent.group_by:
                    metric_key = key
                    break
            
            values = [row[metric_key] for row in result.data] if metric_key else []
            
            chart_type = intent.visualization or "bar"
            return {
                "render_type": "chart_data",
                "chart_type": chart_type,
                "title": f"Caseload analysis by {intent.group_by}",
                "xAxis": {
                    "type": "category",
                    "data": labels
                },
                "yAxis": {
                    "type": "value"
                },
                "series": [
                    {
                        "name": metric_key or "volume",
                        "type": chart_type,
                        "data": values
                    }
                ],
                "metadata": {
                    "execution_time_ms": execution_time_ms,
                    "columns": result.columns
                }
            }

        # Default fallback to Table format
        headers = result.columns
        rows = [[row.get(h) for h in headers] for row in result.data]
        return {
            "render_type": "table",
            "headers": headers,
            "rows": rows,
            "total_rows": len(rows),
            "metadata": {
                "execution_time_ms": execution_time_ms,
                "columns": result.columns
            }
        }
