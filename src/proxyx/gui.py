# gui.py

import io
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import requests

from PIL import Image, ImageTk

from dataclasses import fields
from pathlib import Path

from .config import DEFAULT_SETTINGS_PATH, Config, save_config
from .generator import ProxyGenerator
from .scryfall import HEADERS as SCRYFALL_HEADERS
from .scryfall import download_card_image, get_image_url, get_prints, search_cards

# =========================================================
# THEME
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================================================
# APP
# =========================================================

class ProxyApp:

    def __init__(self, config: Config, settings_path: Path = DEFAULT_SETTINGS_PATH):

        self.config = config
        self.settings_path = settings_path

        self.root = ctk.CTk()

        self.root.title("Proxyx")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)

        self.files = []

        # Nome da mostrare sotto le carte scaricate da Scryfall
        # (il file in cache ha come nome l'id della carta)
        self.card_names = {}
        self.preview_images = []

        self.current_page = 0
        self.cards_per_page = config.cards_per_page

        self.setup_ui()

    # =====================================================
    # UI
    # =====================================================

    def setup_ui(self):

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = ctk.CTkFrame(
            self.root,
            height=90,
            corner_radius=0
        )

        header.pack(fill="x")

        title = ctk.CTkLabel(
            header,
            text="Proxyx - MTG Proxy Generator",
            font=("Segoe UI", 34, "bold")
        )

        title.place(relx=0.5, rely=0.5, anchor="center")

        # -------------------------------------------------
        # MAIN
        # -------------------------------------------------

        main = self.main_page = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        # -------------------------------------------------
        # LEFT SIDEBAR
        # -------------------------------------------------

        left = ctk.CTkFrame(
            main,
            width=260,
            corner_radius=15
        )

        left.pack(
            side="left",
            fill="y",
            padx=(0, 20)
        )

        left.pack_propagate(False)

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        button_group = ctk.CTkFrame(
            left,
            fg_color="transparent"
        )

        button_group.pack(fill="x", pady=(20, 0))

        load_btn = ctk.CTkButton(
            button_group,
            text="Load Images",
            command=self.load_files,
            height=45,
            font=("Segoe UI", 15, "bold")
        )

        load_btn.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        self.scryfall_btn = ctk.CTkButton(
            button_group,
            text="🔎 Search Scryfall",
            command=self.open_scryfall_search,
            height=45,
            font=("Segoe UI", 15, "bold"),
            fg_color="#7c3aed",
            hover_color="#6d28d9"
        )

        self.scryfall_btn.pack(
            fill="x",
            padx=20,
            pady=(0, 15)
        )

        generate_btn = ctk.CTkButton(
            left,
            text="Generate PDF",
            command=self.generate_pdf,
            height=45,
            font=("Segoe UI", 15, "bold"),
            fg_color="#16a34a",
            hover_color="#15803d"
        )

        generate_btn.pack(
            fill="x",
            padx=20
        )

        # -------------------------------------------------
        # CLEAR BUTTON
        # -------------------------------------------------

        clear_btn = ctk.CTkButton(
            left,
            text="Clear",
            command=self.clear_all,
            height=45,
            font=("Segoe UI", 15, "bold"),
            fg_color="#dc2626",
            hover_color="#b91c1c"
        )

        clear_btn.pack(
            fill="x",
            padx=20,
            pady=(15, 0)
        )

        # -------------------------------------------------
        # INFO
        # -------------------------------------------------

        info = ctk.CTkFrame(
            left,
            corner_radius=12,
            fg_color=("gray85", "gray20")
        )

        info.pack(
            fill="x",
            padx=20,
            pady=(30, 0)
        )

        info_title = ctk.CTkLabel(
            info,
            text="OUTPUT",
            font=("Segoe UI", 11, "bold"),
            text_color="gray"
        )

        info_title.pack(anchor="w", padx=15, pady=(12, 4))

        self.info_values = {}

        for key in ("Card", "Page", "Grid", "Export"):

            row = ctk.CTkFrame(info, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=2)

            ctk.CTkLabel(
                row,
                text=key,
                font=("Segoe UI", 13),
                text_color="gray"
            ).pack(side="left")

            value = ctk.CTkLabel(
                row,
                text="",
                font=("Segoe UI", 13, "bold")
            )

            value.pack(side="right")

            self.info_values[key] = value

        ctk.CTkFrame(info, height=10, fg_color="transparent").pack()

        self.update_info()

        settings_btn = ctk.CTkButton(
            left,
            text="⚙  Settings",
            command=self.show_settings,
            height=40,
            font=("Segoe UI", 14),
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        )

        settings_btn.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=20
        )

        # -------------------------------------------------
        # RIGHT CONTENT
        # -------------------------------------------------

        right = ctk.CTkFrame(
            main,
            corner_radius=15
        )

        right.pack(
            side="left",
            fill="both",
            expand=True
        )

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        preview_title = ctk.CTkLabel(
            right,
            text="Card Preview",
            font=("Segoe UI", 24, "bold")
        )

        preview_title.pack(
            pady=(20, 10)
        )

        # -------------------------------------------------
        # NAVIGATION
        # -------------------------------------------------

        nav_frame = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )

        nav_frame.pack(pady=(0, 10))

        prev_btn = ctk.CTkButton(
            nav_frame,
            text="← Previous",
            width=120,
            command=self.prev_page
        )

        prev_btn.pack(side="left", padx=10)

        next_btn = ctk.CTkButton(
            nav_frame,
            text="Next →",
            width=120,
            command=self.next_page
        )

        next_btn.pack(side="left", padx=10)

        # -------------------------------------------------
        # SCROLLABLE AREA
        # -------------------------------------------------

        self.scrollable_frame = ctk.CTkScrollableFrame(
            right,
            corner_radius=10
        )

        self.scrollable_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        # -------------------------------------------------
        # EMPTY LABEL
        # -------------------------------------------------

        empty_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="No cards loaded",
            font=("Segoe UI", 18),
            text_color="gray"
        )

        empty_label.pack(pady=50)

        self.setup_settings_page()

    # =====================================================
    # INFO
    # =====================================================

    def update_info(self):

        c = self.config

        self.info_values["Card"].configure(text=f"{c.card_width_mm:g} × {c.card_height_mm:g} mm")
        self.info_values["Page"].configure(text=f"{c.page_width_mm:g} × {c.page_height_mm:g} mm")
        self.info_values["Grid"].configure(text=f"{c.cols} × {c.rows}")
        self.info_values["Export"].configure(text=f"PDF · {c.dpi} DPI")

    # =====================================================
    # SETTINGS PAGE
    # =====================================================

    SETTINGS_SECTIONS = [
        ("Page", [
            ("page_width_mm", "Width (mm)"),
            ("page_height_mm", "Height (mm)"),
        ]),
        ("Grid", [
            ("cols", "Columns"),
            ("rows", "Rows"),
        ]),
        ("Card", [
            ("card_width_mm", "Width (mm)"),
            ("card_height_mm", "Height (mm)"),
        ]),
        ("Export", [
            ("dpi", "Resolution (DPI)"),
        ]),
    ]

    def setup_settings_page(self):

        page = self.settings_page = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )

        top = ctk.CTkFrame(page, fg_color="transparent")
        top.pack(fill="x", pady=(0, 15))

        ctk.CTkButton(
            top,
            text="← Back",
            width=100,
            command=self.show_main,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        ).pack(side="left")

        ctk.CTkLabel(
            top,
            text="Settings",
            font=("Segoe UI", 24, "bold")
        ).pack(side="left", padx=20)

        body = ctk.CTkScrollableFrame(page, corner_radius=15)
        body.pack(fill="both", expand=True)

        self.settings_entries = {}

        for section, items in self.SETTINGS_SECTIONS:

            card = ctk.CTkFrame(body, corner_radius=12, fg_color=("gray85", "gray20"))
            card.pack(fill="x", padx=20, pady=(20, 0))

            ctk.CTkLabel(
                card,
                text=section.upper(),
                font=("Segoe UI", 11, "bold"),
                text_color="gray"
            ).pack(anchor="w", padx=20, pady=(15, 5))

            for name, label in items:

                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=5)

                ctk.CTkLabel(
                    row,
                    text=label,
                    font=("Segoe UI", 14)
                ).pack(side="left")

                entry = ctk.CTkEntry(row, width=140, justify="right")
                entry.pack(side="right")

                self.settings_entries[name] = entry

            ctk.CTkFrame(card, height=10, fg_color="transparent").pack()

        footer = ctk.CTkFrame(page, fg_color="transparent")
        footer.pack(fill="x", pady=(15, 0))

        self.settings_status = ctk.CTkLabel(
            footer,
            text="",
            font=("Segoe UI", 13),
            text_color="gray"
        )

        self.settings_status.pack(side="left")

        ctk.CTkButton(
            footer,
            text="Save",
            width=120,
            height=40,
            command=self.save_settings,
            font=("Segoe UI", 14, "bold"),
            fg_color="#16a34a",
            hover_color="#15803d"
        ).pack(side="right")

        ctk.CTkButton(
            footer,
            text="Restore defaults",
            width=150,
            height=40,
            command=lambda: self.fill_settings(Config()),
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90")
        ).pack(side="right", padx=10)

    def fill_settings(self, config):

        for name, entry in self.settings_entries.items():
            entry.delete(0, "end")
            entry.insert(0, f"{getattr(config, name):g}")

    def show_settings(self):

        self.fill_settings(self.config)
        self.settings_status.configure(text=f"File: {self.settings_path}", text_color="gray")

        self.main_page.pack_forget()
        self.settings_page.pack(fill="both", expand=True, padx=20, pady=20)

    def show_main(self):

        self.settings_page.pack_forget()
        self.main_page.pack(fill="both", expand=True, padx=20, pady=20)

    def save_settings(self):

        types = {f.name: f.type for f in fields(Config)}
        values = {}

        for name, entry in self.settings_entries.items():

            raw = entry.get().strip().replace(",", ".")

            try:
                value = types[name](raw)
            except ValueError:
                value = None

            if value is None or value <= 0:
                self.settings_status.configure(
                    text=f"Invalid value for {name}: '{raw}'",
                    text_color="#dc2626"
                )
                return

            values[name] = value

        try:
            new_config = Config(**values)
            save_config(new_config, self.settings_path)

        except OSError as e:
            self.settings_status.configure(text=f"Error: {e}", text_color="#dc2626")
            return

        self.config = new_config
        self.cards_per_page = new_config.cards_per_page
        self.current_page = 0

        self.update_info()
        self.preview_images.clear()
        self.refresh_preview()

        self.settings_status.configure(text="Saved ✓", text_color="#16a34a")

    # =====================================================
    # LOAD FILES
    # =====================================================

    def load_files(self):

        files = filedialog.askopenfilenames(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp")
            ]
        )

        self.add_files(files)

    # =====================================================
    # ADD FILES
    # =====================================================

    def add_files(self, files, name=None):

        for file in files:

            self.files.append(file)

            if name:
                self.card_names[file] = name

        self.preview_images.clear()

        self.refresh_preview()

    # =====================================================
    # SCRYFALL SEARCH
    # =====================================================

    def open_scryfall_search(self):

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Search Scryfall")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()

        search_frame = ctk.CTkFrame(dialog, fg_color="transparent")

        search_frame.pack(
            fill="x",
            padx=20,
            pady=20
        )

        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Card name (e.g. Lightning Bolt)",
            height=40,
            font=("Segoe UI", 14)
        )

        search_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        search_entry.focus()

        search_hint = ctk.CTkLabel(
            dialog,
            text=(
                "Search by English card name"
            ),
            font=("Segoe UI", 11),
            text_color="gray"
        )

        search_hint.pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        results_frame = ctk.CTkScrollableFrame(dialog, corner_radius=10)

        results_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 10)
        )

        status_label = ctk.CTkLabel(
            dialog,
            text="",
            font=("Segoe UI", 13),
            text_color="gray"
        )

        status_label.pack(pady=(0, 15))

        thumbnails = []

        def load_thumbnail(card, label_widget, delay=0.0):

            def worker():

                if delay:
                    threading.Event().wait(delay)

                try:
                    url = get_image_url(card, version="small")

                    if not url:
                        return

                    response = requests.get(
                        url,
                        headers={"User-Agent": SCRYFALL_HEADERS["User-Agent"]},
                        timeout=10
                    )
                    response.raise_for_status()

                    img = Image.open(io.BytesIO(response.content))
                    img.thumbnail((140, 195))

                    photo = ImageTk.PhotoImage(img)

                except Exception:
                    return

                def on_done():
                    thumbnails.append(photo)
                    label_widget.configure(image=photo, text="")

                self.root.after(0, on_done)

            threading.Thread(target=worker, daemon=True).start()

        def add_card(card):

            status_label.configure(text=f"Downloading {card.get('name', 'card')}...")

            def worker():

                try:
                    path = download_card_image(card)
                    error = None

                except Exception as e:
                    path = None
                    error = str(e)

                def on_done():

                    if path:
                        self.add_files([path], card.get("name"))
                        status_label.configure(text=f"Added: {card.get('name', 'card')}")

                    else:
                        status_label.configure(text=f"Error: {error}")

                self.root.after(0, on_done)

            threading.Thread(target=worker, daemon=True).start()

        def populate_results(cards):

            for widget in results_frame.winfo_children():
                widget.destroy()

            thumbnails.clear()

            row = 0
            col = 0

            for i, card in enumerate(cards):

                card_frame = ctk.CTkFrame(results_frame, corner_radius=12)

                card_frame.grid(
                    row=row,
                    column=col,
                    padx=10,
                    pady=10,
                    sticky="n"
                )

                thumb_label = ctk.CTkLabel(
                    card_frame,
                    text="...",
                    width=140,
                    height=195
                )

                thumb_label.pack(padx=10, pady=(10, 5))

                name_label = ctk.CTkLabel(
                    card_frame,
                    text=card.get("name", "Unknown"),
                    font=("Segoe UI", 12, "bold"),
                    wraplength=160
                )

                name_label.pack(padx=10)

                set_label = ctk.CTkLabel(
                    card_frame,
                    text=card.get("set_name", ""),
                    font=("Segoe UI", 11),
                    text_color="gray",
                    wraplength=160
                )

                set_label.pack(padx=10, pady=(0, 5))

                btn_row = ctk.CTkFrame(card_frame, fg_color="transparent")

                btn_row.pack(padx=10, pady=(0, 10))

                add_btn = ctk.CTkButton(
                    btn_row,
                    text="+ Add",
                    width=90,
                    command=lambda c=card: add_card(c)
                )

                add_btn.pack(side="left", padx=(0, 5))

                versions_btn = ctk.CTkButton(
                    btn_row,
                    text="Versions",
                    width=45,
                    fg_color="transparent",
                    border_width=1,
                    command=lambda c=card: self.open_version_picker(c)
                )

                versions_btn.pack(side="left")

                load_thumbnail(card, thumb_label, delay=i * 0.05)

                col += 1

                if col >= 3:
                    col = 0
                    row += 1

        def run_search(event=None):

            query = search_entry.get().strip()

            if not query:
                return

            for widget in results_frame.winfo_children():
                widget.destroy()

            status_label.configure(text="Searching...")

            def worker():

                try:
                    cards = search_cards(query)
                    error = None

                except Exception as e:
                    cards = None
                    error = str(e)

                def on_done():

                    if cards is None:
                        status_label.configure(text=f"Error: {error}")
                        return

                    if not cards:
                        status_label.configure(text="No cards found.")
                        return

                    status_label.configure(text=f"{len(cards)} result(s)")
                    populate_results(cards)

                self.root.after(0, on_done)

            threading.Thread(target=worker, daemon=True).start()

        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            width=100,
            command=run_search
        )

        search_btn.pack(side="left")

        search_entry.bind("<Return>", run_search)

    # =====================================================
    # SCRYFALL VERSION PICKER
    # =====================================================

    def open_version_picker(self, card):

        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Versions - {card.get('name', 'Card')}")
        dialog.geometry("700x600")
        dialog.transient(self.root)
        dialog.grab_set()

        status_label = ctk.CTkLabel(
            dialog,
            text="Loading printings...",
            font=("Segoe UI", 13),
            text_color="gray"
        )

        status_label.pack(pady=15)

        results_frame = ctk.CTkScrollableFrame(dialog, corner_radius=10)

        results_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        thumbnails = []

        def load_thumbnail(print_card, label_widget, delay=0.0):

            def worker():

                if delay:
                    threading.Event().wait(delay)

                try:
                    url = get_image_url(print_card, version="small")

                    if not url:
                        return

                    response = requests.get(
                        url,
                        headers={"User-Agent": SCRYFALL_HEADERS["User-Agent"]},
                        timeout=10
                    )
                    response.raise_for_status()

                    img = Image.open(io.BytesIO(response.content))
                    img.thumbnail((140, 195))

                    photo = ImageTk.PhotoImage(img)

                except Exception:
                    return

                def on_done():
                    thumbnails.append(photo)
                    label_widget.configure(image=photo, text="")

                self.root.after(0, on_done)

            threading.Thread(target=worker, daemon=True).start()

        def add_print(print_card):

            status_label.configure(text=f"Downloading {print_card.get('set_name', 'card')}...")

            def worker():

                try:
                    path = download_card_image(print_card)
                    error = None

                except Exception as e:
                    path = None
                    error = str(e)

                def on_done():

                    if path:
                        self.add_files([path], print_card.get("name"))
                        status_label.configure(text=f"Added: {print_card.get('name')} ({print_card.get('set_name')})")

                    else:
                        status_label.configure(text=f"Error: {error}")

                self.root.after(0, on_done)

            threading.Thread(target=worker, daemon=True).start()

        def populate_prints(prints):

            for widget in results_frame.winfo_children():
                widget.destroy()

            thumbnails.clear()

            row = 0
            col = 0

            for i, print_card in enumerate(prints):

                card_frame = ctk.CTkFrame(results_frame, corner_radius=12)

                card_frame.grid(
                    row=row,
                    column=col,
                    padx=10,
                    pady=10,
                    sticky="n"
                )

                thumb_label = ctk.CTkLabel(
                    card_frame,
                    text="...",
                    width=140,
                    height=195
                )

                thumb_label.pack(padx=10, pady=(10, 5))

                set_label = ctk.CTkLabel(
                    card_frame,
                    text=print_card.get("set_name", ""),
                    font=("Segoe UI", 12, "bold"),
                    wraplength=160
                )

                set_label.pack(padx=10)

                info_label = ctk.CTkLabel(
                    card_frame,
                    text=f"#{print_card.get('collector_number', '?')} · {print_card.get('released_at', '')}",
                    font=("Segoe UI", 11),
                    text_color="gray",
                    wraplength=160
                )

                info_label.pack(padx=10, pady=(0, 5))

                add_btn = ctk.CTkButton(
                    card_frame,
                    text="+ Add",
                    width=140,
                    command=lambda c=print_card: add_print(c)
                )

                add_btn.pack(padx=10, pady=(0, 10))

                load_thumbnail(print_card, thumb_label, delay=i * 0.05)

                col += 1

                if col >= 3:
                    col = 0
                    row += 1

        def worker():

            try:
                prints = get_prints(card)
                error = None

            except Exception as e:
                prints = None
                error = str(e)

            def on_done():

                if prints is None:
                    status_label.configure(text=f"Error: {error}")
                    return

                status_label.configure(text=f"{len(prints)} printing(s) — pick one to add")
                populate_prints(prints)

            self.root.after(0, on_done)

        threading.Thread(target=worker, daemon=True).start()

    # =====================================================
    # REFRESH PREVIEW
    # =====================================================

    def refresh_preview(self):

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.files:

            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="No cards loaded",
                font=("Segoe UI", 18),
                text_color="gray"
            )

            empty_label.pack(pady=50)

            return

        start = self.current_page * self.cards_per_page
        end = start + self.cards_per_page

        current_files = self.files[start:end]

        row = 0
        col = 0

        for file in current_files:

            container = ctk.CTkFrame(
                self.scrollable_frame,
                corner_radius=12
            )

            container.grid(
                row=row,
                column=col,
                padx=15,
                pady=15,
                sticky="n"
            )

            img = Image.open(file)

            img.thumbnail((180, 250))

            photo = ImageTk.PhotoImage(img)

            self.preview_images.append(photo)

            img_label = tk.Label(
                container,
                image=photo,
                bd=0
            )

            img_label.pack(
                padx=15,
                pady=(15, 10)
            )

            filename = ctk.CTkLabel(
                container,
                text=self.card_names.get(file, os.path.basename(file)),
                font=("Segoe UI", 13, "bold"),
                wraplength=180
            )

            filename.pack(
                padx=10,
                pady=(0, 15)
            )

            col += 1

            if col >= self.config.cols:

                col = 0
                row += 1

    # =====================================================
    # NEXT PAGE
    # =====================================================

    def next_page(self):

        max_page = (len(self.files) - 1) // self.cards_per_page

        if self.current_page < max_page:

            self.current_page += 1
            self.refresh_preview()

    # =====================================================
    # PREVIOUS PAGE
    # =====================================================

    def prev_page(self):

        if self.current_page > 0:

            self.current_page -= 1
            self.refresh_preview()

    # =====================================================
    # CLEAR ALL
    # =====================================================

    def clear_all(self):

        self.files.clear()

        self.card_names.clear()

        self.preview_images.clear()

        self.current_page = 0

        self.refresh_preview()

    # =====================================================
    # GENERATE PDF
    # =====================================================

    def generate_pdf(self):

        if not self.files:

            messagebox.showerror(
                "Error",
                "No images loaded."
            )

            return

        output = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            initialfile="proxy_cards.pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not output:
            return

        try:

            ProxyGenerator.generate_pdf(
                self.files,
                output,
                self.config
            )

            messagebox.showinfo(
                "Success",
                "PDF generated successfully!"
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    # =====================================================
    # RUN
    # =====================================================

    def run(self):

        self.root.mainloop()