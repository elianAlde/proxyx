from proxyx.scryfall import get_image_url


def test_get_image_url_versione_richiesta():
    card = {"image_uris": {"normal": "n.jpg", "large": "l.jpg"}}
    assert get_image_url(card, "normal") == "n.jpg"


def test_get_image_url_fallback_su_large():
    card = {"image_uris": {"large": "l.jpg"}}
    assert get_image_url(card, "png") == "l.jpg"


def test_get_image_url_carta_doppia_faccia():
    card = {"card_faces": [{"image_uris": {"normal": "front.jpg"}}]}
    assert get_image_url(card, "normal") == "front.jpg"


def test_get_image_url_senza_immagine():
    assert get_image_url({}) is None
