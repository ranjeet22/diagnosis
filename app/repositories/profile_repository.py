from app.storage.interface import StorageInterface
from app.schemas.profile import DatasetProfile


class ProfileRepository:
    """
    Repository managing persistence and retrieval of Dataset Profiles.
    Deploys the registered StorageInterface driver to save and fetch
    generated machine-readable profiling JSON documents.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def save_profile(self, dataset_id: str, profile: DatasetProfile) -> None:
        """Saves a dataset profile document to storage."""
        await self.storage.save_profile(dataset_id=dataset_id, profile=profile)

    async def get_profile(self, dataset_id: str) -> DatasetProfile:
        """Retrieves a dataset profile document from storage."""
        return await self.storage.get_profile(dataset_id=dataset_id)
