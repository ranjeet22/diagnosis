import os
import json
from typing import Dict, List, Any
from app.schemas.semantic import SemanticModel
from app.schemas.plan import ComparisonPlan
from app.core.logging import logger


class AnalysisRuleEngine:
    """
    Scans the Semantic Model to deterministically plan execution tasks
    (e.g., disease trends, age distributions) by loading dynamic rules configuration.
    """
    def __init__(self, rules_path: str = None) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_rules = os.path.abspath(
            os.path.join(current_dir, "..", "..", "config", "semantic", "task_rules.json")
        )
        self.rules_path = rules_path or default_rules
        self.rules_db: Dict[str, Any] = {}
        self._load_rules()

    def _load_rules(self) -> None:
        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    self.rules_db = json.load(f)
                logger.debug(f"AnalysisRuleEngine: Loaded task rules from {self.rules_path}")
            else:
                logger.warning(f"AnalysisRuleEngine rules file missing at: {self.rules_path}")
        except Exception as e:
            logger.error(f"Failed to load AnalysisRuleEngine config rules: {e}")

    def plan_analysis_tasks(self, model: SemanticModel) -> List[Dict[str, Any]]:
        """
        Generates list of dictionaries detailing the AnalysisTasks to create.
        """
        tasks: List[Dict[str, Any]] = []

        # Map semantic types to list of normalized column names in this dataset
        concept_cols: Dict[str, List[str]] = {}
        for norm_name, col in model.columns.items():
            sem_type = col.semantic_type
            if sem_type != "UNKNOWN":
                if sem_type not in concept_cols:
                    concept_cols[sem_type] = []
                concept_cols[sem_type].append(norm_name)

        # 1. Process Concept-Triggered Tasks
        for concept, task_list in self.rules_db.items():
            if concept == "conditional":
                continue
                
            # If the concept is present in the dataset
            if concept in concept_cols:
                primary_col = concept_cols[concept][0]
                for task_rule in task_list:
                    # Create a copy to prevent mutation of the cached config
                    task = dict(task_rule)
                    task["required_columns"] = [primary_col]
                    tasks.append(task)

        # 2. Process Conditional/Multi-Concept Tasks
        conditionals = self.rules_db.get("conditional", [])
        for cond_rule in conditionals:
            req_concepts = cond_rule.get("required_concepts", [])
            
            # Check if all required concepts are present
            if all(c in concept_cols for c in req_concepts):
                resolved_cols = [concept_cols[c][0] for c in req_concepts]
                task = dict(cond_rule)
                # Remove config-only schema keys
                task.pop("required_concepts", None)
                task["required_columns"] = resolved_cols
                tasks.append(task)

        return tasks


class ComparisonPlanner:
    """
    Decides which cross-variable clinical comparison analyses should be executed
    based on the presence of matching semantic concept pairs configured in rules file.
    """
    def __init__(self, rules_path: str = None) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_rules = os.path.abspath(
            os.path.join(current_dir, "..", "..", "config", "semantic", "comparison_rules.json")
        )
        self.rules_path = rules_path or default_rules
        self.rules_db: List[Dict[str, Any]] = []
        self._load_rules()

    def _load_rules(self) -> None:
        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    self.rules_db = json.load(f)
                logger.debug(f"ComparisonPlanner: Loaded comparison rules from {self.rules_path}")
            else:
                logger.warning(f"ComparisonPlanner rules file missing at: {self.rules_path}")
        except Exception as e:
            logger.error(f"Failed to load ComparisonPlanner config rules: {e}")

    def plan_comparisons(self, model: SemanticModel) -> List[ComparisonPlan]:
        """
        Identifies cross-tab comparisons based on rules config.
        """
        comparisons: List[ComparisonPlan] = []
        
        # Group columns by semantic type
        concept_cols: Dict[str, List[str]] = {}
        for norm_name, col in model.columns.items():
            sem_type = col.semantic_type
            if sem_type != "UNKNOWN":
                if sem_type not in concept_cols:
                    concept_cols[sem_type] = []
                concept_cols[sem_type].append(norm_name)

        # Evaluate comparison rules
        for rule in self.rules_db:
            c_a = rule["concept_a"]
            c_b = rule["concept_b"]
            
            if c_a in concept_cols and c_b in concept_cols:
                col_a = concept_cols[c_a][0]
                col_b = concept_cols[c_b][0]
                comparisons.append(ComparisonPlan(
                    name=rule["name"],
                    columns=[col_a, col_b],
                    comparison_type=rule["comparison_type"]
                ))

        return comparisons
