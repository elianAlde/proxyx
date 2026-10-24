from dataclasses import fields
from pathlib import Path
from typing import Callable

import customtkinter as ctk

from ..config import Config, save_config
from .theme import ERROR, GHOST_BUTTON, MUTED, PRIMARY_BUTTON, SUCCESS, font
from .widgets import Section

# Campi di Config mostrati nella pagina, raggruppati per sezione: (campo, etichetta)
SECTIONS = [
    ("Page", [("page_width_mm", "Width (mm)"), ("page_height_mm", "Height (mm)")]),
    ("Grid", [("cols", "Columns"), ("rows", "Rows")]),
    ("Card", [("card_width_mm", "Width (mm)"), ("card_height_mm", "Height (mm)")]),
    ("Export", [("dpi", "Resolution (DPI)")]),
]


class SettingsPage(ctk.CTkFrame):
    """Pagina che modifica Config e la salva su settings_path."""

    def __init__(self, master, settings_path: Path, on_back: Callable[[], None], on_save: Callable[[Config], None]):
        super().__init__(master, fg_color="transparent")
        self.settings_path = settings_path
        self.on_save = on_save
        self.entries: dict[str, ctk.CTkEntry] = {}

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 15))
        ctk.CTkButton(top, text="← Back", width=100, command=on_back, **GHOST_BUTTON).pack(side="left")
        ctk.CTkLabel(top, text="Settings", font=font(24, bold=True)).pack(side="left", padx=20)

        body = ctk.CTkScrollableFrame(self, corner_radius=15)
        body.pack(fill="both", expand=True)

        for title, items in SECTIONS:
            section = Section(body, title, padx=20)
            section.pack(fill="x", padx=20, pady=(20, 0))

            for name, label in items:
                row = section.add_row()
                ctk.CTkLabel(row, text=label, font=font(14)).pack(side="left")
                self.entries[name] = ctk.CTkEntry(row, width=140, justify="right")
                self.entries[name].pack(side="right")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", pady=(15, 0))

        self.status = ctk.CTkLabel(footer, text="", font=font(13), text_color=MUTED)
        self.status.pack(side="left")

        ctk.CTkButton(footer, text="Save", width=120, height=40, font=font(14, bold=True), command=self.save, **PRIMARY_BUTTON).pack(side="right")
        ctk.CTkButton(footer, text="Restore defaults", width=150, height=40, command=lambda: self.fill(Config()), **GHOST_BUTTON).pack(side="right", padx=10)

    def fill(self, config: Config) -> None:
        for name, entry in self.entries.items():
            entry.delete(0, "end")
            entry.insert(0, f"{getattr(config, name):g}")

    def open(self, config: Config) -> None:
        self.fill(config)
        self.status.configure(text=f"File: {self.settings_path}", text_color=MUTED)

    def save(self) -> None:
        types = {f.name: f.type for f in fields(Config)}
        values = {}

        for name, entry in self.entries.items():
            # Accetta anche la virgola come separatore decimale
            raw = entry.get().strip().replace(",", ".")

            try:
                value = types[name](raw)
            except ValueError:
                value = None

            if value is None or value <= 0:
                self.status.configure(text=f"Invalid value for {name}: '{raw}'", text_color=ERROR)
                return

            values[name] = value

        config = Config(**values)

        try:
            save_config(config, self.settings_path)
        except OSError as e:
            self.status.configure(text=f"Error: {e}", text_color=ERROR)
            return

        self.on_save(config)
        self.status.configure(text="Saved ✓", text_color=SUCCESS)
