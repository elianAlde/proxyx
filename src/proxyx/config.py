import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Callable

# src/proxyx/config.py -> parents[2] is the project folder:
# settings.json lives there, outside the source code.
BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS_PATH = BASE_DIR / "settings.json"

# Paper sizes offered in the settings page, in millimetres (portrait)
PAGE_SIZES = {
    "A4": (210, 297),
    "A3": (297, 420),
    "Letter": (215.9, 279.4),
    "Legal": (215.9, 355.6),
}

DPI_OPTIONS = (150, 300, 600)

# Gap left between cards, so each one can be cut out without trimming its neighbour
SPACING_OPTIONS = (0, 0.5, 1, 2, 3)

# Card size may be tweaked to compensate for printer scaling, but only within sensible bounds
CARD_WIDTH_RANGE = (40, 100)
CARD_HEIGHT_RANGE = (55, 140)
PAGE_SIDE_RANGE = (100, 500)
DPI_RANGE = (72, 1200)
SPACING_RANGE = (0, 10)


@dataclass(frozen=True)
class Config:
    # Print resolution and page size (A4 by default)
    dpi: int = 300
    page_width_mm: float = 210
    page_height_mm: float = 297

    # Card grid on each page
    cols: int = 3
    rows: int = 3
    card_spacing_mm: float = 1

    # Size of a standard Magic card, in millimetres
    card_width_mm: float = 63
    card_height_mm: float = 88

    def __post_init__(self) -> None:
        if errors := validate(self):
            raise ValueError("; ".join(errors))

    @property
    def cards_per_page(self) -> int:
        return self.cols * self.rows


def max_grid(page_width_mm: float, page_height_mm: float, card_width_mm: float, card_height_mm: float, spacing_mm: float = 0) -> tuple[int, int]:
    """Most columns and rows of cards that fit on the page.

    n cards take n * card + (n - 1) * spacing, so n fits when n <= (page + spacing) / (card + spacing).
    """

    return int((page_width_mm + spacing_mm) // (card_width_mm + spacing_mm)), int((page_height_mm + spacing_mm) // (card_height_mm + spacing_mm))


def validate(config: Config) -> list[str]:
    """Return a readable message for every invalid value; an empty list means the config is valid."""

    errors = []

    def check_range(name: str, value: float, bounds: tuple[float, float], unit: str = "") -> None:
        low, high = bounds
        if not low <= value <= high:
            errors.append(f"{name} must be between {low:g} and {high:g}{unit} (got {value:g})")

    check_range("DPI", config.dpi, DPI_RANGE)
    check_range("Page width", config.page_width_mm, PAGE_SIDE_RANGE, " mm")
    check_range("Page height", config.page_height_mm, PAGE_SIDE_RANGE, " mm")
    check_range("Card width", config.card_width_mm, CARD_WIDTH_RANGE, " mm")
    check_range("Card height", config.card_height_mm, CARD_HEIGHT_RANGE, " mm")
    check_range("Card spacing", config.card_spacing_mm, SPACING_RANGE, " mm")

    if errors:
        return errors

    max_cols, max_rows = max_grid(config.page_width_mm, config.page_height_mm, config.card_width_mm, config.card_height_mm, config.card_spacing_mm)

    if not 1 <= config.cols <= max_cols:
        errors.append(f"Columns must be between 1 and {max_cols} for this page and card size (got {config.cols})")

    if not 1 <= config.rows <= max_rows:
        errors.append(f"Rows must be between 1 and {max_rows} for this page and card size (got {config.rows})")

    return errors


def load_config(path: Path = DEFAULT_SETTINGS_PATH) -> Config:
    """Load settings.json; missing fields take the class default. Raises ValueError if the file is invalid."""

    if not path.exists():
        return Config()

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Every field is an int or a float: map each one to its converter
    known: dict[str, Callable[[Any], Any]] = {f.name: int if f.type is int else float for f in fields(Config)}

    try:
        # Unknown keys are ignored instead of failing; values are coerced to the declared type
        return Config(**{k: known[k](v) for k, v in data.items() if k in known})
    except (TypeError, ValueError) as e:
        raise ValueError(f"Invalid settings in {path}: {e}") from e


def save_config(config: Config, path: Path = DEFAULT_SETTINGS_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=4)
        f.write("\n")
