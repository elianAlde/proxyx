import math

from PIL import Image

from .config import Config


def mm_to_px(mm: float, dpi: int) -> int:
    return int(mm / 25.4 * dpi)


def count_pages(num_cards: int, cards_per_page: int) -> int:
    return math.ceil(num_cards / cards_per_page)


def card_positions(page_size: tuple[int, int], card_size: tuple[int, int], cols: int, rows: int) -> list[tuple[int, int]]:
    """Angolo in alto a sinistra di ogni carta, griglia centrata nella pagina."""

    page_w, page_h = page_size
    card_w, card_h = card_size

    margin_x = (page_w - cols * card_w) // 2
    margin_y = (page_h - rows * card_h) // 2

    return [(margin_x + col * card_w, margin_y + row * card_h) for row in range(rows) for col in range(cols)]


class ProxyGenerator:

    @staticmethod
    def generate_pdf(files, output_path, config: Config):
        card_size = (mm_to_px(config.card_width_mm, config.dpi), mm_to_px(config.card_height_mm, config.dpi))
        page_size = (mm_to_px(config.page_width_mm, config.dpi), mm_to_px(config.page_height_mm, config.dpi))

        cards = [fit_on_card(file, card_size) for file in files]

        per_page = config.cards_per_page
        positions = card_positions(page_size, card_size, config.cols, config.rows)
        pages = []

        for p in range(count_pages(len(cards), per_page)):
            page = Image.new("RGB", page_size, "white")

            for card, pos in zip(cards[p * per_page:(p + 1) * per_page], positions):
                page.paste(card, pos)

            pages.append(page)

        pages[0].save(output_path, "PDF", resolution=config.dpi, save_all=True, append_images=pages[1:])


def fit_on_card(file, card_size: tuple[int, int]) -> Image.Image:
    """Ridimensiona l'immagine mantenendo le proporzioni e la centra su una carta bianca."""

    with Image.open(file) as img:
        img = img.convert("RGB")

    img.thumbnail(card_size)

    card = Image.new("RGB", card_size, "white")
    card.paste(img, ((card_size[0] - img.width) // 2, (card_size[1] - img.height) // 2))
    return card
