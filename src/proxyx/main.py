import argparse
import sys
from pathlib import Path

from .config import DEFAULT_SETTINGS_PATH, load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Proxyx - printable proxy sheet generator for Magic: The Gathering")
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS_PATH, help="path to the settings.json file (default: the one in the project folder)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        config = load_config(args.settings)
    except ValueError as e:
        sys.exit(f"Error: {e}")

    # Imported here so customtkinter only loads when the GUI is actually needed
    from .gui import ProxyApp

    app = ProxyApp(config, args.settings)
    app.run()
