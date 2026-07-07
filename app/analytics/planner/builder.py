from typing import List, Dict, Any, Tuple
from app.schemas.semantic import SemanticModel
from app.schemas.profile import DatasetProfile
from app.schemas.plan import (
    AnalyticsPlan,
    AnalysisTask,
    KPIPlan,
    DashboardSection,
    AggregationPlan,
    ComparisonPlan,
    FilterDefinition,
    ExecutionGraph
)
from app.analytics.planner.rules import AnalysisRuleEngine, ComparisonPlanner
from app.analytics.planner.kpis import KPIPlanner
from app.analytics.planner.visualizations import VisualizationPlanner
from app.analytics.planner.aggregations import AggregationPlanner
from app.analytics.planner.dashboard import DashboardPlanner, FilterPlanner


class AnalyticsPlanBuilder:
    """
    Orchestrates the entire analytics planning engine workflow, compiling sub-planners
    and generating the priority scores and the DAG execution graph.
    """

    def build_plan(self, dataset_id: str, profile: DatasetProfile, model: SemanticModel) -> AnalyticsPlan:
        # Instantiate rules-driven planners
        kpi_planner = KPIPlanner()
        rule_engine = AnalysisRuleEngine()
        comp_planner = ComparisonPlanner()
        vis_planner = VisualizationPlanner()

        # 1. Plan KPIs
        kpis = kpi_planner.plan_kpis(model=model, profile=profile)

        # 2. Plan raw analysis tasks
        raw_tasks = rule_engine.plan_analysis_tasks(model=model)

        # 3. Plan comparisons
        comparisons = comp_planner.plan_comparisons(model=model)

        # 4. Process AnalysisTasks with visualizations and priority scores
        processed_tasks: List[AnalysisTask] = []
        for rt in raw_tasks:
            tid = rt["task_id"]
            name = rt["name"]
            req_cols = rt["required_columns"]
            
            # Map average column confidence from semantic model
            conf = 1.0
            if req_cols:
                confs = [
                    model.columns[c].confidence_score 
                    for c in req_cols if c in model.columns
                ]
                conf = sum(confs) / len(confs) if confs else 1.0

            # Priority Engine calculations
            # BV weight: high=40, medium=25, low=10
            bv = rt["business_value"]
            bv_score = 40.0 if bv == "high" else (25.0 if bv == "medium" else 10.0)
            
            # Vis Importance weight: high=40, medium=25, low=10
            vi = rt["visualization_importance"]
            vi_score = 40.0 if vi == "high" else (25.0 if vi == "medium" else 10.0)
            
            # Cost Penalty: low=0, medium=5, high=10
            cost = rt["computation_cost"]
            cost_penalty = 0.0 if cost == "low" else (5.0 if cost == "medium" else 10.0)

            # Score = BV + VI + (Conf * 20.0) - Penalty (capped between 0 and 100)
            score = bv_score + vi_score + (conf * 20.0) - cost_penalty
            score = max(0.0, min(100.0, score))

            # Recommend visual
            vis = vis_planner.plan_task_visualization(
                task_id=tid, 
                name=name, 
                required_cols=req_cols
            )

            processed_tasks.append(AnalysisTask(
                task_id=tid,
                name=name,
                description=rt["description"],
                required_columns=req_cols,
                priority_score=round(score, 2),
                business_value=bv,
                visualization_importance=vi,
                computation_cost=cost,
                expected_runtime_ms=rt["expected_runtime_ms"],
                confidence=round(conf, 2),
                visualization=vis
            ))

        # Add comparisons as virtual tasks to processed_tasks list so they have visual recommendations and priority scores too
        for comp in comparisons:
            # Check confidence of columns
            confs = [
                model.columns[c].confidence_score 
                for c in comp.columns if c in model.columns
            ]
            conf = sum(confs) / len(confs) if confs else 1.0
            
            # Comparisons are high business value and visualization importance
            score = 40.0 + 40.0 + (conf * 20.0) - 5.0 # Medium computational cost penalty (5.0)
            score = max(0.0, min(100.0, score))

            vis = vis_planner.plan_comparison_visualization(
                name=comp.name,
                cols=comp.columns,
                comp_type=comp.comparison_type
            )

            # Insert virtual comparison task
            processed_tasks.append(AnalysisTask(
                task_id=comp.name,  # ID matches name
                name=comp.name,
                description=f"Performs comparative cross-tab analysis of {comp.columns[0]} vs {comp.columns[1]}.",
                required_columns=comp.columns,
                priority_score=round(score, 2),
                business_value="high",
                visualization_importance="high",
                computation_cost="medium",
                expected_runtime_ms=30,
                confidence=round(conf, 2),
                visualization=vis
            ))

        # 5. Plan Dashboard sections layout
        sections = DashboardPlanner.plan_dashboard_layout(
            kpis=kpis,
            tasks=processed_tasks,
            comparisons=comparisons
        )

        # 6. Plan filter recommendations
        filters = FilterPlanner.plan_filters(model=model)

        # 7. Plan Aggregations
        aggregations = AggregationPlanner.plan_aggregations(model=model)

        # 8. Plan Execution dependency graph
        exec_graph = self._build_execution_graph(kpis=kpis, tasks=processed_tasks)

        return AnalyticsPlan(
            dataset_id=dataset_id,
            kpis=kpis,
            dashboard_sections=sections,
            analysis_tasks=processed_tasks,
            aggregation_plans=aggregations,
            comparison_plans=comparisons,
            filter_recommendations=filters,
            execution_graph=exec_graph
        )

    def _build_execution_graph(self, kpis: List[KPIPlan], tasks: List[AnalysisTask]) -> ExecutionGraph:
        """
        Builds DAG execution graph showing task computation order.
        """
        nodes: List[str] = []
        edges: List[Tuple[str, str]] = []

        # Add all KPIs and Tasks as nodes
        for k in kpis:
            nodes.append(k.name)
        for t in tasks:
            nodes.append(t.task_id)

        # Helper set to search fast
        task_ids = {t.task_id for t in tasks}
        kpi_names = {k.name for k in kpis}

        # Rules for defining task-to-task directed dependency edges
        dependency_rules: List[Tuple[str, str]] = [
            # Child depends on Parent (Parent Task ID, Dependent Child Task ID)
            ("disease_frequency", "disease_distribution"),
            ("disease_distribution", "top_diseases"),
            ("disease_distribution", "disease_ranking"),
            ("disease_frequency", "disease_trend"),
            ("daily_admission_trend", "admission_moving_average"),
            ("monthly_admission_trend", "admission_growth_rate"),
            ("age_distribution", "age_histogram"),
            ("age_distribution", "age_groups"),
            ("age_distribution", "average_age"),
            ("age_distribution", "median_age"),
        ]

        for parent, child in dependency_rules:
            if parent in task_ids and child in task_ids:
                edges.append((parent, child))

        # Add KPI dependencies on primary tasks
        # E.g. KPI "Total Patients" depends on "Total Records" or patient id distinct count task
        kpi_dep_rules: List[Tuple[str, str]] = [
            # Task ID, KPI Name
            ("average_age", "Average Patient Age"),
            ("recovery_rate", "Recovery Rate"),
            ("mortality_rate", "Mortality Rate"),
            ("disease_distribution", "Most Common Diagnosis"),
            ("disease_distribution", "Unique Diagnoses"),
        ]

        for task, kpi in kpi_dep_rules:
            if task in task_ids and kpi in kpi_names:
                edges.append((task, kpi))

        return ExecutionGraph(
            nodes=nodes,
            edges=edges
        )
