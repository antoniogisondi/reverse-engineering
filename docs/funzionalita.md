# SicurCantiere: funzionalità, scelte e prossimi passi

Documento di riferimento del prodotto, da tenere aggiornato a ogni versione. Serve per il sito
di vendita, per le presentazioni ai clienti e per non perdere le decisioni prese. Il dettaglio
tecnico è nel [README](../README.md).

*Ultimo aggiornamento: versione 0.18.0, ottobre 2026.*

## Lo scopo

SicurCantiere è una suite di programmi per il **consulente della sicurezza**, cioè il
coordinatore, l'RSPP o il tecnico che redige POS, PSC e PiMUS (e in futuro DVR) per conto delle
imprese.

Rispetto agli altri software del settore punta su:
- **meno lavoro per il consulente**: ogni dato si inserisce una volta sola e si ritrova in tutti i
  documenti e in tutti i cantieri;
- **precisione**: controlli di completezza in base alla norma, valutazioni con metodi normati e
  documenti che seguono l'ordine dell'Allegato XV;
- **adattamento al singolo cantiere**: niente documenti generici, perché ogni lavorazione,
  macchina, figura e valutazione è quella del caso reale;
- **leggerezza**: un installatore piccolo, il programma che si aggiorna da solo, file di cantiere
  singoli e portabili.

È scritto da zero a partire dalla normativa e non contiene codice o contenuti di altri software.

## I programmi

| Programma | Per chi | Documenti | File |
| --- | --- | --- | --- |
| **SicurCantiere POS** | Impresa esecutrice o il suo consulente | POS, valutazioni dei rischi specifici, sostanze pericolose, consegna DPI, tesserini, schede dei lavoratori | `.spo` |
| **SicurCantiere PSC** | Coordinatore (CSP/CSE) | PSC, fascicolo dell'opera, notifica preliminare | `.scs` |
| **SicurCantiere PiMUS** | Impresa che monta i ponteggi | PiMUS con verifiche | `.spm` |
| **SicurCantiere DVR** | *in programma* | Documento di valutazione dei rischi aziendale | — |

I programmi condividono gli archivi, il motore dei documenti, l'assistente AI e la licenza. Ogni
programma apre anche i file degli altri: per esempio il POS può partire dal file del PSC.

## Funzionalità

### Dati del cantiere e soggetti
- Dati generali con verifica automatica degli obblighi: PSC e coordinatori (art. 90), notifica
  preliminare (art. 99), picco di lavoratori presenti.
- Committente, responsabile dei lavori (anche coincidente con il committente), CSP, CSE,
  progettisti, direzione lavori, con qualifica, PEC e partita IVA.
- Foto del cantiere nel documento.

### Imprese, figure e lavoratori
- **Anagrafica completa dell'impresa**: posizioni INAIL, INPS e Cassa edile, CCNL, DURC con
  scadenza, DVR, SOA, certificazioni, lavori affidati, impresa affidataria e subappalti, incaricato
  dell'art. 97, logo nel frontespizio.
- **Figure della sicurezza adattate alla realtà dell'impresa**:
  - il datore di lavoro può svolgere di persona i compiti di RSPP, primo soccorso e antincendio
    (art. 34, con avviso oltre 5 lavoratori), direttore tecnico, capocantiere e preposto;
  - le figure che l'impresa non ha (direttore tecnico, capocantiere, medico competente) si
    dichiarano non presenti con il motivo, e il POS lo spiega;
  - una persona può avere più ruoli;
  - i ruoli scritti a mano vengono riconosciuti;
  - preposto obbligatorio (D.L. 146/2021).
- **Maestranze e lavoratori autonomi**:
  - foto, idoneità sanitaria, formazione ricevuta, DPI consegnati scelti da un elenco per parte
    del corpo;
  - mansioni, cioè le lavorazioni svolte e le macchine usate da ciascuno;
  - tesserini di riconoscimento e schede dei lavoratori.
