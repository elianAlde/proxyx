import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

FONT_FAMILY = "Segoe UI"

# customtkinter picks from (light, dark) tuples based on the active appearance mode
SURFACE = ("gray85", "gray20")
MUTED = "gray"
SUCCESS = "#16a34a"
ERROR = "#dc2626"

PRIMARY_BUTTON = {"fg_color": SUCCESS, "hover_color": "#15803d"}
DANGER_BUTTON = {"fg_color": ERROR, "hover_color": "#b91c1c"}
ACCENT_BUTTON = {"fg_color": "#7c3aed", "hover_color": "#6d28d9"}
DANGER_OUTLINE_BUTTON = {"fg_color": "transparent", "border_width": 1, "border_color": ERROR, "text_color": ERROR, "hover_color": ("#fde2e2", "#3b1a1a")}
GHOST_BUTTON = {"fg_color": "transparent", "border_width": 1, "text_color": ("gray10", "gray90")}


def font(size: int, bold: bool = False) -> tuple[str, int] | tuple[str, int, str]:
    return (FONT_FAMILY, size, "bold") if bold else (FONT_FAMILY, size)
