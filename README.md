# SicurCantiere

Applicazione desktop per la sicurezza nei cantieri temporanei o mobili
(Titolo IV del D.Lgs. 81/2008): Piano di Sicurezza e Coordinamento,
cronoprogramma con verifica delle interferenze, stima dei costi della sicurezza.

È un progetto scritto da zero a partire dalla normativa. Non contiene codice,
archivi o contenuti di software commerciali.

## Funzioni

- **Dati generali** del cantiere, con verifica automatica degli obblighi:
  PSC/coordinatori (art. 90) e notifica preliminare (art. 99, soglia 200 uomini-giorno)
- **Soggetti** con compiti di sicurezza (committente, CSP, CSE, ...)
- **Imprese** affidatarie, esecutrici e lavoratori autonomi
- **Fasi di lavoro** con importazione dall'archivio, rischi valutati con la matrice
  P x D, misure di prevenzione e DPI
- **Cronoprogramma** (Gantt) con evidenza delle fasi interferenti in rosso
- **Costi della sicurezza** con totale
- **Relazione**: sezioni testuali dell'Allegato XV
- **Generazione del PSC** in formato Word (.docx)

Ogni cantiere è un singolo file `.scs` (database SQLite).

## Stabilità

- Salvataggio automatico: ogni modifica è scritta subito sul file in una transazione.
- All'apertura viene fatta una copia di sicurezza `nomefile.scs.bak`.
- Schema del file versionato con migrazioni: i progetti vecchi si aggiornano
  da soli; quelli creati con versioni più recenti vengono rifiutati invece di essere danneggiati.
- Gli errori imprevisti vengono registrati nel log e mostrati senza chiudere il programma
  (Windows: `%APPDATA%\SicurCantiere\SicurCantiere\sicurcantiere.log`).

## Avvio da sorgente

Serve Python 3.10 o successivo.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
python -m sicurcantiere
```

## Test

```bash
python -m pytest
```

## Eseguibile per Windows

Da Windows lanciare `scripts\build_windows.bat`: esegue i test e crea
`dist\SicurCantiere\SicurCantiere.exe` (cartella da copiare così com'è).

## Struttura

| Percorso | Contenuto |
| --- | --- |
| `sicurcantiere/db.py` | File di progetto, schema e migrazioni |
| `sicurcantiere/repository.py` | Lettura e scrittura dei dati |
| `sicurcantiere/analisi.py` | Rischi, interferenze, uomini-giorno, obblighi |
| `sicurcantiere/archivio.py` | Archivio di base delle lavorazioni |
| `sicurcantiere/documenti/psc.py` | Generazione del PSC in DOCX |
| `sicurcantiere/ui/` | Interfaccia grafica (PySide6/Qt) |

## Prossimi passi

- POS (Allegato XV punto 3.2) e fascicolo dell'opera (Allegato XVI)
- Notifica preliminare (Allegato XII)
- Archivio delle lavorazioni modificabile dall'utente
- Importazione di prezzari regionali per i costi della sicurezza
- Layout di cantiere (planimetria)

I documenti generati vanno sempre verificati dal coordinatore per la sicurezza.