- **Archivio anagrafiche personale**: persone e imprese, con figure e maestranze, si salvano una
  volta e si riprendono in ogni cantiere e in ogni programma.

### Lavorazioni, rischi e attrezzature
- **Archivio**:
  - 268 fasi di lavoro in 99 lavorazioni e 18 categorie, filtrabili per tipo di intervento;
  - 116 macchine, attrezzi e opere provvisionali con rischi e scheda d'uso (prima, durante e
    dopo l'uso, DPI dell'operatore);
  - lavorazioni personalizzate dall'utente, riutilizzabili negli altri cantieri.
- **Per ogni fase**:
  - descrizione, addetto, modalità organizzative, turni e procedure richieste dal PSC;
  - rischi con probabilità × danno e livello colorato, misure e DPI;
  - rischi dichiarati "non presenti" con la motivazione;
  - vista Struttura con lavoratori, attrezzi, macchine, rischi, misure e DPI.
- **Codici delle fasi automatici**: non si inseriscono a mano. Le fasi dell'archivio tengono il
  loro codice; quelle create da zero prendono la sigla della lavorazione (per esempio ST.xx per le
  strutture), oppure UT.xx finché la lavorazione non viene indicata.
- **Valutazioni specifiche automatiche**: le valutazioni necessarie nascono da sole dai rischi
  delle lavorazioni e delle macchine, e restano "da eseguire" finché non si inseriscono i dati.

### Valutazioni dei rischi specifici con metodi normati
- Sollevamento: NIOSH, compito semplice e composto (UNI ISO 11228-1).
- Traino e spinta: tavole di Snook e Ciriello (UNI ISO 11228-2).
- Trasporto manuale: masse cumulate e tavole (UNI ISO 11228-1).
- Movimenti ripetitivi: indice OCRA (UNI ISO 11228-3).
- Rumore: LEX,8h, picco, valori dell'art. 189 e attenuazione dei protettori (metodo SNR).
- Vibrazioni mano-braccio e corpo intero: A(8), valori dell'art. 201 e tempi d'uso che portano
  al valore d'azione.
- Risultato in tempo reale, misure suggerite in base ai fattori peggiori, relazione Word e
  inclusione automatica nel POS.

### Sostanze pericolose
- Importazione dalla scheda di sicurezza in PDF: frasi H, avvertenza e data della scheda.
- Pittogrammi e categorie di pericolo ricavati dalle frasi H, con le misure.
- Capitolo del POS ed elenco stampabile.

### Coordinamento (PSC)
- Gantt interattivo con colori per impresa, barre trascinabili e scala giorni, settimane o mesi.
- Gantt analitico: uomini-giorno, durata, grafici di affollamento e pericolosità.
- Interferenze tra imprese nella stessa zona, ordinate per gravità, con le prescrizioni del
  coordinatore.
- Costi della sicurezza, fascicolo dell'opera e notifica preliminare.

### Dal PSC al POS
- **PSC fatto con SicurCantiere PSC**: nella pagina Imprese, «Prepara il POS dell'impresa...» crea il
  file `.spo` dell'impresa. Contiene cantiere, soggetti, l'impresa, le sue lavorazioni con rischi,
  macchine, valutazioni e sostanze, e per ogni fase le interferenze con le altre imprese e le
  prescrizioni del coordinatore. Non serve l'AI.
