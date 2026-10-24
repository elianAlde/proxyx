import io
import time
from typing import Callable

import customtkinter as ctk
from PIL import Image

from ..scryfall import download_card_image, fetch_image, get_prints, search_cards
from .theme import GHOST_BUTTON, MUTED, font
from .widgets import CardGrid, CardTile, run_in_background

# Delay between thumbnail downloads, to avoid hammering Scryfall
THUMBNAIL_STAGGER_S = 0.05

OnAdd = Callable[[str, str], None]


class CardBrowserDialog(ctk.CTkToplevel):
    """Modal window showing a grid of Scryfall cards that can be added to the sheet.

    Subclasses decide how cards are fetched and how each one is shown (build_tile).
    """

    def __init__(self, master, title: str, on_add: OnAdd):
        super().__init__(master)
        self.on_add = on_add

        self.title(title)
        self.geometry("700x600")
        self.transient(master)
        self.grab_set()

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=20, pady=(20, 0))

        self.grid_view = CardGrid(self)
        self.grid_view.pack(fill="both", expand=True, padx=20, pady=10)

        self.status = ctk.CTkLabel(self, text="", font=font(13), text_color=MUTED)
        self.status.pack(pady=(0, 15))

    def show_cards(self, cards: list[dict]) -> None:
        self.grid_view.fill(enumerate(cards), lambda parent, item: self._tile(parent, *item))

    def _tile(self, parent, index: int, card: dict) -> CardTile:
        tile = self.build_tile(parent, card)
        self._load_thumbnail(card, tile, delay=index * THUMBNAIL_STAGGER_S)
        return tile

    def build_tile(self, parent, card: dict) -> CardTile:
        raise NotImplementedError

    def _load_thumbnail(self, card: dict, tile: CardTile, delay: float) -> None:
        def work():
            time.sleep(delay)
            data = fetch_image(card, version="small")
            return Image.open(io.BytesIO(data)) if data else None

        def done(img, error):
            if img and tile.winfo_exists():
                tile.set_image(img)

        run_in_background(self, work, done)

    def add_card(self, card: dict, label: str) -> None:
        self.status.configure(text=f"Downloading {label}...")

        def done(path, error):
            if error:
                self.status.configure(text=f"Error: {error}")
                return

            self.on_add(path, card.get("name", label))
            self.status.configure(text=f"Added: {label}")

        run_in_background(self, lambda: download_card_image(card), done)


class SearchDialog(CardBrowserDialog):

    def __init__(self, master, on_add: OnAdd):
        super().__init__(master, "Search Scryfall", on_add)

        self.entry = ctk.CTkEntry(self.header, placeholder_text="Card name (e.g. Lightning Bolt)", height=40, font=font(14))
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda _: self.search())
        self.entry.focus()

        ctk.CTkButton(self.header, text="Search", width=100, command=self.search).pack(side="left")

        hint = ctk.CTkLabel(self, text="Search by English card name", font=font(11), text_color=MUTED)
        hint.pack(anchor="w", padx=20, pady=(5, 0), after=self.header)

    def search(self) -> None:
        query = self.entry.get().strip()

        if not query:
            return

        self.grid_view.clear()
        self.status.configure(text="Searching...")

        def done(cards, error):
            if error:
                self.status.configure(text=f"Error: {error}")
            elif not cards:
                self.status.configure(text="No cards found.")
            else:
                self.status.configure(text=f"{len(cards)} result(s)")
                self.show_cards(cards)

        run_in_background(self, lambda: search_cards(query), done)

    def build_tile(self, parent, card: dict) -> CardTile:
        name = card.get("name", "Unknown")
        tile = CardTile(parent, name, card.get("set_name", ""))

        ctk.CTkButton(tile.actions, text="+ Add", width=90, command=lambda: self.add_card(card, name)).pack(side="left", padx=(0, 5))
        ctk.CTkButton(tile.actions, text="Versions", width=45, command=lambda: VersionPicker(self, card, self.on_add), **GHOST_BUTTON).pack(side="left")

        return tile


class VersionPicker(CardBrowserDialog):
    """Lists every printing of a card so a specific one can be picked."""

    def __init__(self, master, card: dict, on_add: OnAdd):
        super().__init__(master, f"Versions - {card.get('name', 'Card')}", on_add)

        self.status.configure(text="Loading printings...")

        def done(prints, error):
            if error:
                self.status.configure(text=f"Error: {error}")
                return

            self.status.configure(text=f"{len(prints)} printing(s) — pick one to add")
            self.show_cards(prints)

        run_in_background(self, lambda: get_prints(card), done)

    def build_tile(self, parent, card: dict) -> CardTile:
        set_name = card.get("set_name", "")
        details = f"#{card.get('collector_number', '?')} · {card.get('released_at', '')}"
        tile = CardTile(parent, set_name, details)

        label = f"{card.get('name')} ({set_name})"
        ctk.CTkButton(tile.actions, text="+ Add", width=140, command=lambda: self.add_card(card, label)).pack()

        return tile
