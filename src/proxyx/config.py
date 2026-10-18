# config.py

import json
from dataclasses import dataclass, field, fields
from pathlib import Path

# src/proxyx/config.py -> parents[2] è la cartella del componente:
# settings.json resta lì, fuori dal codice sorgente.
BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS_PATH = BASE_DIR / "settings.json"


def _default_card_formats() -> dict[str, dict[str, float]]:
    return {
        "Pokémon": {"width_mm": 63, "height_mm": 88},
        "Magic": {"width_mm": 63, "height_mm": 88},
        "Yu-Gi-Oh!": {"width_mm": 59, "height_mm": 86},
    }


@dataclass
class Config:
    # Risoluzione di stampa e dimensioni del foglio (A4 di default)
    dpi: int = 300
    page_width_mm: float = 210
    page_height_mm: float = 297

    # Griglia di carte per pagina
    cols: int = 3
    rows: int = 3

    # Formati delle carte supportati, in millimetri
    card_formats: dict[str, dict[str, float]] = field(
        default_factory=_default_card_formats
    )

    @property
    def cards_per_page(self) -> int:
        return self.cols * self.rows


def load_config(path: Path = DEFAULT_SETTINGS_PATH) -> Config:
    """Carica settings.json; i campi mancanti prendono il default della classe."""

    if not path.exists():
        return Config()

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Ignora chiavi sconosciute invece di andare in errore
    known = {f.name for f in fields(Config)}

    return Config(**{k: v for k, v in data.items() if k in known})
