from functools import lru_cache
from fastapi import Depends
from app.dependencies.storage import get_storage_provider
from app.storage.interface import StorageInterface
from app.services.dataset_upload import DatasetUploadService
from app.repositories.profile_repository import ProfileRepository
from app.analytics.profiler import DatasetProfiler

from app.semantic.dictionary import SemanticDictionary
from app.semantic.knowledge_base import MedicalKnowledgeBase
from app.semantic.builder import SemanticModelBuilder
from app.semantic.validation import SemanticValidationService
from app.repositories.semantic_repository import SemanticModelRepository
from app.services.semantic_mapping import SemanticMappingService

from app.analytics.planner.builder import AnalyticsPlanBuilder
from app.repositories.plan_repository import AnalyticsPlanRepository
from app.services.analytics_planning import AnalyticsPlanningService

from app.analytics.executor.engine import ExecutionEngine
from app.repositories.result_repository import AnalyticsResultRepository
from app.services.analytics_execution import AnalyticsExecutionService

from app.repositories.visualization_repository import VisualizationRepository
from app.services.visualization_recommendation import VisualizationRecommendationService

from app.repositories.dashboard_repository import DashboardRepository
from app.services.dashboard_composition import DashboardCompositionService
from app.core.config import settings
from app.gemini import GeminiClientWrapper
from app.repositories.insight_repository import InsightRepository
from app.services.insight_generation import InsightGenerationService
from app.services.conversational_analytics import ConversationalAnalyticsService
from app.repositories.conversation_repository import ConversationRepository
from app.services.conversation_history import ConversationHistoryService


def get_dataset_upload_service(
    storage: StorageInterface = Depends(get_storage_provider)
) -> DatasetUploadService:
    """
    Dependency provider that instantiates and returns a DatasetUploadService.
    Injects the active storage provider interface.
    """
    return DatasetUploadService(storage=storage)


def get_profile_repository(
    storage: StorageInterface = Depends(get_storage_provider)
) -> ProfileRepository:
    """
    Dependency provider that returns a ProfileRepository instance.
    """
    return ProfileRepository(storage=storage)


def get_dataset_profiler(
    storage: StorageInterface = Depends(get_storage_provider)
) -> DatasetProfiler:
    """
    Dependency provider that returns a DatasetProfiler instance.
    """
    return DatasetProfiler(storage=storage)


@lru_cache()
def get_semantic_dictionary() -> SemanticDictionary:
    """Provides a singleton instance of SemanticDictionary."""
    return SemanticDictionary()


@lru_cache()
def get_medical_knowledge_base() -> MedicalKnowledgeBase:
    """Provides a singleton instance of MedicalKnowledgeBase."""
    return MedicalKnowledgeBase()


def get_semantic_model_repository(
    storage: StorageInterface = Depends(get_storage_provider)
) -> SemanticModelRepository:
    """Provides a SemanticModelRepository instance."""
    return SemanticModelRepository(storage=storage)


def get_semantic_mapping_service(
    dictionary: SemanticDictionary = Depends(get_semantic_dictionary),
    knowledge_base: MedicalKnowledgeBase = Depends(get_medical_knowledge_base),
    repository: SemanticModelRepository = Depends(get_semantic_model_repository),
    profile_repository: ProfileRepository = Depends(get_profile_repository)
) -> SemanticMappingService:
    """Provides a SemanticMappingService instance with all dependent components injected."""
    builder = SemanticModelBuilder(dictionary=dictionary, knowledge_base=knowledge_base)
    validator = SemanticValidationService()
    return SemanticMappingService(
        builder=builder,
        validator=validator,
        repository=repository,
        profile_repository=profile_repository
    )


def get_analytics_plan_builder() -> AnalyticsPlanBuilder:
    """Provides an AnalyticsPlanBuilder instance."""
    return AnalyticsPlanBuilder()


def get_analytics_plan_repository(
    storage: StorageInterface = Depends(get_storage_provider)
) -> AnalyticsPlanRepository:
    """Provides an AnalyticsPlanRepository instance."""
    return AnalyticsPlanRepository(storage=storage)


def get_analytics_planning_service(
    builder: AnalyticsPlanBuilder = Depends(get_analytics_plan_builder),
    repository: AnalyticsPlanRepository = Depends(get_analytics_plan_repository),
    profile_repository: ProfileRepository = Depends(get_profile_repository),
    semantic_repository: SemanticModelRepository = Depends(get_semantic_model_repository)
) -> AnalyticsPlanningService:
    """Provides an AnalyticsPlanningService instance with all dependencies injected."""
    return AnalyticsPlanningService(
        builder=builder,
        repository=repository,
        profile_repository=profile_repository,
        semantic_repository=semantic_repository
    )


def get_execution_engine() -> ExecutionEngine:
    """Provides an ExecutionEngine instance."""
    return ExecutionEngine()


