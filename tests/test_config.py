import json

import pytest

from proxyx.config import Config, load_config, max_grid, save_config


def test_missing_fields_use_defaults(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"dpi": 600, "unknown_key": 1}))

    config = load_config(path)

    assert config.dpi == 600
    assert config.cols == Config().cols
    assert config.card_width_mm == Config().card_width_mm


def test_missing_file_uses_defaults(tmp_path):
    assert load_config(tmp_path / "missing.json") == Config()


def test_save_then_load_round_trips(tmp_path):
    path = tmp_path / "settings.json"
    config = Config(dpi=600, rows=2, card_width_mm=59)

    save_config(config, path)

    assert load_config(path) == config


def test_invalid_values_are_rejected():
    with pytest.raises(ValueError, match="Card width"):
        Config(card_width_mm=5)


def test_grid_must_fit_on_the_page():
    # Four 63 mm cards need 252 mm: more than an A4 page is wide
    with pytest.raises(ValueError, match="Columns must be between 1 and 3"):
        Config(cols=4)


def test_max_grid():
    assert max_grid(210, 297, 63, 88) == (3, 3)
    assert max_grid(297, 420, 63, 88) == (4, 4)


def test_max_grid_accounts_for_spacing():
    # 3 cards of 63 mm plus 2 gaps of 10 mm = 209 mm: still fits on A4, 11 mm gaps would not
    assert max_grid(210, 297, 63, 88, spacing_mm=10)[0] == 3
    assert max_grid(210, 297, 63, 88, spacing_mm=11)[0] == 2


def test_invalid_file_raises_a_readable_error(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"rows": 10}))

    with pytest.raises(ValueError, match="Rows must be between"):
        load_config(path)
