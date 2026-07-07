from app.storage.interface import StorageInterface
from app.schemas.results import AnalyticsResult


class AnalyticsResultRepository:
    """
    Repository managing persistence and retrieval of computed Analytics Results.
    Uses the active StorageInterface to read and write analytics_results.json.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def save_results(self, dataset_id: str, results: AnalyticsResult) -> None:
        """Saves an analytics results document to storage."""
        await self.storage.save_analytics_results(dataset_id=dataset_id, results=results)

    async def get_results(self, dataset_id: str) -> AnalyticsResult:
        """Retrieves an analytics results document from storage."""
        return await self.storage.get_analytics_results(dataset_id=dataset_id)
