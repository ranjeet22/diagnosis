from app.schemas.visualization import InteractionConfiguration


class InteractionPlanner:
    """
    Recommends clicking cross-filters, zoom bounds, hover triggers,
    and visual brush ranges for ECharts elements.
    """

    @staticmethod
    def plan_interactions(chart_type: str) -> InteractionConfiguration:
        """
        Builds interaction config based on the chart family.
        """
        zoom = False
        pan = False
        brush = False
        cross_filter = False
        click_action = None
        interactions = ["hover"]

        if chart_type == "line":
            zoom = True
            pan = True
            brush = True
            interactions.extend(["zoom", "pan", "brush", "reset"])
        elif chart_type in {"bar", "pie"}:
            cross_filter = True
            click_action = "filter"
            interactions.extend(["click_filter", "tooltip_show"])
        elif chart_type in {"scatter", "heatmap"}:
            zoom = True
            pan = True
            brush = True
            interactions.extend(["zoom", "pan", "brush", "reset"])

        return InteractionConfiguration(
            zoom=zoom,
            pan=pan,
            brush=brush,
            hover=True,
            click_action=click_action,
            cross_filter=cross_filter,
            drill_down=False,
            supported_interactions=interactions
        )
