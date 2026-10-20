# Archivio delle lavorazioni: punti da verificare

L'archivio esteso (versione 0.10) conta 268 fasi di lavoro in 99 lavorazioni e 18 categorie, e
116 macchine, attrezzi e opere provvisionali con la loro scheda d'uso. I testi sono stati scritti
da zero, partendo dal D.Lgs. 81/2008 e da fonti tecniche pubbliche (INAIL, Regioni, PuntoSicuro,
testi di legge su Brocardi, TUSSL e Certifico, documenti dei fabbricanti), senza copiare schede di
altri.

Durante la redazione le ricerche in rete sono state interrotte più volte dal limite di utilizzo.
Molti riferimenti sono quindi stati scritti da conoscenze normative senza un riscontro puntuale
sul testo. In testa a ogni modulo di `sicurcantiere/archivio_dati/` un commento distingue le fonti
consultate da quelle citate a memoria. **Prima dell'uso professionale l'archivio va rivisto da un
coordinatore**, a partire da questi punti.

## Valori numerici (tutti i moduli)
- Probabilità e danno dei rischi e incidenza della manodopera sono stime: vanno tarate sui
  prezzari regionali e sull'esperienza.
- Valori indicativi da confrontare con i dati del fabbricante: livelli di rumore, pressioni del
  jet grouting (400-600 bar) e dell'idrodemolizione (oltre 1000 bar), raggio di interdizione del
  martello demolitore (10-15 m) e della idrodemolitrice (circa 10 m), limite di vento della PLE
  (12,5 m/s), temperatura dell'emulsione bituminosa (60-80 °C), tensioni di prova (500-1000 V).

## Demolizioni e bonifiche (`demolizioni.py`)
- Ordigni bellici: verificare che il parere vincolante dell'autorità militare sia nell'art. 91
  c. 2-bis; impresa iscritta all'albo del Ministero della Difesa (art. 104 c. 4-bis, D.M. 82/2015).
- Amianto:
  - incapsulante di tipo D per la rimozione e di tipo A per le superfici esterne a vista
    (D.M. 20/8/1999);
  - restituibilità a 2 fibre/litro in microscopia elettronica (D.M. 6/9/1994);
  - Albo gestori ambientali categoria 10A (compatto) e 10B (friabile);
  - codici EER 17 06 05* e 17 06 01*;
  - registro degli esposti (art. 243);
  - piano di lavoro 30 giorni prima (art. 256).
- Altri riferimenti da controllare:
  - gas refrigeranti: Reg. UE 2024/573 e D.P.R. 146/2018;
  - deposito temporaneo dei rifiuti: art. 185-bis del D.Lgs. 152/2006;
  - progetto di bonifica dei siti contaminati: art. 242 dello stesso decreto.
- DPI per l'amianto friabile: nell'elenco dei DPI manca una voce precisa ed è indicata come
  «maschera con filtro specifico (pieno facciale P3 o elettrorespiratore)».

## Strutture e murature (`strutture.py`)
- Prefabbricati: l'art. 146 riguarda la difesa delle aperture; le istruzioni scritte di montaggio
  sono citate dalla Circolare del Ministero del Lavoro 13/1982. Verificare se esistono riferimenti
  più aggiornati.
- Da controllare: art. 142 c. 2 (armature provvisorie), artt. 133-136 (ponteggi) in MU.06, fumi di
  saldatura e polveri di legno duro trattati come cancerogeni (Titolo IX).

## Coperture e facciate (`coperture.py`)
- Distanza impalcato-facciata non oltre 20 cm: verificare articolo e comma (citato art. 138).
- Ponteggio come protezione perimetrale in copertura: completare la quota di sporgenza con le
  indicazioni INAIL o regionali.
- Sabbiatura: abrasivi senza silice indicati come buona pratica, non come obbligo.
- Tipologie: CO.07 (capannoni con lastre fragili) è solo «Ristrutturazioni»; impermeabilizzazioni,
  linee vita, sigillature e lavori da PLE valgono per tutte le tipologie.

## Macchine (`macchine.py`)
- Abilitazione degli operatori (Accordo Stato-Regioni 22/02/2012): minipala trattata come pala
  caricatrice (con abilitazione); bulldozer, grader e dumper gommati senza abilitazione specifica,
  dumper cingolati con abilitazione.
- Verifiche periodiche dell'Allegato VII: da confermare la periodicità per sollevatori
  telescopici, montacarichi da cantiere e autocarri con cestello; escavatore usato per sollevare
  carichi oltre 200 kg indicato come soggetto a verifica.
- Motocompressore: verifiche del serbatoio secondo il D.M. 329/2004 solo oltre le soglie.
- Norme di prodotto da confermare: EN 16228-3 (TOC), EN 16228-4 (battipalo), EN 13019
  (spazzatrice), EN 13525 (cippatrice), EN 474-8 (grader).

## Attrezzature specialistiche (`aggiunte.py`)
- Norme di prodotto da confermare: UNI EN 16228-2 per i penetrometri, UNI EN 12001 (pompa per
  massetti), UNI EN 13020 (spanditrice), UNI EN 1829-1 (idrodemolitrice), UNI EN 14492-2
  (paranco elettrico).
- Treppiede di recupero: ammessi argano UNI EN 1496 o dispositivo retrattile UNI EN 360 con
  funzione di recupero.
- Lane minerali (insufflatrice): verificare le note Q/R con la classificazione CLP in vigore.
- Accessori di sollevamento: angolo massimo di 120° al vertice tra i bracci.
- Depressore per l'amianto friabile: verificare se il secondo estrattore di riserva o
  l'alimentazione di emergenza è obbligatorio per il D.M. 6/9/1994.
- Distanze dalle linee elettriche (Allegato IX): verificare la tabella per le tensioni superiori
  a 1 kV dove è citata in forma breve.
