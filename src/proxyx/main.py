# main.py

import argparse
from pathlib import Path

from .config import DEFAULT_SETTINGS_PATH, load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Proxyx - generatore di fogli proxy stampabili per Magic: The Gathering"
    )
    parser.add_argument(
        "--settings",
        type=Path,
        default=DEFAULT_SETTINGS_PATH,
        help="percorso del file settings.json (default: quello del progetto)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.settings)

    # Import qui: customtkinter si carica solo quando serve davvero la GUI
    from .gui import ProxyApp

    app = ProxyApp(config)
    app.run()
