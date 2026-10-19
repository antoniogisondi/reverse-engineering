# SicurCantiere

Applicazione desktop per la sicurezza nei cantieri temporanei o mobili
(Titolo IV del D.Lgs. 81/2008): Piano di Sicurezza e Coordinamento,
cronoprogramma con verifica delle interferenze, stima dei costi della sicurezza.

È un progetto scritto da zero a partire dalla normativa. Non contiene codice,
archivi o contenuti di software commerciali.

## Funzioni

- **Dati generali** del cantiere, con verifica automatica degli obblighi:
  PSC e coordinatori (art. 90), notifica preliminare (art. 99), picco di lavoratori presenti
- **Soggetti** con compiti di sicurezza (committente, CSP, CSE, ...)
- **Imprese e lavoratori**: figure della sicurezza (datore di lavoro, RSPP, medico competente,
  RLS, preposto, addetti alle emergenze), lavoratori con mansione, formazione e idoneità,
  testi specifici del POS
- **Archivio** di 27 lavorazioni in 5 categorie (allestimento, nuove costruzioni,
  ristrutturazioni, infrastrutture, restauro) e di 21 macchine, attrezzi e opere
  provvisionali. Ognuna ha i propri rischi, che vengono importati con la fase
- **Gantt analitico**: per ogni fase importo, incidenza della manodopera e squadra
  → uomini-giorno e durata; grafici di **affollamento** e **pericolosità**
- **Interferenze** tra imprese diverse nella stessa zona, ordinate per gravità, con
  prescrizioni del coordinatore per ogni coppia di fasi
- **Costi della sicurezza** con totale
- **Relazione** del PSC (sezioni dell'Allegato XV)
- **Fascicolo dell'opera**: interventi di manutenzione e documentazione di supporto
- **Documenti Word**: PSC, POS per impresa, fascicolo dell'opera, notifica preliminare,
  con tabella delle **revisioni** nel frontespizio
- **Controlli di completezza** prima della stampa (errori e avvisi)

Le funzioni da implementare sono state individuate dalla documentazione pubblica dei
software del settore e realizzate da zero: vedi [docs/analisi-funzionale.md](docs/analisi-funzionale.md).

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
| `sicurcantiere/analisi.py` | Rischi, Gantt analitico, interferenze, affollamento, obblighi |
| `sicurcantiere/archivio.py` | Archivio di lavorazioni, macchine e attrezzi |
| `sicurcantiere/controlli.py` | Controlli di completezza |
| `sicurcantiere/documenti/` | Generazione di PSC, POS, fascicolo e notifica in DOCX |
| `sicurcantiere/ui/` | Interfaccia grafica (PySide6/Qt) |

## Prossimi passi

- Archivio delle lavorazioni modificabile dall'utente e archivi dei responsabili ricorrenti
- DUVRI, PSS, piano di emergenza
- Valutazioni specifiche (rumore, vibrazioni, movimentazione carichi)
- Esportazione dei costi in Excel
- Modulistica (verbali di coordinamento, consegna DPI)
- Importazione di prezzari regionali per i costi della sicurezza
- Layout di cantiere (planimetria)

I documenti generati vanno sempre verificati dal coordinatore per la sicurezza.
