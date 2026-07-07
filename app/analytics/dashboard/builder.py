from datetime import datetime, timezone
from typing import List, Dict, Any
from app.schemas.visualization import VisualizationPlan
from app.schemas.semantic import SemanticModel
from app.schemas.dashboard import (
    Dashboard,
    DashboardPage,
    DashboardSection,
    DashboardWidget,
    DashboardFilter,
    DashboardState,
    UserPreferences,
    DashboardMetadata
)
from app.analytics.dashboard.theme import DashboardThemeEngine
from app.analytics.dashboard.layout import LayoutEngine
from app.analytics.dashboard.widget import WidgetFactory


class DashboardBuilder:
    """
    Assembles pages, sections, themes, and global filter definitions,
    coordinating LayoutEngine and WidgetFactory to build the final Dashboard model.
    """

    @staticmethod
    def compose_dashboard(
        vis_plan: VisualizationPlan,
        semantic_model: SemanticModel
    ) -> Dashboard:
        """
        Builds the complete Dashboard model.
        """
        dataset_id = vis_plan.dataset_id

        # 1. Build Theme
        theme = DashboardThemeEngine.build_dashboard_theme(vis_plan.theme)

        # 2. Build Global Sidebar Filters based on semantic mappings
        global_filters = []
        for col_name, col in semantic_model.columns.items():
            stype = col.semantic_type
            if stype == "GENDER":
                global_filters.append(DashboardFilter(
                    filter_id="filter_gender", column=col_name, filter_type="select", label="Gender"
                ))
            elif stype == "AGE":
                global_filters.append(DashboardFilter(
                    filter_id="filter_age", column=col_name, filter_type="multiselect", label="Age Cohorts"
                ))
            elif stype == "HOSPITAL":
                global_filters.append(DashboardFilter(
                    filter_id="filter_hospital", column=col_name, filter_type="select", label="Facility Hospital"
                ))
            elif stype == "DISEASE":
                global_filters.append(DashboardFilter(
                    filter_id="filter_disease", column=col_name, filter_type="multiselect", label="Diagnosis"
                ))
            elif stype == "LOCATION":
                global_filters.append(DashboardFilter(
                    filter_id="filter_region", column=col_name, filter_type="select", label="Zipcode / Region"
                ))
            elif stype == "OUTCOME":
                global_filters.append(DashboardFilter(
                    filter_id="filter_outcome", column=col_name, filter_type="select", label="Outcome Status"
                ))
            elif stype == "SEVERITY":
                global_filters.append(DashboardFilter(
                    filter_id="filter_severity", column=col_name, filter_type="select", label="Triage Severity"
                ))
            elif stype == "ADMISSION_DATE":
                global_filters.append(DashboardFilter(
                    filter_id="filter_dates", column=col_name, filter_type="date-range", label="Timeline Period"
                ))

        # 3. Initialize Page structures
        # We group pages dynamically but populate them with layouts
        pages_defs = [
            {"id": "overview", "title": "Overview", "sec_title": "Overview Indicators"},
            {"id": "demographics", "title": "Demographics", "sec_title": "Demographic Cohorts"},
            {"id": "disease_analytics", "title": "Disease Analytics", "sec_title": "Prevalence & Caseloads"},
            {"id": "hospital_analytics", "title": "Hospital Analytics", "sec_title": "Hospitalization & Stays"},
            {"id": "trend_analysis", "title": "Trend Analysis", "sec_title": "Temporal Trends Patterns"},
            {"id": "regional_analysis", "title": "Regional Analysis", "sec_title": "Geographical Distributions"},
            {"id": "data_quality", "title": "Data Quality", "sec_title": "clean Score & Completeness Metrics"}
        ]

        pages_map: Dict[str, DashboardPage] = {}
        layouts_map: Dict[str, LayoutEngine] = {}

        for p in pages_defs:
            pid = p["id"]
            pages_map[pid] = DashboardPage(
                id=pid,
                title=p["title"],
                sections=[
                    DashboardSection(
                        id=f"sec_{pid}",
                        title=p["sec_title"],
                        description=f"Analysis of clinical factors relating to {p['title'].lower()}.",
                        widgets=[],
                        display_order=0
                    )
                ],
                display_order=len(pages_map)
            )
            # Create a separate LayoutEngine pointer per page to prevent layout overlaps across pages
            layouts_map[pid] = LayoutEngine()

        # 4. Sort and assign widgets to pages dynamically based on recommendation ID or Section
        sorted_recs = sorted(vis_plan.recommendations.values(), key=lambda r: r.layout.priority_score, reverse=True)
        
        for rec in sorted_recs:
            r_id = rec.chart_id
            layout_sec = rec.layout.section

            # Determine page mapping
            if rec.chart_config.chart_type == "card":
                pid = "overview"
            elif "demographics" in layout_sec.lower() or "age" in r_id.lower() or "gender" in r_id.lower():
                pid = "demographics"
            elif "trend" in r_id.lower() or "moving_average" in r_id.lower() or "trends" in layout_sec.lower():
                pid = "trend_analysis"
            elif "disease" in r_id.lower() or "outcome" in r_id.lower() or "prevalence" in r_id.lower():
                pid = "disease_analytics"
            elif "hospital" in r_id.lower() or "stay" in r_id.lower() or "admissions" in r_id.lower() or "discharges" in r_id.lower():
                pid = "hospital_analytics"
            elif "location" in r_id.lower() or "region" in r_id.lower() or "zipcode" in r_id.lower():
                pid = "regional_analysis"
            elif "quality" in layout_sec.lower() or "quality" in r_id.lower() or "completeness" in r_id.lower():
                pid = "data_quality"
            else:
                pid = "overview"

            # Allocate position in page
            engine = layouts_map[pid]
            grid_layout = engine.allocate_coordinates(
                card_size=rec.layout.card_size,
                priority=int(rec.layout.priority_score)
            )

            # Create and append widget
            widget = WidgetFactory.create_widget(dataset_id=dataset_id, rec=rec, grid_layout=grid_layout)
            pages_map[pid].sections[0].widgets.append(widget)

        # 5. Filter out empty pages to present a clean visual dashboard
        active_pages = []
        order = 0
        for p in pages_defs:
            pid = p["id"]
            page = pages_map[pid]
            if len(page.sections[0].widgets) > 0:
                page.display_order = order
                active_pages.append(page)
                order += 1

        # 6. Initialize State & Preferences
        state = DashboardState(
            collapsed_widgets=[],
            expanded_widgets=[],
            selected_filters={},
            theme=theme.theme_name,
            user_layout={},
            hidden_widgets=[],
            pinned_widgets=[],
            last_refresh=datetime.now(timezone.utc)
        )

        preferences = UserPreferences(
            theme=theme.theme_name,
            layout_density="comfortable",
            pinned_widgets=[]
        )

        metadata = DashboardMetadata(
            dataset_id=dataset_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            version="1.0.0"
        )

        return Dashboard(
            metadata=metadata,
            theme=theme,
            global_filters=global_filters,
            pages=active_pages,
            state=state,
            user_preferences=preferences
        )
