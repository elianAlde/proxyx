# Proxyx – app desktop

Applicazione desktop che impagina immagini di carte TCG su fogli A4 e le esporta in PDF.
Per la panoramica del progetto e la roadmap vedi il [README principale](../README.md).

## Installazione

Serve Python 3.10 o superiore. Dalla cartella `proxyx/` (quella che contiene `pyproject.toml`):

```bash
python3 -m venv venv
source venv/bin/activate          # macOS / Linux  (Windows: venv\Scripts\activate)
pip install -e ".[dev]"           # progetto + dipendenze + pytest
```

Con `-e` (editable) le modifiche in `src/` hanno effetto subito: si reinstalla solo quando cambia `pyproject.toml`.

## Avvio

```bash
proxyx                            # oppure: python -m proxyx
proxyx --settings altro.json      # usa un file di configurazione diverso
```

## Test

```bash
pytest
```

I test coprono le funzioni pure (conversioni mm → pixel, impaginazione, parsing delle risposte Scryfall, caricamento della configurazione). GUI e chiamate di rete non vengono testate.

## Configurazione (`settings.json`)

| Campo | Default | Significato |
|---|---|---|
| `dpi` | `300` | Risoluzione del PDF generato |
| `page_width_mm` | `210` | Larghezza del foglio (A4) |
| `page_height_mm` | `297` | Altezza del foglio (A4) |
| `cols` | `3` | Carte per riga |
| `rows` | `3` | Righe per pagina |
| `card_formats` | Pokémon, Magic, Yu-Gi-Oh! | Formati disponibili nel menu, con `width_mm` e `height_mm` |

Un campo che manca prende il valore di default. Le immagini scaricate da Scryfall vengono salvate in cache in `~/.proxyx/scryfall_cache`.

## Note di stampa

- Scala al 100%, senza "adatta alla pagina"
- Qualità alta, carta spessa o fotografica opaca

## Problemi tipici

| Sintomo | Causa |
|---|---|
| `ModuleNotFoundError: No module named 'proxyx'` o `command not found: proxyx` | Il venv non è attivo (il prompt deve mostrare `(venv)`), oppure manca `pip install -e .` |
| `ImportError: attempted relative import with no known parent package` | `main.py` è stato lanciato come file (es. "Run Python File" di VS Code). Avvia con `proxyx` o `python -m proxyx`; nel debugger usa `"module": "proxyx"` |
| Pylance segna gli import come "could not be resolved" | In VS Code non è selezionato l'interprete `proxyx/venv/bin/python` (`Cmd+Shift+P` → *Python: Select Interpreter*) |
| `No module named '_tkinter'` | Il Python installato non include Tk (es. Homebrew: `brew install python-tk`) |
