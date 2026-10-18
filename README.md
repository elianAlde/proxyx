
<div align="center">

# ⚡ Proxyx - Fast TCG Proxy Generator

Genera fogli di proxy TCG stampabili in pochi secondi.

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" /></a>
  <a href="#"><img src="https://img.shields.io/badge/CustomTkinter-UI-1f6feb?style=for-the-badge" /></a>
  <a href="#"><img src="https://img.shields.io/badge/PDF-Generation-red?style=for-the-badge&logo=adobeacrobatreader" /></a>
  <a href="#"><img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" /></a>
  <a href="#"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" /></a>
</p>

</div>


## ✨ Panoramica

Proxyx è un'applicazione desktop per generare velocemente fogli di proxy TCG pronti da stampare.

Il programma dispone automaticamente le carte su pagine stampabili, mostra un'anteprima con paginazione ed esporta tutto in PDF.

È nato per risolvere un problema semplice:

"Voglio solo stampare dei proxy in fretta, senza passare ore a modificare template a mano."


## 🚀 Funzionalità

✅ Interfaccia desktop moderna
<br>
✅ Anteprima a griglia di più carte
<br>
✅ Impaginazione automatica
<br>
✅ Paginazione per lotti grandi
<br>
✅ Esportazione PDF pronta per la stampa
<br>
✅ Ricerca delle carte Magic tramite Scryfall
<br>
✅ Formati, griglia e DPI configurabili da `settings.json`


## 📸 Screenshot

### Interfaccia principale:

<p align="center">
  <img src="assets/proxyx-screenshot.png" width="60%" />
</p>

### Layout stampabile generato:

<p align="center">
  <img src="assets/printable-layout-generated-screenshot.png" width="60%" />
</p>


## ⚙ Installazione

Serve Python 3.10 o superiore. Dalla radice della repository:

```bash
python3 -m venv venv
source venv/bin/activate          # macOS / Linux  (Windows: venv\Scripts\activate)
pip install -e ".[dev]"           # progetto + dipendenze + pytest
```

Con `-e` (editable) le modifiche in `src/` hanno effetto subito: si reinstalla solo quando cambia `pyproject.toml`.

## ▶ Avvio

```bash
proxyx                            # oppure: python -m proxyx
proxyx --settings altro.json      # usa un file di configurazione diverso
```

## 🧪 Test

```bash
pytest
```

I test coprono le funzioni pure (conversioni mm → pixel, impaginazione, parsing delle risposte Scryfall, caricamento della configurazione). GUI e chiamate di rete non vengono testate.

## 🔧 Configurazione (`settings.json`)

| Campo | Default | Significato |
|---|---|---|
| `dpi` | `300` | Risoluzione del PDF generato |
| `page_width_mm` | `210` | Larghezza del foglio (A4) |
| `page_height_mm` | `297` | Altezza del foglio (A4) |
| `cols` | `3` | Carte per riga |
| `rows` | `3` | Righe per pagina |
| `card_formats` | Pokémon, Magic, Yu-Gi-Oh! | Formati disponibili nel menu, con `width_mm` e `height_mm` |

Un campo che manca prende il valore di default. Le immagini scaricate da Scryfall vengono salvate in cache in `~/.proxyx/scryfall_cache`.

## 🖨 Note di stampa

- Scala al 100%, senza "adatta alla pagina"
- Qualità alta, carta spessa o fotografica opaca

## 🩺 Problemi tipici

| Sintomo | Causa |
|---|---|
| `ModuleNotFoundError: No module named 'proxyx'` o `command not found: proxyx` | Il venv non è attivo (il prompt deve mostrare `(venv)`), oppure manca `pip install -e .` |
| `ImportError: attempted relative import with no known parent package` | `main.py` è stato lanciato come file (es. "Run Python File" di VS Code). Avvia con `proxyx` o `python -m proxyx`; nel debugger usa `"module": "proxyx"` |
| Pylance segna gli import come "could not be resolved" | In VS Code non è selezionato l'interprete `venv/bin/python` (`Cmd+Shift+P` → *Python: Select Interpreter*) |
| `No module named '_tkinter'` | Il Python installato non include Tk (es. Homebrew: `brew install python-tk`) |


## 🛠 Tecnologie

| Tecnologia | Uso |
|---|---|
| Python | Logica dell'applicazione |
| CustomTkinter | Interfaccia desktop |
| Pillow (PIL) | Elaborazione immagini ed export PDF |
| Requests | API di Scryfall |


## 🛣 Roadmap

- [x] 🔎 **Integrazione Scryfall**
  - Ricerca e importazione delle carte Magic direttamente dall'app
- [ ] 🔎 **Altri database di carte**
  - Pokémon e Yu-Gi-Oh! usano ancora il caricamento manuale delle immagini
- [ ] 🖨 **Controlli di stampa avanzati**
  - Margini di abbondanza (bleed)
  - Segni di taglio
  - Calibrazione della stampante
- [ ] 📱 **App mobile di supporto**
  - Gestione delle liste di proxy da telefono
  - Sincronizzazione con l'app desktop


## 🤝 Contribuire

Suggerimenti e richieste di funzionalità sono benvenuti: apri una issue o una pull request.


## 📜 Licenza

Distribuito con licenza MIT.


---
<div align="center">

Fatto con ❤️ per la community TCG

</div>
