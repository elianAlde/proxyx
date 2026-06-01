# gui.py

import os
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk

from PIL import Image, ImageTk

from config import *
from generator import ProxyGenerator

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
            dropdown_font=("Segoe UI", 13)
        )

        self.card_type.set("Magic")

        self.card_type.pack(
            padx=20,
            pady=(0, 30)
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        load_btn = ctk.CTkButton(
            left,
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
    # ADD FILES
    # =====================================================

    def add_files(self, files):

        for file in files:

            self.files.append(file)

        self.preview_images.clear()

        self.refresh_preview()

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