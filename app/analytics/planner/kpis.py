import os
import json
from typing import List, Dict, Any
from app.schemas.semantic import SemanticModel
from app.schemas.profile import DatasetProfile
from app.schemas.plan import KPIPlan
from app.core.logging import logger


class KPIPlanner:
    """
    Determines which high-level KPIs can be computed based on mapped clinical concepts,
    loading configurations dynamically from kpi_rules.json.
    """
    def __init__(self, rules_path: str = None) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        default_rules = os.path.abspath(
            os.path.join(current_dir, "..", "..", "config", "semantic", "kpi_rules.json")
        )
        self.rules_path = rules_path or default_rules
        self.kpi_rules: List[Dict[str, Any]] = []
        self._load_rules()

    def _load_rules(self) -> None:
        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    self.kpi_rules = json.load(f)
                logger.debug(f"KPIPlanner: Loaded KPI rules from {self.rules_path}")
            else:
                logger.warning(f"KPIPlanner rules file missing at: {self.rules_path}")
        except Exception as e:
            logger.error(f"Failed to load KPI rules config file: {e}")

    def plan_kpis(self, model: SemanticModel, profile: DatasetProfile) -> List[KPIPlan]:
        """
        Builds list of KPIs based on column availability in SemanticModel and kpi_rules config.
        """
        kpis: List[KPIPlan] = []

        # Find columns by semantic concept
        concept_cols: Dict[str, List[str]] = {}
        for norm_name, col in model.columns.items():
            sem_type = col.semantic_type
            if sem_type != "UNKNOWN":
                if sem_type not in concept_cols:
                    concept_cols[sem_type] = []
                concept_cols[sem_type].append(norm_name)

        # Process each rule dynamically
        for rule in self.kpi_rules:
            trigger = rule.get("concept_trigger")
            add_triggers = rule.get("additional_triggers", [])
            
            # 1. Check if trigger conditions are met
            if trigger is None:
                # Always triggers (general/quality metrics)
                req_cols = []
                kpis.append(KPIPlan(
                    name=rule["name"],
                    description=rule["description"],
                    formula=rule["formula"],
                    required_columns=req_cols,
                    aggregation_type=rule["aggregation_type"],
                    priority=rule["priority"],
                    dashboard_placement=rule["dashboard_placement"]
                ))
            else:
                # Requires trigger concept to be present in dataset
                if trigger in concept_cols:
                    # Verify additional dependencies if defined
                    if all(c in concept_cols for c in add_triggers):
                        primary_col = concept_cols[trigger][0]
                        req_cols = [primary_col]
                        for c in add_triggers:
                            req_cols.append(concept_cols[c][0])
                            
                        kpis.append(KPIPlan(
                            name=rule["name"],
                            description=rule["description"],
                            formula=rule["formula"],
                            required_columns=req_cols,
                            aggregation_type=rule["aggregation_type"],
                            priority=rule["priority"],
                            dashboard_placement=rule["dashboard_placement"]
                        ))

        return kpis
