import tkinter as tk
from pathlib import Path
from typing import Callable

import customtkinter as ctk

from ..config import CARD_HEIGHT_RANGE, CARD_WIDTH_RANGE, DPI_OPTIONS, PAGE_SIZES, SPACING_OPTIONS, Config, max_grid, save_config
from .theme import ERROR, GHOST_BUTTON, MUTED, PRIMARY_BUTTON, SUCCESS, font
from .widgets import Section


def in_range(value: float, bounds: tuple[float, float]) -> bool:
    return bounds[0] <= value <= bounds[1]


def page_label(name: str, size: tuple[float, float]) -> str:
    return f"{name} ({size[0]:g} × {size[1]:g} mm)"


class SettingsPage(ctk.CTkFrame):
    """Edits Config through guided controls and saves it to settings_path.

    Columns and rows only offer values that fit the chosen page and card size, so the
    user cannot build a grid that overflows the sheet.
    """

    def __init__(self, master: tk.Misc, settings_path: Path, on_back: Callable[[], None], on_save: Callable[[Config], None]):
        super().__init__(master, fg_color="transparent")
        self.settings_path = settings_path
        self.on_save = on_save
        self.pages: dict[str, tuple[float, float]] = {}
        self.pending: Config | None = None

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 15))
        ctk.CTkButton(top, text="← Back", width=100, command=on_back, **GHOST_BUTTON).pack(side="left")
        ctk.CTkLabel(top, text="Settings", font=font(24, bold=True)).pack(side="left", padx=20)

        body = ctk.CTkScrollableFrame(self, corner_radius=15)
        body.pack(fill="both", expand=True)

        page = self._section(body, "Page")
        self.page_menu = self._option(page, "Paper size", [], width=220)

        card = self._section(body, "Card")
        self.card_width = self._entry(card, f"Width (mm, {CARD_WIDTH_RANGE[0]}–{CARD_WIDTH_RANGE[1]})")
        self.card_height = self._entry(card, f"Height (mm, {CARD_HEIGHT_RANGE[0]}–{CARD_HEIGHT_RANGE[1]})")
        hint = "A standard Magic card is 63 × 88 mm. Change it only to compensate for a printer that scales the page."
        ctk.CTkLabel(card.add_row(), text=hint, font=font(12), text_color=MUTED, wraplength=520, justify="left").pack(side="left")

        grid = self._section(body, "Grid")
        self.cols_menu = self._option(grid, "Columns", ["1"])
        self.rows_menu = self._option(grid, "Rows", ["1"])
        self.spacing = self._segmented(grid, "Space between cards (mm)")

        export = self._section(body, "Export")
        self.dpi = self._segmented(export, "Resolution (DPI)")

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", pady=(15, 0))

        self.status = ctk.CTkLabel(footer, text="", font=font(13), text_color=MUTED, wraplength=600, justify="left")
        self.status.pack(side="left")

        self.save_button = ctk.CTkButton(footer, text="Save", width=120, height=40, font=font(14, bold=True), command=self.save, **PRIMARY_BUTTON)
        self.save_button.pack(side="right")
        ctk.CTkButton(footer, text="Restore defaults", width=150, height=40, command=lambda: self.fill(Config()), **GHOST_BUTTON).pack(side="right", padx=10)

    def _section(self, parent: tk.Misc, title: str) -> Section:
        section = Section(parent, title, padx=20)
        section.pack(fill="x", padx=20, pady=(20, 0))
        return section

    def _option(self, section: Section, label: str, values: list[str], width: int = 140) -> ctk.CTkOptionMenu:
        row = section.add_row()
        ctk.CTkLabel(row, text=label, font=font(14)).pack(side="left")
        menu = ctk.CTkOptionMenu(row, values=values, width=width, command=lambda _: self.refresh())
        menu.pack(side="right")
        return menu

    def _segmented(self, section: Section, label: str) -> ctk.CTkSegmentedButton:
        row = section.add_row()
        ctk.CTkLabel(row, text=label, font=font(14)).pack(side="left")
        button = ctk.CTkSegmentedButton(row, values=["-"], command=lambda _: self.refresh())
        button.pack(side="right")
        return button

    def _entry(self, section: Section, label: str) -> ctk.CTkEntry:
        row = section.add_row()
        ctk.CTkLabel(row, text=label, font=font(14)).pack(side="left")
        entry = ctk.CTkEntry(row, width=140, justify="right")
        entry.pack(side="right")
        entry.bind("<KeyRelease>", lambda _: self.refresh())
        return entry

    def open(self, config: Config) -> None:
        self.fill(config)
        self.status.configure(text=f"File: {self.settings_path}", text_color=MUTED)

    def fill(self, config: Config) -> None:
        current = (config.page_width_mm, config.page_height_mm)
        self.pages = {page_label(name, size): size for name, size in PAGE_SIZES.items()}

        # A page size set by hand in settings.json stays selectable instead of being lost
        if current not in self.pages.values():
            self.pages[page_label("Custom", current)] = current

        self.page_menu.configure(values=list(self.pages))
        self.page_menu.set(next(label for label, size in self.pages.items() if size == current))

        for entry, value in ((self.card_width, config.card_width_mm), (self.card_height, config.card_height_mm)):
            entry.delete(0, "end")
            entry.insert(0, f"{value:g}")

        # A value set by hand in settings.json is added to the choices instead of being lost
        for button, options, value in ((self.dpi, DPI_OPTIONS, config.dpi), (self.spacing, SPACING_OPTIONS, config.card_spacing_mm)):
            button.configure(values=[f"{v:g}" for v in sorted({*options, value})])
            button.set(f"{value:g}")

        self.cols_menu.set(str(config.cols))
        self.rows_menu.set(str(config.rows))
        self.refresh()

    def refresh(self) -> None:
        """Re-validate the form: limit the grid to what fits and enable Save only for a valid config."""

        self.pending = None
        self.save_button.configure(state="disabled")

        try:
            # Accept a comma as decimal separator too
            card_w = float(self.card_width.get().replace(",", "."))
            card_h = float(self.card_height.get().replace(",", "."))
        except ValueError:
            self.status.configure(text="Card width and height must be numbers.", text_color=ERROR)
            return

        page_w, page_h = self.pages[self.page_menu.get()]
        spacing = float(self.spacing.get())

        # Limit the grid only for a card size in range: an invalid one is reported below by Config
        if in_range(card_w, CARD_WIDTH_RANGE) and in_range(card_h, CARD_HEIGHT_RANGE):
            for menu, limit in zip((self.cols_menu, self.rows_menu), max_grid(page_w, page_h, card_w, card_h, spacing)):
                menu.configure(values=[str(n) for n in range(1, limit + 1)])

                # Keep the user's choice when it still fits, otherwise fall back to the largest grid that does
                if int(menu.get()) > limit:
                    menu.set(str(limit))

        try:
            grid = {"cols": int(self.cols_menu.get()), "rows": int(self.rows_menu.get())}
            self.pending = Config(dpi=int(self.dpi.get()), page_width_mm=page_w, page_height_mm=page_h, card_width_mm=card_w, card_height_mm=card_h, card_spacing_mm=spacing, **grid)
        except ValueError as e:
            self.status.configure(text=str(e), text_color=ERROR)
            return

        self.status.configure(text=f"{self.pending.cards_per_page} cards per page · File: {self.settings_path}", text_color=MUTED)
        self.save_button.configure(state="normal")

    def save(self) -> None:
        if self.pending is None:
            return

        try:
            save_config(self.pending, self.settings_path)
        except OSError as e:
            self.status.configure(text=f"Error: {e}", text_color=ERROR)
            return

        self.on_save(self.pending)
        self.status.configure(text="Saved ✓", text_color=SUCCESS)
