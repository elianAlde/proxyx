from proxyx.scryfall import get_image_url


def test_get_image_url_requested_version():
    card = {"image_uris": {"normal": "n.jpg", "large": "l.jpg"}}
    assert get_image_url(card, "normal") == "n.jpg"


def test_get_image_url_falls_back_to_large():
    card = {"image_uris": {"large": "l.jpg"}}
    assert get_image_url(card, "png") == "l.jpg"


def test_get_image_url_double_faced_card():
    card = {"card_faces": [{"image_uris": {"normal": "front.jpg"}}]}
    assert get_image_url(card, "normal") == "front.jpg"


def test_get_image_url_without_image():
    assert get_image_url({}) is None
