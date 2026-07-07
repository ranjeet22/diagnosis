from typing import List, Dict, Any, Tuple
from app.schemas.semantic import SemanticModel
from app.schemas.conversation import IntentResponse


class IntentValidationError(ValueError):
    """Exception raised for semantic validation issues in parsed LLM query intents."""
    pass


class IntentValidator:
    """
    Validates the parsed query IntentResponse against dataset metadata,
    rejecting hallucinated columns, unsupported aggregations, and invalid operators.
    """

    @staticmethod
    def validate_intent(intent: IntentResponse, semantic_model: SemanticModel) -> Tuple[List[str], bool]:
        """
        Validates columns, operators, and aggregations against the semantic model.
        Returns a list of error message strings and a boolean validation flag.
        """
        errors = []
        is_valid = True
        
        valid_columns = set(semantic_model.columns.keys())

        # 1. Skip validation for open explanation or unknown actions
        if intent.action in ["GENERAL_EXPLANATION", "UNKNOWN"]:
            return errors, is_valid

        # 2. Check group_by column existence
        if intent.group_by and intent.group_by not in valid_columns:
            errors.append(f"Validation Error: Grouping column '{intent.group_by}' does not exist in the dataset.")
            is_valid = False

        # 3. Check filters columns & operators
        valid_operators = {"equals", "greater_than", "less_than", "greater_than_or_equal", "less_than_or_equal"}
        for idx, filt in enumerate(intent.filters):
            col = filt.get("column")
            op = filt.get("operator")
            
            if not col:
                errors.append(f"Validation Error: Filter at index {idx} is missing the target 'column' property.")
                is_valid = False
                continue

            if col not in valid_columns:
                errors.append(f"Validation Error: Filter column '{col}' does not exist in this dataset.")
                is_valid = False

            if op not in valid_operators:
                errors.append(f"Validation Warning: Filter at index {idx} has unsupported operator '{op}'. Standardized to 'equals'.")
                filt["operator"] = "equals"

        # 4. Check aggregation operations
        if intent.aggregation:
            valid_aggs = {"count", "sum", "average", "median", "min", "max", "distinct_count"}
            if intent.aggregation.lower() not in valid_aggs:
                errors.append(f"Validation Error: Aggregation operation '{intent.aggregation}' is not supported.")
                is_valid = False

        # 5. Check sort direction
        if intent.sort:
            if intent.sort.lower() not in ["descending", "ascending"]:
                errors.append(f"Validation Warning: Invalid sort direction '{intent.sort}'. Standardized to 'descending'.")
                intent.sort = "descending"

        # 6. Check visualization overrides
        if intent.visualization:
            valid_viz = {"bar", "pie", "line", "boxplot", "heatmap", "card", "table"}
            if intent.visualization.lower() not in valid_viz:
                errors.append(f"Validation Warning: Unsupported visualization type '{intent.visualization}'.")
                # Do not reject entirely, fallback to standard card/table
                intent.visualization = None

        return errors, is_valid
