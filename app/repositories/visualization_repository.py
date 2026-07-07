from app.storage.interface import StorageInterface
from app.schemas.visualization import VisualizationPlan


class VisualizationRepository:
    """
    Repository layer managing serialization, persistence, and retrieval
    of computed Visualization Plans from the storage driver.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def save_plan(self, dataset_id: str, plan: VisualizationPlan) -> None:
        """Saves a visualization plan document to storage."""
        await self.storage.save_visualization_plan(dataset_id=dataset_id, plan=plan)

    async def get_plan(self, dataset_id: str) -> VisualizationPlan:
        """Retrieves a visualization plan document from storage."""
        return await self.storage.get_visualization_plan(dataset_id=dataset_id)
