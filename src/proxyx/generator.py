import math
from typing import Callable

from PIL import Image, ImageOps

from .config import Config


def mm_to_px(mm: float, dpi: int) -> int:
    return round(mm / 25.4 * dpi)


def count_pages(num_cards: int, cards_per_page: int) -> int:
    return math.ceil(num_cards / cards_per_page)


def card_positions(page_size: tuple[int, int], card_size: tuple[int, int], cols: int, rows: int, spacing: int = 0) -> list[tuple[int, int]]:
    """Top-left corner of each card, with the grid (spacing included) centred on the page."""

    page_w, page_h = page_size
    step_x, step_y = card_size[0] + spacing, card_size[1] + spacing

    margin_x = (page_w - cols * step_x + spacing) // 2
    margin_y = (page_h - rows * step_y + spacing) // 2

    return [(margin_x + col * step_x, margin_y + row * step_y) for row in range(rows) for col in range(cols)]


class ProxyGenerator:

    @staticmethod
    def generate_pdf(files, output_path, config: Config, on_progress: Callable[[int, int], None] | None = None):
        """Render the cards into a multi-page PDF.

        on_progress(done, total) is called after each card and once more after saving:
        scaling the images is the slow part, so it is what the progress follows.
        """

        card_size = (mm_to_px(config.card_width_mm, config.dpi), mm_to_px(config.card_height_mm, config.dpi))
        page_size = (mm_to_px(config.page_width_mm, config.dpi), mm_to_px(config.page_height_mm, config.dpi))
        positions = card_positions(page_size, card_size, config.cols, config.rows, mm_to_px(config.card_spacing_mm, config.dpi))

        per_page = config.cards_per_page
        total = len(files) + 1
        pages = []

        for p in range(count_pages(len(files), per_page)):
            page = Image.new("RGB", page_size, "white")

            for i, (file, pos) in enumerate(zip(files[p * per_page:(p + 1) * per_page], positions), start=p * per_page + 1):
                page.paste(fit_on_card(file, card_size), pos)

                if on_progress:
                    on_progress(i, total)

            pages.append(page)

        pages[0].save(output_path, "PDF", resolution=config.dpi, save_all=True, append_images=pages[1:])

        if on_progress:
            on_progress(total, total)


def fit_on_card(file, card_size: tuple[int, int]) -> Image.Image:
    """Scale the image to exactly fill the card, cropping the few pixels that differ in aspect ratio.

    Image.thumbnail() would only ever shrink: smaller sources (e.g. Scryfall's 672 px "large")
    would end up printed smaller than a real card.
    """

    with Image.open(file) as img:
        return ImageOps.fit(img.convert("RGB"), card_size, Image.Resampling.LANCZOS)
