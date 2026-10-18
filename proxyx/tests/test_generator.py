from proxyx.generator import card_positions, count_pages, mm_to_px


def test_mm_to_px_un_pollice():
    # 25.4 mm = 1 pollice = esattamente dpi pixel
    assert mm_to_px(25.4, 300) == 300


def test_mm_to_px_carta_magic():
    assert mm_to_px(63, 300) == 744
    assert mm_to_px(88, 300) == 1039


def test_count_pages():
    assert count_pages(0, 9) == 0
    assert count_pages(9, 9) == 1
    assert count_pages(10, 9) == 2


def test_card_positions_griglia_centrata():
    positions = card_positions((100, 100), (30, 40), cols=3, rows=2)

    assert len(positions) == 6
    # margini: (100 - 90) // 2 = 5 e (100 - 80) // 2 = 10
    assert positions[0] == (5, 10)
    assert positions[2] == (65, 10)
    assert positions[3] == (5, 50)
