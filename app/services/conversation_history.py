import uuid
from datetime import datetime, timezone
from typing import Optional
from app.core.exceptions import DatasetNotFound
from app.schemas.conversation import Conversation, ConversationMessage, ConversationMetadata
from app.repositories.conversation_repository import ConversationRepository


class ConversationHistoryService:
    """
    Manages session lifecycle, message logs appending, metadata audits,
    and history serialization for stateful dataset conversation feeds.
    """
    def __init__(self, repository: ConversationRepository) -> None:
        self.repository = repository

    async def get_or_create_conversation(
        self,
        dataset_id: str,
        conversation_id: Optional[str]
    ) -> Conversation:
        """Retrieves an existing conversation session or instantiates a new one."""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            
        try:
            return await self.repository.get_conversation(dataset_id=dataset_id, conversation_id=conversation_id)
        except (DatasetNotFound, Exception):
            # Create a brand new session
            now = datetime.now(timezone.utc)
            metadata = ConversationMetadata(
                conversation_id=conversation_id,
                dataset_id=dataset_id,
                created_at=now,
                updated_at=now,
                message_count=0
            )
            conv = Conversation(
                conversation_id=conversation_id,
                dataset_id=dataset_id,
                messages=[],
                metadata=metadata
            )
            await self.repository.save_conversation(dataset_id=dataset_id, conversation=conv)
            return conv

    async def add_message(
        self,
        dataset_id: str,
        conversation: Conversation,
        role: str,
        content: str
    ) -> Conversation:
        """Appends a user/assistant message to history and saves to storage."""
        msg = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        conversation.messages.append(msg)
        
        # Update metadata
        conversation.metadata.message_count = len(conversation.messages)
        conversation.metadata.updated_at = datetime.now(timezone.utc)
        
        await self.repository.save_conversation(dataset_id=dataset_id, conversation=conversation)
        return conversation

    async def reset_conversation(self, dataset_id: str, conversation_id: str) -> Conversation:
        """Wipes conversation message history logs and updates timestamps."""
        conv = await self.get_or_create_conversation(dataset_id=dataset_id, conversation_id=conversation_id)
        conv.messages = []
        conv.metadata.message_count = 0
        conv.metadata.updated_at = datetime.now(timezone.utc)
        await self.repository.save_conversation(dataset_id=dataset_id, conversation=conv)
        return conv
