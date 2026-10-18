# scryfall.py

import os

import requests

# =========================================================
# CONFIG
# =========================================================

SCRYFALL_SEARCH_URL = "https://api.scryfall.com/cards/search"

CACHE_DIR = os.path.join(
    os.path.expanduser("~"),
    ".proxyx",
    "scryfall_cache"
)

# Scryfall asks integrations to identify themselves via headers.
# https://scryfall.com/docs/api
HEADERS = {
    "User-Agent": "Proxyx/1.0 (+https://github.com/elianAlde/proxyx)",
    "Accept": "application/json"
}


# =========================================================
# SEARCH
# =========================================================

def search_cards(query, max_results=24):

    if not query or not query.strip():
        return []

    response = requests.get(
        SCRYFALL_SEARCH_URL,
        params={"q": query.strip(), "unique": "cards"},
        headers=HEADERS,
        timeout=10
    )

    if response.status_code == 404:
        return []

    response.raise_for_status()

    data = response.json()

    return data.get("data", [])[:max_results]


# =========================================================
# PRINTS / VERSIONS
# =========================================================

def get_prints(card, max_results=75):

    uri = card.get("prints_search_uri")

    if not uri:
        return [card]

    response = requests.get(uri, headers=HEADERS, timeout=10)
    response.raise_for_status()

    data = response.json()

    return data.get("data", [card])[:max_results]


# =========================================================
# IMAGE HELPERS
# =========================================================

def get_image_url(card, version="normal"):

    image_uris = card.get("image_uris")

    if not image_uris:
        faces = card.get("card_faces") or []

        if faces:
            image_uris = faces[0].get("image_uris")

    if not image_uris:
        return None

    return (
        image_uris.get(version)
        or image_uris.get("large")
        or image_uris.get("normal")
        or image_uris.get("small")
    )


def download_card_image(card, version="large"):

    url = get_image_url(card, version)

    if not url:
        raise ValueError(
            f"No image available for '{card.get('name', 'this card')}'."
        )

    os.makedirs(CACHE_DIR, exist_ok=True)

    dest = os.path.join(CACHE_DIR, f"{card.get('id', 'card')}.jpg")

    if os.path.exists(dest):
        return dest

    response = requests.get(
        url,
        headers={"User-Agent": HEADERS["User-Agent"]},
        timeout=20
    )
    response.raise_for_status()

    with open(dest, "wb") as f:
        f.write(response.content)

    return dest
