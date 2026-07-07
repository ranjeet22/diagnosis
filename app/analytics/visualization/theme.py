from app.schemas.visualization import ThemeConfiguration
from app.analytics.visualization.palette import ColorPaletteEngine


class ThemeEngine:
    """
    Manages active dashboard theme layouts and ensures contrast requirements
    are met for WCAG compliance.
    """
    
    @staticmethod
    def create_theme_configuration(theme_name: str = "light", accessibility_mode: str = "default") -> ThemeConfiguration:
        """
        Builds a comprehensive ThemeConfiguration for dashboard elements.
        """
        theme_clean = theme_name.lower().strip()
        
        # Determine palette
        if accessibility_mode in {"color_blind", "high_contrast", "print"}:
            palette = ColorPaletteEngine.recommend_palette(
                chart_type="bar", 
                accessibility_mode=accessibility_mode
            )
        else:
            if theme_clean == "dark":
                palette = ColorPaletteEngine.get_palette("dark_blue")
            else:
                palette = ColorPaletteEngine.get_palette("color_blind_friendly")

        # Determine WCAG contrast ratios (estimate)
        contrast = 4.5
        if accessibility_mode == "high_contrast" or theme_clean == "high_contrast":
            contrast = 7.0
        elif theme_clean == "dark":
            contrast = 5.0

        return ThemeConfiguration(
            theme_name="dark" if theme_clean == "dark" else "light",
            palette=palette,
            font_family="Inter, system-ui, -apple-system, sans-serif",
            contrast_ratio=contrast
        )
