from app.storage.interface import StorageInterface
from app.schemas.plan import AnalyticsPlan


class AnalyticsPlanRepository:
    """
    Repository managing persistence and retrieval of Analytics Execution Plans.
    Uses the active StorageInterface to read and write analytics_plan.json.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def save_plan(self, dataset_id: str, plan: AnalyticsPlan) -> None:
        """Saves an analytics plan document to storage."""
        await self.storage.save_analytics_plan(dataset_id=dataset_id, plan=plan)

    async def get_plan(self, dataset_id: str) -> AnalyticsPlan:
        """Retrieves an analytics plan document from storage."""
        return await self.storage.get_analytics_plan(dataset_id=dataset_id)
