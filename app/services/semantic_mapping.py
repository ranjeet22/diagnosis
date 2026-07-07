from app.core.logging import logger
from app.core.exceptions import DatasetNotFound, AnalyticsError
from app.schemas.semantic import SemanticModel
from app.repositories.profile_repository import ProfileRepository
from app.repositories.semantic_repository import SemanticModelRepository
from app.semantic.builder import SemanticModelBuilder
from app.semantic.validation import SemanticValidationService


class SemanticMappingService:
    """
    Application service orchestrating the healthcare semantic mapping workflow.
    Loads previously computed Dataset Profiles, maps them to concepts, detects
    relationships, validates integrity, and persists the semantic model.
    """
    def __init__(
        self,
        builder: SemanticModelBuilder,
        validator: SemanticValidationService,
        repository: SemanticModelRepository,
        profile_repository: ProfileRepository
    ) -> None:
        self.builder = builder
        self.validator = validator
        self.repository = repository
        self.profile_repository = profile_repository

    async def generate_semantic_model(self, dataset_id: str) -> SemanticModel:
        """
        Orchestrates mapping generation: Profile Loading -> Mapping -> Validation -> Storage.
        """
        logger.info(f"Generating healthcare semantic model for dataset ID: {dataset_id}")
        
        # 1. Fetch previously generated Dataset Profile (Cache check)
        try:
            profile = await self.profile_repository.get_profile(dataset_id=dataset_id)
        except DatasetNotFound:
            logger.error(f"Cannot map dataset: Profile for '{dataset_id}' does not exist.")
            raise DatasetNotFound(
                f"Profile for dataset '{dataset_id}' could not be found. Please generate the profile first."
            )
        except Exception as e:
            raise AnalyticsError(f"Failed to load dataset profile: {e}")

        # 2. Build the semantic model (Deterministic mappings + relationships)
        try:
            model = self.builder.build_model(profile)
        except Exception as e:
            logger.error(f"Failed to build semantic model: {e}", exc_info=True)
            raise AnalyticsError(f"Failed to build semantic model: {e}")

        # 3. Validate semantic mappings (Log warnings)
        validation_flags = self.validator.validate_model(model)
        for flag in validation_flags:
            logger.warning(
                f"Semantic Validation Flag [{flag['issue_type']}] ({flag['severity']}): {flag['message']}"
            )
            
        # 4. Persist the semantic model JSON to disk
        try:
            await self.repository.save_model(dataset_id=dataset_id, model=model)
            logger.info(f"Persisted healthcare semantic model successfully for dataset {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to persist semantic model: {e}")
            raise AnalyticsError(f"Failed to persist semantic model document: {e}")

        return model
