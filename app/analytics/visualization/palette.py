from typing import List
from app.schemas.visualization import ColorPalette


class ColorPaletteEngine:
    """
    Deterministically recommends the most appropriate color palettes based on
    chart types, semantic roles, and accessibility options.
    """
    
    PALETTES = {
        "medical_blue": ColorPalette(
            name="Medical Blue",
            colors=["#1e3a8a", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"],
            background="#ffffff",
            text_color="#1f2937"
        ),
        "medical_green": ColorPalette(
            name="Medical Green",
            colors=["#065f46", "#10b981", "#34d399", "#6ee7b7", "#a7f3d0"],
            background="#ffffff",
            text_color="#1f2937"
        ),
        "professional_gray": ColorPalette(
            name="Professional Gray",
            colors=["#374151", "#4b5563", "#6b7280", "#9ca3af", "#d1d5db"],
            background="#ffffff",
            text_color="#1f2937"
        ),
        "color_blind_friendly": ColorPalette(
            name="Color Blind Friendly (Okabe-Ito)",
            colors=["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"],
            background="#ffffff",
            text_color="#1f2937"
        ),
        "high_contrast": ColorPalette(
            name="High Contrast",
            colors=["#000000", "#ffff00", "#00ffff", "#ff00ff", "#ffffff"],
            background="#000000",
            text_color="#ffffff"
        ),
        "print_friendly": ColorPalette(
            name="Print Friendly",
            colors=["#000000", "#404040", "#808080", "#c0c0c0", "#e0e0e0"],
            background="#ffffff",
            text_color="#000000"
        ),
        # Dark palettes
        "dark_blue": ColorPalette(
            name="Dark Blue Theme",
            colors=["#60a5fa", "#3b82f6", "#1e3a8a", "#1d4ed8", "#93c5fd"],
            background="#1e293b",
            text_color="#f8fafc"
        )
    }

    @classmethod
    def get_palette(cls, palette_name: str) -> ColorPalette:
        """Retrieves a palette by name, falling back to colorblind friendly."""
        name_clean = palette_name.lower().replace(" ", "_")
        return cls.PALETTES.get(name_clean, cls.PALETTES["color_blind_friendly"])

    @classmethod
    def recommend_palette(cls, chart_type: str, concept: str = "", accessibility_mode: str = "default") -> ColorPalette:
        """
        Recommends the best palette based on chart type, medical concept, and access preferences.
        """
        if accessibility_mode == "color_blind":
            return cls.PALETTES["color_blind_friendly"]
        elif accessibility_mode == "high_contrast":
            return cls.PALETTES["high_contrast"]
        elif accessibility_mode == "print":
            return cls.PALETTES["print_friendly"]

        # Medical concepts mapping
        if concept in {"PATIENT_ID", "AGE", "GENDER", "BMI"}:
            return cls.PALETTES["medical_blue"]
        elif concept in {"OUTCOME", "DISEASE", "ADMISSION_DATE", "DISCHARGE_DATE"}:
            return cls.PALETTES["medical_green"]
            
        # Chart-type recommendations
        if chart_type in {"line", "boxplot"}:
            return cls.PALETTES["medical_blue"]
        elif chart_type in {"pie", "bar"}:
            return cls.PALETTES["color_blind_friendly"]
            
        return cls.PALETTES["professional_gray"]
