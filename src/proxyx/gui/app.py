import os
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from ..config import DEFAULT_SETTINGS_PATH, Config
from ..generator import ProxyGenerator
from .dialogs import SearchDialog
from .settings_page import SettingsPage
from .theme import ACCENT_BUTTON, DANGER_BUTTON, GHOST_BUTTON, PRIMARY_BUTTON, font
from .widgets import CardGrid, CardTile, InfoPanel

PREVIEW_SIZE = (180, 250)
PAGE_PADDING = {"padx": 20, "pady": 20}


class ProxyApp:

    def __init__(self, config: Config, settings_path: Path = DEFAULT_SETTINGS_PATH):
        self.config = config
        self.files: list[str] = []
        # Le immagini Scryfall in cache si chiamano con l'id della carta: qui teniamo il nome leggibile
        self.card_names: dict[str, str] = {}
        self.current_page = 0

        self.root = ctk.CTk()
        self.root.title("Proxyx")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)

        header = ctk.CTkFrame(self.root, height=90, corner_radius=0)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Proxyx - MTG Proxy Generator", font=font(34, bold=True)).place(relx=0.5, rely=0.5, anchor="center")

        self.main_page = ctk.CTkFrame(self.root, fg_color="transparent")
        self._build_sidebar(self.main_page)
        self._build_preview(self.main_page)

        self.settings_page = SettingsPage(self.root, settings_path, on_back=self.show_main, on_save=self.apply_config)

        self.show_main()
        self.update_info()
        self.refresh_preview()

    def _build_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, width=260, corner_radius=15)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        sidebar.pack_propagate(False)

        actions = [
            ("Load Images", self.load_files, {}),
            ("🔎 Search Scryfall", self.open_scryfall_search, ACCENT_BUTTON),
            ("Generate PDF", self.generate_pdf, PRIMARY_BUTTON),
            ("Clear", self.clear_all, DANGER_BUTTON),
        ]

        for i, (text, command, style) in enumerate(actions):
            button = ctk.CTkButton(sidebar, text=text, command=command, height=45, font=font(15, bold=True), **style)
            button.pack(fill="x", padx=20, pady=(20 if i == 0 else 15, 0))

        self.info = InfoPanel(sidebar, "Output", ["Card", "Page", "Grid", "Export"])
        self.info.pack(fill="x", padx=20, pady=(30, 0))

        settings_button = ctk.CTkButton(sidebar, text="⚙  Settings", command=self.show_settings, height=40, font=font(14), **GHOST_BUTTON)
        settings_button.pack(side="bottom", fill="x", **PAGE_PADDING)

    def _build_preview(self, parent):
        content = ctk.CTkFrame(parent, corner_radius=15)
        content.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(content, text="Card Preview", font=font(24, bold=True)).pack(pady=(20, 10))

        nav = ctk.CTkFrame(content, fg_color="transparent")
        nav.pack(pady=(0, 10))
        ctk.CTkButton(nav, text="← Previous", width=120, command=lambda: self.go_to_page(self.current_page - 1)).pack(side="left", padx=10)
        ctk.CTkButton(nav, text="Next →", width=120, command=lambda: self.go_to_page(self.current_page + 1)).pack(side="left", padx=10)

        self.preview = CardGrid(content, columns=self.config.cols)
        self.preview.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # --- Navigazione tra le pagine dell'app ---

    def show_main(self):
        self.settings_page.pack_forget()
        self.main_page.pack(fill="both", expand=True, **PAGE_PADDING)

    def show_settings(self):
        self.settings_page.open(self.config)
        self.main_page.pack_forget()
        self.settings_page.pack(fill="both", expand=True, **PAGE_PADDING)

    def apply_config(self, config: Config):
        self.config = config
        self.preview.columns = config.cols
        self.current_page = 0
        self.update_info()
        self.refresh_preview()

    def update_info(self):
        c = self.config
        self.info.set("Card", f"{c.card_width_mm:g} × {c.card_height_mm:g} mm")
        self.info.set("Page", f"{c.page_width_mm:g} × {c.page_height_mm:g} mm")
        self.info.set("Grid", f"{c.cols} × {c.rows}")
        self.info.set("Export", f"PDF · {c.dpi} DPI")

    # --- Carte caricate e anteprima ---

    def load_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp")])
        self.add_files(files)

    def add_files(self, files, name: str | None = None):
        for file in files:
            self.files.append(file)

            if name:
                self.card_names[file] = name

        self.refresh_preview()

    def open_scryfall_search(self):
        SearchDialog(self.root, on_add=lambda path, name: self.add_files([path], name))

    def go_to_page(self, page: int):
        last_page = max(0, (len(self.files) - 1) // self.config.cards_per_page)

        if 0 <= page <= last_page and page != self.current_page:
            self.current_page = page
            self.refresh_preview()

    def refresh_preview(self):
        if not self.files:
            self.preview.show_message("No cards loaded")
            return

        per_page = self.config.cards_per_page
        start = self.current_page * per_page
        self.preview.fill(self.files[start:start + per_page], self._preview_tile)

    def _preview_tile(self, parent, file: str) -> CardTile:
        tile = CardTile(parent, self.card_names.get(file, os.path.basename(file)), image_size=PREVIEW_SIZE, wrap=180)

        with Image.open(file) as img:
            tile.set_image(img)

        return tile

    def clear_all(self):
        self.files.clear()
        self.card_names.clear()
        self.current_page = 0
        self.refresh_preview()

    def generate_pdf(self):
        if not self.files:
            messagebox.showerror("Error", "No images loaded.")
            return

        output = filedialog.asksaveasfilename(title="Save PDF", defaultextension=".pdf", initialfile="proxy_cards.pdf", filetypes=[("PDF files", "*.pdf")])

        if not output:
            return

        try:
            ProxyGenerator.generate_pdf(self.files, output, self.config)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        messagebox.showinfo("Success", "PDF generated successfully!")

    def run(self):
        self.root.mainloop()
