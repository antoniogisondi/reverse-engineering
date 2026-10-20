"""Fasi di lavoro: allestimento e smobilizzo del cantiere; tagli, carotaggi e perforazioni.

Testi redatti da zero per questo progetto. Fonti consultate per verificare contenuti e riferimenti
(non copiate): D.Lgs. 81/2008 (Titolo IV capi I e II, artt. 71, 73, 80-87, 96, 108-138, 150-151;
Allegati IV, VI, VII, XIII, XV, XVIII, XIX, XXI, XXII, XXIV-XXXII, XLII, XLIII); D.Lgs. 44/2020
(silice cristallina respirabile); D.P.R. 462/2001; D.M. 37/2008; D.M. 10/07/2002 e D.M. 22/01/2019
(segnaletica temporanea e formazione per lavori in presenza di traffico); norme CEI 64-8/7 sez. 704,
guida CEI 64-17, CEI EN 61439-4, CEI EN 60309, CEI EN 62305, CEI 11-27; UNI EN 12811-1, UNI EN 13374,
UNI EN 1263-1/2, UNI EN 795, UNI EN 363, UNI EN 12158-1, UNI EN 14439, UNI ISO 12480-1,
UNI EN 12504-1; NTC 2018 cap. 8 (interventi locali su costruzioni esistenti); materiali divulgativi
INAIL e PuntoSicuro (infortuni nello smontaggio dei ponteggi, tagliatrici a filo diamantato,
troncatrici a disco), linee guida della Regione Emilia-Romagna (impianti elettrici di cantiere,
buone pratiche in edilizia), opuscoli AUSL/ANCE sulla silice cristallina in edilizia.
I contenuti vanno sempre verificati e adattati dal coordinatore al cantiere specifico.
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import DPI_BASE, EDILIZIA, TUTTE, fase, r

_AL = "Allestimento e smobilizzo del cantiere"
_TP = "Tagli, carotaggi e perforazioni"

# Attrezzature non presenti nel CATALOGO di base.py: nome -> (tipo, motivo).
MANCANTI = {
    "Sega murale su binario": (
        "Attrezzo",
        "Sega a disco diamantato montata su binario fissato alla parete, a motore elettrico o idraulico: "
        "è l'attrezzatura tipica per tagliare pareti e solette in c.a. di grosso spessore con tagli "
        "rettilinei e profondi, non sostituibile con la sega a disco manuale né con il filo diamantato.",
    ),
}

# --- DPI ricorrenti ---
_DPI_ANTICADUTA = DPI_BASE + ", casco con sottogola, imbracatura, cordino con assorbitore"
_DPI_POLVERI = DPI_BASE + ", facciale filtrante FFP3, occhiali a maschera"
_DPI_FANGHI = DPI_BASE + ", stivali di sicurezza, indumenti impermeabili, occhiali a maschera"

# --- Rischi riusati: allestimento ---
_MMC = r("Movimentazione manuale dei carichi", 3, 2,
         "Carichi oltre i 25 kg (uomini) e 20 kg (donne) movimentati in due o con mezzi di sollevamento; "
         "elementi pesanti (pannelli, basette, tubi, chiusini) depositati vicino al punto di posa; "
         "valutazione secondo il Titolo VI e l'Allegato XXXIII del D.Lgs. 81/2008; formazione sulle "
         "corrette posture di sollevamento.")
_CARICHI_SOSPESI = r("Caduta di materiale dall'alto o a livello", 2, 4,
                     "Imbracature con brache e ganci di portata adeguata, con dispositivo di sicurezza e "
                     "marcatura leggibile; imbracatore formato che segue il carico e comunica con il "
                     "manovratore con i gesti convenzionali dell'Allegato XXXII; nessuno sotto il carico "
                     "sospeso; guida del carico con funi e non con le mani (Allegato VI punto 3.1).",
                     DPI_BASE + ", casco con sottogola")
_SCHIACCIAMENTO_POSA = r("Urti, colpi, impatti e compressioni", 2, 3,
                         "Avvicinarsi all'elemento solo quando è fermo a pochi centimetri dal piano di "
                         "posa; mani lontane dai punti di appoggio e dagli spigoli; sganciare solo dopo "
                         "averne verificato la stabilità e il fissaggio.")
_INVESTIMENTO = r("Investimento da mezzi in manovra", 2, 4,
                  "Percorsi pedonali separati da quelli dei mezzi; manovre in retromarcia assistite da un "
                  "moviere; addetti a terra fuori dal raggio d'azione delle macchine e visibili "
                  "all'operatore; velocità ridotta nelle aree di cantiere.")
_CADUTA_ALTO_MONTAGGIO = r("Caduta dall'alto", 3, 4,
                           "Lavoro in quota con imbracatura collegata a punti di ancoraggio idonei o a "
                           "linea di ancoraggio (UNI EN 795, UNI EN 363) in ogni fase non protetta da "
                           "parapetti; mai sganciarsi durante gli spostamenti (doppio cordino); "
                           "piano di recupero di un lavoratore sospeso; formazione e addestramento sui "
                           "DPI di terza categoria (art. 77 c. 5).", _DPI_ANTICADUTA)
_VENTO = r("Microclima: vento, pioggia e temperature estreme", 2, 3,
           "Sospendere i lavori in quota e i sollevamenti con vento oltre i limiti indicati dal "
           "fabbricante o dal piano di montaggio, con pioggia, ghiaccio o scarsa visibilità; "
           "anemometro consultabile; indumenti adatti alla stagione; acqua e pause all'ombra nei mesi "
           "caldi.", DPI_BASE + ", indumenti impermeabili, indumenti per il freddo")
_ELETTRO_LINEE = r("Elettrocuzione per vicinanza a linee elettriche aeree", 1, 4,
                   "Individuare in anticipo le linee aeree e mantenere da parti attive e conduttori le "
                   "distanze della tabella 1 dell'Allegato IX, considerando gli ingombri di carichi, "
                   "bracci e funi; se non è possibile, chiedere all'ente gestore la messa fuori tensione "
                   "o la protezione delle linee (artt. 83 e 117).")
_SOTTOSERVIZI = r("Contatto con sottoservizi interrati", 2, 4,
                  "Prima di scavare o infiggere picchetti acquisire dagli enti gestori le planimetrie "
                  "delle reti, tracciarle sul terreno e procedere a mano in prossimità di cavi e "
                  "condotte del gas; sospendere e avvisare il gestore in caso di danneggiamento.")
_SCIVOLAMENTI = r("Scivolamenti e cadute a livello", 2, 2,
                  "Percorsi e aree di lavoro sgombri da materiali, cavi e ritagli; buche e scavi "
                  "segnalati o coperti; calzature con suola antiscivolo; illuminazione sufficiente "
                  "nelle ore serali.")
_PUNTURE = r("Punture, tagli e abrasioni", 3, 2,
             "Guanti adatti al materiale maneggiato (lamiere, reti, tubi tagliati); bordi e spigoli vivi "
             "protetti o rifiniti; attrezzi manuali integri e riposti dopo l'uso.",
             DPI_BASE + ", guanti antitaglio")

# --- Rischi riusati: tagli, carotaggi, perforazioni ---
_SILICE = r("Polveri e fibre (silice cristallina respirabile)", 3, 3,
            "Taglio e foratura a umido con alimentazione d'acqua continua o, a secco, con aspirazione "
            "alla fonte tramite aspiratore di classe H; il taglio di laterizi, pietre e calcestruzzo è "
            "lavoro che espone a cancerogeno (Allegato XLII, Titolo IX Capo II; VLEP dell'Allegato "
            "XLIII): valutazione dell'esposizione, zona di lavoro delimitata, pulizia ad aspirazione e "
            "non con scopa o aria compressa, sorveglianza sanitaria.", _DPI_POLVERI)
_IMPIANTI_NASCOSTI = r("Elettrocuzione per contatto con impianti annegati nelle strutture", 2, 4,
                       "Prima di forare o tagliare consultare gli schemi degli impianti esistenti e "
                       "ricercare cavi e tubazioni con rilevatore; mettere fuori tensione e sezionare i "
                       "circuiti della zona interessata, con cartello di divieto di manovra; intercettare "
                       "le tubazioni di gas e acqua che attraversano l'area di lavoro.",
                       DPI_BASE + ", occhiali protettivi")
_FANGHI = r("Getti e schizzi di acqua e fanghi di taglio", 3, 2,
            "Raccogliere i fanghi con teli, vasche o aspiraliquidi e impedirne il deflusso verso "
            "quadri, prese e locali sottostanti; i fanghi cementizi sono alcalini e irritanti per cute "
            "e occhi: evitare il contatto, lavare subito le parti colpite; smaltire i fanghi come "
            "rifiuto (D.Lgs. 152/2006).", _DPI_FANGHI)
_SCHEGGE = r("Proiezione di schegge e frammenti", 3, 2,
             "Area di lavoro delimitata e interdetta a terzi anche sul lato opposto della struttura "
             "forata o tagliata; schermi o teli di protezione verso le zone frequentate; occhiali o "
             "visiera sempre indossati da chi lavora e da chi assiste.",
             DPI_BASE + ", occhiali a maschera, visiera protettiva")
_CROLLO = r("Crollo o ribaltamento di strutture", 2, 4,
            "Tagli, aperture e demolizioni su strutture portanti eseguiti solo secondo il progetto e la "
            "sequenza indicati dal tecnico strutturista, previa verifica delle condizioni di stabilità "
            "e rafforzamento preventivo delle parti che possono cedere (art. 150); puntellazioni messe "
            "in carico prima di iniziare; sospendere in presenza di lesioni o deformazioni impreviste.")
_CADUTA_BLOCCO = r("Caduta del blocco tagliato", 2, 4,
                   "Prima dell'ultimo taglio il blocco è imbracato al mezzo di sollevamento o "
                   "sostenuto da puntelli, cunei o mensole, in modo che non possa cadere o ruotare; "
                   "nessuno sotto o davanti al blocco durante il distacco; sotto le solette area "
                   "sottostante interdetta e protetta.")
_POSTURE = r("Posture incongrue", 3, 2,
             "Lavorare a un'altezza comoda usando ponti su cavalletti o trabattelli invece di sporgersi "
             "o lavorare sopra la testa; alternare le mansioni e fare pause brevi e frequenti; "
             "ginocchiere per i lavori a pavimento.", DPI_BASE + ", ginocchiere")
_CADUTA_QUOTA_TP = r("Caduta dall'alto", 2, 4,
                     "Lavori oltre i 2 m da trabattello, ponte su cavalletti o ponteggio con parapetti, "
                     "non da scala; in prossimità di aperture e bordi creati dal taglio, parapetti o "
                     "coperture prima di lasciare il vano libero (art. 146); imbracatura se le "
                     "protezioni collettive non sono possibili.", _DPI_ANTICADUTA)


LAVORAZIONI = [
    # ------------------------------------------------------------------ Apprestamenti del cantiere
    fase("AL.20", _AL, "Apprestamenti del cantiere",
         "Installazione di baraccamenti e servizi igienico-assistenziali",
         "Posa con autocarro con gru o autogru di monoblocchi prefabbricati per uffici, spogliatoi, "
         "refettorio, locali di riposo, servizi igienici e docce, su basamento livellato e portante. "
         "Segue l'unione dei moduli, il collegamento alle reti elettrica, idrica e di scarico e la posa "
         "dei gradini di accesso. Dotazioni e dimensioni secondo l'Allegato XIII del D.Lgs. 81/2008 e il "
         "numero massimo di addetti presenti.",
         "Addetto all'installazione di baraccamenti e servizi igienico-assistenziali", 30, TUTTE,
         ["Autocarro con gru", "Autogru", "Avvitatore elettrico", "Utensili manuali", "Scala a mano"], [
             _CARICHI_SOSPESI, _SCHIACCIAMENTO_POSA, _ELETTRO_LINEE,
             r("Ribaltamento o cedimento del monoblocco", 1, 3,
               "Basamento in cls o su travi livellate e verificato per il carico; moduli sovrapposti "
               "solo se previsto dal fabbricante e collegati con i suoi accessori; ancoraggi "
               "antivento dove richiesto; scale e ballatoi di accesso con parapetto."),
             r("Caduta dall'alto", 2, 3,
               "Agganci e sganci sul tetto dei moduli da scala a mano vincolata o con sistemi di "
               "aggancio a terra (bilancini con funi di sgancio); mai camminare sulla copertura dei "
               "box se non previsto dal fabbricante."),
             _MMC,
         ]),
    fase("AL.21", _AL, "Apprestamenti del cantiere",
         "Allestimento di depositi, zone di stoccaggio e aree per i rifiuti",
         "Individuazione e preparazione delle aree per il deposito dei materiali, delle attrezzature, "
         "delle bombole e delle sostanze pericolose e per il deposito temporaneo dei rifiuti, come "
         "previsto dal layout di cantiere (Allegato XV punto 2.2.2). Comprende la stesa di misto o "
         "piattaforme, la posa di rastrelliere, scaffalature, cassoni e contenitori con bacino di "
         "contenimento, tettoie e la relativa segnaletica.",
         "Addetto all'allestimento di depositi e zone di stoccaggio", 50, TUTTE,
         ["Autocarro con gru", "Carrello elevatore", "Avvitatore elettrico", "Utensili manuali"], [
             _MMC, _INVESTIMENTO, _CARICHI_SOSPESI,
             r("Crollo o ribaltamento di strutture", 2, 3,
               "Cataste stabili e di altezza limitata, su piani orizzontali e portanti, con elementi "
               "bloccati da cunei o montanti; scaffalature ancorate e con portata indicata; materiali "
               "lunghi su rastrelliere; depositi lontani dai cigli degli scavi."),
             r("Incendio ed esplosione", 1, 4,
               "Bombole in deposito separato, ventilato e protetto dal sole, in posizione verticale e "
               "legate, con cappellotto; infiammabili lontani da fonti di calore e dalle aree di "
               "saldatura; estintori segnalati vicino ai depositi; divieto di fumo e di fiamme libere."),
             _PUNTURE,
         ]),

    # ------------------------------------------------------------------ Impianti di servizio
    fase("AL.22", _AL, "Impianti di servizio del cantiere",
         "Realizzazione dell'impianto elettrico di cantiere",
         "Installazione, a partire dal punto di consegna o dal gruppo elettrogeno, del quadro generale e "
         "dei quadri di distribuzione per cantiere (ASC, CEI EN 61439-4) e posa delle linee di "
         "alimentazione verso baraccamenti, macchine e prese, interrate o aeree e protette dal "
         "danneggiamento. Impianto eseguito da impresa abilitata secondo CEI 64-8/7 sez. 704, con "
         "dichiarazione di conformità (D.M. 37/2008) prima della messa in servizio.",
         "Addetto alla realizzazione dell'impianto elettrico di cantiere", 55, TUTTE,
         ["Trapano elettrico", "Martello perforatore (tassellatore)", "Miniescavatore", "Utensili manuali",
          "Scala doppia"], [
             r("Elettrocuzione", 2, 4,
               "Lavori eseguiti fuori tensione da persone esperte o avvertite (PES/PAV, CEI 11-27) "
               "nominate dal datore di lavoro; sezionamento a monte, blocco e cartello di lavori in "
               "corso, verifica di assenza di tensione prima di toccare le parti; vietati i lavori "
               "sotto tensione oltre i limiti dell'art. 82; collaudo con prove strumentali di "
               "continuità, isolamento e intervento dei differenziali prima dell'alimentazione.",
               DPI_BASE + ", guanti dielettrici, occhiali protettivi"),
             r("Danneggiamento delle linee da parte di mezzi e lavorazioni", 2, 3,
               "Cavi per posa mobile adatti all'uso gravoso (tipo H07RN-F o equivalente); linee "
               "interrate in tubo protettivo con nastro segnalatore oppure aeree ad altezza adeguata "
               "sopra le vie di transito; prese e spine industriali CEI EN 60309 con grado di "
               "protezione adatto al cantiere; quadri chiusi a chiave."),
             _SOTTOSERVIZI, _SCIVOLAMENTI,
             r("Caduta dall'alto", 2, 3,
               "Posa di linee aeree e di quadri su pali da scala doppia stabile o da piattaforma "
               "elevabile, non salendo sui pali o sulle strutture; scale con piedini antiscivolo."),
         ]),
    fase("AL.23", _AL, "Impianti di servizio del cantiere",
         "Realizzazione dell'impianto di terra e di protezione contro le scariche atmosferiche",
         "Posa dei dispersori a picchetto o a corda nuda, dei pozzetti ispezionabili e dei conduttori di "
         "terra e di protezione, con collegamento dei quadri, delle masse e delle masse estranee "
         "(ponteggi, gru, silos, baracche metalliche). La necessità della protezione dai fulmini delle "
         "grandi strutture metalliche è valutata con CEI EN 62305-2. L'installatore rilascia la "
         "dichiarazione di conformità, che va inviata a INAIL e ASL/ARPA entro 30 giorni dalla messa in "
         "esercizio; seguono le verifiche periodiche del D.P.R. 462/2001.",
         "Addetto alla realizzazione dell'impianto di terra e di protezione dalle scariche atmosferiche",
         50, TUTTE,
         ["Miniescavatore", "Martello demolitore", "Utensili manuali"], [
             _SOTTOSERVIZI, _MMC,
             r("Urti, colpi, impatti e compressioni", 2, 2,
               "Infissione dei picchetti con battipicchetto o martello con apposito cuffia; il "
               "picchetto è tenuto con un attrezzo di guida e non con le mani; mazze integre e "
               "con manico ben fissato."),
             r("Elettrocuzione", 1, 4,
               "Collegamenti alla rete di terra di masse già alimentate eseguiti solo con impianto "
               "sezionato; misura della resistenza di terra e coordinamento con i differenziali prima "
               "della messa in servizio; lavori sospesi durante i temporali.",
               DPI_BASE + ", guanti dielettrici"),
             r("Seppellimento e sprofondamento", 1, 3,
               "Trincee per la corda di terra poco profonde e con pareti inclinate o sostenute; materiale "
               "di scavo depositato lontano dal ciglio; nessuno nello scavo durante il lavoro della "
               "macchina."),
         ]),
    fase("AL.24", _AL, "Impianti di servizio del cantiere",
         "Realizzazione degli impianti idrico e fognario di cantiere",
         "Allaccio alla rete idrica pubblica o a serbatoio di accumulo, con posa delle tubazioni di "
         "adduzione in polietilene verso servizi, docce, betoniera e punti di lavaggio. Raccolta degli "
         "scarichi dei servizi igienici e convogliamento alla fognatura esistente o a vasca a tenuta "
         "periodicamente svuotata con autospurgo, come autorizzato dal gestore.",
         "Addetto alla realizzazione degli impianti idrico e fognario di cantiere", 40, TUTTE,
         ["Miniescavatore", "Saldatrice per polietilene", "Autocarro con gru", "Autospurgo",
          "Utensili manuali"], [
             _SOTTOSERVIZI,
             r("Seppellimento e sprofondamento", 2, 4,
               "Scavi oltre 1,50 m con pareti armate o con inclinazione adeguata al terreno (art. 119); "
               "materiali e mezzi lontani dal ciglio; scala per uscire rapidamente dallo scavo."),
             r("Rischio biologico", 2, 3,
               "Allacci a condotte fognarie esistenti con guanti impermeabili e indumenti protettivi; "
               "lavaggio delle mani prima di mangiare; vaccinazione antitetanica; mai entrare in "
               "pozzetti o camerette senza la procedura per ambienti confinati (D.P.R. 177/2011).",
               DPI_BASE + ", guanti in lattice o nitrile, stivali di sicurezza"),
             r("Ambienti confinati o sospetti di inquinamento", 1, 4,
               "Lavori dall'esterno dei pozzetti ogni volta che è possibile; se è necessario entrare, "
               "solo personale qualificato ai sensi del D.P.R. 177/2011, misura dell'atmosfera con "
               "rilevatore multigas, ventilazione e sorvegliante esterno con mezzi di recupero.",
               DPI_BASE + ", imbracatura, autorespiratore"),
             _MMC, _INVESTIMENTO,
         ]),

    # ------------------------------------------------------------------ Macchine e impianti fissi
    fase("AL.25", _AL, "Installazione e smontaggio di macchine e impianti fissi",
         "Montaggio della gru a torre",
         "Montaggio della gru a torre su basamento o fondazione verificati, eseguito da squadra "
         "specializzata secondo le istruzioni del fabbricante, con autogru per il sollevamento di "
         "traliccio, torre, braccio, controbraccio e zavorre. Comprende il collegamento all'impianto di "
         "terra, la taratura dei limitatori di carico e di momento e le prove di funzionamento. Prima "
         "dell'uso: comunicazione di messa in servizio e prima verifica INAIL (art. 71 c. 11, Allegato "
         "VII).",
         "Addetto al montaggio della gru a torre", 45, ("Nuove costruzioni", "Ristrutturazioni",
                                                        "Opere infrastrutturali"),
         ["Autogru", "Autocarro", "Utensili manuali"], [
             _CADUTA_ALTO_MONTAGGIO, _CARICHI_SOSPESI,
             r("Crollo o ribaltamento di strutture", 1, 4,
               "Fondazione progettata sulle reazioni fornite dal fabbricante e sulla portanza del "
               "terreno; zavorre nel numero e nella posizione indicati; perni e bulloni serrati con le "
               "coppie prescritte; mai lasciare la gru parzialmente montata senza le condizioni di "
               "stabilità previste; distanze dagli scavi e interferenze con altre gru valutate."),
             _VENTO, _ELETTRO_LINEE,
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "Accoppiamento di conci e perni guidando gli elementi con funi; mani mai negli "
               "accoppiamenti durante l'avvicinamento; zona di montaggio recintata e interdetta ai non "
               "addetti; comunicazione via radio con il gruista dell'autogru.",
               DPI_BASE + ", casco con sottogola"),
         ]),
    fase("AL.26", _AL, "Installazione e smontaggio di macchine e impianti fissi",
         "Smontaggio della gru a torre",
         "Smontaggio a fine lavori, con la sequenza inversa al montaggio indicata dal fabbricante: "
         "messa a riposo, scollegamento elettrico, rimozione delle zavorre del controbraccio, calo di "
         "braccio, controbraccio e conci della torre con autogru e carico su autocarro. Lo spazio "
         "per l'autogru e le traiettorie dei carichi vanno verificati in anticipo, perché a fine "
         "lavori l'edificio costruito riduce l'area disponibile.",
         "Addetto allo smontaggio della gru a torre", 45, ("Nuove costruzioni", "Ristrutturazioni",
                                                           "Opere infrastrutturali"),
         ["Autogru", "Autocarro", "Utensili manuali"], [
             _CADUTA_ALTO_MONTAGGIO, _CARICHI_SOSPESI,
             r("Crollo o ribaltamento di strutture", 1, 4,
               "Rispettare l'ordine di rimozione di zavorre e braccio per non sbilanciare la torre; "
               "sfilare i perni solo con l'elemento già imbracato e in tiro; controllo dei perni "
               "grippati senza colpi violenti dall'alto."),
             _VENTO,
             r("Urti contro l'edificio costruito durante il calo", 2, 3,
               "Traiettorie di calo studiate in anticipo; carichi guidati con funi da terra; "
               "sgombero dei solai e dei balconi vicini; segnalatore in vista del gruista."),
         ]),
    fase("AL.27", _AL, "Installazione e smontaggio di macchine e impianti fissi",
         "Installazione e smontaggio di betoniera e impianto di betonaggio con silo",
         "Posa della betoniera a bicchiere o dell'impianto di betonaggio con silo per cemento o premiscelati, "
         "su platea o piastre di ripartizione, con ancoraggio alla fondazione e controventatura del silo "
         "secondo il fabbricante. Comprende i collegamenti elettrici e idrici, la tettoia di protezione "
         "del posto di manovra se nel raggio della gru (art. 114) e lo smontaggio a fine lavori.",
         "Addetto all'installazione e smontaggio dell'impianto di betonaggio", 35,
         ("Nuove costruzioni", "Ristrutturazioni", "Opere infrastrutturali"),
         ["Autogru", "Autocarro con gru", "Trapano elettrico", "Utensili manuali", "Scala a mano"], [
             _CARICHI_SOSPESI,
             r("Ribaltamento del silo", 1, 4,
               "Fondazione dimensionata per peso pieno e azione del vento; tirafondi e piedi fissati "
               "prima di sganciare il silo dall'autogru; verticalità verificata; nessun riempimento "
               "prima del completamento degli ancoraggi."),
             r("Caduta dall'alto", 2, 4,
               "Accesso alla sommità del silo solo dalla scala fissa con gabbia o con anticaduta "
               "retrattile; collegamenti del filtro e del tubo di carico eseguiti, se possibile, prima "
               "del sollevamento; piattaforma elevabile per i lavori in quota.",
               _DPI_ANTICADUTA),
             r("Ambienti confinati o sospetti di inquinamento", 1, 4,
               "Vietato entrare nel silo per pulizie o sblocchi senza procedura del D.P.R. 177/2011, "
               "macchina sezionata e bloccata, verifica dell'atmosfera e sorvegliante esterno."),
             _SCHIACCIAMENTO_POSA, _ELETTRO_LINEE,
         ]),
    fase("AL.28", _AL, "Installazione e smontaggio di macchine e impianti fissi",
         "Installazione e smontaggio del montacarichi a cremagliera",
         "Montaggio del montacarichi a cremagliera (UNI EN 12158-1) a partire dalla base, con aggiunta "
         "progressiva degli elementi di colonna e degli ancoraggi alla struttura alle quote prescritte "
         "dal fabbricante. Comprende la recinzione della base, i cancelli ai piani di sbarco, i "
         "finecorsa, le prove di funzionamento e la verifica periodica se di portata superiore a 200 kg "
         "(Allegato VII); a fine lavori lo smontaggio in sequenza inversa.",
         "Addetto all'installazione e smontaggio del montacarichi", 50, EDILIZIA,
         ["Montacarichi a cremagliera", "Autocarro con gru", "Trapano elettrico", "Utensili manuali"], [
             _CADUTA_ALTO_MONTAGGIO,
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Area sottostante recintata durante il montaggio; elementi di colonna e attrezzi "
               "trattenuti sulla piattaforma con fermapiede; mai superare il carico di montaggio "
               "indicato dal fabbricante.", DPI_BASE + ", casco con sottogola"),
             r("Ribaltamento della colonna per ancoraggi insufficienti", 1, 4,
               "Ancoraggi a elementi strutturali e non a tamponamenti, con tasselli di tipo e "
               "resistenza previsti dal fabbricante e verificati; rispetto dell'altezza libera massima "
               "sopra l'ultimo ancoraggio."),
             r("Cesoiamenti e stritolamenti", 2, 4,
               "Durante il montaggio comandi solo dalla pulsantiera sulla piattaforma a velocità di "
               "montaggio; nessuno nel vano corsa o sotto la piattaforma; cancelli di piano chiusi "
               "e interbloccati prima della messa in servizio."),
             _VENTO,
         ]),

    # ------------------------------------------------------------------ Opere provvisionali
    fase("AL.29", _AL, "Opere provvisionali",
         "Montaggio del ponteggio metallico fisso",
         "Montaggio di ponteggio a telai prefabbricati, a tubi e giunti o a montanti e traversi, "
         "autorizzato dal Ministero del lavoro, secondo lo schema del libretto o il progetto (oltre 20 m "
         "o fuori schema, art. 133) e il PiMUS (Allegato XXII). Comprende basette e ripartitori su "
         "terreno verificato, ancoraggi alla facciata, impalcati, parapetti, fermapiede, mantovane e "
         "reti; squadra formata secondo l'Allegato XXI sotto la sorveglianza di un preposto (art. 136).",
         "Addetto al montaggio del ponteggio metallico fisso", 65, EDILIZIA,
         ["Autocarro con gru", "Argano a bandiera", "Martello perforatore (tassellatore)", "Utensili manuali",
          "Linea vita provvisoria"], [
             r("Caduta dall'alto", 3, 4,
               "Sequenza di montaggio del PiMUS che consente di salire solo su impalcati completi e "
               "protetti; imbracatura con doppio cordino o dispositivo collegato al ponteggio nei "
               "punti indicati dal fabbricante o a linea vita provvisoria; parapetti di montaggio "
               "anticipati dove il sistema li prevede; formazione e addestramento sui DPI di terza "
               "categoria.", _DPI_ANTICADUTA),
             r("Caduta di materiale dall'alto o a livello", 3, 3,
               "Area sottostante recintata e interdetta; sollevamento degli elementi con argano o gru "
               "e non a lancio; elementi e attrezzi trattenuti; fermapiede posati subito; mantovana o "
               "rete verso i passaggi pubblici.", DPI_BASE + ", casco con sottogola"),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Appoggi su basette regolabili e tavole di ripartizione su piano livellato; ancoraggi "
               "nel numero e nella posizione dello schema, con tasselli verificati con prova di "
               "estrazione dove richiesto; nessun carico di materiali prima del completamento; "
               "verifiche degli elementi secondo l'Allegato XIX."),
             _ELETTRO_LINEE, _MMC, _VENTO,
         ]),
    fase("AL.30", _AL, "Opere provvisionali",
         "Smontaggio del ponteggio metallico fisso",
         "Smontaggio dall'alto verso il basso, piano per piano, con la sequenza inversa del PiMUS: gli "
         "ancoraggi si rimuovono solo quando si smonta il piano corrispondente e mai prima. Gli elementi "
         "vengono calati con argano o gru, accatastati a terra per tipo e caricati su autocarro, dopo "
         "aver sgombrato gli impalcati da materiali e detriti.",
         "Addetto allo smontaggio del ponteggio metallico fisso", 70, EDILIZIA,
         ["Autocarro con gru", "Argano a bandiera", "Utensili manuali", "Linea vita provvisoria"], [
             r("Caduta dall'alto", 3, 4,
               "Imbracatura sempre collegata, anche durante la rimozione di parapetti e impalcati che "
               "lasciano il bordo libero; mai rimuovere parapetti del piano su cui si sta lavorando "
               "prima di aver predisposto l'aggancio; preposto presente per tutta la durata.",
               _DPI_ANTICADUTA),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Gli ancoraggi si tolgono solo al momento dello smontaggio del livello che vincolano; "
               "verificare prima che nessuno li abbia già rimossi durante le lavorazioni di facciata; "
               "non lasciare a fine giornata parti di ponteggio prive di ancoraggio."),
             r("Caduta di materiale dall'alto o a livello", 3, 3,
               "Impalcati ripuliti prima di iniziare; elementi calati con argano o gru e mai gettati; "
               "area a terra recintata e sorvegliata; chiusura o protezione dei passaggi pubblici "
               "adiacenti.", DPI_BASE + ", casco con sottogola"),
             _MMC, _VENTO,
         ]),
    fase("AL.31", _AL, "Opere provvisionali",
         "Installazione e rimozione di parapetti provvisori e linee vita provvisorie",
         "Posa di parapetti provvisori a morsa, a montante con piastra tassellata o a contrappeso sui "
         "bordi di solai, coperture, scale e aperture, scegliendo la classe A, B o C della UNI EN 13374 "
         "in base alla pendenza. Installazione di linee di ancoraggio provvisorie (UNI EN 795) tra "
         "punti strutturali verificati, con eventuale assorbitore di estremità, e rimozione a fine uso.",
         "Addetto all'installazione di parapetti provvisori e linee vita", 60, EDILIZIA,
         ["Parapetto provvisorio", "Linea vita provvisoria", "Martello perforatore (tassellatore)",
          "Avvitatore elettrico", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Chi posa le protezioni sul bordo è a sua volta trattenuto: imbracatura con cordino "
               "regolato in trattenuta a un ancoraggio già posato o a un elemento strutturale; posa "
               "procedendo da zone già protette; rimozione solo a lavorazione terminata e con "
               "aggancio attivo.", _DPI_ANTICADUTA),
             r("Cedimento dell'ancoraggio della linea vita o del parapetto", 1, 4,
               "Ancoraggi su strutture di resistenza verificata, con tasselli del tipo indicato dal "
               "fabbricante e serraggio controllato; tensione e freccia della linea secondo le "
               "istruzioni, con verifica del tirante d'aria sotto il bordo; numero massimo di "
               "utilizzatori dichiarato; registro delle installazioni."),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Montanti, morse e attrezzi trattenuti durante la posa sul bordo; area sottostante "
               "interdetta; fermapiede posato insieme al parapetto."),
             _MMC,
         ]),
    fase("AL.32", _AL, "Opere provvisionali",
         "Posa e rimozione di reti di sicurezza anticaduta",
         "Installazione di reti di sicurezza (UNI EN 1263-1 e 1263-2) sotto solai e coperture in "
         "costruzione o sui bordi, fissate con funi o ganci a strutture verificate, con altezza di "
         "caduta e spazio libero sotto la rete conformi alla norma. Il lavoro si svolge da piattaforma "
         "elevabile o da ponteggio; a fine uso le reti si rimuovono, si controllano e si ripongono "
         "al riparo da raggi UV e sostanze aggressive.",
         "Addetto alla posa e rimozione di reti di sicurezza", 65, ("Nuove costruzioni", "Ristrutturazioni",
                                                                   "Opere infrastrutturali"),
         ["Rete di sicurezza anticaduta", "Piattaforma di lavoro elevabile", "Utensili manuali"], [
             _CADUTA_ALTO_MONTAGGIO,
             r("Inefficacia della rete per posa o stato non corretti", 1, 4,
               "Usare reti etichettate e con prova della maglia di controllo in corso di validità; "
               "sovrapposizione tra teli e distanza dai punti di ancoraggio secondo UNI EN 1263-2; "
               "rete sostituita dopo una caduta o se danneggiata; detriti rimossi regolarmente."),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Area sotto la zona di posa interdetta; ganci, moschettoni e funi trattenuti; nessun "
               "lavoro sovrapposto sulla stessa verticale."),
             _MMC,
         ]),

    # ------------------------------------------------------------------ Segnaletica e viabilità
    fase("AL.33", _AL, "Segnaletica e viabilità temporanea",
         "Posa della segnaletica di sicurezza e della segnaletica stradale temporanea",
         "Posa dei cartelli di sicurezza all'ingresso e nelle zone di lavoro (Titolo V, Allegati "
         "XXIV-XXXII), dei percorsi pedonali delimitati e, per cantieri su strada o in adiacenza, "
         "della segnaletica temporanea secondo il Codice della Strada (art. 21, D.P.R. 495/1992) e gli "
         "schemi del D.M. 10/07/2002: preavvisi, delimitazioni con coni e barriere, luci e impianti "
         "semaforici. Posa, controllo giornaliero e rimozione seguono l'ordine di marcia indicato e "
         "sono svolti da addetti formati secondo il D.M. 22/01/2019.",
         "Addetto alla posa della segnaletica di cantiere e stradale temporanea", 55, TUTTE,
         ["Autocarro", "Trapano elettrico", "Utensili manuali"], [
             r("Investimento da veicoli in transito", 3, 4,
               "Posa e rimozione nel senso di marcia stabilito, partendo dal preavviso e muovendosi "
               "protetti dal veicolo operativo con pannello luminoso; scendere dal veicolo sul lato "
               "opposto al traffico; indumenti ad alta visibilità di classe 3 per strade "
               "extraurbane o con visibilità ridotta; movieri con palette per i sensi unici "
               "alternati; formazione del D.M. 22/01/2019.",
               "Casco, calzature di sicurezza, guanti, indumenti ad alta visibilità"),
             _INVESTIMENTO, _MMC, _SCIVOLAMENTI,
             r("Microclima", 2, 2,
               "Pause e acqua nei periodi caldi; indumenti per pioggia e freddo con bande riflettenti "
               "per non ridurre la visibilità; posa notturna solo con illuminazione del veicolo e "
               "lampeggianti.", DPI_BASE + ", indumenti impermeabili"),
         ]),

    # ------------------------------------------------------------------ Smobilizzo
    fase("AL.34", _AL, "Smobilizzo del cantiere",
         "Smontaggio di baraccamenti, servizi e impianti di cantiere",
         "A fine lavori, distacco e messa in sicurezza degli impianti elettrico, idrico e fognario "
         "(prima il sezionamento elettrico a monte), svuotamento delle vasche di scarico con "
         "autospurgo, scollegamento dei monoblocchi e loro carico su autocarro con gru. Comprende la "
         "rimozione delle linee, dei quadri, dei dispersori dove richiesto e dei basamenti.",
         "Addetto allo smontaggio di baraccamenti e impianti di cantiere", 45, TUTTE,
         ["Autocarro con gru", "Autospurgo", "Miniescavatore", "Martello demolitore", "Utensili manuali"], [
             r("Elettrocuzione", 1, 4,
               "Linee e quadri smontati solo dopo il sezionamento e il distacco a monte verificati da "
               "persona esperta (CEI 11-27); cartello di divieto di manovra sul punto di consegna; "
               "le macchine ancora in uso sono alimentate da linee separate e segnalate.",
               DPI_BASE + ", guanti dielettrici"),
             _CARICHI_SOSPESI, _SCHIACCIAMENTO_POSA,
             r("Rischio biologico", 2, 2,
               "Svuotamento e lavaggio di bagni chimici e vasche con autospurgo, senza contatto "
               "diretto con i reflui; guanti impermeabili; igiene delle mani.",
               DPI_BASE + ", guanti in lattice o nitrile"),
             _MMC, _INVESTIMENTO,
         ]),
    fase("AL.35", _AL, "Smobilizzo del cantiere",
         "Rimozione della recinzione, pulizia finale e riconsegna dell'area",
         "Rimozione di recinzioni, accessi, segnaletica e delimitazioni, demolizione delle piste e "
         "delle platee provvisorie, raccolta e separazione dei rifiuti residui con avvio a recupero o "
         "smaltimento (D.Lgs. 152/2006) e ripristino dei luoghi. Il cantiere resta segnalato e chiuso "
         "ai terzi fino alla rimozione dell'ultimo mezzo.",
         "Addetto alla pulizia finale e allo smobilizzo del cantiere", 60, TUTTE,
         ["Minipala (skid loader)", "Autocarro", "Martello demolitore", "Spazzatrice stradale",
          "Utensili manuali"], [
             _INVESTIMENTO, _MMC, _PUNTURE,
             r("Polveri e fibre", 2, 2,
               "Bagnare le superfici prima di spazzare e demolire le platee; spazzatrice con "
               "abbattimento a umido; evitare di sollevare polvere verso le aree abitate.",
               DPI_BASE + ", facciale filtrante FFP2"),
             r("Rischio chimico", 1, 3,
               "Contenitori di oli, vernici e prodotti residui chiusi ed etichettati, raccolti senza "
               "travasi improvvisati; terreni macchiati da perdite segnalati al direttore tecnico per "
               "la gestione come rifiuto.", DPI_BASE + ", guanti in lattice o nitrile"),
             _SOTTOSERVIZI,
         ]),

    # ================================================================== Tagli, carotaggi e perforazioni
    # ------------------------------------------------------------------ Tagli di murature e c.a.
    fase("TP.01", _TP, "Tagli di murature e strutture in calcestruzzo",
         "Taglio di murature con sega a disco",
         "Taglio di murature in laterizio, pietra o blocchi con sega a disco diamantato manuale o "
         "troncatrice, per aperture, riduzioni di spessore o separazione di parti da demolire, "
         "seguendo la traccia segnata e con alimentazione d'acqua o aspirazione. Il taglio in profondità "
         "si esegue a passate successive, da ponte su cavalletti o trabattello per le parti alte.",
         "Addetto al taglio di murature con sega a disco", 60, ("Ristrutturazioni", "Restauri",
                                                                "Opere infrastrutturali"),
         ["Sega a disco per murature e calcestruzzo", "Aspiratore con filtro HEPA", "Ponte su cavalletti",
          "Trabattello", "Utensili manuali"], [
             _SILICE, _IMPIANTI_NASCOSTI, _SCHEGGE, _POSTURE,
             r("Crollo o ribaltamento di strutture", 2, 3,
               "Tagli su murature portanti solo su indicazione del tecnico; porzioni di muratura "
               "isolate dal taglio sostenute o demolite subito, senza lasciare parti a sbalzo o "
               "instabili; nessun taglio dal basso di elementi che possono cadere sull'operatore."),
             _FANGHI,
         ]),
    fase("TP.02", _TP, "Tagli di murature e strutture in calcestruzzo",
         "Taglio di pareti e solette in c.a. con sega murale su binario",
         "Taglio rettilineo di pareti e solette in calcestruzzo armato con sega a disco diamantato che "
         "scorre su binario fissato con tasselli, a motore elettrico o idraulico, comandata a distanza. "
         "Il taglio è raffreddato ad acqua e procede a passate successive fino allo spessore completo; "
         "i conci isolati sono sostenuti e rimossi con mezzi di sollevamento.",
         "Addetto al taglio di strutture in c.a. con sega murale", 45, ("Ristrutturazioni",
                                                                        "Opere infrastrutturali",
                                                                        "Restauri"),
         ["Sega murale su binario", "Martello perforatore (tassellatore)", "Autogru", "Carrello elevatore",
          "Utensili manuali"], [
             _CROLLO, _CADUTA_BLOCCO, _FANGHI, _IMPIANTI_NASCOSTI, _SCHEGGE,
             r("Movimentazione manuale dei carichi", 3, 2,
               "Binario, testa motore e carter montati in due o con paranco; elementi più pesanti "
               "portati sul posto con carrello; percorsi liberi da ostacoli.")
         ]),
    fase("TP.03", _TP, "Tagli di murature e strutture in calcestruzzo",
         "Taglio di strutture in c.a. con sega a filo diamantato",
         "Taglio di elementi in c.a. di grande spessore o forma irregolare (travi, pile, fondazioni, "
         "solette) con filo diamantato avvolto attorno all'elemento attraverso fori passanti eseguiti "
         "con carotatrice, mosso dalla macchina a pulegge e raffreddato ad acqua. Prima del taglio "
         "finale il blocco viene imbracato o vincolato e poi rimosso con autogru.",
         "Addetto al taglio di strutture in c.a. con sega a filo diamantato", 40,
         ("Ristrutturazioni", "Opere infrastrutturali", "Restauri"),
         ["Sega a filo diamantato", "Carotatrice", "Autogru", "Utensili manuali"], [
             r("Proiezione di schegge e frammenti per rottura del filo", 2, 4,
               "Area di rispetto recintata lungo il piano del filo e nelle direzioni di possibile "
               "frustata, indicate dal fabbricante; carter o schermi sul tratto libero del filo; "
               "operatore alla pulsantiera in posizione protetta; giunti e perline controllati e "
               "sostituiti se usurati; filo tensionato senza strappi.",
               DPI_BASE + ", visiera protettiva"),
             _CADUTA_BLOCCO, _CROLLO, _FANGHI,
             r("Cesoiamenti e stritolamenti", 2, 3,
               "Nessun intervento su pulegge e filo con macchina in moto; avvolgimento del filo e "
               "regolazioni solo a motore fermo e sezionato."),
         ]),
    fase("TP.04", _TP, "Tagli di murature e strutture in calcestruzzo",
         "Taglio di pavimentazioni e solette in calcestruzzo con sega da pavimento",
         "Taglio di pavimentazioni industriali, massetti e solette controterra con tagliasfalto a disco "
         "diamantato raffreddato ad acqua, per giunti, aperture di cavedi, rimozione di porzioni o "
         "scavi a sezione per reti. Il tracciato viene segnato e verificato rispetto a impianti e "
         "armature prima del taglio.",
         "Addetto al taglio di pavimentazioni in calcestruzzo", 45, TUTTE,
         ["Tagliasfalto a disco", "Martello demolitore", "Minipala (skid loader)", "Utensili manuali"], [
             _IMPIANTI_NASCOSTI, _FANGHI,
             r("Polveri e fibre (silice cristallina respirabile)", 2, 3,
               "Taglio sempre a umido con serbatoio pieno; rimozione dei fanghi prima che asciughino; "
               "in ambienti chiusi ricambio d'aria.", _DPI_POLVERI),
             r("Ambienti confinati o sospetti di inquinamento (gas di scarico)", 2, 3,
               "In locali chiusi o seminterrati usare macchine elettriche; se a motore endotermico, "
               "solo con ventilazione forzata e misura del monossido di carbonio con rilevatore."),
             _MMC,
         ]),

    # ------------------------------------------------------------------ Carotaggi
    fase("TP.05", _TP, "Carotaggi",
         "Carotaggi in murature e strutture in c.a. per passaggi impiantistici",
         "Esecuzione di fori cilindrici con carotatrice a corona diamantata, montata su supporto fissato "
         "con tassello o base a vuoto, per il passaggio di tubazioni, canne e cavi in pareti e solai. "
         "La posizione è verificata con il tecnico per non intercettare armature principali; il "
         "carotaggio procede a umido con raccolta dell'acqua e recupero della carota.",
         "Addetto ai carotaggi per passaggi impiantistici", 50, TUTTE,
         ["Carotatrice", "Martello perforatore (tassellatore)", "Trabattello", "Utensili manuali"], [
             _IMPIANTI_NASCOSTI, _FANGHI,
             r("Caduta della carota o di frammenti sul lato opposto", 2, 3,
               "Zona sottostante o retrostante il foro delimitata e controllata prima di forare; "
               "nei solai carota trattenuta con apposito tappo o ritegno; avvisare chi lavora nei "
               "locali adiacenti."),
             r("Urti, colpi, impatti e compressioni per rotazione della carotatrice", 2, 3,
               "Supporto fissato saldamente prima di avviare; per carotaggi a mano oltre il diametro "
               "indicato dal fabbricante usare sempre il supporto; frizione di sicurezza efficiente; "
               "posizione stabile dell'operatore."),
             _POSTURE,
         ]),
    fase("TP.06", _TP, "Carotaggi",
         "Prelievo di carote per indagini sui materiali",
         "Prelievo di campioni cilindrici da strutture in calcestruzzo (UNI EN 12504-1) o in muratura "
         "per prove di laboratorio, nelle posizioni scelte dal tecnico dopo aver individuato le armature "
         "con pacometro. Dopo l'estrazione il foro viene richiuso con malta a ritiro compensato; il "
         "lavoro è spesso svolto in edifici abitati o in uso.",
         "Addetto al prelievo di carote per indagini", 55, ("Ristrutturazioni", "Restauri",
                                                           "Opere infrastrutturali"),
         ["Carotatrice", "Martello perforatore (tassellatore)", "Trabattello", "Scala doppia",
          "Utensili manuali"], [
             _IMPIANTI_NASCOSTI, _FANGHI,
             r("Crollo o ribaltamento di strutture", 1, 4,
               "Numero, diametro e posizione dei prelievi stabiliti dal tecnico per non indebolire "
               "elementi già critici; puntellare prima gli elementi degradati o lesionati; "
               "ripristino del foro subito dopo il prelievo."),
             r("Interferenza con occupanti dell'edificio", 2, 2,
               "Zona di lavoro delimitata e segnalata; teli per contenere acqua e polvere; "
               "accordo con il committente su orari e percorsi."),
             _CADUTA_QUOTA_TP,
         ]),

    # ------------------------------------------------------------------ Perforazioni e ancoraggi
    fase("TP.07", _TP, "Perforazioni e ancoraggi",
         "Perforazioni per tasselli e ancoraggi meccanici",
         "Foratura di calcestruzzo e murature con martello perforatore per la posa di tasselli "
         "meccanici a espansione o a vite destinati a staffe, mensole, impianti e ancoraggi di opere "
         "provvisionali. Diametro, profondità, interasse e distanza dai bordi sono quelli del "
         "fabbricante; il foro viene pulito e il tassello serrato con chiave dinamometrica.",
         "Addetto alle perforazioni e alla posa di ancoraggi meccanici", 65, TUTTE,
         ["Martello perforatore (tassellatore)", "Aspiratore con filtro HEPA", "Avvitatore elettrico",
          "Trabattello", "Utensili manuali"], [
             r("Polveri e fibre (silice cristallina respirabile)", 3, 2,
               "Punte con aspirazione integrata o aspiratore di classe H collegato; pulizia dei fori "
               "con pompetta solo indossando la protezione respiratoria; in locali chiusi limitare "
               "la presenza di altri lavoratori.", _DPI_POLVERI),
             _IMPIANTI_NASCOSTI, _POSTURE, _CADUTA_QUOTA_TP,
             r("Cedimento dell'ancoraggio", 1, 4,
               "Ancoraggi solo su supporto idoneo (non su intonaci o laterizi forati senza tassello "
               "specifico); prove di carico o di estrazione a campione per gli ancoraggi di sicurezza "
               "(ponteggi, linee vita); annotazione dei risultati."),
         ]),
    fase("TP.08", _TP, "Perforazioni e ancoraggi",
         "Ancoraggi chimici e inghisaggio di barre con resine",
         "Foratura, pulizia accurata del foro con scovolo e soffiaggio, iniezione di resina epossidica, "
         "vinilestere o poliestere con pistola dosatrice e inserimento di barre o tirafondi. Il carico "
         "si applica solo dopo il tempo di indurimento previsto alla temperatura del supporto; per "
         "ancoraggi strutturali è richiesta la verifica a campione con prove di estrazione.",
         "Addetto all'esecuzione di ancoraggi chimici", 60, TUTTE,
         ["Martello perforatore (tassellatore)", "Aspiratore con filtro HEPA", "Trapano elettrico",
          "Utensili manuali", "Trabattello"], [
             r("Rischio chimico", 3, 2,
               "Consultare la scheda di dati di sicurezza: le resine e gli indurenti possono essere "
               "sensibilizzanti e irritanti per pelle e occhi; guanti in nitrile cambiati spesso, mai "
               "toccare la resina a mani nude; cartucce usate chiuse e smaltite come rifiuto; "
               "ventilazione nei locali chiusi; informare il medico competente in caso di dermatiti.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
             r("Polveri e fibre (silice cristallina respirabile)", 3, 2,
               "Soffiaggio del foro con pompetta indirizzata lontano dal viso e aspirazione della "
               "polvere; maschera durante la foratura e la pulizia dei fori.", _DPI_POLVERI),
             _IMPIANTI_NASCOSTI,
             r("Getti e schizzi", 2, 2,
               "Iniettare dal fondo del foro estraendo lentamente il miscelatore; con fori verso "
               "l'alto usare i tappi di ritenuta; occhiali sempre indossati.",
               DPI_BASE + ", occhiali a maschera"),
             _POSTURE,
         ]),
    fase("TP.09", _TP, "Perforazioni e ancoraggi",
         "Perforazioni armate per cuciture e consolidamento di murature",
         "Esecuzione di fori lunghi, anche inclinati, in murature e volte con carotatrice o "
         "perforatore a rotazione, per inserire barre in acciaio inox o fibre e iniettare miscele "
         "leganti a bassa pressione con pompa. Il lavoro, tipico degli interventi di consolidamento, "
         "si svolge da ponteggio secondo lo schema e la sequenza del progetto.",
         "Addetto alle perforazioni armate per il consolidamento delle murature", 55,
         ("Ristrutturazioni", "Restauri"),
         ["Carotatrice", "Martello perforatore (tassellatore)", "Pompa per malte e iniezioni", "Impastatrice",
          "Ponteggio metallico fisso", "Utensili manuali"], [
             _SILICE,
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Murature degradate o lesionate puntellate e presidiate prima di forare; fori eseguiti "
               "nella sequenza del progetto, a umido o a rotazione senza percussione nelle murature "
               "deboli; pressioni di iniezione limitate e controllate per non spingere le murature."),
             r("Getti e schizzi di miscela", 3, 2,
               "Raccordi e tubi della pompa controllati prima dell'uso; scaricare la pressione prima di "
               "staccare l'ugello; tappi di sfiato sui fori adiacenti; le miscele cementizie sono "
               "irritanti per cute e occhi.", DPI_BASE + ", occhiali a maschera, guanti in lattice o nitrile"),
             _MMC, _POSTURE,
         ]),

    # ------------------------------------------------------------------ Scanalature e tracce
    fase("TP.10", _TP, "Scanalature e tracce per impianti",
         "Esecuzione di scanalature in murature per impianti",
         "Apertura di tracce orizzontali e verticali in murature e tramezzi con scanalatrice a due dischi "
         "e rifinitura con utensili manuali o martello leggero, per incassare tubazioni e corrugati. "
         "Profondità e tracciati rispettano i limiti del progettista per le murature portanti; le "
         "tracce orizzontali lunghe nei muri portanti vanno evitate o autorizzate.",
         "Addetto all'esecuzione di scanalature per impianti", 70, EDILIZIA,
         ["Scanalatrice per murature", "Aspiratore con filtro HEPA", "Martello perforatore (tassellatore)",
          "Ponte su cavalletti", "Utensili manuali"], [
             _SILICE, _IMPIANTI_NASCOSTI, _SCHEGGE, _POSTURE,
             r("Movimenti ripetitivi degli arti superiori", 2, 2,
               "Alternare la scanalatura con altre attività; pause programmate; scanalatrice con "
               "impugnature regolabili e peso adeguato all'uso prolungato."),
         ]),
    fase("TP.11", _TP, "Scanalature e tracce per impianti",
         "Esecuzione di tracce e nicchie in solette, massetti e pareti in calcestruzzo",
         "Taglio dei bordi della traccia con sega a disco o smerigliatrice con disco diamantato e "
         "asportazione del materiale con martello demolitore leggero, per incassare impianti, "
         "cassette e collettori in massetti, solette e pareti in c.a. Le armature non vanno tagliate "
         "senza autorizzazione del tecnico.",
         "Addetto all'esecuzione di tracce in calcestruzzo", 70, EDILIZIA,
         ["Sega a disco per murature e calcestruzzo", "Smerigliatrice angolare", "Martello demolitore",
          "Aspiratore con filtro HEPA", "Utensili manuali"], [
             _SILICE, _IMPIANTI_NASCOSTI, _SCHEGGE,
             r("Posture incongrue", 3, 2,
               "Lavori a pavimento in ginocchio con ginocchiere e pause frequenti; uso del martello con "
               "il peso sorretto dall'attrezzo e non dalla schiena; alternanza degli addetti.",
               DPI_BASE + ", ginocchiere"),
             r("Crollo o ribaltamento di strutture", 1, 3,
               "Tracce in solai e pareti in c.a. solo nei tracciati approvati; mai tagliare ferri di "
               "armatura o indebolire travetti e nervature senza indicazione del tecnico."),
         ]),

    # ------------------------------------------------------------------ Aperture di vani
    fase("TP.12", _TP, "Aperture di vani in murature portanti",
         "Puntellazione provvisoria per l'apertura di vani",
         "Prima di aprire il vano si sostengono i carichi sovrastanti con puntelli metallici regolabili "
         "e traversi, su entrambi i lati del muro, e si scaricano i solai interessati con rompitratta. "
         "Se previsto dal progetto, si eseguono passanti (fori) sopra il vano per travi di sostegno "
         "provvisorie. I puntelli poggiano su tavole di ripartizione su piani verificati e vengono messi "
         "in carico prima di qualsiasi taglio.",
         "Addetto alla puntellazione per l'apertura di vani", 65, ("Ristrutturazioni", "Restauri"),
         ["Puntelli metallici", "Martello perforatore (tassellatore)", "Carotatrice", "Ponte su cavalletti",
          "Utensili manuali"], [
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Puntellazione eseguita secondo lo schema del tecnico (numero, portata e posizione dei "
               "puntelli); appoggi su elementi portanti, non su pavimenti galleggianti o solai non "
               "verificati, con eventuale puntellazione anche ai piani inferiori; puntelli a piombo, "
               "bloccati e con spinotti originali; controllo prima di ogni ripresa del lavoro."),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Puntelli e traversi sollevati in due e trattenuti fino al bloccaggio; rimozione "
               "preventiva di controsoffitti, intonaci e elementi instabili nell'area."),
             _MMC,
             r("Urti, colpi, impatti e compressioni", 2, 2,
               "Mani lontane dal tubo interno e dai fori di regolazione durante la messa in "
               "altezza; regolazione fine solo con la ghiera filettata."),
         ]),
    fase("TP.13", _TP, "Aperture di vani in murature portanti",
         "Apertura del vano e posa della cerchiatura metallica",
         "Con la puntellazione in carico si taglia il perimetro del vano con sega a disco, si demolisce "
         "la muratura interna dall'alto verso il basso e si inseriscono architrave e piedritti in "
         "acciaio (o in c.a.) previsti dal progetto, collegati alla muratura e messi in carico con "
         "cunei, malta a ritiro compensato o martinetti. I puntelli si rimuovono solo dopo "
         "l'autorizzazione del direttore dei lavori.",
         "Addetto all'apertura di vani e alla posa di cerchiature", 55, ("Ristrutturazioni", "Restauri"),
         ["Sega a disco per murature e calcestruzzo", "Martello demolitore", "Saldatrice",
          "Martello perforatore (tassellatore)", "Puntelli metallici", "Ponte su cavalletti",
          "Utensili manuali"], [
             _CROLLO, _SILICE,
             r("Caduta di materiale dall'alto o a livello", 3, 3,
               "Demolizione dall'alto verso il basso a piccoli elementi, senza scalzare la muratura "
               "alla base; nessuno sotto la zona di demolizione; profili metallici sollevati con "
               "argano, paranco o in numero adeguato di addetti e mai lasciati in bilico.",
               DPI_BASE + ", occhiali protettivi"),
             _MMC, _IMPIANTI_NASCOSTI,
             r("Incendio ed esplosione", 1, 3,
               "Saldature e tagli a caldo dei profili lontano da materiali combustibili, che vanno "
               "rimossi o coperti; estintore a portata di mano; controllo dell'area dopo la fine dei "
               "lavori a caldo.", DPI_BASE + ", schermo per saldatura, guanti per saldatura"),
         ]),

    # ------------------------------------------------------------------ Demolizioni controllate
    fase("TP.14", _TP, "Demolizioni controllate per tagli",
         "Demolizione controllata per tagli a blocchi e rimozione con mezzi di sollevamento",
         "Demolizione di solette, travi, scale o porzioni di strutture eseguita senza percussioni, "
         "suddividendo l'elemento in blocchi con tagli a disco, a filo o carotaggi accostati. Ogni blocco "
         "viene imbracato o sostenuto prima del distacco, sollevato con autogru o calato con carrello e "
         "ridotto a terra per il trasporto. La sequenza dei tagli è stabilita nel programma delle "
         "demolizioni (art. 151) per non compromettere la stabilità delle parti che restano.",
         "Addetto alla demolizione controllata per tagli", 45, ("Ristrutturazioni", "Opere infrastrutturali",
                                                                "Restauri"),
         ["Sega a disco per murature e calcestruzzo", "Sega a filo diamantato", "Carotatrice", "Autogru",
          "Carrello elevatore", "Escavatore con pinza demolitrice", "Utensili manuali"], [
             _CROLLO, _CADUTA_BLOCCO, _CARICHI_SOSPESI, _FANGHI,
             r("Caduta dall'alto", 2, 4,
               "Bordi di solette e aperture lasciati dal taglio protetti con parapetti o coperture "
               "prima della rimozione del blocco; imbracatura collegata a punti di ancoraggio "
               "indipendenti dalla parte da rimuovere.", _DPI_ANTICADUTA),
             r("Sovraccarico dei solai sottostanti", 2, 4,
               "Blocchi deposti solo su aree verificate per il carico o direttamente a terra; "
               "puntellazione dei solai sottostanti se il progetto lo prevede."),
         ]),
    fase("TP.15", _TP, "Demolizioni controllate per tagli",
         "Demolizione con malte espansive",
         "Frantumazione silenziosa e senza vibrazioni di calcestruzzo, roccia o murature massive "
         "riempiendo fori eseguiti a maglia regolare con malta espansiva miscelata ad acqua, che "
         "fessura l'elemento in alcune ore. Le parti fessurate si rimuovono poi con martello o mezzi "
         "meccanici; l'area resta interdetta durante l'espansione.",
         "Addetto alla demolizione con malte espansive", 55, ("Ristrutturazioni", "Opere infrastrutturali",
                                                              "Restauri"),
         ["Martello perforatore (tassellatore)", "Martello demolitore", "Impastatrice",
          "Escavatore con martello demolitore", "Utensili manuali"], [
             r("Getti e schizzi di malta dai fori (blow-out)", 2, 3,
               "Rispettare diametro dei fori, temperatura dei materiali e tipo di prodotto adatto "
               "alla stagione indicati dal fabbricante; non guardare né sporgersi sui fori riempiti; "
               "coprire i fori con teli o sacchi; area interdetta fino al termine della reazione.",
               DPI_BASE + ", occhiali a maschera, visiera protettiva"),
             r("Rischio chimico", 3, 2,
               "Il prodotto è fortemente alcalino e corrosivo per occhi e pelle: miscelazione con "
               "guanti e occhiali, senza contatto con la cute; acqua per il lavaggio oculare a "
               "disposizione; scheda di dati di sicurezza consultabile.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali a maschera, facciale filtrante FFP2"),
             _SILICE, _CROLLO,
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Rimozione dei frammenti fessurati dall'alto verso il basso e solo dopo la fine "
               "dell'espansione; parti instabili disgaggiate a distanza con mezzo meccanico."),
         ]),
]