- **PSC fatto con qualsiasi altro programma** (PDF o Word): in SicurCantiere POS, «Nuovo POS da un
  PSC...».
  - **Lettura**: l'assistente AI legge il PSC una volta sola e trova cantiere, soggetti, imprese,
    fasi con rischi e prescrizioni, interferenze e procedure richieste ai POS.
  - **Scelta**: si spuntano le imprese di cui preparare il POS e, se il PSC non le assegna, le fasi
    che ciascuna svolge.
  - **Risultato**: per ogni impresa nasce un file `.spo` da completare. Le fasi riconosciute
    nell'archivio portano con sé macchine, attrezzi, rischi e misure; le altre riportano i rischi
    del PSC da valutare.
  - **Consumo contenuto**: il testo viene ripulito in locale prima dell'invio (intestazioni,
    numeri di pagina, indice). Prima dell'invio il programma mostra la stima dei token e chiede
    conferma. Per esempio, un PSC di 126 pagine richiede circa 65 mila token in 6 richieste.
  - **Verifiche future**: la lettura del PSC resta salvata nel file del POS, per controllare in
    seguito che il POS risponda a ogni richiesta del PSC.
- In entrambi i casi il POS non si genera subito: prima si completa il file in SicurCantiere POS.

### PiMUS
- Dati del ponteggio, testi base per tutte le sezioni e verifiche prima del montaggio e durante
  l'uso.
- Avviso automatico quando serve il progetto (art. 133).

### Il documento finale (POS)
- **Capitoli nell'ordine dell'Allegato XV 3.2.1**, in tre parti:
  - il cantiere e l'impresa;
  - attività e valutazione dei rischi;
  - misure, protezione ed emergenze.
- **Impaginazione propria**:
  - copertina con dati e firme;
  - capitoli numerati con il riferimento di legge e indice automatico;
  - intestazione con impresa e revisione, "Pagina X di Y";
  - tabelle leggere con l'intestazione ripetuta a ogni pagina e il livello di rischio colorato;
  - lavorazioni e fasi in riquadri.
- **Tutto quello che si compila finisce nel documento**, compresi i testi scritti con l'AI:
  - le voci vuote non stampano righe vuote;
  - le firme finali portano i nomi del datore di lavoro, dell'RSPP, del medico competente e
    dell'RLS o RLST.
- **Contenuti generati in automatico**:
  - cartelli di sicurezza scelti in base ai rischi;
  - icone dei DPI;
  - numeri di emergenza;
  - documenti da tenere in cantiere;
  - allegati riportati solo se pertinenti.
- Tabella delle revisioni, con la data del documento presa dall'ultima revisione.

### Controlli prima della stampa
- Errori e avvisi per ogni pagina, ciascuno con il collegamento alla pagina da correggere. Per
  esempio: DURC o idoneità scaduti, figure obbligatorie mancanti, rischi senza misure,
  valutazioni da eseguire, sostanze senza scheda.

### Assistente AI (incluso nella licenza, spento all'inizio)
- **Incluso nella licenza**: "SicurCantiere AI" funziona senza chiavi API, passando dal server ponte
  dell'ufficio.
  - **Quota mensile per piano**: 1,5 milioni di crediti per i singoli, 3 milioni per il Completo,
    8 milioni per lo Studio.
  - **Limiti**: tetto giornaliero del 30% e ricariche acquistabili.
  - **Motori**: Standard (DeepSeek) per tutti; Avanzato (Claude) nel piano Studio, a 8 crediti per
    token.
  - **Credito**: si verifica in *Strumenti > Impostazioni assistente AI*.
- **Solo con licenza**: durante la prova gratuita, o con la licenza scaduta, l'assistente non è
  disponibile e i suoi pulsanti non compaiono. Nel programma non ci sono chiavi API: quelle delle
  versioni precedenti vengono cancellate dal PC.
- **Cosa fa**: suggerisce rischi, misure e DPI di fasi, macchine e attrezzature, scrive bozze dei
  testi, compila i parametri delle valutazioni dichiarando le ipotesi e completa le schede delle
  sostanze.
- **Riservatezza**: non invia nomi di persone. Il programma dice dove ciascun fornitore tratta i
  dati.

### Programma
- **Aggiornamento automatico**: il programma avvisa della nuova versione, la installa e si riapre
  da solo.
- **Interfaccia**: tema chiaro e scuro, colore per programma, barra laterale con i problemi di
  ogni pagina, guida rapida (F1).
