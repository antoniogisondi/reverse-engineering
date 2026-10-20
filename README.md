# SicurCantiere

Famiglia di programmi desktop per la sicurezza nei cantieri temporanei o mobili
(Titolo IV del D.Lgs. 81/2008):

| Programma | Per chi | Documenti | File |
| --- | --- | --- | --- |
| **SicurCantiere POS** | Impresa esecutrice | POS, valutazioni dei rischi specifici (NIOSH, traino e spinta, trasporto, OCRA, rumore, vibrazioni), sostanze pericolose, verbali di consegna DPI | `.spo` |
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
- **Soggetti** con compiti di sicurezza (committente, responsabile dei lavori, CSP, CSE, progettisti,
  direzione lavori, collaudatore...), con qualifica, "nella persona di", P. IVA e PEC; una spunta indica
  che il **committente è anche responsabile dei lavori** e i documenti lo riportano in entrambi i ruoli
- **Imprese e lavoratori**:
  - tipologia (affidataria, affidataria ed esecutrice, esecutrice, subappaltatrice, lavoratore autonomo,
    nolo a caldo) e impresa affidataria di riferimento per i subappalti;
  - anagrafica completa: forma giuridica, sede legale, email e PEC, recapito in cantiere, CCIAA, ATECO,
    posizioni INAIL, INPS e Cassa edile, CCNL, organico, scadenza del DURC, data del DVR, SOA,
    certificazioni, tipologia e importo dei lavori affidati;
  - figure della sicurezza come elenco (RSPP, ASPP, medico competente, RLS/RLST, dirigenti, direttore
    tecnico, capocantiere, preposti, addetti al primo soccorso e antincendio...) con recapiti e
    formazione; spunta per il datore di lavoro che svolge i compiti di RSPP (art. 34);
  - **maestranze**: nome e cognome, qualifica da elenco, data e luogo di nascita, matricola, assunzione,
    foto, idoneità sanitaria, **DPI consegnati** scelti da un elenco per parte del corpo (con quelli delle
    lavorazioni già proposti), formazione ricevuta (base, rischi della mansione, rischi del cantiere,
    DPI di terza categoria, altri corsi);
  - **lavoratori autonomi** dell'impresa, con periodo in cantiere e dati fiscali;
  - **mansioni**: per ogni lavoratore le lavorazioni svolte e le macchine o attrezzature utilizzate;
    in rosso quelle a cui non è ancora assegnato nessuno;
  - **tesserini di riconoscimento** con foto (artt. 18, 21 e 26; L. 136/2010) e **schede dei lavoratori**
    con mansioni, rischi, valutazioni specifiche, DPI e formazione;
  - testi specifici del POS
- **Archivio anagrafiche** comune a tutti i cantieri e ai tre programmi: persone (committenti,
  coordinatori, RSPP, medici, preposti...) e imprese con figure e maestranze si salvano una volta e si
  riprendono con «Dall'archivio...» (menu Strumenti > Archivio anagrafiche per consultarlo)
- **Archivio** di **268 fasi di lavoro** in 99 lavorazioni e 18 categorie (allestimento e smobilizzo,
  demolizioni, bonifiche, movimento terra, fondazioni speciali, strutture, murature, coperture, facciate,
  opere interne, impianti, rinnovabili, reti, strade, pubblica illuminazione, aree verdi, restauri, tagli
  e perforazioni), filtrabili per tipologia di intervento, e di **116 macchine, attrezzi e opere
  provvisionali** con rischi e scheda d'uso. Contenuti scritti da zero dalla normativa: i punti da far
  verificare a un coordinatore sono in [docs/verifiche-archivio.md](docs/verifiche-archivio.md). Nodo
  **UTENTE** con le lavorazioni personalizzate salvate da un cantiere e riutilizzabili negli altri
- **Fasi di lavoro** con descrizione dell'attività, addetto, modalità organizzative, turni, procedure richieste
  dal PSC, vista **Struttura** (lavoratori, attrezzi, macchine, rischi, misure, DPI) e collegamento di ogni
  rischio alla sua valutazione specifica
- **Schede d'uso** di macchine e attrezzi con misure prima, durante e dopo l'uso e DPI dell'operatore, riportate
  nel POS nei capitoli delle attrezzature e delle macchine
- **Gantt analitico**: per ogni fase importo, incidenza della manodopera e squadra
  → uomini-giorno e durata; grafici di **affollamento** e **pericolosità**
- **Interferenze** tra imprese diverse nella stessa zona, ordinate per gravità, con
  prescrizioni del coordinatore per ogni coppia di fasi
