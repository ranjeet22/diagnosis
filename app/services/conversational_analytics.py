import os
import json
import re
from typing import Dict, Any, List, Optional
from app.core.logging import logger
from app.core.exceptions import DatasetNotFound, AnalyticsError
from app.schemas.conversation import (
    Conversation,
    ConversationMessage,
    IntentResponse,
    QueryResult,
    ConversationalChatResponse
)
from app.repositories.semantic_repository import SemanticModelRepository
from app.repositories.plan_repository import AnalyticsPlanRepository
from app.repositories.result_repository import AnalyticsResultRepository
from app.storage.interface import StorageInterface
from app.analytics.dataframe_provider import load_dataset_df
from app.analytics.profiler import normalize_column_name
from app.analytics.conversational.router import IntentRouter
from app.analytics.conversational.validator import IntentValidator
from app.analytics.conversational.executor import IntentExecutor
from app.analytics.conversational.formatter import ResponseFormatter
from app.analytics.conversational.cache import QueryCache
from app.services.conversation_history import ConversationHistoryService
from app.gemini import GeminiClientWrapper

DEFAULT_CONV_PROMPTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config",
    "prompts",
    "conversational_prompts.json"
)

DEFAULT_EXPLANATION_SYSTEM = (
    "You are a senior clinical data analyst. Explain the calculated query outcome in natural language."
)

DEFAULT_EXPLANATION_PROMPT = (
    "Provide a 2-3 sentence clinical narrative summarizing these computed results.\n\n"
    "User Query: \"{user_query}\"\nResults: {execution_result}\nIntent: {intent}"
)


class SecurityValidationError(ValueError):
    """Exception raised when conversational queries fail security criteria checks."""
    pass