- **Chiusura con modifiche non salvate**: il programma chiede "Salva / Non salvare / Annulla".
  "Non salvare" riporta il cantiere all'ultimo salvataggio (o all'apertura).
- **Tutto in italiano**, compresi i pulsanti e i menu standard (Sì/No/Annulla, Copia/Incolla).
- **Sicurezza dei dati**: salvataggio automatico a ogni modifica e copie di sicurezza all'apertura.
  I file dei progetti vecchi si aggiornano da soli.

## Licenze

- **Codice offline**: il codice `SC1-…` è firmato e il programma lo verifica senza collegarsi a
  internet. Non è legato al PC.
- **Piani**:
  - POS, PSC o PiMUS singoli;
  - Completo (tutti e tre);
  - Studio (tutti e tre, più postazioni).
- **Prova gratuita**: 30 giorni con un solo cantiere. I documenti stampati in prova riportano
  "versione di prova".
- **Alla scadenza** il programma continua a funzionare, ma non riceve più gli aggiornamenti
  pubblicati dopo la scadenza né l'assistenza.
- **Programmi non inclusi** nel piano: compare la pagina "Non incluso nella tua licenza".
- **Codice nascosto**: il codice di licenza è nascosto come una password in *Aiuto > Licenza*, con
  la spunta "Mostra il codice" per controllarlo.
- **Titolare in vista**: il nome compare nella barra del programma, in *Aiuto > Licenza* e in
  piccolo a piè di pagina di ogni documento generato, oltre che nelle proprietà del file. Passare
  il codice ad altri significa stampare documenti con il nome di un altro studio.
- **Gestionale web** sul server dell'ufficio ([licenze/README.md](../licenze/README.md)):
  - clienti, emissione, rinnovo, pagamenti ed esportazione CSV;
  - promemoria delle scadenze a 30, 60 o 90 giorni;
  - email di consegna e di rinnovo pronte;
  - registro dei codici consegnati e dei promemoria inviati;
  - accesso con verifica in due passaggi.

## Decisioni prese

- Licenze offline, senza vincolo al PC; alla scadenza il programma continua a funzionare.
- La chiave privata delle licenze resta solo sul server; nel programma c'è la chiave pubblica.
- AI spenta finché il cliente non la attiva con la sua chiave; nessun nome di persona viene inviato.
- Si pubblica una nuova versione solo quando lo decide il titolare.
- Grafica dei documenti propria, diversa da quella degli altri software del settore.

## Prossimi passi

1. **Licenze, passo 2**: attivazione online con conteggio delle postazioni, sullo stesso server
   ponte dell'AI (già raggiungibile da internet con Tailscale Funnel).
1. **Server ponte AI**: valutare un motore Standard ospitato in Europa (stesso modello DeepSeek
   presso un fornitore UE, oppure Mistral) per il GDPR. Basta cambiare l'indirizzo, il modello e la
   sede in `ai.env`.
2. **Sito di vendita**: presentazione, prezzi, acquisto della licenza e download.
3. **SicurCantiere DVR.**
4. **Idee per distinguersi**, da scegliere:
   - verifica automatica, punto per punto, che il POS risponda alle richieste del PSC letto (la
     lettura è già salvata nel file);
   - verifica dei POS ricevuti da parte del coordinatore (art. 92), con il verbale di verifica;
   - più documenti dagli stessi dati: nomine, richiesta della documentazione dell'Allegato XVII,
     verbali di coordinamento, informativa ai lavoratori;
   - scadenzario di tutti i cantieri (DURC, idoneità, formazione, verifiche) con le email di
     sollecito;
   - modelli di cantiere tipo che si arricchiscono con l'uso;
   - revisioni con l'elenco automatico delle modifiche;
   - sopralluogo dal telefono con il verbale;
   - importazione dei vecchi documenti per chi arriva da altri programmi;
   - assistente AI che cita l'articolo di legge di ogni suggerimento.
