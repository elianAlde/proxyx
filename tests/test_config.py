import json

from proxyx.config import Config, load_config


def test_campi_mancanti_prendono_il_default(tmp_path):
    path = tmp_path / "settings.json"
    path.write_text(json.dumps({"dpi": 600, "chiave_sconosciuta": 1}))

    config = load_config(path)

    assert config.dpi == 600
    assert config.cols == Config().cols
    assert config.card_width_mm == Config().card_width_mm


def test_file_assente_usa_i_default(tmp_path):
    assert load_config(tmp_path / "manca.json") == Config()
