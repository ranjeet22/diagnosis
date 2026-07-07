from app.storage.interface import StorageInterface
from app.schemas.insight import InsightCollection


class InsightRepository:
    """
    Repository layer managing serialization, persistence, and retrieval
    of generated AI Insights from the storage provider.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def save_insights(self, dataset_id: str, insights: InsightCollection) -> None:
        """Saves generated insights document to storage."""
        await self.storage.save_insights(dataset_id=dataset_id, insights=insights)

    async def get_insights(self, dataset_id: str) -> InsightCollection:
        """Retrieves generated insights document from storage."""
        return await self.storage.get_insights(dataset_id=dataset_id)
