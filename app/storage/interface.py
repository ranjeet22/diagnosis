from abc import ABC, abstractmethod
from app.schemas.dataset import StorageResult, DatasetMetadata
from app.schemas.profile import DatasetProfile
from app.schemas.semantic import SemanticModel
from app.schemas.plan import AnalyticsPlan
from app.schemas.results import AnalyticsResult
from app.schemas.visualization import VisualizationPlan
from app.schemas.dashboard import DashboardConfiguration
from app.schemas.insight import InsightCollection
from app.schemas.conversation import Conversation


class StorageInterface(ABC):
    """
    Abstract interface defining standard methods for reading and writing files
    and metadata in the Diagnōsis platform. Enables hot-swapping local storage
    for cloud providers (e.g. GCS, AWS S3) without affecting business logic.
    """

    @abstractmethod
    async def save_file(
        self, dataset_id: str, filename: str, content: bytes
    ) -> StorageResult:
        """
        Saves a raw uploaded dataset file to the storage provider.
        
        Args:
            dataset_id: The UUID of the dataset.
            filename: The target filename (e.g. original.csv).
            content: The file content in bytes.
            
        Returns:
            StorageResult object mapping where the file is stored.
            
        Raises:
            StorageFailure: If saving the file fails due to permissions or missing volumes.
        """
        pass

    @abstractmethod
    async def save_metadata(
        self, dataset_id: str, metadata: DatasetMetadata
    ) -> None:
        """
        Saves dataset metadata as a JSON document to the storage provider.
        
        Args:
            dataset_id: The UUID of the dataset.
            metadata: DatasetMetadata schema holding extracted headers, rowcounts, etc.
            
        Raises:
            StorageFailure: If metadata cannot be successfully written.
        """
        pass

    @abstractmethod
    async def get_metadata(self, dataset_id: str) -> DatasetMetadata:
        """
        Retrieves the saved dataset metadata JSON document from storage.
        
        Args:
            dataset_id: The UUID of the dataset.
            
        Returns:
            The reconstructed DatasetMetadata object.
            
        Raises:
            DatasetNotFound: If metadata or the dataset directory does not exist.
            StorageFailure: If reading the metadata file fails.
        """
        pass

    @abstractmethod
    def get_file_path(self, dataset_id: str, filename: str) -> str:
        """
        Returns the absolute local filesystem path or URI to a file.
        
        Args:
            dataset_id: The UUID of the dataset.
            filename: The target filename.
            
        Returns:
            Absolute filepath or resource locator URI string.
        """
        pass

    @abstractmethod
    async def save_profile(self, dataset_id: str, profile: DatasetProfile) -> None:
        """
        Saves dataset profile as a JSON document to the storage provider.
        """
        pass

    @abstractmethod
    async def get_profile(self, dataset_id: str) -> DatasetProfile:
        """
        Retrieves the saved dataset profile from storage.
        """
        pass

    @abstractmethod
    async def save_semantic_model(self, dataset_id: str, model: SemanticModel) -> None:
        """
        Saves dataset semantic model as a JSON document to the storage provider.
        """
        pass

    @abstractmethod
    async def get_semantic_model(self, dataset_id: str) -> SemanticModel:
        """
        Retrieves the saved dataset semantic model from storage.
        """
        pass

    @abstractmethod
    async def save_analytics_plan(self, dataset_id: str, plan: AnalyticsPlan) -> None:
        """
        Saves dataset analytics execution plan as a JSON document to the storage provider.
        """
        pass

    @abstractmethod
    async def get_analytics_plan(self, dataset_id: str) -> AnalyticsPlan:
        """
        Retrieves the saved dataset analytics execution plan from storage.
        """
        pass

    @abstractmethod
    async def save_analytics_results(self, dataset_id: str, results: AnalyticsResult) -> None:
        """
        Saves computed analytics results as a JSON document to the storage provider.
        """
        pass

    @abstractmethod
    async def get_analytics_results(self, dataset_id: str) -> AnalyticsResult:
        """
        Retrieves the saved computed analytics results from storage.
        """
        pass

    @abstractmethod
    async def save_visualization_plan(self, dataset_id: str, plan: VisualizationPlan) -> None:
        """
        Saves computed visualization plan configuration as a JSON document.
        """
        pass

    @abstractmethod
    async def get_visualization_plan(self, dataset_id: str) -> VisualizationPlan:
        """
        Retrieves the saved computed visualization plan from storage.
        """
        pass

    @abstractmethod
    async def save_dashboard(self, dataset_id: str, dashboard: DashboardConfiguration) -> None:
        """
        Saves composed dashboard configuration as a JSON document.
        """
        pass

    @abstractmethod
    async def get_dashboard(self, dataset_id: str) -> DashboardConfiguration:
        """
        Retrieves the saved composed dashboard configuration from storage.
        """
        pass

    @abstractmethod
    async def save_insights(self, dataset_id: str, insights: InsightCollection) -> None:
        """
        Saves computed AI insights as a JSON document.
        """
        pass

    @abstractmethod
    async def get_insights(self, dataset_id: str) -> InsightCollection:
        """
        Retrieves the saved computed AI insights from storage.
        """
        pass

    @abstractmethod
    async def save_conversation(self, dataset_id: str, conversation: Conversation) -> None:
        """
        Saves a stateful conversation log as a JSON document.
        """
        pass

    @abstractmethod
    async def get_conversation(self, dataset_id: str, conversation_id: str) -> Conversation:
        """
        Retrieves a saved stateful conversation log from storage.
        """
        pass
