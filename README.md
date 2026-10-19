# SicurCantiere

Famiglia di programmi desktop per la sicurezza nei cantieri temporanei o mobili
(Titolo IV del D.Lgs. 81/2008):

| Programma | Per chi | Documenti | File |
| --- | --- | --- | --- |
| **SicurCantiere POS** | Impresa esecutrice | POS, valutazioni dei rischi specifici (NIOSH, OCRA), verbali di consegna DPI | `.spo` |
| **SicurCantiere PSC** | Coordinatore (CSP/CSE) | PSC, fascicolo dell'opera, notifica preliminare | `.scs` |
| **SicurCantiere PiMUS** | Impresa che monta i ponteggi | PiMUS con verifiche | `.spm` |

I programmi condividono archivi, motore dei documenti e assistente AI. I file hanno la
stessa struttura interna, quindi ogni programma può aprire anche quelli degli altri
(per esempio il POS può partire dal file del PSC ricevuto dal coordinatore).

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
- **Interfaccia** con tema chiaro e scuro, barra laterale con icone, barra degli strumenti
  e barra di stato con ultimo salvataggio e riepilogo dei controlli sempre visibili
- **Pagina iniziale** con le schede dei cantieri recenti; **riepilogo a riquadri** del cantiere
  (importo, durata, uomini-giorno, picco di lavoratori, interferenze, obblighi, controlli)
- **Valutazioni dei rischi specifici con metodi normati** (non semplici checklist):
  - sollevamento manuale, compito semplice e composto: **NIOSH** (UNI ISO 11228-1), con peso limite
    raccomandato, indice di sollevamento (LI / CLI) e tutti i fattori;
  - movimenti ripetitivi degli arti superiori: **indice OCRA** (UNI ISO 11228-3), più compiti per arto;
  - risultato in tempo reale con classe colorata e **misure suggerite in base ai fattori più penalizzanti**;
  - relazione Word per ogni valutazione e inclusione automatica nel POS dell'impresa
- **Assistente AI** (OpenAI/ChatGPT predefinito, Claude in alternativa):
  - compila i parametri NIOSH/OCRA dalla descrizione dell'attività, dichiarando le ipotesi fatte;
  - suggerisce rischi, misure e DPI di una fase di lavoro;
  - scrive bozze delle sezioni della relazione del PSC e del PiMUS a partire dai dati del cantiere
- **PiMUS** (art. 136, Allegato XXII): dati del ponteggio, testi base per tutte le sezioni,
  verifiche prima del montaggio e durante l'uso, avviso automatico quando serve il progetto (art. 133)
- **Gantt interattivo**: colori per impresa con legenda, interferenze tratteggiate in rosso,
  scala giorni/settimane/mesi, linea di oggi, barre trascinabili per spostare le fasi o
  cambiarne la durata

Le funzioni da implementare sono state individuate dalla documentazione pubblica dei
software del settore e realizzate da zero: vedi [docs/analisi-funzionale.md](docs/analisi-funzionale.md).

Ogni cantiere è un singolo file (database SQLite) con l'estensione del programma, per esempio
`Cliente X.spo` nel programma POS: l'estensione viene aggiunta automaticamente. I documenti
generati (PSC, POS, PiMUS, fascicolo, notifica, relazioni di valutazione) sono file Word `.docx` separati.

## Assistente AI

Menu **Strumenti > Impostazioni assistente AI**: scegliere il fornitore (OpenAI è il
predefinito), incollare la chiave API e, se si vuole, cambiare modello. Senza chiave nelle
impostazioni si usa la variabile d'ambiente `OPENAI_API_KEY` (o `ANTHROPIC_API_KEY` per Claude).
L'assistente propone valori e testi: vanno sempre verificati, e le ipotesi fatte vengono
mostrate e riportate nella relazione.

## Stabilità

- Salvataggio automatico: ogni modifica è scritta subito sul file in una transazione.
- All'apertura viene fatta una copia di sicurezza `nomefile.scs.bak`.
- Schema del file versionato con migrazioni: i progetti vecchi si aggiornano
  da soli; quelli creati con versioni più recenti vengono rifiutati invece di essere danneggiati.
- Gli errori imprevisti vengono registrati nel log e mostrati senza chiudere il programma
  (Windows: `%APPDATA%\SicurCantiere\<nome del programma>\sicurcantiere.log`).

## Avvio da sorgente

Serve Python 3.10 o successivo.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
python -m sicurcantiere pos     # oppure psc, pimus
```

## Test

```bash
python -m pytest
```

## Eseguibile e installatore per Windows

Da Windows lanciare `scripts\build_windows.bat`: esegue i test, genera le icone e crea i tre
eseguibili in `dist\`. Se è installato [Inno Setup 6](https://jrsoftware.org/isinfo.php)
crea anche l'installatore `dist\SicurCantiere-<versione>-setup.exe`, che permette di scegliere
quali programmi installare e associa le estensioni: con un doppio clic su un file `.spo` si apre
il POS, su `.scs` il PSC, su `.spm` il PiMUS.

## Struttura

| Percorso | Contenuto |
| --- | --- |
| `sicurcantiere/db.py` | File di progetto, schema e migrazioni |
| `sicurcantiere/repository.py` | Lettura e scrittura dei dati |
| `sicurcantiere/analisi.py` | Rischi, Gantt analitico, interferenze, affollamento, obblighi |
| `sicurcantiere/archivio.py` | Archivio di lavorazioni, macchine e attrezzi |
| `sicurcantiere/controlli.py` | Controlli di completezza |
| `sicurcantiere/valutazioni/` | Metodi NIOSH e OCRA (tabelle dei fattori in un unico punto) |
| `sicurcantiere/pimus.py` | Contenuti e controlli del PiMUS |
| `sicurcantiere/ai.py` | Assistente AI (OpenAI e Claude) |
| `sicurcantiere/documenti/` | Generazione di PSC, POS, fascicolo e notifica in DOCX |
| `sicurcantiere/ui/` | Interfaccia grafica (PySide6/Qt); programmi e pagine in `edizioni.py`, tema in `tema.py`, icone in `icone.py` |
| `sicurcantiere/documenti/moduli.py` | Modulistica dell'impresa (verbale di consegna DPI) |

## Prossimi passi

- Archivio delle lavorazioni modificabile dall'utente e archivi dei responsabili ricorrenti
- DUVRI, PSS, piano di emergenza
- Altre valutazioni specifiche: traino e spinta, trasporto (ISO 11228-2), rumore, vibrazioni
- Esportazione dei costi in Excel
- Modulistica (verbali di coordinamento, consegna DPI)
- Importazione di prezzari regionali per i costi della sicurezza
- Layout di cantiere (planimetria)

I documenti generati vanno sempre verificati dal coordinatore per la sicurezza.
