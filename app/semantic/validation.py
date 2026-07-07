from typing import List, Dict, Any
from app.core.logging import logger
from app.schemas.semantic import SemanticModel


class SemanticValidationService:
    """
    Validates the generated Healthcare Semantic Model for consistency,
    integrity, and analytical completeness. Flags missing critical clinical concepts.
    """

    @staticmethod
    def validate_model(model: SemanticModel) -> List[Dict[str, Any]]:
        """
        Validates model definitions. Returns list of warning or error details.
        """
        issues: List[Dict[str, Any]] = []

        # 1. Check for duplicate standard concepts mapped to different columns
        concept_occurrences: Dict[str, List[str]] = {}
        for norm_name, col in model.columns.items():
            sem_type = col.semantic_type
            if sem_type != "UNKNOWN":
                if sem_type not in concept_occurrences:
                    concept_occurrences[sem_type] = []
                concept_occurrences[sem_type].append(col.original_name)

        for concept, cols in concept_occurrences.items():
            if len(cols) > 1:
                issues.append({
                    "issue_type": "duplicate_concept_mapping",
                    "severity": "warning",
                    "message": f"Concept '{concept}' is mapped to multiple columns: {cols}. This could indicate redundancy or classification conflict.",
                    "details": {"columns": cols}
                })

        # 2. Check for missing core targets (like Disease/Diagnosis)
        if "DISEASE" not in concept_occurrences:
            issues.append({
                "issue_type": "missing_critical_concept",
                "severity": "warning",
                "message": "No column mapped to 'DISEASE' or clinical diagnosis. Downstream disease analytics will be constrained.",
                "details": {"missing_concept": "DISEASE"}
            })

        # 3. Check for missing patient demographics (Age/Gender)
        if "AGE" not in concept_occurrences and "DATE_OF_BIRTH" not in concept_occurrences:
            issues.append({
                "issue_type": "missing_patient_age",
                "severity": "info",
                "message": "Patient age or date of birth columns could not be identified. Demographic age grouping will be disabled.",
                "details": {"missing_concept": "AGE"}
            })

        # 4. Check for low confidence score overall
        mean_conf = model.metadata.mean_confidence_score
        if mean_conf < 0.60:
            issues.append({
                "issue_type": "low_mapping_confidence",
                "severity": "warning",
                "message": f"The average semantic mapping confidence score is low ({mean_conf}). Ensure columns match standard naming conventions.",
                "details": {"mean_confidence": mean_conf}
            })

        logger.info(f"Validated semantic model for dataset {model.dataset_id}. Found {len(issues)} validation flags.")
        return issues