- **Costi della sicurezza** con totale
- **Relazione** del PSC (sezioni dell'Allegato XV)
- **Fascicolo dell'opera**: interventi di manutenzione e documentazione di supporto
- **Documenti Word**: PSC, POS per impresa, fascicolo dell'opera, notifica preliminare,
  con tabella delle **revisioni** nel frontespizio
- **Impaginazione del POS**: copertina incorniciata, capitoli su banda colorata con il riferimento
  normativo, indice automatico, foto del cantiere, cartelli di sicurezza scelti in base ai rischi,
  icone dei DPI per fase e attrezzatura, tabella dei rischi con il livello colorato, numeri utili
  e documenti da tenere in cantiere
- **Controlli di completezza** prima della stampa (errori e avvisi)
- **Interfaccia** con tema chiaro e scuro, barra laterale con icone, barra degli strumenti
  e barra di stato con ultimo salvataggio e riepilogo dei controlli sempre visibili
- **Pagina iniziale** con le schede dei cantieri recenti; **riepilogo a riquadri** del cantiere
  (importo, durata, uomini-giorno, picco di lavoratori, interferenze, obblighi, controlli)
- **Valutazioni dei rischi specifici con metodi normati** (non semplici checklist):
  - sollevamento manuale, compito semplice e composto: **NIOSH** (UNI ISO 11228-1), con peso limite
    raccomandato, indice di sollevamento (LI / CLI) e tutti i fattori;
  - **traino e spinta** (UNI ISO 11228-2, metodo 1): forze iniziali e di mantenimento misurate confrontate
    con le tavole di Snook e Ciriello (1991) per il 90% della popolazione, più azioni per valutazione;
  - **trasporto manuale** (UNI ISO 11228-1): massa cumulata al minuto, all'ora e nel turno rispetto ai limiti
    per distanza, più il confronto di ogni trasporto con le tavole di Snook e Ciriello;
  - movimenti ripetitivi degli arti superiori: **indice OCRA** (UNI ISO 11228-3), più compiti per arto;
  - **rumore** (Titolo VIII Capo II): LEX,8h dalle attività del turno, picco, confronto con i valori
    di azione e limite dell'art. 189, attenuazione dei protettori (metodo SNR della UNI EN 458);
  - **vibrazioni** mano-braccio e corpo intero (Titolo VIII Capo III): A(8), valori d'azione e
    limite dell'art. 201, minuti di utilizzo che portano al valore d'azione per ogni attrezzatura;
  - risultato in tempo reale con classe colorata e **misure suggerite in base ai fattori più penalizzanti**;
  - relazione Word per ogni valutazione e inclusione automatica nel POS dell'impresa
- **Assistente AI** (DeepSeek predefinito, OpenAI/ChatGPT e Claude in alternativa):
  - compila i parametri NIOSH/OCRA dalla descrizione dell'attività, dichiarando le ipotesi fatte;
  - suggerisce rischi, misure e DPI di una fase di lavoro;
  - scrive bozze delle sezioni della relazione del PSC e del PiMUS a partire dai dati del cantiere
- **Sostanze e miscele pericolose** (POS, Allegato XV 3.2.1 lett. e): importazione dalla scheda
  di sicurezza in PDF (frasi H, avvertenza, data di revisione; l'assistente AI completa produttore,
  DPI, misure e conservazione), pittogrammi ricavati dalle frasi H con le precedenze del CLP,
  categorie di pericolo (cancerogeni/mutageni, tossici per la riproduzione, sensibilizzanti,
  corrosivi, infiammabili...) con le misure; capitolo nel POS ed elenco stampabile
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

Menu **Strumenti > Impostazioni assistente AI**: scegliere il fornitore (DeepSeek è il
predefinito, con il modello `deepseek-flash`; in alternativa OpenAI o Claude), incollare la chiave API
e, se si vuole, cambiare modello. Senza chiave nelle impostazioni si usa la variabile d'ambiente
`DEEPSEEK_API_KEY` (oppure `OPENAI_API_KEY` o `ANTHROPIC_API_KEY`). Su Windows la variabile si imposta da
Pannello di controllo > Sistema > Impostazioni di sistema avanzate > Variabili d'ambiente, oppure con
`setx DEEPSEEK_API_KEY "la-tua-chiave"` dal prompt dei comandi, poi riaprendo il programma.
L'assistente propone valori e testi: vanno sempre verificati, e le ipotesi fatte vengono
mostrate e riportate nella relazione.

## Stabilità

- Salvataggio automatico: ogni modifica è scritta subito sul file in una transazione; il pulsante
  **Salva** (Ctrl+S) scrive anche il campo in corso di modifica.
- All'apertura viene fatta una copia di sicurezza del cantiere nella cartella del programma
  (Windows: `%APPDATA%\SicurCantiere\copie di sicurezza`), tenendo le ultime 5 per ogni cantiere:
  accanto ai file dei cantieri non compaiono altri file.
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
| `sicurcantiere/valutazioni/` | Metodi NIOSH, OCRA, rumore e vibrazioni (tabelle e soglie in un unico punto per metodo) |
| `sicurcantiere/pimus.py` | Contenuti e controlli del PiMUS |
| `sicurcantiere/sostanze.py`, `sds.py` | Classificazione dalle frasi H e lettura delle schede di sicurezza |
| `sicurcantiere/ai.py` | Assistente AI (OpenAI e Claude) |
| `sicurcantiere/documenti/` | Generazione di PSC, POS, fascicolo e notifica in DOCX |
| `sicurcantiere/ui/` | Interfaccia grafica (PySide6/Qt); programmi e pagine in `edizioni.py`, tema in `tema.py`, icone in `icone.py` |
| `sicurcantiere/documenti/moduli.py`, `maestranze.py` | Modulistica dell'impresa: consegna DPI, tesserini, schede dei lavoratori |
| `sicurcantiere/documenti/stile.py`, `segnaletica.py` | Stile dei documenti (bande, schede, tabelle colorate, copertina) e cartelli di sicurezza; le immagini in `risorse/segnali` si rigenerano con `scripts/genera_segnali.py` |
| `sicurcantiere/anagrafiche.py`, `archivio_utente.py` | Ruoli, figure, DPI, mansioni; archivio anagrafiche dell'utente |

## Prossimi passi

- Ampliamento dell'archivio delle lavorazioni (contenuti scritti da zero)
- DUVRI, PSS, piano di emergenza
- Altre valutazioni specifiche: rischio chimico
- Esportazione dei costi in Excel
- Modulistica del CSE (verbali di coordinamento e di sopralluogo)
- Importazione di prezzari regionali per i costi della sicurezza
- Layout di cantiere (planimetria)

I documenti generati vanno sempre verificati dal coordinatore per la sicurezza.
