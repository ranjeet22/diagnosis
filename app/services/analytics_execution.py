from app.core.logging import logger
from app.core.exceptions import DatasetNotFound, AnalyticsError
from app.schemas.results import AnalyticsResult
from app.repositories.profile_repository import ProfileRepository
from app.repositories.semantic_repository import SemanticModelRepository
from app.repositories.plan_repository import AnalyticsPlanRepository
from app.repositories.result_repository import AnalyticsResultRepository
from app.analytics.executor.engine import ExecutionEngine
from app.analytics.dataframe_provider import load_dataset_df
from app.storage.interface import StorageInterface


class AnalyticsExecutionService:
    """
    Application service orchestrating the Analytics Execution Pipeline.
    Loads dataset metadata, profile, semantic mappings, and execution plans,
    reads raw data into cuDF/Pandas, executes calculations, and persists results.
    """
    def __init__(
        self,
        engine: ExecutionEngine,
        repository: AnalyticsResultRepository,
        profile_repository: ProfileRepository,
        semantic_repository: SemanticModelRepository,
        plan_repository: AnalyticsPlanRepository,
        storage: StorageInterface
    ) -> None:
        self.engine = engine
        self.repository = repository
        self.profile_repository = profile_repository
        self.semantic_repository = semantic_repository
        self.plan_repository = plan_repository
        self.storage = storage

    async def execute_analytics(self, dataset_id: str) -> AnalyticsResult:
        """
        Coordinates full planning execution, caching, and persistence.
        """
        logger.info(f"AnalyticsExecutionService: Initiating execution for dataset ID: {dataset_id}")

        # 1. Fetch Plan
        try:
            plan = await self.plan_repository.get_plan(dataset_id=dataset_id)
        except DatasetNotFound:
            logger.error(f"Cannot execute plan: Analytics plan for '{dataset_id}' not found.")
            raise DatasetNotFound(
                f"Analytics plan for dataset '{dataset_id}' not found. Please generate the plan first."
            )
        except Exception as e:
            raise AnalyticsError(f"Failed to load dataset analytics plan: {e}")

        # 2. Fetch Profile
        try:
            profile = await self.profile_repository.get_profile(dataset_id=dataset_id)
        except Exception as e:
            raise AnalyticsError(f"Failed to load dataset profile: {e}")

        # 3. Fetch Semantic Model
        try:
            model = await self.semantic_repository.get_model(dataset_id=dataset_id)
        except Exception as e:
            raise AnalyticsError(f"Failed to load semantic model: {e}")

        # 4. Fetch Metadata and Load Dataframe
        try:
            metadata = await self.storage.get_metadata(dataset_id=dataset_id)
            file_path = self.storage.get_file_path(dataset_id=dataset_id, filename="original.csv")
            
            # Load dataset via cuDF / Pandas Fallback
            df = load_dataset_df(
                file_path=file_path,
                delimiter=metadata.delimiter,
                encoding=metadata.encoding
            )

            # Normalize and rename DataFrame column headers to match semantic/plan schema names
            from app.analytics.profiler import normalize_column_name
            normalized_cols = []
            seen_normalized_names = {}
            for pos, col in enumerate(df.columns):
                norm = normalize_column_name(col)
                if not norm:
                    norm = f"column_{pos}"
                if norm in seen_normalized_names:
                    seen_normalized_names[norm] += 1
                    norm = f"{norm}_{seen_normalized_names[norm]}"
                else:
                    seen_normalized_names[norm] = 0
                normalized_cols.append(norm)
            df.columns = normalized_cols

        except Exception as e:
            logger.error(f"Failed to load dataset DataFrame: {e}")
            raise AnalyticsError(f"Failed to load dataset raw data: {e}")

        # 5. Run Execution Engine
        try:
            results = self.engine.execute_plan(
                df=df,
                plan=plan,
                profile=profile,
                model=model
            )
        except Exception as e:
            logger.error(f"Failed to execute analytics tasks: {e}", exc_info=True)
            raise AnalyticsError(f"Failed to execute planned analytics tasks: {e}")

        # 6. Save results to disk
        try:
            await self.repository.save_results(dataset_id=dataset_id, results=results)
            logger.info(f"Persisted analytics results successfully for dataset {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to save analytics results: {e}")
            raise AnalyticsError(f"Failed to save computed analytics results: {e}")

        return results
