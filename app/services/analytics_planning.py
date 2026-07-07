from app.core.logging import logger
from app.core.exceptions import DatasetNotFound, AnalyticsError
from app.schemas.plan import AnalyticsPlan
from app.repositories.profile_repository import ProfileRepository
from app.repositories.semantic_repository import SemanticModelRepository
from app.repositories.plan_repository import AnalyticsPlanRepository
from app.analytics.planner.builder import AnalyticsPlanBuilder


class AnalyticsPlanningService:
    """
    Application service that coordinates the Analytics Planning Pipeline.
    Loads profile and semantic data, executes the deterministic rule engine planners,
    builds the execution graph, and caches the resulting plan.
    """
    def __init__(
        self,
        builder: AnalyticsPlanBuilder,
        repository: AnalyticsPlanRepository,
        profile_repository: ProfileRepository,
        semantic_repository: SemanticModelRepository
    ) -> None:
        self.builder = builder
        self.repository = repository
        self.profile_repository = profile_repository
        self.semantic_repository = semantic_repository

    async def generate_plan(self, dataset_id: str) -> AnalyticsPlan:
        """
        Loads the required source profiles, runs the planners, and saves the resulting plan.
        """
        logger.info(f"Generating analytics execution plan for dataset ID: {dataset_id}")

        # 1. Fetch Profile
        try:
            profile = await self.profile_repository.get_profile(dataset_id=dataset_id)
        except DatasetNotFound:
            logger.error(f"Cannot generate plan: Dataset profile '{dataset_id}' not found.")
            raise DatasetNotFound(
                f"Profile for dataset '{dataset_id}' not found. Please profile the dataset first."
            )
        except Exception as e:
            raise AnalyticsError(f"Failed to load dataset profile: {e}")

        # 2. Fetch Semantic Model
        try:
            model = await self.semantic_repository.get_model(dataset_id=dataset_id)
        except DatasetNotFound:
            logger.error(f"Cannot generate plan: Healthcare semantic model for '{dataset_id}' not found.")
            raise DatasetNotFound(
                f"Healthcare semantic model for dataset '{dataset_id}' not found. Please map the semantic model first."
            )
        except Exception as e:
            raise AnalyticsError(f"Failed to load semantic model: {e}")

        # 3. Build the plan
        try:
            plan = self.builder.build_plan(dataset_id=dataset_id, profile=profile, model=model)
        except Exception as e:
            logger.error(f"Failed to build analytics plan: {e}", exc_info=True)
            raise AnalyticsError(f"Failed to build analytics execution plan: {e}")

        # 4. Save to storage
        try:
            await self.repository.save_plan(dataset_id=dataset_id, plan=plan)
            logger.info(f"Persisted analytics execution plan successfully for dataset {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to save analytics plan: {e}")
            raise AnalyticsError(f"Failed to save analytics plan document: {e}")

        return plan
