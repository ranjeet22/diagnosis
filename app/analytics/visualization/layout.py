from app.schemas.visualization import LayoutConfiguration


class LayoutRecommendationEngine:
    """
    Assigns logical grid positioning, responsiveness markers, section tabs,
    and dimensions to each visual dashboard element.
    """

    @staticmethod
    def recommend_layout(
        chart_id: str, 
        is_kpi: bool = False,
        priority: float = 50.0,
        section: str = "Overview",
        display_order: int = 0
    ) -> LayoutConfiguration:
        """
        Determines width, height, and display positions on the grid layout.
        """
        width = 100.0
        height = 400
        card_size = "medium"
        
        # 1. KPI elements
        if is_kpi:
            width = 25.0  # 4 KPI cards per row
            height = 150
            card_size = "small"
            return LayoutConfiguration(
                width_percent=width,
                height_px=height,
                card_size=card_size,
                grid_row=0,
                grid_col=0,
                priority_score=priority,
                responsive_behavior="fluid",
                section=section,
                display_order=display_order
            )

        # 2. Large complex plots (correlations heatmap or trend analysis)
        if "correlation" in chart_id or "heatmap" in chart_id or "trend" in chart_id or "moving_average" in chart_id:
            width = 100.0
            height = 450
            card_size = "full"
        # 3. Categorical distributions and comparisons
        elif "distribution" in chart_id or "groups" in chart_id or "vs" in chart_id:
            width = 50.0  # 2 charts per row
            height = 380
            card_size = "medium"

        # Resolve section labels
        section_resolved = section
        if section == "Overview" and not is_kpi:
            # Re-map task layouts to clinical sections
            if "trend" in chart_id or "moving_average" in chart_id:
                section_resolved = "Temporal Trends"
            elif "age" in chart_id or "gender" in chart_id:
                section_resolved = "Demographics"
            elif "disease" in chart_id or "outcome" in chart_id or "severity" in chart_id:
                section_resolved = "Clinical Analyses"
            elif "quality" in chart_id or "completeness" in chart_id:
                section_resolved = "Data Quality"

        return LayoutConfiguration(
            width_percent=width,
            height_px=height,
            card_size=card_size,
            grid_row=0,
            grid_col=0,
            priority_score=priority,
            responsive_behavior="fluid",
            section=section_resolved,
            display_order=display_order
        )
