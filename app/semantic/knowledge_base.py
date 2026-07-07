import os
import json
from typing import Dict, Any, List, Optional
from app.core.logging import logger


class MedicalKnowledgeBase:
    """
    Lightweight deterministic clinical ontology. Loads configuration files
    specifying rules for grouping, expected analysis types, chart visualization options,
    units, and missing value management.
    """
    def __init__(self, entities_path: str = None, rules_path: str = None) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_entities = os.path.abspath(
            os.path.join(current_dir, "..", "config", "semantic", "medical_entities.json")
        )
        default_rules = os.path.abspath(
            os.path.join(current_dir, "..", "config", "semantic", "analysis_rules.json")
        )

        self.entities_path = entities_path or default_entities
        self.rules_path = rules_path or default_rules

        self.entities_db: Dict[str, Dict[str, Any]] = {}
        self.rules_db: Dict[str, Dict[str, Any]] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Reads entities and rules from config directories."""
        try:
            if os.path.exists(self.entities_path):
                with open(self.entities_path, "r", encoding="utf-8") as f:
                    self.entities_db = json.load(f)
                logger.debug(f"MedicalKnowledgeBase: Loaded entities from {self.entities_path}")
            else:
                logger.warning(f"MedicalKnowledgeBase file missing: {self.entities_path}")
        except Exception as e:
            logger.error(f"Failed to load medical entities database: {e}")

        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    self.rules_db = json.load(f)
                logger.debug(f"MedicalKnowledgeBase: Loaded analysis rules from {self.rules_path}")
            else:
                logger.warning(f"MedicalKnowledgeBase rules file missing: {self.rules_path}")
        except Exception as e:
            logger.error(f"Failed to load analysis rules database: {e}")

    def get_entity_metadata(self, concept: str) -> Dict[str, Any]:
        """
        Retrieves logical groups, category groupings, and units.
        Returns a dictionary with default values if the concept is unmapped.
        """
        concept_upper = concept.upper()
        if concept_upper in self.entities_db:
            return self.entities_db[concept_upper]

        # Defaults for unmapped/UNKNOWN concepts
        return {
            "entity_group": "Unmapped",
            "medical_category": "General",
            "expected_units": None,
            "nullable_recommendation": {
                "allowed": True,
                "imputation_strategy": "none"
            }
        }

    def get_analysis_metadata(self, concept: str, data_type: str = "STRING") -> Dict[str, Any]:
        """
        Retrieves expected analysis steps, visual chart suggestions, and allowed aggregations.
        """
        concept_upper = concept.upper()
        if concept_upper in self.rules_db:
            return self.rules_db[concept_upper]

        # Fallbacks based on logical datatype if not in database
        datatype_upper = data_type.upper()
        if datatype_upper in {"INTEGER", "FLOAT"}:
            return {
                "expected_analysis": ["distribution", "summary statistics"],
                "suggested_visualizations": ["Histogram", "Box Plot"],
                "allowed_aggregations": ["mean", "median", "min", "max"]
            }
        elif datatype_upper in {"DATE", "DATETIME", "TIME"}:
            return {
                "expected_analysis": ["temporal trend", "seasonality"],
                "suggested_visualizations": ["Line", "Area"],
                "allowed_aggregations": ["count", "min", "max"]
            }
        elif datatype_upper == "BOOLEAN":
            return {
                "expected_analysis": ["ratio division", "binary comparison"],
                "suggested_visualizations": ["Pie", "Bar"],
                "allowed_aggregations": ["count", "mode"]
            }
        else:
            return {
                "expected_analysis": ["frequency distribution"],
                "suggested_visualizations": ["Bar", "Pie"],
                "allowed_aggregations": ["count", "mode"]
            }
