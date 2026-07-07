from app.core.logging import logger
from app.core.exceptions import DatasetNotFound, AnalyticsError
from app.schemas.dashboard import DashboardConfiguration
from app.repositories.semantic_repository import SemanticModelRepository
from app.repositories.visualization_repository import VisualizationRepository
from app.repositories.dashboard_repository import DashboardRepository
from app.analytics.dashboard.builder import DashboardBuilder
from app.analytics.dashboard.validation import DashboardValidationService


class DashboardCompositionService:
    """
    Orchestration application service generating structured Dashboard Configurations.
    Combines ECharts visualization recommendations and ontology mappings,
    verifies configuration integrity, and persists layout definitions.
    """
    def __init__(self,
        repository: DashboardRepository,
        semantic_repository: SemanticModelRepository,
        visualization_repository: VisualizationRepository
    ) -> None:
        self.repository = repository
        self.semantic_repository = semantic_repository
        self.visualization_repository = visualization_repository

    async def compose_dashboard(self, dataset_id: str) -> DashboardConfiguration:
        logger.info(f"DashboardCompositionService: Generating dashboard config for dataset {dataset_id}")

        # 1. Fetch dependencies
        try:
            model = await self.semantic_repository.get_model(dataset_id=dataset_id)
            vis_plan = await self.visualization_repository.get_plan(dataset_id=dataset_id)
        except DatasetNotFound as e:
            raise DatasetNotFound(f"Cannot compose dashboard: {e}")
        except Exception as e:
            raise AnalyticsError(f"Failed to load dependencies for dashboard composition: {e}")

        # 2. Compose Dashboard
        try:
            dashboard = DashboardBuilder.compose_dashboard(
                vis_plan=vis_plan,
                semantic_model=model
            )
        except Exception as e:
            logger.error(f"Dashboard Builder failed during composition: {e}")
            raise AnalyticsError(f"Dashboard composition process failed: {e}")

        # 3. Validate Dashboard Configuration
        logs, is_valid = DashboardValidationService.validate_dashboard(
            dashboard=dashboard,
            vis_plan=vis_plan
        )

        config = DashboardConfiguration(
            dashboard=dashboard,
            validation_logs=logs,
            is_valid=is_valid
        )

        # 4. Save to Storage
        try:
            await self.repository.save_dashboard(dataset_id=dataset_id, dashboard=config)
            logger.info(f"DashboardCompositionService: Saved config successfully for dataset {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write dashboard configuration json: {e}")
            raise AnalyticsError(f"Failed to persist dashboard config: {e}")

        return config
