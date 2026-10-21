# Prompt per Claude Design: SicurCantiere

> Copia tutto il testo qui sotto in Claude Design. Completa la sezione finale
> «Le mie preferenze di design» prima di inviarlo.

---

Progetta l'interfaccia di **SicurCantiere**, un programma desktop per Windows che serve a redigere i documenti di sicurezza dei cantieri edili italiani previsti dal D.Lgs. 81/2008. Il programma esiste già e funziona: ti chiedo un nuovo design delle schermate, non nuove funzioni. Qui sotto trovi come funziona oggi, schermata per schermata.

## Chi lo usa

- Coordinatori per la sicurezza (CSP/CSE), RSPP e consulenti, spesso geometri o ingegneri, che redigono POS e PSC per più imprese.
- Titolari e impiegati di piccole imprese edili (in media 3 addetti) che preparano il proprio POS.
- Persone abituate a Word ed Excel, non a software complessi: lavorano in ufficio su un PC Windows con schermo da 14 a 24 pollici, a volte con dati su una cartella di rete. Scrivono molto testo (misure di prevenzione, descrizioni delle lavorazioni) e compilano tante tabelle.

## La famiglia di programmi

Tre programmi con la stessa interfaccia e lo stesso motore; ognuno ha il suo colore, la sua icona e la sua estensione di file:

| Programma | A cosa serve | Colore | File |
| --- | --- | --- | --- |
| SicurCantiere POS | Piano operativo di sicurezza dell'impresa esecutrice | blu #2E86C1 | .spo |
| SicurCantiere PSC | Piano di sicurezza e coordinamento del coordinatore | arancio #E8792B | .scs |
| SicurCantiere PiMUS | Piano di montaggio dei ponteggi | verde acqua #2E9C8F | .spm |

Il POS è il programma più usato: progetta prima quello, gli altri ne seguono lo schema.

## Come funziona

- Un file = un cantiere. I dati si salvano da soli a ogni modifica; c'è anche un pulsante Salva (Ctrl+S) che conferma il campo in modifica. All'apertura il programma fa una copia di sicurezza in una cartella dedicata.
- Si compilano le pagine dall'alto in basso nella barra laterale; alla fine si genera il documento in Word (.docx), che l'utente rilegge e firma.
- Un archivio interno fornisce lavorazioni già pronte (268 fasi di lavoro in 18 categorie, 116 macchine e attrezzature, ognuna con rischi, misure di prevenzione e DPI).
- Il programma controlla continuamente i dati (errori e avvisi) e crea da solo le valutazioni dei rischi specifici necessarie (rumore, vibrazioni, movimentazione manuale dei carichi, movimenti ripetitivi) in base ai rischi delle lavorazioni.
- Un assistente AI facoltativo suggerisce rischi, macchine e attrezzature e scrive bozze di testi: l'utente sceglie sempre da un elenco a spunta cosa accettare.

## Struttura della finestra

- **Barra dei menu**: File (Nuovo cantiere, Apri, Salva, Salva con nome, File recenti, Chiudi cantiere, Esci), Strumenti (Genera POS, Controlli, Archivio anagrafiche, Impostazioni assistente AI), Visualizza (tema chiaro/scuro), Aiuto (Informazioni).
- **Barra degli strumenti** con icone: Nuovo, Apri, Salva, Salva con nome, il pulsante principale «Genera POS» (Ctrl+P), Controlli (F7).
- **Barra laterale** di navigazione a sinistra con icona e nome di ogni pagina; disattivata finché non c'è un cantiere aperto.
- **Area centrale** con la pagina scelta: titolo grande in alto, poi il contenuto.
- **Barra di stato** in basso: percorso del file aperto, «Salvato alle hh:mm:ss», e un indicatore cliccabile con il numero di errori e avvisi (rosso se ci sono errori) che porta alla pagina dei controlli.
- Tema chiaro e tema scuro.

## Pagina iniziale (nessun cantiere aperto)

Logo e nome del programma, sottotitolo, due pulsanti grandi «Nuovo cantiere...» (in evidenza) e «Apri cantiere...», sotto una griglia di schede dei **cantieri recenti** (nome del cantiere, comune, nome del file); un clic apre il cantiere.

