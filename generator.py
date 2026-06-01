# generator.py

from PIL import Image
import math

from config import *


class ProxyGenerator:

    @staticmethod
    def mm_to_px(mm):
        return int(mm / 25.4 * DPI)

    @staticmethod
    def generate_pdf(files, card_type, output_path):

        config = CARD_FORMATS[card_type]

        card_width = ProxyGenerator.mm_to_px(config["width_mm"])
        card_height = ProxyGenerator.mm_to_px(config["height_mm"])

        a4_width = ProxyGenerator.mm_to_px(A4_WIDTH_MM)
        a4_height = ProxyGenerator.mm_to_px(A4_HEIGHT_MM)

        images = []

        for file in files:

            img = Image.open(file).convert("RGB")

            img.thumbnail((card_width, card_height))

            background = Image.new(
                "RGB",
                (card_width, card_height),
                "white"
            )

            x = (card_width - img.width) // 2
            y = (card_height - img.height) // 2

            background.paste(img, (x, y))

            images.append(background)

        cards_per_page = COLS * ROWS
        num_pages = math.ceil(len(images) / cards_per_page)

        margin_x = (a4_width - COLS * card_width) // 2
        margin_y = (a4_height - ROWS * card_height) // 2

        pages = []

        for p in range(num_pages):

            page = Image.new(
                "RGB",
                (a4_width, a4_height),
                "white"
            )

            for i in range(cards_per_page):

                idx = p * cards_per_page + i

                if idx >= len(images):
                    break

                row = i // COLS
                col = i % COLS

                x = margin_x + col * card_width
                y = margin_y + row * card_height

                page.paste(images[idx], (x, y))

            pages.append(page)

        pages[0].save(
            output_path,
            "PDF",
            resolution=DPI,
            save_all=True,
            append_images=pages[1:]
        )