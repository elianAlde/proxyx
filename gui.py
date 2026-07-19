# gui.py

import io
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
import requests

from PIL import Image, ImageTk

from config import *
from generator import ProxyGenerator
from scryfall import HEADERS as SCRYFALL_HEADERS
from scryfall import download_card_image, get_image_url, get_prints, search_cards

# =========================================================
# THEME
# =========================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================================================
# APP
# =========================================================

class ProxyApp:

    def __init__(self):

        self.root = ctk.CTk()

        self.root.title("Proxyx")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)

        self.files = []
        self.preview_images = []

        self.current_page = 0
        self.cards_per_page = 9

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
            text="Proxyx - Fast TCG Proxy Generator",
            font=("Segoe UI", 34, "bold")
        )

        title.place(relx=0.5, rely=0.5, anchor="center")

        # -------------------------------------------------
        # MAIN
        # -------------------------------------------------

        main = ctk.CTkFrame(
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
        # CARD TYPE
        # -------------------------------------------------

        card_label = ctk.CTkLabel(
            left,
            text="Card Type",
            font=("Segoe UI", 18, "bold")
        )

        card_label.pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        self.card_type = ctk.CTkComboBox(
            left,
            values=list(CARD_FORMATS.keys()),
            width=220,
            height=40,
            font=("Segoe UI", 14),
            dropdown_font=("Segoe UI", 13),
            command=self.on_card_type_change
        )

        self.card_type.set("Magic")

        self.card_type.pack(
            padx=20,
            pady=(0, 30)
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        button_group = ctk.CTkFrame(
            left,
            fg_color="transparent"
        )

        button_group.pack(fill="x")

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

        info = ctk.CTkLabel(
            left,
            text=(
                "Supported:\n"
                "• Pokémon\n"
                "• Magic\n"
                "• Yu-Gi-Oh!\n\n"
                "Export:\n"
                "• A4 PDF\n"
                "• 300 DPI"
            ),
            justify="left",
            font=("Segoe UI", 13)
        )

        info.pack(
            anchor="w",
            padx=20,
            pady=30
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
    # CARD TYPE CHANGE
    # =====================================================

    def on_card_type_change(self, choice):

        if choice == "Magic":

            self.scryfall_btn.pack(
                fill="x",
                padx=20,
                pady=(0, 15)
            )

        else:

            self.scryfall_btn.pack_forget()

    # =====================================================
    # ADD FILES
    # =====================================================

    def add_files(self, files):

        for file in files:

            self.files.append(file)

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
                        self.add_files([path])
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
                        self.add_files([path])
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
                text=os.path.basename(file),
                font=("Segoe UI", 13, "bold"),
                wraplength=180
            )

            filename.pack(
                padx=10,
                pady=(0, 15)
            )

            col += 1

            if col >= 3:

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
                self.card_type.get(),
                output
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