def get_analytics_result_repository(
    storage: StorageInterface = Depends(get_storage_provider)
) -> AnalyticsResultRepository:
    """Provides an AnalyticsResultRepository instance."""
    return AnalyticsResultRepository(storage=storage)


def get_analytics_execution_service(
    engine: ExecutionEngine = Depends(get_execution_engine),
    repository: AnalyticsResultRepository = Depends(get_analytics_result_repository),
    profile_repository: ProfileRepository = Depends(get_profile_repository),
    semantic_repository: SemanticModelRepository = Depends(get_semantic_model_repository),
    plan_repository: AnalyticsPlanRepository = Depends(get_analytics_plan_repository),
    storage: StorageInterface = Depends(get_storage_provider)
) -> AnalyticsExecutionService:
    """Provides an AnalyticsExecutionService instance with all dependencies injected."""
    return AnalyticsExecutionService(
        engine=engine,
        repository=repository,
        profile_repository=profile_repository,
        semantic_repository=semantic_repository,
        plan_repository=plan_repository,
        storage=storage
    )


def get_visualization_repository(
    storage: StorageInterface = Depends(get_storage_provider)
) -> VisualizationRepository:
    """Provides a VisualizationRepository instance."""
    return VisualizationRepository(storage=storage)


def get_visualization_recommendation_service(
    repository: VisualizationRepository = Depends(get_visualization_repository),
    profile_repository: ProfileRepository = Depends(get_profile_repository),
    semantic_repository: SemanticModelRepository = Depends(get_semantic_model_repository),
    plan_repository: AnalyticsPlanRepository = Depends(get_analytics_plan_repository),
    result_repository: AnalyticsResultRepository = Depends(get_analytics_result_repository)
) -> VisualizationRecommendationService:
    """Provides a VisualizationRecommendationService instance with all dependencies injected."""
    return VisualizationRecommendationService(
        repository=repository,
        profile_repository=profile_repository,
        semantic_repository=semantic_repository,
        plan_repository=plan_repository,
        result_repository=result_repository
    )


def get_dashboard_repository(
    storage: StorageInterface = Depends(get_storage_provider)
) -> DashboardRepository:
    """Provides a DashboardRepository instance."""
    return DashboardRepository(storage=storage)


def get_dashboard_composition_service(
    repository: DashboardRepository = Depends(get_dashboard_repository),
    semantic_repository: SemanticModelRepository = Depends(get_semantic_model_repository),
    visualization_repository: VisualizationRepository = Depends(get_visualization_repository)
) -> DashboardCompositionService:
    """Provides a DashboardCompositionService instance with all dependencies injected."""
    return DashboardCompositionService(
        repository=repository,
        semantic_repository=semantic_repository,
        visualization_repository=visualization_repository
    )


def get_insight_repository(
    storage: StorageInterface = Depends(get_storage_provider)
) -> InsightRepository:
    """Provides an InsightRepository instance."""
    return InsightRepository(storage=storage)


@lru_cache()
def get_gemini_client_wrapper() -> GeminiClientWrapper:
    """Provides a singleton GeminiClientWrapper instance."""
    return GeminiClientWrapper(
        api_key=settings.GEMINI_API_KEY,
        default_model=settings.GEMINI_MODEL_NAME
    )


def get_insight_generation_service(
    repository: InsightRepository = Depends(get_insight_repository),
    result_repository: AnalyticsResultRepository = Depends(get_analytics_result_repository),
    client_wrapper: GeminiClientWrapper = Depends(get_gemini_client_wrapper)
) -> InsightGenerationService:
    """Provides an InsightGenerationService instance with all dependencies injected."""
    return InsightGenerationService(
        repository=repository,
        result_repository=result_repository,
        client_wrapper=client_wrapper
    )


def get_conversation_repository(
    storage: StorageInterface = Depends(get_storage_provider)
) -> ConversationRepository:
    """Provides a ConversationRepository instance."""
    return ConversationRepository(storage=storage)


def get_conversation_history_service(
    repository: ConversationRepository = Depends(get_conversation_repository)
) -> ConversationHistoryService:
    """Provides a ConversationHistoryService instance."""
    return ConversationHistoryService(repository=repository)


def get_conversational_analytics_service(
    semantic_repository: SemanticModelRepository = Depends(get_semantic_model_repository),
    plan_repository: AnalyticsPlanRepository = Depends(get_analytics_plan_repository),
    result_repository: AnalyticsResultRepository = Depends(get_analytics_result_repository),
    storage: StorageInterface = Depends(get_storage_provider),
    client_wrapper: GeminiClientWrapper = Depends(get_gemini_client_wrapper),
    history_service: ConversationHistoryService = Depends(get_conversation_history_service)
) -> ConversationalAnalyticsService:
    """Provides a ConversationalAnalyticsService instance with all dependencies injected."""
    return ConversationalAnalyticsService(
        semantic_repository=semantic_repository,
        plan_repository=plan_repository,
        result_repository=result_repository,
        storage=storage,
        client_wrapper=client_wrapper,
        history_service=history_service
    )
