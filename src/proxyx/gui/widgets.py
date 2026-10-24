import threading
from typing import Callable, Iterable

import customtkinter as ctk
from PIL import Image

from .theme import MUTED, SURFACE, font

THUMBNAIL_SIZE = (140, 195)


def run_in_background(widget: ctk.CTkBaseClass, work: Callable, on_done: Callable) -> None:
    """Run work() in a thread and call on_done(result, error) on the UI thread.

    Tkinter is not thread-safe: the callback goes through after() to get back on the main loop.
    """

    def worker():
        try:
            result, error = work(), None
        except Exception as e:
            result, error = None, e

        try:
            widget.after(0, lambda: on_done(result, error))
        except RuntimeError:
            pass  # window already closed: the result is no longer needed

    threading.Thread(target=worker, daemon=True).start()


def to_ctk_image(img: Image.Image, max_size: tuple[int, int]) -> ctk.CTkImage:
    img = img.copy()
    img.thumbnail(max_size)
    return ctk.CTkImage(light_image=img, size=img.size)


class Section(ctk.CTkFrame):
    """Panel with an uppercase title, used to group related content."""

    def __init__(self, master, title: str, padx: int = 15):
        super().__init__(master, corner_radius=12, fg_color=SURFACE)
        self.padx = padx

        ctk.CTkLabel(self, text=title.upper(), font=font(11, bold=True), text_color=MUTED).pack(anchor="w", padx=padx, pady=(12, 4))
        self._bottom_spacer = ctk.CTkFrame(self, height=10, fg_color="transparent")
        self._bottom_spacer.pack()

    def add_row(self) -> ctk.CTkFrame:
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=self.padx, pady=3, before=self._bottom_spacer)
        return row


class InfoPanel(Section):
    """Read-only list of key/value rows."""

    def __init__(self, master, title: str, keys: Iterable[str]):
        super().__init__(master, title)
        self._values = {}

        for key in keys:
            row = self.add_row()
            ctk.CTkLabel(row, text=key, font=font(13), text_color=MUTED).pack(side="left")
            self._values[key] = ctk.CTkLabel(row, text="", font=font(13, bold=True))
            self._values[key].pack(side="right")

    def set(self, key: str, value: str) -> None:
        self._values[key].configure(text=value)


class CardTile(ctk.CTkFrame):
    """Card thumbnail with a title, a subtitle and a row of actions."""

    def __init__(self, master, title: str, subtitle: str = "", image_size=THUMBNAIL_SIZE, wrap: int = 160):
        super().__init__(master, corner_radius=12)
        self.image_size = image_size

        self.image = ctk.CTkLabel(self, text="...", width=image_size[0], height=image_size[1])
        self.image.pack(padx=10, pady=(10, 5))

        ctk.CTkLabel(self, text=title, font=font(12, bold=True), wraplength=wrap).pack(padx=10)

        if subtitle:
            ctk.CTkLabel(self, text=subtitle, font=font(11), text_color=MUTED, wraplength=wrap).pack(padx=10)

        # Space below the text: hosts the actions if any are added, otherwise acts as a margin
        self._footer = ctk.CTkFrame(self, height=10, fg_color="transparent")
        self._footer.pack()
        self._actions = None

    @property
    def actions(self) -> ctk.CTkFrame:
        """Button row, created only when needed: an empty CTkFrame stays 200 px tall."""

        if self._actions is None:
            self._actions = ctk.CTkFrame(self, fg_color="transparent")
            self._actions.pack(padx=10, pady=(5, 10), before=self._footer)
            self._footer.destroy()

        return self._actions

    def set_image(self, img: Image.Image) -> None:
        self.image.configure(image=to_ctk_image(img, self.image_size), text="")


class CardGrid(ctk.CTkScrollableFrame):
    """Scrollable area that lays out its children in a fixed-column grid, centred in the available space."""

    def __init__(self, master, columns: int = 3, **kwargs):
        super().__init__(master, corner_radius=10, **kwargs)
        self.columns = columns

    def clear(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def show_message(self, text: str) -> None:
        self.clear()
        self._set_column_weights(1)
        ctk.CTkLabel(self, text=text, font=font(18), text_color=MUTED).grid(row=0, column=0, padx=20, pady=50)

    def fill(self, items: Iterable, build: Callable[[ctk.CTkFrame, object], ctk.CTkBaseClass]) -> None:
        """Clear the grid and create one widget per item with build(self, item)."""

        self.clear()
        self._set_column_weights(self.columns)

        for i, item in enumerate(items):
            build(self, item).grid(row=i // self.columns, column=i % self.columns, padx=10, pady=10, sticky="n")

    def _set_column_weights(self, columns: int) -> None:
        # Equally weighted columns: leftover space is split evenly instead of piling up on the right
        for col in range(max(columns, self.grid_size()[0])):
            active = col < columns
            self.grid_columnconfigure(col, weight=int(active), uniform="tile" if active else "")
