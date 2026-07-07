import os
import json
from typing import Dict, Any, Optional
from app.core.logging import logger
from app.schemas.conversation import ConversationalChatResponse


class QueryCache:
    """
    Local query cache managing read/write serialization of previous user queries
    stored as query_cache.json to prevent redundant Gemini API calls.
    """
    def __init__(self, storage_dir: str) -> None:
        self.storage_dir = storage_dir

    def _get_cache_filepath(self, dataset_id: str) -> str:
        return os.path.join(self.storage_dir, dataset_id, "query_cache.json")

    def _normalize_query(self, query: str) -> str:
        return "".join(c for c in query.lower() if c.isalnum() or c.isspace()).strip()

    def get_cached_response(self, dataset_id: str, query: str) -> Optional[ConversationalChatResponse]:
        """Retrieves cached ConversationalChatResponse if present."""
        path = self._get_cache_filepath(dataset_id)
        if not os.path.exists(path):
            return None

        normalized = self._normalize_query(query)
        try:
            with open(path, "r", encoding="utf-8") as f:
                cache_map = json.load(f)
            
            if normalized in cache_map:
                logger.debug(f"QueryCache: Hit for query: '{query}'")
                return ConversationalChatResponse.model_validate(cache_map[normalized])
        except Exception as e:
            logger.error(f"QueryCache: Failed to read cache {path}: {e}")
        return None

    def save_response(self, dataset_id: str, query: str, response: ConversationalChatResponse) -> None:
        """Saves ConversationalChatResponse to query cache."""
        path = self._get_cache_filepath(dataset_id)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        normalized = self._normalize_query(query)
        cache_map = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    cache_map = json.load(f)
            except Exception:
                pass

        try:
            cache_map[normalized] = response.model_dump()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(cache_map, f, indent=2, default=str)
            logger.debug(f"QueryCache: Cached query successfully at {path}")
        except Exception as e:
            logger.error(f"QueryCache: Failed to write cache {path}: {e}")
