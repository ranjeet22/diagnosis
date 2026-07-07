from typing import Dict, Any
from app.schemas.visualization import ThemeConfiguration
from app.schemas.dashboard import DashboardTheme


class DashboardThemeEngine:
    """
    Translates visualization plan ThemeConfiguration settings into a detailed,
    reusable DashboardTheme specifying typography, spacings, border radii, shadows, and animations.
    """

    @staticmethod
    def build_dashboard_theme(v_theme: ThemeConfiguration) -> DashboardTheme:
        """
        Builds a comprehensive DashboardTheme matching light/dark modes.
        """
        theme_name = v_theme.theme_name.lower().strip()
        palette = v_theme.palette.colors
        background = v_theme.palette.background
        text_color = v_theme.palette.text_color

        # Default typography rules
        typography = {
            "fontFamily": v_theme.font_family,
            "fontSizeBase": 14,
            "fontWeightTitle": 600,
            "fontWeightBody": 400
        }

        # Default grid spacing
        spacing = {
            "gridGap": 16,
            "cardPadding": 20,
            "marginBase": 12
        }

        # Visual decorators based on theme styles
        if theme_name == "dark":
            border_radius = "10px"
            shadow = "0 10px 15px -3px rgba(0, 0, 0, 0.3)"
        elif theme_name == "high_contrast":
            border_radius = "0px"
            shadow = "none"
        else:
            border_radius = "8px"
            shadow = "0 4px 6px -1px rgba(0, 0, 0, 0.1)"

        # Animation bounds
        animation_settings = {
            "duration": 1000,
            "easing": "cubicOut",
            "threshold": 10
        }

        return DashboardTheme(
            theme_name=theme_name,
            palette=palette,
            background=background,
            text_color=text_color,
            typography=typography,
            spacing=spacing,
            border_radius=border_radius,
            shadow=shadow,
            animation_settings=animation_settings
        )
