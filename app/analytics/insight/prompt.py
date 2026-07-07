import os
import json
from app.core.logging import logger
from app.schemas.insight import InsightContext, PromptPayload

DEFAULT_PROMPTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config",
    "prompts",
    "insight_prompts.json"
)

DEFAULT_SYSTEM_INSTRUCTION = (
    "You are a senior medical statistician and expert clinical data analyst for the Diagnōsis health analytics platform. "
    "Your job is to translate complex, deterministic statistical calculations into clear, high-fidelity, professional medical insights. "
    "Keep your tone clinical, professional, and objective."
)

DEFAULT_PROMPT_TEMPLATE = (
    "Analyze the following structured health cohort statistics context and compile a professional clinical insight report.\n\n"
    "### Cohort Statistics Context\n{context}\n\n"
    "### Instructions:\n"
    "Generate an Executive Summary and a list of observations/insights analyzing the findings as a valid JSON object matching this schema:\n"
    "{{\n"
    "  \"executive_summary\": {{\n"
    "    \"title\": \"string\",\n"
    "    \"summary\": \"string\",\n"
    "    \"key_takeaways\": [\"string\"]\n"
    "  }},\n"
    "  \"insights\": [\n"
    "    {{\n"
    "      \"id\": \"string\",\n"
    "      \"title\": \"string\",\n"
    "      \"summary\": \"string\",\n"
    "      \"detailed_explanation\": \"string\",\n"
    "      \"evidence\": \"string\",\n"
    "      \"source_metrics\": [\"string\"],\n"
    "      \"importance\": \"high\" | \"medium\" | \"low\",\n"
    "      \"confidence\": 0.0 to 1.0,\n"
    "      \"category\": \"string\"\n"
    "    }}\n"
    "  ]\n"
    "}}"
)


class PromptBuilder:
    """
    Loads and compiles configurable and versioned prompt templates,
    combining them with structured analytics context to build the final prompt payload.
    """
    def __init__(self, prompts_filepath: str = DEFAULT_PROMPTS_PATH) -> None:
        self.prompts_filepath = prompts_filepath
        self.version = "1.0.0"
        self.system_instruction = DEFAULT_SYSTEM_INSTRUCTION
        self.prompt_template = DEFAULT_PROMPT_TEMPLATE
        self._load_templates()

    def _load_templates(self) -> None:
        """Loads prompt templates from the configuration JSON file."""
        if not os.path.exists(self.prompts_filepath):
            logger.warning(
                f"PromptBuilder: Configuration file {self.prompts_filepath} not found. "
                "Falling back to default prompt templates."
            )
            return

        try:
            with open(self.prompts_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.version = data.get("version", "1.0.0")
            templates = data.get("templates", {})
            gen_tpl = templates.get("insight_generation", {})
            
            self.system_instruction = gen_tpl.get("system_instruction", DEFAULT_SYSTEM_INSTRUCTION)
            self.prompt_template = gen_tpl.get("prompt_template", DEFAULT_PROMPT_TEMPLATE)
            logger.debug(f"PromptBuilder: Loaded prompt templates version {self.version} successfully.")
        except Exception as e:
            logger.error(f"PromptBuilder: Failed to parse prompt file {self.prompts_filepath}: {e}")

    def build_prompt_payload(self, context: InsightContext) -> PromptPayload:
        """
        Assembles PromptPayload using context values.
        """
        context_json = context.model_dump_json(indent=2)
        prompt_str = self.prompt_template.replace("{context}", context_json)

        return PromptPayload(
            system_instruction=self.system_instruction,
            prompt=prompt_str
        )
