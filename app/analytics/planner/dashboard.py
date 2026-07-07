from typing import List, Dict, Any
from app.schemas.plan import DashboardSection, KPIPlan, AnalysisTask


class DashboardPlanner:
    """
    Dynamically orchestrates dashboard layout grids, grouping planned tasks
    and KPIs into thematic dashboard sections.
    """

    @staticmethod
    def plan_dashboard_layout(
        kpis: List[KPIPlan],
        tasks: List[AnalysisTask],
        comparisons: List[Any]
    ) -> List[DashboardSection]:
        """
        Groups tasks and KPIs into dashboard sections.
        """
        # Define layout mappings
        sections_dict: Dict[str, DashboardSection] = {
            "Overview": DashboardSection(
                section_name="Overview",
                description="High-level dashboard overview presenting vital clinical indicators and workload metrics.",
                kpis=[],
                tasks=[]
            ),
            "Demographics": DashboardSection(
                section_name="Demographics",
                description="Demographic breakdowns including age cohorts, gender splits, and demographic outcomes.",
                kpis=[],
                tasks=[]
            ),
            "Disease Analytics": DashboardSection(
                section_name="Disease Analytics",
                description="Detailed diagnostic breakdowns, caseload distributions, and rankings.",
                kpis=[],
                tasks=[]
            ),
            "Temporal Trends": DashboardSection(
                section_name="Temporal Trends",
                description="Time-series analyses mapping admission caseload spikes, rolling averages, and growth trajectories.",
                kpis=[],
                tasks=[]
            ),
            "Hospital Analytics": DashboardSection(
                section_name="Hospital Analytics",
                description="Hospital performance comparisons, caseload volume distribution, and outcome correlations.",
                kpis=[],
                tasks=[]
            ),
            "Regional Analytics": DashboardSection(
                section_name="Regional Analytics",
                description="Geographical maps comparing patient zipcode distributions and caseload hot-spots.",
                kpis=[],
                tasks=[]
            ),
            "Outcome Analytics": DashboardSection(
                section_name="Outcome Analytics",
                description="Clinical recovery rates, mortality ratios, and outcomes correlations.",
                kpis=[],
                tasks=[]
            ),
            "Severity Analytics": DashboardSection(
                section_name="Severity Analytics",
                description="Triage severity profiles and high-acuity patient statistics.",
                kpis=[],
                tasks=[]
            ),
            "Data Quality": DashboardSection(
                section_name="Data Quality",
                description="Aggregated data completeness metrics and file validation scorecards.",
                kpis=[],
                tasks=[]
            )
        }

        # 1. Allocate KPIs
        for kpi in kpis:
            placement = kpi.dashboard_placement
            if placement in sections_dict:
                sections_dict[placement].kpis.append(kpi.name)
            else:
                sections_dict["Overview"].kpis.append(kpi.name)

        # 2. Allocate Analysis Tasks
        for task in tasks:
            tid = task.task_id
            
            # Map task ID keyword to target dashboard section
            if "admission_trend" in tid or "moving_average" in tid or "growth_rate" in tid or "trend" in tid:
                sections_dict["Temporal Trends"].tasks.append(tid)
            elif "age" in tid or "gender" in tid:
                sections_dict["Demographics"].tasks.append(tid)
            elif "disease" in tid or "ranking" in tid or "diagnosis" in tid:
                sections_dict["Disease Analytics"].tasks.append(tid)
            elif "hospital" in tid:
                sections_dict["Hospital Analytics"].tasks.append(tid)
            elif "location" in tid or "regional" in tid or "heatmap" in tid:
                sections_dict["Regional Analytics"].tasks.append(tid)
            elif "outcome" in tid or "recovery" in tid or "mortality" in tid:
                sections_dict["Outcome Analytics"].tasks.append(tid)
            elif "severity" in tid:
                sections_dict["Severity Analytics"].tasks.append(tid)
            else:
                sections_dict["Overview"].tasks.append(tid)

        # 3. Add Comparison Plans to respective sections
        # In comparison plans, we represent them by their names.
        # Since comparison names like 'Disease vs Age' compare two things, we can add them to
        # 'Demographics' or 'Disease Analytics' based on the name.
        for comp in comparisons:
            name = comp.name
            # Treat comparison as a virtual task in sections
            if "Age" in name or "Gender" in name:
                sections_dict["Demographics"].tasks.append(name)
            elif "Hospital" in name:
                sections_dict["Hospital Analytics"].tasks.append(name)
            elif "Region" in name or "Location" in name:
                sections_dict["Regional Analytics"].tasks.append(name)
            elif "Outcome" in name:
                sections_dict["Outcome Analytics"].tasks.append(name)
            elif "Date" in name:
                sections_dict["Temporal Trends"].tasks.append(name)
            else:
                sections_dict["Overview"].tasks.append(name)

        # Filter out empty sections to keep the dashboard clean
        active_sections = [
            sec for sec in sections_dict.values()
            if len(sec.kpis) > 0 or len(sec.tasks) > 0
        ]

        return active_sections
class FilterPlanner:
    """
    Decides which filter dropdown panels should be displayed on the dashboard
    based on the presence of categorical columns.
    """
    @staticmethod
    def plan_filters(model: SemanticModel) -> List[Any]:
        from app.schemas.plan import FilterDefinition
        filters = []
        
        # Group columns by semantic type
        concept_cols = {}
        for norm_name, col in model.columns.items():
            sem_type = col.semantic_type
            if sem_type != "UNKNOWN":
                if sem_type not in concept_cols:
                    concept_cols[sem_type] = []
                concept_cols[sem_type].append(norm_name)
                
        # Recommended filters
        filter_specs = [
            ("AGE", "range", "Age Range"),
            ("GENDER", "multiselect", "Gender"),
            ("DISEASE", "multiselect", "Diagnosis"),
            ("HOSPITAL", "multiselect", "Hospital"),
            ("LOCATION", "multiselect", "Region"),
            ("ADMISSION_DATE", "date-range", "Date Range"),
            ("SEVERITY", "multiselect", "Severity"),
            ("OUTCOME", "multiselect", "Outcome")
        ]
        
        for concept, f_type, label in filter_specs:
            if concept in concept_cols:
                col_name = concept_cols[concept][0]
                filters.append(FilterDefinition(
                    column=col_name,
                    filter_type=f_type,
                    label=label
                ))
        return filters
