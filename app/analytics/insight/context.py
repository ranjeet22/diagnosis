from typing import Dict, Any, List
from app.schemas.results import AnalyticsResult
from app.schemas.insight import InsightContext


class InsightContextBuilder:
    """
    Summarization layer that extracts key analytics parameters from AnalyticsResult
    and formats a highly compressed payload (InsightContext) to minimize token consumption.
    """

    @staticmethod
    def build_context(results: AnalyticsResult) -> InsightContext:
        """
        Transforms raw AnalyticsResult into a compact, token-optimized InsightContext.
        """
        # 1. Compress KPIs: name -> value (exclude formula & execution logs)
        compressed_kpis = {}
        for kpi_key, kpi in results.kpis.items():
            compressed_kpis[kpi.name] = kpi.value

        # 2. Compress Distributions: task_id -> {label: (count, percentage)}
        compressed_dists = {}
        for dist_key, dist in results.distributions.items():
            # Only keep counts and percentages map
            compressed_dists[dist.task_id] = {
                label: (count, round(pct, 2))
                for label, count, pct in zip(dist.labels, dist.counts, dist.percentages)
            }

        # 3. Compress Trends: Summarize long timelines to prevent token bloat
        compressed_trends = {}
        for trend_key, trend in results.trends.items():
            # If timestamps list is long, summarize it to top details
            total_intervals = len(trend.timestamps)
            max_idx = trend.counts.index(max(trend.counts)) if trend.counts else 0
            min_idx = trend.counts.index(min(trend.counts)) if trend.counts else 0

            summary = {
                "total_intervals": total_intervals,
                "overall_sum": sum(trend.counts) if trend.counts else 0,
                "average_per_interval": round(sum(trend.counts) / total_intervals, 2) if total_intervals > 0 else 0,
                "peak_interval": {
                    "timestamp": trend.timestamps[max_idx] if trend.timestamps else None,
                    "count": trend.counts[max_idx] if trend.counts else 0
                },
                "trough_interval": {
                    "timestamp": trend.timestamps[min_idx] if trend.timestamps else None,
                    "count": trend.counts[min_idx] if trend.counts else 0
                },
                "seasonality": trend.seasonality_metadata
            }

            # Append first 3 and last 3 intervals to capture trajectory without sending hundreds of points
            if total_intervals > 6:
                summary["start_trajectory"] = [
                    {"date": trend.timestamps[i], "count": trend.counts[i]}
                    for i in range(3)
                ]
                summary["end_trajectory"] = [
                    {"date": trend.timestamps[i], "count": trend.counts[i]}
                    for i in range(total_intervals - 3, total_intervals)
                ]
            else:
                summary["full_trajectory"] = [
                    {"date": trend.timestamps[i], "count": trend.counts[i]}
                    for i in range(total_intervals)
                ]

            compressed_trends[trend.task_id] = summary

        # 4. Compress Comparisons: Keep only structured cross-tab values
        compressed_comps = {}
        for comp_key, comp in results.comparisons.items():
            # Avoid sending large nested formats, keep raw compact overview
            compressed_comps[comp.name] = {
                "columns": comp.columns,
                "type": comp.comparison_type,
                "summary": comp.data
            }

        # 5. Extract Data Quality and Aggregations
        aggregations_summary = []
        for agg in results.aggregations:
            aggregations_summary.append({
                "column": agg.column,
                "operation": agg.operation,
                "value": agg.value
            })

        correlations_summary = {}
        if results.correlations:
            correlations_summary = {
                "strong_positive": results.correlations.strong_positive,
                "strong_negative": results.correlations.strong_negative
            }

        quality_metrics = {
            "aggregations": aggregations_summary,
            "correlations": correlations_summary
        }

        return InsightContext(
            kpis=compressed_kpis,
            distributions=compressed_dists,
            trends=compressed_trends,
            comparisons=compressed_comps,
            quality_metrics=quality_metrics
        )
