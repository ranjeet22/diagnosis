from app.core.exceptions import DatasetNotFound
from app.schemas.conversation import Conversation
from app.storage.interface import StorageInterface


class ConversationRepository:
    """
    Handles persistence operations for Conversation state files using StorageInterface.
    """
    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    async def get_conversation(self, dataset_id: str, conversation_id: str) -> Conversation:
        """Retrieves a stateful conversation by session ID."""
        return await self.storage.get_conversation(dataset_id=dataset_id, conversation_id=conversation_id)

    async def save_conversation(self, dataset_id: str, conversation: Conversation) -> None:
        """Persists a stateful conversation session."""
        await self.storage.save_conversation(dataset_id=dataset_id, conversation=conversation)
