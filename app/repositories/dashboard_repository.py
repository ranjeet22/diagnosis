from app.storage.interface import StorageInterface
from app.schemas.dashboard import DashboardConfiguration


class DashboardRepository:
    """
    Repository layer managing serialization, persistence, and retrieval
    of Dashboard Configurations from the storage driver.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def save_dashboard(self, dataset_id: str, dashboard: DashboardConfiguration) -> None:
        """Saves a composed dashboard configuration to storage."""
        await self.storage.save_dashboard(dataset_id=dataset_id, dashboard=dashboard)

    async def get_dashboard(self, dataset_id: str) -> DashboardConfiguration:
        """Retrieves a dashboard configuration from storage."""
        return await self.storage.get_dashboard(dataset_id=dataset_id)
