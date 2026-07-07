from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.conversation import ConversationalChatResponse, Conversation, UserQuestion
from app.services.conversational_analytics import ConversationalAnalyticsService, SecurityValidationError
from app.services.conversation_history import ConversationHistoryService
from app.dependencies.services import (
    get_conversational_analytics_service,
    get_conversation_history_service
)
from app.core.logging import logger

router = APIRouter()


class ResetRequest(BaseModel):
    """Payload to reset a stateful conversation log."""
    conversation_id: str = Field(..., description="Active session ID to reset.")
    dataset_id: str = Field(..., description="Target dataset UUID.")


@router.post(
    "/query",
    response_model=ConversationalChatResponse,
    status_code=200,
    summary="Submit conversational query",
    description="Processes user text questions via LLM intent routing, DataFrame execution, and format outputs."
)
async def submit_chat_query(
    payload: UserQuestion,
    dataset_id: str = Query(..., description="Target dataset UUID."),
    service: ConversationalAnalyticsService = Depends(get_conversational_analytics_service)
) -> ConversationalChatResponse:
    logger.info(f"Chat query received for dataset ID: {dataset_id}")
    try:
        return await service.execute_query(
            dataset_id=dataset_id,
            user_query=payload.query,
            conversation_id=payload.conversation_id
        )
    except SecurityValidationError as e:
        logger.error(f"Security validation match: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process chat query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/history/{conversation_id}",
    response_model=Conversation,
    status_code=200,
    summary="Get conversation history",
    description="Retrieves stateful message history logs and metadata for a conversation session."
)
async def get_chat_history(
    conversation_id: str,
    dataset_id: str = Query(..., description="Target dataset UUID."),
    history_service: ConversationHistoryService = Depends(get_conversation_history_service)
) -> Conversation:
    logger.info(f"Retrieve history request for session {conversation_id}")
    try:
        return await history_service.get_or_create_conversation(
            dataset_id=dataset_id,
            conversation_id=conversation_id
        )
    except Exception as e:
        logger.error(f"Failed to fetch conversation history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve conversation: {str(e)}")


@router.post(
    "/reset",
    status_code=200,
    summary="Reset conversation session",
    description="Wipes the active conversation log history."
)
async def reset_chat_conversation(
    payload: ResetRequest,
    history_service: ConversationHistoryService = Depends(get_conversation_history_service)
) -> dict:
    logger.info(f"Reset history requested for session {payload.conversation_id}")
    try:
        await history_service.reset_conversation(
            dataset_id=payload.dataset_id,
            conversation_id=payload.conversation_id
        )
        return {"status": "success", "message": f"Conversation '{payload.conversation_id}' reset successfully."}
    except Exception as e:
        logger.error(f"Failed to reset conversation session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset session: {str(e)}")