class ConversationalAnalyticsService:
    """
    Coordinates stateful conversational analytics pipeline:
    1. Audits queries against SQL, prompt injection, and code execution attempts.
    2. Retrieves stateful session logs.
    3. Leverages a normalized query cache to bypass LLM computations.
    4. Routes natural language to structured IntentResponse objects.
    5. Validates intent schema attributes against active semantic columns.
    6. Runs execution queries deterministically on DataFrames.
    7. Formats data outcomes and requests Gemini explanations.
    """
    def __init__(self,
        semantic_repository: SemanticModelRepository,
        plan_repository: AnalyticsPlanRepository,
        result_repository: AnalyticsResultRepository,
        storage: StorageInterface,
        client_wrapper: GeminiClientWrapper,
        history_service: ConversationHistoryService
    ) -> None:
        self.semantic_repository = semantic_repository
        self.plan_repository = plan_repository
        self.result_repository = result_repository
        self.storage = storage
        self.client_wrapper = client_wrapper
        self.history_service = history_service
        self.prompts_filepath = DEFAULT_CONV_PROMPTS_PATH
        
        # Load local Query Cache pointing to uploads base directory
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "storage", "uploads")
        self.query_cache = QueryCache(storage_dir=uploads_dir)

    def _audit_security(self, query: str) -> None:
        """Scan queries for SQL injection patterns, prompt overrides, or code injections."""
        lower_q = query.lower()

        # Prompt injection patterns
        prompt_injection = [
            "ignore previous instructions",
            "system instruction override",
            "tell me your system instructions",
            "reveal your instructions",
            "you are now a",
            "bypass safety"
        ]
        for pattern in prompt_injection:
            if pattern in lower_q:
                raise SecurityValidationError("Query rejected: security protocol audit match (prompt injection attempt).")

        # SQL Injection patterns
        sql_injection = [
            "union select",
            "drop table",
            "insert into",
            "delete from",
            "update ",
            "select * from",
            "shutdown"
        ]
        for pattern in sql_injection:
            if re.search(r"\b" + re.escape(pattern) + r"\b", lower_q) or "--" in lower_q:
                raise SecurityValidationError("Query rejected: security protocol audit match (SQL injection attempt).")

        # Code execution keywords
        code_injection = [
            "import os",
            "subprocess",
            "sys.exit",
            "eval(",
            "exec(",
            "__builtins__"
        ]
        for pattern in code_injection:
            if pattern in lower_q:
                raise SecurityValidationError("Query rejected: security protocol audit match (code injection attempt).")

    async def execute_query(
        self,
        dataset_id: str,
        user_query: str,
        conversation_id: Optional[str] = None
    ) -> ConversationalChatResponse:
        logger.info(f"ConversationalAnalyticsService: Submit query: '{user_query}' for dataset {dataset_id}")

        # 1. Security Audit Check
        self._audit_security(user_query)

        # 2. Get stateful conversation session
        conv = await self.history_service.get_or_create_conversation(dataset_id=dataset_id, conversation_id=conversation_id)

        # Log incoming user message
        conv = await self.history_service.add_message(dataset_id=dataset_id, conversation=conv, role="user", content=user_query)

        # 3. Check Query Cache (bypass Gemini if exact query exists)
        cached = self.query_cache.get_cached_response(dataset_id=dataset_id, query=user_query)
        if cached:
            # Overwrite session details for correctness
            cached.conversation_id = conv.conversation_id
            cached.metadata = conv.metadata
            
            # Log cached assistant answer
            await self.history_service.add_message(
                dataset_id=dataset_id,
                conversation=conv,
                role="assistant",
                content=cached.nl_explanation
            )
            return cached

        # 4. Fetch Semantic Model, Plan, and Results
        try:
            semantic_model = await self.semantic_repository.get_model(dataset_id=dataset_id)
            analytics_plan = await self.plan_repository.get_plan(dataset_id=dataset_id)
            results = await self.result_repository.get_results(dataset_id=dataset_id)
        except DatasetNotFound as e:
            raise DatasetNotFound(f"Cannot run conversational query: {e}")
        except Exception as e:
            raise AnalyticsError(f"Failed to load context dependencies: {e}")

        # 5. Load and Normalize DataFrame
        try:
            metadata = await self.storage.get_metadata(dataset_id=dataset_id)
            file_path = self.storage.get_file_path(dataset_id=dataset_id, filename="original.csv")
            
            df = load_dataset_df(
                file_path=file_path,
                delimiter=metadata.delimiter,
                encoding=metadata.encoding
            )

            # Match exact column normalization from profiling step
            normalized_cols = []
            seen_normalized_names = {}
            for pos, col in enumerate(df.columns):
                norm = normalize_column_name(col)
                if not norm:
                    norm = f"column_{pos}"
                if norm in seen_normalized_names:
                    seen_normalized_names[norm] += 1
                    norm = f"{norm}_{seen_normalized_names[norm]}"
                else:
                    seen_normalized_names[norm] = 0
                normalized_cols.append(norm)
            df.columns = normalized_cols

        except Exception as e:
            logger.error(f"Failed to load dataset dataframe for query: {e}")
            raise AnalyticsError(f"Failed to load dataset values: {e}")

        # 6. Intent Routing (LLM)
        router = IntentRouter(self.client_wrapper, prompts_filepath=self.prompts_filepath)
        intent = await router.route_query(
            user_query=user_query,
            semantic_model=semantic_model,
            analytics_plan=analytics_plan,
            history=conv.messages[:-1] # exclude the current user query from history context during routing
        )

        # 7. Intent Validation
        validation_errors, is_valid = IntentValidator.validate_intent(intent, semantic_model)
        if not is_valid:
            error_msg = "; ".join(validation_errors)
            logger.warning(f"ConversationalAnalyticsService: Intent validation failed: {error_msg}")
            
            # Construct failure response
            failed_res = ConversationalChatResponse(
                conversation_id=conv.conversation_id,
                intent=intent,
                execution_result=QueryResult(data=[], summary="Validation failure.", columns=[]),
                formatted_response={
                    "render_type": "table",
                    "headers": [],
                    "rows": [],
                    "total_rows": 0,
                    "error": error_msg
                },
                suggested_visualization=intent.visualization,
                nl_explanation=f"I couldn't run that query: {error_msg}",
                metadata=conv.metadata
            )
            
            await self.history_service.add_message(
                dataset_id=dataset_id,
                conversation=conv,
                role="assistant",
                content=failed_res.nl_explanation
            )
            return failed_res

        # 8. Deterministic Intent Execution
        exec_details = IntentExecutor.execute_intent(intent, df, results)
        
        # 9. Format Outcomes
        formatted = ResponseFormatter.format_response(
            intent=intent,
            result=exec_details.query_result,
            execution_time_ms=exec_details.execution_time_ms
        )

        # 10. Generate natural language explanation
        nl_explanation = ""
        if not exec_details.success:
            nl_explanation = f"Query Execution Error: {exec_details.error_message}"
        else:
            system_instruction, prompt_template = self._load_explanation_templates()
            rendered = (
                prompt_template
                .replace("{user_query}", user_query)
                .replace("{execution_result}", json.dumps(exec_details.query_result.data))
                .replace("{intent}", intent.model_dump_json())
            )

            try:
                nl_explanation = await self.client_wrapper.generate_explanation(
                    system_instruction=system_instruction,
                    prompt=rendered
                )
            except Exception as e:
                logger.warning(f"ConversationalAnalyticsService: Gemini explanation failed: {e}. Falling back.")
                nl_explanation = self._get_fallback_explanation(exec_details.query_result)

        # Construct ultimate chat response
        chat_response = ConversationalChatResponse(
            conversation_id=conv.conversation_id,
            intent=intent,
            execution_result=exec_details.query_result,
            formatted_response=formatted,
            suggested_visualization=intent.visualization,
            nl_explanation=nl_explanation,
            metadata=conv.metadata
        )

        # Cache response
        if exec_details.success:
            self.query_cache.save_response(dataset_id=dataset_id, query=user_query, response=chat_response)

        # Log assistant response to conversation history
        await self.history_service.add_message(
            dataset_id=dataset_id,
            conversation=conv,
            role="assistant",
            content=nl_explanation
        )

        return chat_response

    def _load_explanation_templates(self) -> tuple[str, str]:
        """Loads explanation templates from prompt configuration file."""
        if not os.path.exists(self.prompts_filepath):
            return DEFAULT_EXPLANATION_SYSTEM, DEFAULT_EXPLANATION_PROMPT
        try:
            with open(self.prompts_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            templates = data.get("templates", {})
            tpl = templates.get("conversational_explanation", {})
            return (
                tpl.get("system_instruction", DEFAULT_EXPLANATION_SYSTEM),
                tpl.get("prompt_template", DEFAULT_EXPLANATION_PROMPT)
            )
        except Exception as e:
            logger.error(f"ConversationalAnalyticsService: Failed to parse templates: {e}")
            return DEFAULT_EXPLANATION_SYSTEM, DEFAULT_EXPLANATION_PROMPT

    def _get_fallback_explanation(self, result: QueryResult) -> str:
        """Deterministic fallback clinical summary if external LLM is offline."""
        if not result.data:
            return "No matching dataset rows were found for your query filters."
        
        first_row = result.data[0]
        desc = ", ".join([f"{k}: {v}" for k, v in first_row.items()])
        return (
            f"The deterministic execution completed returning {len(result.data)} records. "
            f"Primary indicators: {desc}."
        )
