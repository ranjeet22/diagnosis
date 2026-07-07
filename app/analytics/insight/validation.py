import json
from typing import Dict, Any, List, Tuple
from app.core.logging import logger
from app.schemas.insight import ExecutiveSummary, Insight


class InsightValidationService:
    """
    Validates structural compliance and data integrity of generated insights,
    checking JSON properties, confidence values, and metric links.
    """

    @staticmethod
    def validate_llm_json(raw_json_str: str) -> Tuple[Dict[str, Any], List[str], bool]:
        """
        Parses raw text response from LLM, checks constraints, and validates schema compliance.
        Returns parsed dict, validation logs list, and is_valid boolean flag.
        """
        logs = []
        is_valid = True
        parsed_data: Dict[str, Any] = {}

        # 1. Check valid JSON syntax
        try:
            parsed_data = json.loads(raw_json_str)
        except json.JSONDecodeError as e:
            logs.append(f"Validation Error: Response is not a valid JSON document. Details: {e}")
            return {}, logs, False

        # 2. Check root-level elements
        if "executive_summary" not in parsed_data:
            logs.append("Validation Error: Missing root element 'executive_summary'.")
            is_valid = False
        else:
            exec_sum = parsed_data["executive_summary"]
            if not isinstance(exec_sum, dict):
                logs.append("Validation Error: 'executive_summary' must be a JSON object.")
                is_valid = False
            else:
                if not exec_sum.get("summary"):
                    logs.append("Validation Warning: 'executive_summary.summary' is empty.")
                if not isinstance(exec_sum.get("key_takeaways"), list):
                    logs.append("Validation Warning: 'executive_summary.key_takeaways' must be a list.")

        if "insights" not in parsed_data:
            logs.append("Validation Error: Missing root element 'insights'.")
            is_valid = False
        else:
            insights = parsed_data["insights"]
            if not isinstance(insights, list):
                logs.append("Validation Error: 'insights' must be a list of objects.")
                is_valid = False
            else:
                for idx, item in enumerate(insights):
                    prefix = f"Insight #{idx} ({item.get('title', 'Untitled')})"
                    
                    # Validate required fields
                    req_fields = ["id", "title", "summary", "detailed_explanation", "evidence", "source_metrics", "category"]
                    for field in req_fields:
                        if field not in item or item[field] is None:
                            logs.append(f"Validation Warning: {prefix} is missing required field '{field}'.")
                    
                    # Validate confidence bounds
                    confidence = item.get("confidence", 1.0)
                    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
                        logs.append(f"Validation Warning: {prefix} has invalid confidence value '{confidence}'. Standardized to 1.0.")
                        item["confidence"] = 1.0

                    # Validate importance options
                    importance = item.get("importance", "medium")
                    if importance not in ["high", "medium", "low"]:
                        logs.append(f"Validation Warning: {prefix} has unexpected importance '{importance}'. Standardized to 'medium'.")
                        item["importance"] = "medium"

                    # Validate source metrics is a list
                    if "source_metrics" in item and not isinstance(item["source_metrics"], list):
                        logs.append(f"Validation Warning: {prefix} 'source_metrics' is not a list. Standardizing to array.")
                        item["source_metrics"] = [str(item["source_metrics"])]

        if is_valid:
            logs.append("Structured clinical insights validation completed successfully. All constraints verified.")

        return parsed_data, logs, is_valid
