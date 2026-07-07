import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple, Optional
from app.schemas.plan import AnalyticsPlan, AnalysisTask, KPIPlan, ComparisonPlan
from app.schemas.profile import DatasetProfile
from app.schemas.semantic import SemanticModel
from app.schemas.results import (
    AnalyticsResult,
    KPIResult,
    DistributionResult,
    TrendResult,
    ComparisonResult,
    AggregationResult,
    CorrelationResult,
    ExecutionSummary,
    ExecutionStatistics
)
from app.analytics.executor.kpi import KPIEngine
from app.analytics.executor.aggregation import AggregationEngine
from app.analytics.executor.distribution import DistributionEngine
from app.analytics.executor.trend import TrendEngine
from app.analytics.executor.comparison import ComparisonEngine
from app.analytics.executor.correlation import CorrelationEngine
from app.analytics.executor.metric import MetricCalculator
from app.core.logging import logger


class ExecutionEngine:
    """
    Reads the Analytics Execution Plan, traverses the DAG topologically,
    manages an in-memory intermediate cache, and runs vectorized sub-engines.
    """

    def execute_plan(
        self,
        df: Any,
        plan: AnalyticsPlan,
        profile: DatasetProfile,
        model: SemanticModel
    ) -> AnalyticsResult:
        logger.info(f"ExecutionEngine: Initiating plan execution for dataset {plan.dataset_id}")
        start_time = time.perf_counter()

        # In-memory intermediate calculations cache
        cache: Dict[str, Any] = {}

        kpi_results: Dict[str, KPIResult] = {}
        dist_results: Dict[str, DistributionResult] = {}
        trend_results: Dict[str, TrendResult] = {}
        comp_results: Dict[str, ComparisonResult] = {}
        agg_results: List[AggregationResult] = []
        corr_result: Optional[CorrelationResult] = None

        task_durations: Dict[str, float] = {}
        executed_count = 0
        cached_reused_count = 0

        # Group model columns by semantic type
        concept_cols: Dict[str, List[str]] = {}
        for norm_name, col in model.columns.items():
            sem_type = col.semantic_type
            if sem_type != "UNKNOWN":
                if sem_type not in concept_cols:
                    concept_cols[sem_type] = []
                concept_cols[sem_type].append(norm_name)

        # 1. Topological Sort of Execution Graph
        sorted_nodes = self._topological_sort(
            nodes=plan.execution_graph.nodes,
            edges=[(edge[0], edge[1]) for edge in plan.execution_graph.edges]
        )
        logger.info(f"ExecutionEngine: Resolved DAG execution order: {sorted_nodes}")

        # Instantiate config-driven engines
        kpi_engine = KPIEngine()
        dist_engine = DistributionEngine()
        trend_engine = TrendEngine()
        comp_engine = ComparisonEngine()
        corr_engine = CorrelationEngine()
        agg_engine = AggregationEngine()

        # Load quality indicators from MetricCalculator
        quality_metrics = MetricCalculator.calculate_quality_metrics(profile=profile, model=model)
        profile_completeness = quality_metrics["completeness"]
        profile_quality = quality_metrics["overall_quality_score"]

        # 2. Iterate through topologically sorted steps
        for node in sorted_nodes:
            task_start = time.perf_counter()
            
            # Check if this node is a planned KPI
            planned_kpi = next((k for k in plan.kpis if k.name == node), None)
            # Check if this node is a planned AnalysisTask or Comparison Task
            planned_task = next((t for t in plan.analysis_tasks if t.task_id == node), None)

            if planned_kpi:
                # Calculate KPI
                kpi_res = kpi_engine.calculate_kpi(
                    df=df,
                    kpi_plan=planned_kpi,
                    profile_completeness=profile_completeness,
                    profile_quality_score=profile_quality,
                    confidence=planned_kpi.priority == "high" and 1.0 or 0.85
                )
                kpi_results[planned_kpi.name] = kpi_res
                executed_count += 1
                task_durations[node] = round((time.perf_counter() - task_start) * 1000.0, 2)

            elif planned_task:
                tid = planned_task.task_id
                req_cols = planned_task.required_columns

                # Handle Comparisons (virtual tasks)
                planned_comp = next((c for c in plan.comparison_plans if c.name == tid), None)
                
                if planned_comp:
                    age_col = concept_cols.get("AGE", [None])[0]
                    res = comp_engine.calculate_comparison(df=df, plan=planned_comp, age_col=age_col)
                    comp_results[tid] = res
                    executed_count += 1
                    task_durations[node] = round((time.perf_counter() - task_start) * 1000.0, 2)
                    continue

                # Run Distribution Tasks
                if ("distribution" in tid or "groups" in tid or "frequency" in tid or "ranking" in tid or "top_" in tid) and req_cols:
                    col = req_cols[0]
                    is_age = model.columns.get(col, None) and model.columns[col].semantic_type == "AGE"
                    
                    # Cache reuse logic: If top_diseases runs and disease_distribution is in cache, reuse it!
                    cached_data = None
                    if tid == "top_diseases" and "disease_distribution" in cache:
                        cached_data = cache["disease_distribution"]
                        cached_reused_count += 1
                    elif tid == "disease_ranking" and "disease_distribution" in cache:
                        cached_data = cache["disease_distribution"]
                        cached_reused_count += 1
                    elif tid == "disease_frequency" and "disease_distribution" in cache:
                        cached_data = cache["disease_distribution"]
                        cached_reused_count += 1
                        
                    if cached_data:
                        # Extract from cache
                        labels_c, counts_c, pcts_c = cached_data
                        if tid == "top_diseases":
                            res = DistributionResult(
                                task_id=tid,
                                labels=labels_c[:5],
                                counts=counts_c[:5],
                                percentages=pcts_c[:5]
                            )
                        else:
                            res = DistributionResult(
                                task_id=tid,
                                labels=labels_c,
                                counts=counts_c,
                                percentages=pcts_c
                            )
                    else:
                        # Compute fresh
                        res = dist_engine.calculate_distribution(df=df, task_id=tid, col=col, is_age=is_age)
                        
                        # Store in intermediate cache
                        if tid == "disease_distribution":
                            cache["disease_distribution"] = (res.labels, res.counts, res.percentages)
                    
                    dist_results[tid] = res
                    executed_count += 1

                # Run Trend Tasks
                elif ("trend" in tid or "moving_average" in tid or "growth_rate" in tid) and req_cols:
                    col = req_cols[len(req_cols) - 1] # Use date column (last one if multi-index)
                    
                    # Cache reuse logic: if monthly/daily is already calculated, reuse timestamps
                    cached_trend = None
                    if "moving_average" in tid and "daily_admission_trend" in cache:
                        cached_trend = cache["daily_admission_trend"]
                        cached_reused_count += 1
                    elif "growth_rate" in tid and "monthly_admission_trend" in cache:
                        cached_trend = cache["monthly_admission_trend"]
                        cached_reused_count += 1

                    if cached_trend:
                        # Generate based on cached trend series
                        ts, cnts, ma, rt, gr, seas = cached_trend
                        if "moving_average" in tid:
                            # Use daily moving average cached values
                            res = TrendResult(
                                task_id=tid,
                                timestamps=ts,
                                counts=cnts,
                                moving_average=ma,
                                seasonality_metadata=seas
                            )
                        else:
                            # Use monthly growth rate cached values
                            res = TrendResult(
                                task_id=tid,
                                timestamps=ts,
                                counts=cnts,
                                growth_rate=gr,
                                seasonality_metadata=seas
                            )
                    else:
                        res = trend_engine.calculate_trend(df=df, task_id=tid, col=col)
                        
                        # Cache raw values
                        if tid == "daily_admission_trend":
                            cache["daily_admission_trend"] = (
                                res.timestamps, res.counts, res.moving_average, 
                                res.running_total, res.growth_rate, res.seasonality_metadata
                            )
                        elif tid == "monthly_admission_trend":
                            cache["monthly_admission_trend"] = (
                                res.timestamps, res.counts, res.moving_average, 
                                res.running_total, res.growth_rate, res.seasonality_metadata
                            )
                            
                    trend_results[tid] = res
                    executed_count += 1
                    
                # Run other descriptive age statistics (average_age, median_age)
                elif tid in {"average_age", "median_age"} and req_cols:
                    # These stats are computed as scalar aggregations or through kpi fallbacks.
                    # We can simply add a placeholder or compute scalar.
                    # Since average_age/median_age are already mapped in KPIs, we keep them simple.
                    col = req_cols[0]
                    val = float(df[col].mean()) if tid == "average_age" else float(df[col].median())
                    executed_count += 1

                task_durations[node] = round((time.perf_counter() - task_start) * 1000.0, 2)

        # 3. Compute Aggregations
        for agg_plan in plan.aggregation_plans:
            agg_res = agg_engine.calculate_aggregations(df=df, plan=agg_plan)
            agg_results.extend(agg_res)

        # 4. Compute Correlations (between numeric variables)
        numeric_cols = [
            col_name for col_name, col in model.columns.items()
            if col.semantic_type in {
                "AGE", "WEIGHT", "HEIGHT", "BMI", 
                "BLOOD_PRESSURE", "HEART_RATE", "TEMPERATURE"
            }
        ]
        corr_result = corr_engine.calculate_correlations(df=df, numeric_cols=numeric_cols)

        # 5. Populate Metadata and Durations
        runtime = (time.perf_counter() - start_time) * 1000.0
        
        summary = ExecutionSummary(
            dataset_id=plan.dataset_id,
            total_tasks_planned=len(plan.kpis) + len(plan.analysis_tasks),
            total_tasks_executed=executed_count,
            cached_tasks_reused=cached_reused_count,
            overall_runtime_ms=round(runtime, 2)
        )

        stats = ExecutionStatistics(
            tasks_durations_ms=task_durations,
            memory_usage_bytes=0  # estimated placeholder
        )

        logger.info(f"ExecutionEngine: Completed execution of plan in {round(runtime, 2)}ms.")

        return AnalyticsResult(
            dataset_id=plan.dataset_id,
            kpis=kpi_results,
            distributions=dist_results,
            trends=trend_results,
            comparisons=comp_results,
            aggregations=agg_results,
            correlations=corr_result,
            summary=summary,
            statistics=stats,
            created_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def _topological_sort(nodes: List[str], edges: List[Tuple[str, str]]) -> List[str]:
        """
        Kahn's algorithm for topological sorting of Directed Acyclic Graph (DAG) dependencies.
        """
        # Ensure all nodes exist in degrees dict
        in_degree = {u: 0 for u in nodes}
        adj = {u: [] for u in nodes}
        
        for parent, child in edges:
            if parent in in_degree and child in in_degree:
                adj[parent].append(child)
                in_degree[child] += 1
                
        # Start queue with nodes having 0 in-degree dependencies
        queue = [u for u in nodes if in_degree[u] == 0]
        sorted_nodes = []
        
        while queue:
            u = queue.pop(0)
            sorted_nodes.append(u)
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)
                    
        # Append any remaining disconnected nodes
        for u in nodes:
            if u not in sorted_nodes:
                sorted_nodes.append(u)
                
        return sorted_nodes