## Pagine del programma POS

### 1. Cantiere

- In alto un **riepilogo a riquadri** (tessere) con i numeri chiave: imprese, lavoratori, periodo dei lavori, lavorazioni e rischi valutati, rischi alti e molto alti, valutazioni specifiche, stato dei controlli.
- Modulo con i dati del cantiere: denominazione dell'opera, natura dell'opera, indirizzo, CAP, comune, provincia, titolo abilitativo, importo dei lavori, descrizione sintetica (testo lungo).
- Riquadro **Foto del cantiere**: miniature in fila, pulsanti «Aggiungi foto...» e «Rimuovi».

### 2. Committente e CSE

- Spunta «Il committente è anche responsabile dei lavori».
- Tabella dei soggetti: ruolo (committente, responsabile dei lavori, CSP, CSE, direttore dei lavori...), nominativo, nella persona di, qualifica, codice fiscale, P. IVA, indirizzo, telefono, email.
- Pulsanti per prendere un soggetto dall'archivio anagrafiche personale o salvarlo nell'archivio.

### 3. Impresa e lavoratori

- In alto la tabella delle imprese (ragione sociale, tipologia: affidataria, esecutrice, subappaltatrice, lavoratore autonomo; P. IVA, referente, telefono), con «Dall'archivio...» e «Salva in archivio».
- Sotto, per l'impresa selezionata, cinque schede:
  - **Dati dell'impresa**: modulo lungo diviso in sezioni (anagrafica e logo; dati dei lavori con date e autorizzazione al subappalto; incaricato art. 97; sede legale e recapiti; posizioni INAIL, INPS, cassa edile, CCNL, DURC; qualificazione: DVR, SOA, certificazioni).
  - **Figure della sicurezza**: datore di lavoro e un elenco di figure scelte da un menu (dirigente, direttore tecnico, capocantiere, preposto, RSPP con spunta «coincide con il datore di lavoro», ASPP, medico competente, RLS o RLST, addetti al primo soccorso, all'antincendio e alle emergenze), ciascuna con i propri compiti.
  - **Maestranze**: tabella dei lavoratori (cognome, nome, mansione, matricola, date, idoneità sanitaria), con scheda di dettaglio: foto, DPI consegnati (scelti da un catalogo con spunte), formazione (caselle per i corsi), e **mansioni**: un albero delle fasi di lavoro con le macchine e attrezzature, in cui si spunta cosa usa il lavoratore.
  - **Lavoratori autonomi**: come sopra, con P. IVA.
  - **Testi del POS**: sezioni di testo libero del documento, ognuna con il pulsante per farla scrivere all'assistente AI.

### 4. Lavorazioni e rischi

La pagina più usata e più densa.

- In alto la tabella delle fasi: codice, lavorazione (gruppo di fasi, per esempio «Strutture in elevazione in c.a.»), fase di lavoro (l'attività concreta), impresa. Pulsanti: Aggiungi, Elimina, **Importa da archivio...** (in evidenza), Salva nell'archivio utente.
- Sotto, per la fase selezionata, quattro schede:
  - **Descrizione e organizzazione**: descrizione dell'attività, addetto, modalità organizzative, turni, procedure richieste dal PSC.
  - **Struttura**: albero che mostra la fase con i lavoratori e gli attrezzi che usano, le macchine con il loro operatore, e i rischi di ciascuno.
  - **Rischi e misure**: tabella con rischio, origine (la macchina da cui deriva), probabilità P e danno D da 1 a 4, livello calcolato (P x D, da basso a molto alto, da mostrare a colori), misure di prevenzione, DPI, valutazione specifica collegata, spunta **Non presente** e motivazione. Pulsante «Suggerisci rischi con l'AI».
  - **Macchine, attrezzi e opere provvisionali**: tabella con tipo, nome, descrizione, misure prima, durante e dopo l'uso, DPI dell'operatore. Un menu a tendina con l'archivio e «Aggiungi con i suoi rischi», più «Suggerisci con l'AI» e «Completa rischi e scheda con l'AI».
- **Importa da archivio** apre una finestra con un albero a tre livelli (categoria, lavorazione, fase) filtrabile per tipologia d'intervento (nuove costruzioni, ristrutturazioni, opere infrastrutturali, restauri) e per testo; si spuntano più fasi; c'è un nodo UTENTE con le lavorazioni salvate dall'utente.

### 5. Valutazioni specifiche

- Una frase spiega che le valutazioni necessarie vengono create in automatico dai rischi delle lavorazioni; un avviso elenca quelle appena create.
- Tabella delle valutazioni: titolo, metodo (NIOSH, traino e spinta, trasporto, OCRA, rumore, vibrazioni), mansione o gruppo omogeneo, lavorazioni collegate, risultato («Da eseguire» finché non si inseriscono i parametri). Pulsante «Lavorazioni...» per scegliere le fasi con un elenco a spunta.
- Sotto, divisa in due colonne: a sinistra la descrizione dell'attività con «Compila con l'assistente AI», i parametri del metodo (campi numerici e scelte; per alcuni metodi una tabella di compiti) e le note; a destra il **risultato**: indice grande, classe di rischio a colori (verde, giallo, rosso, viola), dettagli del calcolo, misure consigliate, e «Genera relazione (.docx)».

### 6. Sostanze pericolose

- Tabella dei prodotti: nome, impresa, lavorazioni in cui si usa, frasi H, avvertenza, data della scheda di sicurezza, pittogrammi.
- Pulsanti: «Importa da scheda di sicurezza (PDF)...», «Apri la scheda», «Lavorazioni...».
- Sotto due schede: classificazione e misure (le frasi H spiegate e le categorie di pericolo a colori) e dati del prodotto.

### 7. POS e controlli

- Scelta dell'impresa e griglia di pulsanti per generare i documenti: POS, elenco delle sostanze, verbali di consegna DPI, tesserini di riconoscimento, schede dei lavoratori.
- Tabella delle revisioni del documento.
- Elenco dei **controlli**: errori in rosso e avvisi in arancio, ognuno con la sezione e il messaggio (per esempio «DURC scaduto», «rischio senza misure», «valutazione da eseguire»). Prima di generare, se ci sono errori il programma chiede conferma.

## Finestre secondarie

- Archivio anagrafiche (persone e imprese salvate per riusarle in altri cantieri).
- Impostazioni assistente AI (fornitore e chiave).
- Elenchi a spunta delle proposte dell'assistente AI.
- Scelta dei DPI da catalogo, scelta delle lavorazioni, messaggi di conferma.

## Vincoli tecnici

- Il programma è scritto in Python con **Qt (PySide6)**: il design deve essere realizzabile con widget Qt e fogli di stile Qt (QSS). Niente effetti solo web (sfumature animate complesse, trasparenze sul desktop, layout HTML).
- Deve restare leggibile con molte tabelle e testi lunghi: la densità di informazioni è alta e va gestita, non nascosta.
- Tema chiaro e scuro per ogni schermata; contrasto adeguato per lavorare molte ore.
- Finestra ridimensionabile da 1280x720 in su; le tabelle si allargano con la finestra.
- L'interfaccia è solo in italiano.

## Cosa ti chiedo di consegnare

1. Un sistema di design: colori (con le varianti per i tre programmi e per il tema scuro), caratteri, dimensioni, spaziature, stili di pulsanti, campi, tabelle, schede, tessere del riepilogo, badge dei livelli di rischio.
2. Le schermate del programma POS: pagina iniziale, Cantiere, Impresa e lavoratori (scheda Maestranze), Lavorazioni e rischi (scheda Rischi e misure), Valutazioni specifiche, POS e controlli, e la finestra Importa da archivio.
3. Gli stati principali: nessun cantiere aperto, tabella vuota, campo con errore, controlli con errori, attesa dell'assistente AI.
4. Indicazioni per tradurre il design in QSS e widget Qt.

## Le mie preferenze di design

<!-- Scrivi qui come vuoi il design: stile (sobrio, moderno, istituzionale...), colori,
     programmi o siti che ti piacciono come riferimento, cosa non ti piace di come è oggi,
     cosa deve risaltare di più. -->
