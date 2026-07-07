from app.storage.interface import StorageInterface
from app.schemas.semantic import SemanticModel


class SemanticModelRepository:
    """
    Repository managing persistence and retrieval of Healthcare Semantic Models.
    Deploys the registered StorageInterface driver to save and fetch
    generated semantic_model.json documents.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def save_model(self, dataset_id: str, model: SemanticModel) -> None:
        """Saves a semantic model document to storage."""
        await self.storage.save_semantic_model(dataset_id=dataset_id, model=model)

    async def get_model(self, dataset_id: str) -> SemanticModel:
        """Retrieves a semantic model document from storage."""
        return await self.storage.get_semantic_model(dataset_id=dataset_id)
