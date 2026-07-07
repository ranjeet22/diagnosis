import os
import json
from typing import Dict, Any, List
from app.core.logging import logger
from app.schemas.semantic import SemanticModel
from app.schemas.plan import AnalyticsPlan
from app.schemas.conversation import ConversationMessage, IntentResponse
from app.gemini import GeminiClientWrapper

DEFAULT_CONV_PROMPTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config",
    "prompts",
    "conversational_prompts.json"
)

DEFAULT_ROUTER_SYSTEM = (
    "You are a senior query intent compiler for the Diagnōsis health platform. "
    "Translate the user query and history context into a strict structured JSON intent."
)

DEFAULT_ROUTER_PROMPT = (
    "Analyze the query and context and map to structured JSON.\n\n"
    "Schema:\n{columns_context}\nKPIs:\n{kpis_context}\n"
    "History:\n{history_context}\nQuery:\n\"{user_query}\"\n\n"
    "Output must match IntentResponse schema."
)


class IntentRouter:
    """
    Parses stateful clinical natural language questions into structured IntentResponse objects
    using Gemini, aware of conversational history, dataset semantics, and plan definitions.
    """
    def __init__(self,
        client_wrapper: GeminiClientWrapper,
        prompts_filepath: str = DEFAULT_CONV_PROMPTS_PATH
    ) -> None:
        self.client_wrapper = client_wrapper
        self.prompts_filepath = prompts_filepath
        self.system_instruction = DEFAULT_ROUTER_SYSTEM
        self.prompt_template = DEFAULT_ROUTER_PROMPT
        self._load_templates()

    def _load_templates(self) -> None:
        """Loads intent templates from the JSON configuration."""
        if not os.path.exists(self.prompts_filepath):
            return
        try:
            with open(self.prompts_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            templates = data.get("templates", {})
            tpl = templates.get("intent_routing", {})
            self.system_instruction = tpl.get("system_instruction", DEFAULT_ROUTER_SYSTEM)
            self.prompt_template = tpl.get("prompt_template", DEFAULT_ROUTER_PROMPT)
        except Exception as e:
            logger.error(f"IntentRouter: Failed to load prompts file {self.prompts_filepath}: {e}")

    async def route_query(self,
        user_query: str,
        semantic_model: SemanticModel,
        analytics_plan: AnalyticsPlan,
        history: List[ConversationMessage]
    ) -> IntentResponse:
        logger.info(f"IntentRouter: Stateful parse of query: '{user_query}'")

        # 1. Compile schema context
        cols_list = []
        for col_name, col in semantic_model.columns.items():
            cols_list.append(f"'{col_name}' ({col.semantic_type})")
        columns_context = ", ".join(cols_list)

        # 2. Compile KPI context
        kpis_list = []
        for kpi in analytics_plan.kpis:
            kpis_list.append(f"'{kpi.name}'")
        kpis_context = ", ".join(kpis_list)

        # 3. Format stateful history context (last 5 messages)
        history_context = ""
        for msg in history[-5:]:
            history_context += f"- {msg.role.capitalize()}: {msg.content}\n"
        if not history_context:
            history_context = "No previous conversation history."

        # 4. Render prompt
        rendered_prompt = (
            self.prompt_template
            .replace("{columns_context}", columns_context)
            .replace("{kpis_context}", kpis_context)
            .replace("{history_context}", history_context)
            .replace("{user_query}", user_query)
        )

        try:
            # Call Gemini
            raw_text = await self.client_wrapper.generate_explanation(
                system_instruction=self.system_instruction,
                prompt=rendered_prompt
            )
            parsed = json.loads(raw_text)

            return IntentResponse(
                action=parsed.get("action", "UNKNOWN"),
                filters=parsed.get("filters", []),
                group_by=parsed.get("group_by"),
                aggregation=parsed.get("aggregation"),
                sort=parsed.get("sort", "descending"),
                limit=parsed.get("limit"),
                visualization=parsed.get("visualization"),
                kpi_name=parsed.get("kpi_name"),
                explanation_request=parsed.get("explanation_request")
            )
        except Exception as e:
            logger.error(f"IntentRouter: Stateful parse failed: {e}. Reverting to local heuristic parser.")
            
            # Simple local heuristic resolver
            q_lower = user_query.lower()
            action = "UNKNOWN"
            kpi_name = None
            if "how many" in q_lower or "count" in q_lower or "total records" in q_lower:
                action = "KPI_QUERY"
                kpi_name = "Total Records"
            elif "age" in q_lower or "disease" in q_lower or "gender" in q_lower:
                action = "FILTER"

            return IntentResponse(
                action=action,
                filters=[],
                group_by="diagnosis" if "disease" in q_lower or "diagnosis" in q_lower else None,
                aggregation="count",
                sort="descending",
                kpi_name=kpi_name
            )
