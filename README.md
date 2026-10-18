
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


## 📁 Struttura della repository

```
proxyx/                 # repository
├── README.md           # questa panoramica + roadmap
├── assets/             # screenshot usati nei README
└── proxyx/             # l'applicazione desktop (package Python)
    └── README.md       # installazione, avvio, configurazione
```

Per installare e avviare l'app: **[proxyx/README.md](proxyx/README.md)**.


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
