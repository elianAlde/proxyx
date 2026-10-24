from PIL import Image

from proxyx.generator import card_positions, count_pages, fit_on_card, mm_to_px


def test_mm_to_px_one_inch():
    # 25.4 mm = 1 inch = exactly dpi pixels
    assert mm_to_px(25.4, 300) == 300


def test_mm_to_px_magic_card():
    assert mm_to_px(63, 300) == 744
    assert mm_to_px(88, 300) == 1039


def test_count_pages():
    assert count_pages(0, 9) == 0
    assert count_pages(9, 9) == 1
    assert count_pages(10, 9) == 2


def test_card_positions_centred_grid():
    positions = card_positions((100, 100), (30, 40), cols=3, rows=2)

    assert len(positions) == 6
    # margins: (100 - 90) // 2 = 5 and (100 - 80) // 2 = 10
    assert positions[0] == (5, 10)
    assert positions[2] == (65, 10)
    assert positions[3] == (5, 50)


def test_card_positions_with_spacing():
    positions = card_positions((100, 100), (30, 40), cols=3, rows=2, spacing=2)

    # grid: 3 * 30 + 2 * 2 = 94 wide and 2 * 40 + 2 = 82 tall -> margins 3 and 9
    assert positions[0] == (3, 9)
    assert positions[1] == (35, 9)
    assert positions[3] == (3, 51)


def test_fit_on_card_upscales_small_images(tmp_path):
    path = tmp_path / "small.png"
    Image.new("RGB", (672, 936), "black").save(path)

    card = fit_on_card(path, (744, 1039))

    # The whole card must be covered, with no white border left by a smaller image
    assert card.size == (744, 1039)
    assert card.getpixel((0, 0)) == (0, 0, 0)
    assert card.getpixel((743, 1038)) == (0, 0, 0)
