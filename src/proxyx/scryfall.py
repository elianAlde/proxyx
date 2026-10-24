import os

import requests

SCRYFALL_SEARCH_URL = "https://api.scryfall.com/cards/search"

CACHE_DIR = os.path.join(os.path.expanduser("~"), ".proxyx", "scryfall_cache")

# Scryfall chiede alle integrazioni di identificarsi tramite header.
# https://scryfall.com/docs/api
HEADERS = {
    "User-Agent": "Proxyx/0.1 (+https://github.com/elianAlde/proxyx)",
    "Accept": "application/json",
}

# Le immagini stanno su un CDN che non vuole l'header Accept: application/json
IMAGE_HEADERS = {"User-Agent": HEADERS["User-Agent"]}


def search_cards(query, max_results=24):
    if not query or not query.strip():
        return []

    response = requests.get(SCRYFALL_SEARCH_URL, params={"q": query.strip(), "unique": "cards"}, headers=HEADERS, timeout=10)

    # Scryfall risponde 404 quando la ricerca non trova nulla
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

    # Le carte double-faced non hanno image_uris in radice: si usa il fronte
    if not image_uris:
        faces = card.get("card_faces") or []
        image_uris = faces[0].get("image_uris") if faces else None

    if not image_uris:
        return None

    return image_uris.get(version) or image_uris.get("large") or image_uris.get("normal") or image_uris.get("small")


def fetch_image(card, version="normal", timeout=10):
    """Scarica l'immagine della carta e ne restituisce i byte, o None se non ce l'ha."""

    url = get_image_url(card, version)

    if not url:
        return None

    response = requests.get(url, headers=IMAGE_HEADERS, timeout=timeout)
    response.raise_for_status()
    return response.content


def download_card_image(card, version="large"):
    """Salva l'immagine nella cache su disco (una volta sola per carta) e ne restituisce il percorso."""

    dest = os.path.join(CACHE_DIR, f"{card.get('id', 'card')}.jpg")

    if os.path.exists(dest):
        return dest

    data = fetch_image(card, version, timeout=20)

    if data is None:
        raise ValueError(f"No image available for '{card.get('name', 'this card')}'.")

    os.makedirs(CACHE_DIR, exist_ok=True)

    with open(dest, "wb") as f:
        f.write(data)

    return dest
