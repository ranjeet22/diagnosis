from datetime import datetime, timezone
from typing import Dict, List, Any
from app.core.logging import logger
from app.core.exceptions import DatasetNotFound, AnalyticsError
from app.schemas.visualization import (
    VisualizationPlan,
    VisualizationRecommendation,
    ChartConfiguration,
    AxisConfiguration,
    LegendConfiguration,
    TooltipConfiguration
)
from app.repositories.profile_repository import ProfileRepository
from app.repositories.semantic_repository import SemanticModelRepository
from app.repositories.plan_repository import AnalyticsPlanRepository
from app.repositories.result_repository import AnalyticsResultRepository
from app.repositories.visualization_repository import VisualizationRepository
from app.analytics.visualization.theme import ThemeEngine
from app.analytics.visualization.rules import VisualizationRuleEngine
from app.analytics.visualization.layout import LayoutRecommendationEngine
from app.analytics.visualization.interaction import InteractionPlanner
from app.analytics.visualization.accessibility import AccessibilityPlanner
from app.analytics.visualization.chart import ChartRecommendationEngine


class VisualizationRecommendationService:
    """
    Orchestration application service generating structured visualization plans.
    Translates raw analytics results into complete ECharts components layouts.
    """
    def __init__(self,
        repository: VisualizationRepository,
        profile_repository: ProfileRepository,
        semantic_repository: SemanticModelRepository,
        plan_repository: AnalyticsPlanRepository,
        result_repository: AnalyticsResultRepository
    ) -> None:
        self.repository = repository
        self.profile_repository = profile_repository
        self.semantic_repository = semantic_repository
        self.plan_repository = plan_repository
        self.result_repository = result_repository

    async def generate_visualization_plan(
        self, 
        dataset_id: str,
        theme_name: str = "light",
        accessibility_mode: str = "default"
    ) -> VisualizationPlan:
        logger.info(f"VisualizationRecommendationService: Generating plan for dataset {dataset_id}")

        # 1. Fetch dependencies
        try:
            profile = await self.profile_repository.get_profile(dataset_id=dataset_id)
            model = await self.semantic_repository.get_model(dataset_id=dataset_id)
            plan = await self.plan_repository.get_plan(dataset_id=dataset_id)
            results = await self.result_repository.get_results(dataset_id=dataset_id)
        except DatasetNotFound as e:
            raise DatasetNotFound(f"Cannot generate visualization plan: {e}")
        except Exception as e:
            raise AnalyticsError(f"Failed to load dependencies for visualization planning: {e}")

        # 2. Build Theme Configuration
        theme_conf = ThemeEngine.create_theme_configuration(theme_name, accessibility_mode)

        # Map task_id/kpi_name to section name
        node_sections: Dict[str, str] = {}
        for sec in plan.dashboard_sections:
            for kpi in sec.kpis:
                node_sections[kpi] = sec.section_name
            for t in sec.tasks:
                node_sections[t] = sec.section_name

        recommendations: Dict[str, VisualizationRecommendation] = {}

        # 3. Process overview KPI metrics
        display_order = 0
        for planned_kpi in plan.kpis:
            kpi_name = planned_kpi.name
            result_kpi = results.kpis.get(kpi_name)
            
            val = result_kpi.value if result_kpi else None
            
            layout = LayoutRecommendationEngine.recommend_layout(
                chart_id=kpi_name,
                is_kpi=True,
                priority=90.0 if planned_kpi.priority == "high" else 60.0,
                section=node_sections.get(kpi_name, planned_kpi.dashboard_placement),
                display_order=display_order
            )
            
            access = AccessibilityPlanner.plan_accessibility(
                chart_id=kpi_name,
                name=kpi_name,
                chart_type="card",
                result_data=val
            )
            
            chart_config = ChartConfiguration(
                chart_type="card",
                legend=LegendConfiguration(position="bottom", visible=False, labels=[]),
                tooltip=TooltipConfiguration(trigger="none", format="", displayed_metrics=[], precision=2)
            )
            
            recommendations[kpi_name] = VisualizationRecommendation(
                chart_id=kpi_name,
                name=kpi_name,
                description=planned_kpi.description,
                chart_config=chart_config,
                layout=layout,
                interaction=InteractionPlanner.plan_interactions("card"),
                accessibility=access,
                filters=[],
                confidence_score=1.0,
                readability_score=1.0,
                business_value_score=1.0,
                complexity_score=0.0,
                accessibility_score=1.0
            )
            display_order += 1

        # Find categorical columns for filtering candidates
        filter_candidates = [
            col_name for col_name, col in model.columns.items()
            if col.semantic_type in {"GENDER", "HOSPITAL", "OUTCOME", "SEVERITY", "LOCATION"}
        ]

        # 4. Process Planned Analysis Tasks
        task_order = 0
        for task in plan.analysis_tasks:
            tid = task.task_id
            name = task.name
            cols = task.required_columns

            result_data = None
            unique_cnt = 0
            
            # Retrieve computed results values
            if tid in results.distributions:
                dist = results.distributions[tid]
                result_data = dist.model_dump()
                unique_cnt = len(dist.labels)
            elif tid in results.trends:
                trend = results.trends[tid]
                result_data = trend.model_dump()
            elif tid in results.comparisons:
                comp = results.comparisons[tid]
                result_data = comp.data
            else:
                # General fallback lookup in aggregations list
                agg = next((a for a in results.aggregations if a.column in cols), None)
                if agg:
                    result_data = agg.value

            # If result data is missing or empty, skip recommendation
            if result_data is None:
                continue

            # Deterministic Chart Selection
            chart_type = VisualizationRuleEngine.recommend_chart_type(
                task_id=tid,
                cols=cols,
                cols_profiles=profile.columns,
                unique_count=unique_cnt,
                planned_family=task.visualization.chart_family if task.visualization else None
            )

            # Responsive Layout Recommendations
            layout = LayoutRecommendationEngine.recommend_layout(
                chart_id=tid,
                is_kpi=False,
                priority=float(task.priority_score),
                section=node_sections.get(tid, "Overview"),
                display_order=task_order
            )

            # Accessibility Alt Text Generator
            access = AccessibilityPlanner.plan_accessibility(
                chart_id=tid,
                name=name,
                chart_type=chart_type,
                result_data=result_data
            )

            # Interactions
            interaction = InteractionPlanner.plan_interactions(chart_type=chart_type)

            # Chart Config (axis formatting, legends, tooltips)
            chart_config = ChartRecommendationEngine.build_chart_configuration(
                chart_type=chart_type,
                task_id=tid,
                cols=cols,
                result_data=result_data
            )

            # Filters recommendations
            # Charts are affected by any filter column present in the dataset except their own mapped columns
            linked_filters = [f for f in filter_candidates if f not in cols]

            # Quality Scoring Metrics
            readability = 0.95 if chart_type in {"pie", "line"} else 0.90
            bv = 0.90 if task.business_value == "high" else (0.75 if task.business_value == "medium" else 0.50)
            complexity = 0.35 if chart_type in {"heatmap", "boxplot"} else 0.15

            rec = VisualizationRecommendation(
                chart_id=tid,
                name=name,
                description=task.description,
                chart_config=chart_config,
                layout=layout,
                interaction=interaction,
                accessibility=access,
                filters=linked_filters,
                confidence_score=float(task.confidence),
                readability_score=readability,
                business_value_score=bv,
                complexity_score=complexity,
                accessibility_score=0.98
            )

            recommendations[tid] = rec
            task_order += 1

        # 5. Build Visualization Plan
        vis_plan = VisualizationPlan(
            dataset_id=dataset_id,
            theme=theme_conf,
            recommendations=recommendations,
            created_at=datetime.now(timezone.utc)
        )

        # Save to storage
        try:
            await self.repository.save_plan(dataset_id=dataset_id, plan=vis_plan)
            logger.info(f"VisualizationRecommendationService: Saved plan successfully for dataset {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write visualization plan json: {e}")
            raise AnalyticsError(f"Failed to persist visualization plan: {e}")

        return vis_plan
