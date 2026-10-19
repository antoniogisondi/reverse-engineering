# Analisi funzionale

Questo documento confronta le funzioni dichiarate nella documentazione
**pubblica** dei software per la sicurezza nei cantieri presenti sul mercato
(pagine prodotto ACCA CerTus, consultate a ottobre 2026) con il modo in cui
SicurCantiere le realizza.

## Regole del progetto (clean room)

- Si usano solo informazioni pubbliche su **cosa** fa un programma, cioè le funzioni.
  Non si decompila, non si disassembla e non si analizzano gli eseguibili.
- Non si copiano testi, schede di rischio, piani-tipo, prezzari, grafica,
  icone o nomi commerciali. Gli archivi di SicurCantiere sono scritti da zero
  partendo dal D.Lgs. 81/2008 e dai suoi allegati.
- La struttura dei documenti (PSC, POS, fascicolo, notifica) segue gli
  allegati di legge (XV, XVI, XII) e non i modelli di stampa altrui.
- L'interfaccia è progettata per SicurCantiere e non imita schermate esistenti.

## Mappa delle funzioni

| Funzione descritta pubblicamente | SicurCantiere | Stato |
| --- | --- | --- |
| Redazione di PSC (Allegato XV 2.1.2) | `documenti/psc.py` | v0.1 |
| Redazione di POS (Allegato XV 3.2.1) | `documenti/pos.py`, con dati di impresa e lavoratori | v0.2 |
| Fascicolo dell'opera (Allegato XVI) | `documenti/fascicolo.py`, schede I, II e III | v0.2 |
| Notifica preliminare (Allegato XII) | `documenti/notifica.py`, campi ricavati dal progetto | v0.2 |
| Archivio delle fasi di lavoro per macrocategorie (nuove costruzioni, ristrutturazioni, infrastrutture, restauro) | `archivio.py`: lavorazioni con categoria, macchine e attrezzi, rischi, misure, DPI | v0.2 |
| Archivio di macchine e attrezzi con i loro rischi | `archivio.py`, `ATTREZZATURE`: i rischi della macchina vengono importati insieme alla fase | v0.2 |
| Personalizzazione delle lavorazioni (rischi, misure, attrezzature) | Tabelle modificabili nella pagina Fasi | v0.2 |
| Gantt analitico: importo, incidenza della manodopera, squadra → durata | `analisi.durata_stimata`, pulsante "Calcola durata" | v0.2 |
| Grafici di affollamento e di pericolosità | Strisce sotto il Gantt (`ui/gantt.py`) | v0.2 |
| Contemporaneità e interferenze per impresa e zona di lavoro | `analisi.interferenze`, campo *zona* delle fasi | v0.2 |
| Prescrizioni assegnate solo alle interferenze selezionate | Pagina Interferenze, tabella `prescrizioni` | v0.2 |
| Gravità delle interferenze | Livello massimo di rischio delle due fasi | v0.2 |
| Stima dei costi della sicurezza | Pagina Costi | v0.1 |
| Gestione delle revisioni dei piani | Tabella `revisioni`, riportata nel frontespizio | v0.2 |
| Controlli che segnalano errori o parti incomplete prima della stampa | `controlli.py`, pagina Documenti | v0.2 |
| Archivi utente (responsabili ricorrenti) | - | da fare |
| Esportazione dei costi in xlsx | - | da fare |
| DUVRI, PSS, PEE, piano scavi, demolizioni, amianto | - | da fare |
| Valutazioni specifiche con metodi normati | `valutazioni/`: NIOSH semplice e composto, OCRA; misure dai fattori peggiori | v0.3 |
| PiMUS ponteggi (modulo separato nel prodotto commerciale) | `pimus.py`, `documenti/pimus.py` | v0.3 |
| Assistente AI (chatbot per la redazione) | `ai.py`: compilazione parametri, rischi, testi; OpenAI o Claude | v0.3 |
| Sostanze pericolose e schede di sicurezza | `sostanze.py`, `sds.py`: classificazione dalle frasi H, lettura SDS in PDF | v0.5 |
| Valutazioni rumore e vibrazioni | `valutazioni/rumore.py`, `valutazioni/vibrazioni.py` | v0.6 |
| Valutazioni traino/spinta, trasporto, rischio chimico | - | da fare |
| Modulistica per CSE e imprese (verbali, consegna DPI) | - | da fare |
| Layout di cantiere e modello 3D/BIM | - | fuori obiettivo per ora |

## Scelte di progetto

### Gantt analitico
Per ogni fase si può indicare l'**importo** e l'**incidenza della manodopera** (%).
Con il **costo medio di un uomo-giorno** (nei dati generali) si ottengono gli
uomini-giorno della fase, `importo × incidenza / costo`. Dividendoli per i
lavoratori della squadra si ottiene la durata in giorni lavorativi, da cui la
data di fine.

### Affollamento e pericolosità
Per ogni giorno lavorativo:
- **affollamento**: somma dei lavoratori delle fasi attive;
- **pericolosità**: livello di rischio P×D più alto tra le fasi attive.

Il picco di affollamento è il "numero massimo presunto di lavoratori"
richiesto dalla notifica preliminare.

### Interferenze
Due fasi interferiscono quando i periodi si sovrappongono, le imprese sono
diverse (o non ancora assegnate) e la zona di lavoro coincide (o non è indicata).
La gravità è il livello di rischio più alto tra le due fasi. Il coordinatore
scrive le prescrizioni solo per le coppie che lo richiedono. Nel PSC le
interferenze senza prescrizione ricevono quella generica di sfasamento.
