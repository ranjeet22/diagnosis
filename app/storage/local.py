import os
import aiofiles
from app.core.config import settings
from app.core.exceptions import StorageFailure, DatasetNotFound
from app.core.logging import logger
from app.schemas.dataset import StorageResult, DatasetMetadata
from app.schemas.profile import DatasetProfile
from app.schemas.semantic import SemanticModel
from app.schemas.plan import AnalyticsPlan
from app.schemas.results import AnalyticsResult
from app.schemas.visualization import VisualizationPlan
from app.schemas.dashboard import DashboardConfiguration
from app.schemas.insight import InsightCollection
from app.schemas.conversation import Conversation
from app.storage.interface import StorageInterface


class LocalStorageProvider(StorageInterface):
    """
    Concrete implementation of StorageInterface that stores files and metadata
    on the local filesystem under the directory specified in configuration.
    """
    def __init__(self, upload_dir: str = None) -> None:
        self.upload_dir = upload_dir or settings.STORAGE_LOCAL_DIR
        # Ensure root upload directory exists
        if not os.path.exists(self.upload_dir):
            try:
                os.makedirs(self.upload_dir, exist_ok=True)
                logger.info(f"Created local storage upload directory at: {self.upload_dir}")
            except Exception as e:
                logger.critical(f"Failed to create upload directory {self.upload_dir}: {e}")
                raise StorageFailure(f"Failed to initialize local upload directory: {e}")

    def _get_dataset_dir(self, dataset_id: str) -> str:
        """Returns the subfolder path dedicated to a specific dataset ID."""
        return os.path.join(self.upload_dir, dataset_id)

    async def save_file(
        self, dataset_id: str, filename: str, content: bytes
    ) -> StorageResult:
        dataset_dir = self._get_dataset_dir(dataset_id)
        
        try:
            # Ensure dataset specific directory exists
            os.makedirs(dataset_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory {dataset_dir}: {e}")
            raise StorageFailure(f"Could not create storage directory for dataset {dataset_id}: {e}")
            
        file_path = os.path.join(dataset_dir, filename)
        
        try:
            # Write file content asynchronously
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)
            logger.debug(f"Successfully saved file {filename} for dataset {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise StorageFailure(f"Failed to write dataset file to disk: {e}")
            
        return StorageResult(
            dataset_id=dataset_id,
            stored_filename=filename,
            file_size=len(content),
            storage_path=os.path.abspath(file_path)
        )

    async def save_metadata(
        self, dataset_id: str, metadata: DatasetMetadata
    ) -> None:
        dataset_dir = self._get_dataset_dir(dataset_id)
        metadata_path = os.path.join(dataset_dir, "metadata.json")
        
        # Ensure folder exists
        os.makedirs(dataset_dir, exist_ok=True)
        
        try:
            # Write metadata json asynchronously
            async with aiofiles.open(metadata_path, "w", encoding="utf-8") as f:
                await f.write(metadata.model_dump_json(indent=2))
            logger.debug(f"Saved metadata json for dataset {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write metadata file {metadata_path}: {e}")
            raise StorageFailure(f"Failed to write dataset metadata to disk: {e}")

    async def get_metadata(self, dataset_id: str) -> DatasetMetadata:
        metadata_path = os.path.join(self._get_dataset_dir(dataset_id), "metadata.json")
        
        if not os.path.exists(metadata_path):
            raise DatasetNotFound(f"Metadata for dataset '{dataset_id}' could not be found.")
            
        try:
            async with aiofiles.open(metadata_path, "r", encoding="utf-8") as f:
                content = await f.write("") # placeholder or read? wait, reading
                # Let's fix this, we want to read!
                # async with aiofiles.open(metadata_path, "r") as f:
                #    content = await f.read()
        except Exception as e:
            # Wait, let's make sure it's read correctly! Let's do `await f.read()`
            pass
        # I will write the reading code correctly below.
        
        try:
            async with aiofiles.open(metadata_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return DatasetMetadata.model_validate_json(content)
        except Exception as e:
            logger.error(f"Failed to read/validate metadata file {metadata_path}: {e}")
            raise StorageFailure(f"Failed to read or parse dataset metadata: {e}")

    def get_file_path(self, dataset_id: str, filename: str) -> str:
        return os.path.abspath(os.path.join(self._get_dataset_dir(dataset_id), filename))

    async def save_profile(self, dataset_id: str, profile: DatasetProfile) -> None:
        dataset_dir = self._get_dataset_dir(dataset_id)
        profile_path = os.path.join(dataset_dir, "profile.json")
        os.makedirs(dataset_dir, exist_ok=True)
        try:
            async with aiofiles.open(profile_path, "w", encoding="utf-8") as f:
                await f.write(profile.model_dump_json(indent=2))
            logger.debug(f"Saved dataset profile json for {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write profile file {profile_path}: {e}")
            raise StorageFailure(f"Failed to write dataset profile to disk: {e}")

    async def get_profile(self, dataset_id: str) -> DatasetProfile:
        profile_path = os.path.join(self._get_dataset_dir(dataset_id), "profile.json")
        if not os.path.exists(profile_path):
            raise DatasetNotFound(f"Profile for dataset '{dataset_id}' could not be found.")
        try:
            async with aiofiles.open(profile_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return DatasetProfile.model_validate_json(content)
        except Exception as e:
            logger.error(f"Failed to read/validate profile file {profile_path}: {e}")
            raise StorageFailure(f"Failed to read or parse dataset profile: {e}")

    async def save_semantic_model(self, dataset_id: str, model: SemanticModel) -> None:
        dataset_dir = self._get_dataset_dir(dataset_id)
        model_path = os.path.join(dataset_dir, "semantic_model.json")
        os.makedirs(dataset_dir, exist_ok=True)
        try:
            async with aiofiles.open(model_path, "w", encoding="utf-8") as f:
                await f.write(model.model_dump_json(indent=2))
            logger.debug(f"Saved dataset semantic model json for {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write semantic model file {model_path}: {e}")
            raise StorageFailure(f"Failed to write dataset semantic model to disk: {e}")

    async def get_semantic_model(self, dataset_id: str) -> SemanticModel:
        model_path = os.path.join(self._get_dataset_dir(dataset_id), "semantic_model.json")
        if not os.path.exists(model_path):
            raise DatasetNotFound(f"Semantic model for dataset '{dataset_id}' could not be found.")
        try:
            async with aiofiles.open(model_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return SemanticModel.model_validate_json(content)
        except Exception as e:
            logger.error(f"Failed to read/validate semantic model file {model_path}: {e}")
            raise StorageFailure(f"Failed to read or parse dataset semantic model: {e}")

    async def save_analytics_plan(self, dataset_id: str, plan: AnalyticsPlan) -> None:
        dataset_dir = self._get_dataset_dir(dataset_id)
        plan_path = os.path.join(dataset_dir, "analytics_plan.json")
        os.makedirs(dataset_dir, exist_ok=True)
        try:
            async with aiofiles.open(plan_path, "w", encoding="utf-8") as f:
                await f.write(plan.model_dump_json(indent=2))
            logger.debug(f"Saved dataset analytics plan json for {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write analytics plan file {plan_path}: {e}")
            raise StorageFailure(f"Failed to write dataset analytics plan to disk: {e}")

    async def get_analytics_plan(self, dataset_id: str) -> AnalyticsPlan:
        plan_path = os.path.join(self._get_dataset_dir(dataset_id), "analytics_plan.json")
        if not os.path.exists(plan_path):
            raise DatasetNotFound(f"Analytics plan for dataset '{dataset_id}' could not be found.")
        try:
            async with aiofiles.open(plan_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return AnalyticsPlan.model_validate_json(content)
        except Exception as e:
            logger.error(f"Failed to read/validate analytics plan file {plan_path}: {e}")
            raise StorageFailure(f"Failed to read or parse dataset analytics plan: {e}")

    async def save_analytics_results(self, dataset_id: str, results: AnalyticsResult) -> None:
        dataset_dir = self._get_dataset_dir(dataset_id)
        results_path = os.path.join(dataset_dir, "analytics_results.json")
        os.makedirs(dataset_dir, exist_ok=True)
        try:
            async with aiofiles.open(results_path, "w", encoding="utf-8") as f:
                await f.write(results.model_dump_json(indent=2))
            logger.debug(f"Saved dataset analytics results json for {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write analytics results file {results_path}: {e}")
            raise StorageFailure(f"Failed to write dataset analytics results to disk: {e}")

    async def get_analytics_results(self, dataset_id: str) -> AnalyticsResult:
        results_path = os.path.join(self._get_dataset_dir(dataset_id), "analytics_results.json")
        if not os.path.exists(results_path):
            raise DatasetNotFound(f"Analytics results for dataset '{dataset_id}' could not be found.")
        try:
            async with aiofiles.open(results_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return AnalyticsResult.model_validate_json(content)
        except Exception as e:
            logger.error(f"Failed to read/validate analytics results file {results_path}: {e}")
            raise StorageFailure(f"Failed to read or parse dataset analytics results: {e}")

    async def save_visualization_plan(self, dataset_id: str, plan: VisualizationPlan) -> None:
        dataset_dir = self._get_dataset_dir(dataset_id)
        plan_path = os.path.join(dataset_dir, "visualization_plan.json")
        os.makedirs(dataset_dir, exist_ok=True)
        try:
            async with aiofiles.open(plan_path, "w", encoding="utf-8") as f:
                await f.write(plan.model_dump_json(indent=2))
            logger.debug(f"Saved dataset visualization plan json for {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write visualization plan file {plan_path}: {e}")
            raise StorageFailure(f"Failed to write dataset visualization plan to disk: {e}")

    async def get_visualization_plan(self, dataset_id: str) -> VisualizationPlan:
        plan_path = os.path.join(self._get_dataset_dir(dataset_id), "visualization_plan.json")
        if not os.path.exists(plan_path):
            raise DatasetNotFound(f"Visualization plan for dataset '{dataset_id}' could not be found.")
        try:
            async with aiofiles.open(plan_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return VisualizationPlan.model_validate_json(content)
        except Exception as e:
            logger.error(f"Failed to read/validate visualization plan file {plan_path}: {e}")
            raise StorageFailure(f"Failed to read or parse dataset visualization plan: {e}")

    async def save_dashboard(self, dataset_id: str, dashboard: DashboardConfiguration) -> None:
        dataset_dir = self._get_dataset_dir(dataset_id)
        dash_path = os.path.join(dataset_dir, "dashboard.json")
        os.makedirs(dataset_dir, exist_ok=True)
        try:
            async with aiofiles.open(dash_path, "w", encoding="utf-8") as f:
                await f.write(dashboard.model_dump_json(indent=2))
            logger.debug(f"Saved dataset dashboard config json for {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write dashboard configuration file {dash_path}: {e}")
            raise StorageFailure(f"Failed to write dataset dashboard to disk: {e}")

    async def get_dashboard(self, dataset_id: str) -> DashboardConfiguration:
        dash_path = os.path.join(self._get_dataset_dir(dataset_id), "dashboard.json")
        if not os.path.exists(dash_path):
            raise DatasetNotFound(f"Dashboard configuration for dataset '{dataset_id}' could not be found.")
        try:
            async with aiofiles.open(dash_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return DashboardConfiguration.model_validate_json(content)
        except Exception as e:
            logger.error(f"Failed to read/validate dashboard configuration file {dash_path}: {e}")
            raise StorageFailure(f"Failed to read or parse dataset dashboard: {e}")

    async def save_insights(self, dataset_id: str, insights: InsightCollection) -> None:
        dataset_dir = self._get_dataset_dir(dataset_id)
        ins_path = os.path.join(dataset_dir, "insights.json")
        os.makedirs(dataset_dir, exist_ok=True)
        try:
            async with aiofiles.open(ins_path, "w", encoding="utf-8") as f:
                await f.write(insights.model_dump_json(indent=2))
            logger.debug(f"Saved dataset AI insights json for {dataset_id}")
        except Exception as e:
            logger.error(f"Failed to write AI insights file {ins_path}: {e}")
            raise StorageFailure(f"Failed to write dataset AI insights to disk: {e}")

    async def get_insights(self, dataset_id: str) -> InsightCollection:
        ins_path = os.path.join(self._get_dataset_dir(dataset_id), "insights.json")
        if not os.path.exists(ins_path):
            raise DatasetNotFound(f"AI insights for dataset '{dataset_id}' could not be found.")
        try:
            async with aiofiles.open(ins_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return InsightCollection.model_validate_json(content)
        except Exception as e:
            logger.error(f"Failed to read/validate AI insights file {ins_path}: {e}")
            raise StorageFailure(f"Failed to read or parse dataset AI insights: {e}")

    async def save_conversation(self, dataset_id: str, conversation: Conversation) -> None:
        dataset_dir = self._get_dataset_dir(dataset_id)
        conv_dir = os.path.join(dataset_dir, "conversations")
        os.makedirs(conv_dir, exist_ok=True)
        conv_path = os.path.join(conv_dir, f"{conversation.conversation_id}.json")
        try:
            async with aiofiles.open(conv_path, "w", encoding="utf-8") as f:
                await f.write(conversation.model_dump_json(indent=2))
            logger.debug(f"Saved dataset conversation json for {conversation.conversation_id}")
        except Exception as e:
            logger.error(f"Failed to write conversation file {conv_path}: {e}")
            raise StorageFailure(f"Failed to write dataset conversation to disk: {e}")

    async def get_conversation(self, dataset_id: str, conversation_id: str) -> Conversation:
        conv_path = os.path.join(self._get_dataset_dir(dataset_id), "conversations", f"{conversation_id}.json")
        if not os.path.exists(conv_path):
            raise DatasetNotFound(f"Conversation '{conversation_id}' for dataset '{dataset_id}' could not be found.")
        try:
            async with aiofiles.open(conv_path, "r", encoding="utf-8") as f:
                content = await f.read()
            return Conversation.model_validate_json(content)
        except Exception as e:
            logger.error(f"Failed to read/validate conversation file {conv_path}: {e}")
            raise StorageFailure(f"Failed to read or parse dataset conversation: {e}")
