# SicurCantiere: funzionalità, scelte e prossimi passi

Documento di riferimento del prodotto, da tenere aggiornato a ogni versione. Serve per il sito
di vendita, per le presentazioni ai clienti e per non perdere le decisioni prese. Il dettaglio
tecnico è nel [README](../README.md).

*Ultimo aggiornamento: versione 0.20.0, ottobre 2026.*

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

### Il documento finale (PSC, fascicolo, notifica)
- **Stessa impaginazione del POS**, nei colori arancioni del programma PSC: copertina con
  committente, firme, logo e dati dello studio del coordinatore, indice, revisioni, capitoli
  numerati con il riferimento di legge.
- **Tutti i contenuti dell'Allegato XV** (punti 2.1.2, 2.1.3, 2.1.4, 2.2, 2.3 e 4), in quattro parti:
  - *l'opera e i soggetti*: dati generali (imprese, lavoratori, uomini-giorno, durata), contesto
    dell'area con foto e mappe, descrizione dell'opera, soggetti con la data di incarico, imprese
    con datori di lavoro e subappalti, **organigramma disegnato automaticamente**, documentazione da
    tenere in cantiere;
  - *area, organizzazione e lavorazioni*: metodo con le scale di probabilità e danno e la matrice
    colorata, area di cantiere nelle tre voci del punto 2.2.1, caratteristiche idrogeologiche,
    **organizzazione del cantiere nelle voci a)-n) del punto 2.2.2**, segnaletica, scelte
    progettuali, lavorazioni con i rischi per fase, **riepilogo per rischio**, schede di macchine
    e attrezzature con la **potenza sonora** (art. 190), **lavori a rischio particolare (Allegato
    XI)** e **valutazione del rischio da ordigni bellici** (art. 91, comma 2-bis);
  - *coordinamento*: interferenze con gravità e prescrizioni, modalità di verifica del CSE,
    **procedure complementari da sviluppare nei POS** (punto 2.1.3), uso comune, cooperazione,
    emergenze con i numeri nazionali e le strutture del territorio;
  - *tempi e costi*: programma dei lavori, **diagramma di Gantt** su pagine orizzontali (barre per
    impresa, zone, interferenze in rosso, affollamento e pericolosità), **costi della sicurezza per
    categoria del punto 4.1.1** con subtotali e prezzario di riferimento.
- **Tavole allegate** (punto 2.1.4): planimetria, tavola degli scavi, profilo altimetrico, come
  immagini o **PDF inseriti pagina per pagina** nel documento.
- Firme del coordinatore, del committente o responsabile dei lavori, del CSE e, per accettazione,
  dei datori di lavoro delle imprese.
- Nella pagina «Relazione del PSC» ogni voce ha la sua guida alla compilazione e la bozza con l'AI;
  i controlli segnalano voci obbligatorie vuote, Allegato XI non verificato, scavi senza valutazione
  degli ordigni, planimetria mancante, costi senza categoria.
- **Dati da completare** come nel POS.
- **Fascicolo dell'opera** con le schede dell'Allegato XVI e **notifica preliminare** con le voci
  dell'Allegato XII, con la stessa grafica e i dati mancanti evidenziati.

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

### Documenti composti: bozza, emissione, consegna (POS e PSC)
- **Il documento resta salvato nel cantiere**, con lo storico delle revisioni. Per ognuna si
  vedono stato, data, descrizione e dati mancanti.
- **Stati**:
  - *bozza*: si ricompone quante volte serve, con la filigrana BOZZA;
  - *emessa*: versione definitiva bloccata; per cambiarla si compone la revisione successiva;
  - *consegnata*: con destinatario e data;
  - *annullata*: resta nello storico ma non vale più.
- **Revisioni automatiche**: ogni composizione scrive la sua riga nella tabella delle revisioni del
  documento (numero, data, motivo).
- **Modifica in Word senza perdere il collegamento**: la bozza si apre in Word, si modifica e si
  riprende nel cantiere; le revisioni emesse si aprono in sola lettura.
- **Capitoli su misura che restano quando si ricompone** (dove gli altri programmi perdono le
  modifiche):
  - togliere un capitolo;
  - aggiungere un testo in fondo al capitolo;
  - sostituirne il contenuto (titolo e riferimento di legge restano);
  - se poi cambiano i dati da cui il capitolo era composto, il programma avvisa di ricontrollare
    il testo scritto a mano.
- **Confronto tra due revisioni**, capitolo per capitolo: capitoli aggiunti, tolti e righe
  cambiate.
