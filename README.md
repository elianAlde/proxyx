
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


## ⬇ Installazione

Non ci sono eseguibili precompilati: Proxyx si avvia dal codice sorgente. Ti servono [Python 3.10+](https://www.python.org/downloads/) e [Git](https://git-scm.com/downloads).

**1. Scarica il progetto**

```bash
git clone https://github.com/elianAlde/proxyx.git
cd proxyx
```

**2. Crea un ambiente virtuale e installa Proxyx**

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\activate
pip install -e .
```

**3. Avvia l'app**

```bash
proxyx
```

Le volte successive basta entrare nella cartella, riattivare l'ambiente (`source venv/bin/activate`, oppure `venv\Scripts\activate` su Windows) e lanciare `proxyx`.

## 🃏 Come si usa

1. In **Card Type** scegli il formato delle carte (Pokémon, Magic, Yu-Gi-Oh!)
2. Aggiungi le carte con **Load Images**, oppure cerca le carte Magic con **🔎 Search Scryfall**
3. Scorri l'anteprima delle pagine con **← Previous** / **Next →**
4. Premi **Generate PDF** e stampa il file

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

| Problema | Soluzione |
|---|---|
| `command not found: proxyx` | L'ambiente virtuale non è attivo: lancia `source venv/bin/activate` (Windows: `venv\Scripts\activate`) dalla cartella `proxyx` |
| `No module named '_tkinter'` | Il tuo Python non include Tk. Su macOS con Homebrew: `brew install python-tk` |
| Le carte stampate hanno la misura sbagliata | Nella finestra di stampa imposta la scala al 100% e disattiva "adatta alla pagina" |

## 🧑‍💻 Sviluppo

Per lanciare i test installa anche le dipendenze di sviluppo:

```bash
pip install -e ".[dev]"
pytest
```


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
