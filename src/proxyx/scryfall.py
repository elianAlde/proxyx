import os

import requests

SCRYFALL_SEARCH_URL = "https://api.scryfall.com/cards/search"

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".proxyx", "scryfall_cache")

# Scryfall asks integrations to identify themselves through headers.
# https://scryfall.com/docs/api
HEADERS = {
    "User-Agent": "Proxyx/0.1 (+https://github.com/elianAlde/proxyx)",
    "Accept": "application/json",
}

# Images are served by a CDN that rejects the Accept: application/json header
IMAGE_HEADERS = {"User-Agent": HEADERS["User-Agent"]}


def search_cards(query, max_results=24):
    if not query or not query.strip():
        return []

    response = requests.get(SCRYFALL_SEARCH_URL, params={"q": query.strip(), "unique": "cards"}, headers=HEADERS, timeout=10)

    # Scryfall answers 404 when a search has no results
    if response.status_code == 404:
        return []

    response.raise_for_status()
    return response.json().get("data", [])[:max_results]


def get_prints(card, max_results=75):
    uri = card.get("prints_search_uri")

    if not uri:
        return [card]

    response = requests.get(uri, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json().get("data", [card])[:max_results]


def get_image_url(card, version="normal"):
    image_uris = card.get("image_uris")

    # Double-faced cards have no top-level image_uris: use the front face
    if not image_uris:
        faces = card.get("card_faces") or []
        image_uris = faces[0].get("image_uris") if faces else None

    if not image_uris:
        return None

    return image_uris.get(version) or image_uris.get("large") or image_uris.get("normal") or image_uris.get("small")


def fetch_image(card, version="normal", timeout=10):
    """Download the card image and return its bytes, or None if the card has no image."""

    url = get_image_url(card, version)

    if not url:
        return None

    response = requests.get(url, headers=IMAGE_HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.content


def download_card_image(card, version="png"):
    """Save the image to the disk cache (once per card) and return its path.

    The "png" version is 745 × 1040 px: a 63 × 88 mm card at 300 DPI, so it prints without upscaling.
    """

    ext = "png" if version == "png" else "jpg"
    dest = os.path.join(CACHE_DIR, f"{card.get('id', 'card')}-{version}.{ext}")

    if os.path.exists(dest):
        return dest

    data = fetch_image(card, version, timeout=20)

    if data is None:
        raise ValueError(f"No image available for '{card.get('name', 'this card')}'.")

    os.makedirs(CACHE_DIR, exist_ok=True)

    with open(dest, "wb") as f:
        f.write(data)

    return dest