- Esportazione in Word della revisione scelta.

### Dati da completare (al posto dei campi tra simboli degli altri programmi)
- Ogni dato mancante è classificato:
  - *obbligatorio per legge* (contenuti minimi dell'Allegato XV);
  - *consigliato*;
  - *facoltativo*: non si stampa, compare solo nell'elenco.
- **Nella bozza**:
  - il dato mancante è evidenziato in giallo con un testo chiaro, per esempio
    "[Da compilare: nominativo RSPP]";
  - un commento di Word accanto dice in quale pagina del programma si compila;
  - prima dell'indice c'è la pagina "Dati da completare" con tutti i mancanti, divisi per livello,
    con capitolo e pagina del programma.
- **Nel programma**: l'elenco "Dati da completare" della bozza; con un doppio clic si va alla
  pagina in cui il dato si compila.
- **All'emissione**:
  - spariscono filigrana, riepilogo ed evidenziazioni;
  - i dati rimasti vuoti diventano righe da compilare a mano;
  - con dati obbligatori mancanti serve una conferma esplicita con il motivo, che resta registrata
    con la revisione.

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
  - **Motori**: Standard (DeepSeek, oggi su Scaleway in UE) per tutti; Avanzato (Claude) nel piano Studio, a 8 crediti per
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
1. **Server ponte AI**: da ottobre 2026 il motore Standard è DeepSeek V4.1 Flash su **Scaleway**
   (Parigi, dati trattati nell'UE). Il programma mostra ai clienti la sede comunicata dal server (riga
   SEDE di `ai.env`), quindi cambiando fornitore non serve una nuova versione. All'arrivo dei primi
   clienti si valuta se restare o passare a:
   - AI in locale (Ollama o vLLM su un server con GPU da circa 24 GB): i dati non escono dal server;
   - modello aperto su un server con GPU noleggiato in Europa;
   - DeepSeek V4 Pro presso un altro fornitore UE (più preciso di Flash), oppure Mistral.
   In tutti i casi basta cambiare indirizzo, modello, chiave e sede in `ai.env`, senza toccare il
   programma. Prima di passare, provare su uno o due PSC veri quante imprese e fasi trova e quanto
   tempo impiega rispetto a DeepSeek.
2. **Sito di vendita**: presentazione, prezzi, acquisto della licenza e download.
3. **SicurCantiere DVR.**
3. **SicurCantiere Formazione** (quarto programma della suite, idea approvata da sviluppare):
   - stesso archivio di aziende e lavoratori degli altri programmi;
   - struttura clienti → aziende → lavoratori → attestati;
   - corsi richiesti per ogni mansione, con chi è scoperto o in scadenza;
   - scadenzario con le scadenze già impostate per i corsi più comuni (lavoratori, preposto,
     antincendio, primo soccorso, attrezzature, ponteggi), da ricontrollare sul nuovo Accordo
     Stato-Regioni del 2025;
   - email di promemoria ai clienti con l'elenco di chi scade;
   - calendario dei corsi, registro presenze, test di verifica, attestati numerati;
   - lettura degli attestati in PDF con l'AI (corso, data, ore);
   - collegamento al POS: formazione dei lavoratori stampata in automatico e avviso se un corso è
     scaduto nelle date del cantiere.
3. **Documenti composti, prossimi passi**: allegati in PDF uniti in coda con la numerazione,
   esportazione in PDF, composizione salvata anche per il PiMUS.
3. **Strumenti del CSE durante i lavori**: verbali di sopralluogo e di riunione di coordinamento,
   verifica dei POS ricevuti (art. 92), verifica dell'idoneità tecnico-professionale (Allegato XVII),
   registro delle prescrizioni e delle sospensioni, avviso ai condomini o ai terzi.
4. **Idee per distinguersi**, da scegliere:
   - verifica automatica, punto per punto, che il POS risponda alle richieste del PSC letto (la
     lettura è già salvata nel file);
   - verifica dei POS ricevuti da parte del coordinatore (art. 92), con il verbale di verifica;
   - più documenti dagli stessi dati: nomine, richiesta della documentazione dell'Allegato XVII,
     verbali di coordinamento, informativa ai lavoratori;
   - scadenzario di tutti i cantieri (DURC, idoneità, formazione, verifiche) con le email di
     sollecito;
   - modelli di cantiere tipo che si arricchiscono con l'uso;
   - sopralluogo dal telefono con il verbale;
   - importazione dei vecchi documenti per chi arriva da altri programmi;
   - assistente AI che cita l'articolo di legge di ogni suggerimento.
