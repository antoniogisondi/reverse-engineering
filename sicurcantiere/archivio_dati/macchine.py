"""Rischi e schede d'uso delle nuove macchine dell'archivio (movimento terra, sollevamento,
macchine stradali, perforazione e fondazioni, servizi di cantiere).

Testi redatti per questo progetto, con parole proprie, a partire da:
- D.Lgs. 81/2008: artt. 70-73 e Allegati V e VI (requisiti e uso delle attrezzature), art. 71 c. 11 e
  Allegato VII (verifiche periodiche), artt. 83 e 117 e Allegato IX (lavori vicino a linee elettriche),
  Titolo VIII capi II e III (rumore e vibrazioni), Titolo IX (agenti chimici e silice);
- Accordo Stato-Regioni 22/02/2012 sulle attrezzature che richiedono l'abilitazione degli operatori
  (art. 73 c. 5);
- norme armonizzate di prodotto: serie EN 474 (macchine movimento terra), EN ISO 3471 / EN ISO 12117-2
  (ROPS), EN ISO 3449 (FOPS), EN 280 (PLE), EN 1459 (sollevatori telescopici), EN ISO 3691-1 (carrelli),
  EN 12158-1 / EN 12159 (montacarichi da cantiere), EN 1012-1 (compressori), ISO 8528-13 (gruppi
  elettrogeni), serie EN 500 e EN 13019 (macchine stradali e spazzatrici), serie EN 16228 (perforazione
  e fondazioni), EN 1829-1 (getti ad alta pressione), EN 13525 (cippatrici);
- D.I. 22/01/2019 (segnaletica per attività in presenza di traffico) e D.P.R. 177/2011 (ambienti
  confinati);
- pubblicazione INAIL DIT «Macchine per cantiere e costruzione. L'accertamento tecnico per la sicurezza
  delle macchine per cantiere e costruzione» (2024) e articoli di PuntoSicuro sulle macchine movimento
  terra e sull'Accordo Stato-Regioni; manuali d'uso tipici dei fabbricanti.
Le misure vanno sempre adattate alle istruzioni del fabbricante della macchina effettivamente usata.
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import MACCHINA, attrezzatura, r, scheda

# DPI ricorrenti (stringhe per i rischi, liste per le schede).
_DPI = "Casco, calzature di sicurezza, guanti, indumenti ad alta visibilità"
_DPI_CABINA = "Calzature di sicurezza; fuori dalla cabina casco, guanti e indumenti ad alta visibilità"
_DPI_RUMORE = "Otoprotettori (cuffie antirumore o inserti auricolari)"
_DPI_POLVERI = "Facciale filtrante FFP3 (FFP2 per polveri non silicee), occhiali protettivi"

_SCHEDA_DPI_CONDUCENTE = ["calzature di sicurezza", "casco", "guanti", "indumenti ad alta visibilità",
                          "otoprotettori"]
_SCHEDA_DPI_A_TERRA = ["casco", "calzature di sicurezza", "guanti", "indumenti ad alta visibilità",
                       "otoprotettori", "occhiali protettivi"]

# Testi delle misure comuni a più macchine.
_LINEE = ("Prima dell'inizio individuare le linee elettriche aeree e mantenere da esse, con ogni parte "
          "della macchina e del carico, le distanze dell'Allegato IX tab. 1 (3 m fino a 1 kV, 3,5 m fino a "
          "30 kV, 5 m fino a 132 kV, 7 m oltre); se non è possibile far mettere fuori tensione la linea "
          "dall'ente gestore o installare barriere e portali di limitazione (artt. 83 e 117)")
_ROPS = ("cabina o telaio ROPS/FOPS integri e cintura di sicurezza sempre allacciata; in caso di "
         "ribaltamento restare al posto di guida")
_MMT_ABILITAZIONE = ("operatore abilitato secondo l'Accordo Stato-Regioni 17 aprile 2025 (art. 73, comma 5, "
                     "D.Lgs. 81/2008)")


def _rumore(lex: str, misure_extra: str = "") -> dict:
    return r("Rumore", 3, 2,
             f"Livello di esposizione indicativo {lex}: valutazione ai sensi del Titolo VIII Capo II; cabina "
             "insonorizzata con porte e finestrini chiusi, silenziatori e carter fonoassorbenti integri; "
             "sorveglianza sanitaria oltre 85 dB(A); segnalazione delle aree oltre il valore superiore di "
             "azione" + (f"; {misure_extra}" if misure_extra else ""),
             _DPI_RUMORE)


def _wbv(p: int = 3) -> dict:
    return r("Vibrazioni al corpo intero", p, 2,
             "Valutazione ai sensi dell'art. 202 (valore d'azione 0,5 m/s², limite 1,0 m/s² su 8 ore); "
             "sedile a sospensione regolato sul peso del conducente; piste di cantiere livellate e prive "
             "di buche; velocità adeguata al fondo; rotazione degli operatori nei lavori di lunga durata",
             "Calzature di sicurezza")


def _gas_scarico(macchina: str) -> dict:
    return r("Inalazione di gas di scarico", 2, 3,
             f"Non usare {macchina} in locali chiusi, scavi profondi o gallerie senza ventilazione forzata e "
             "misura dei gas (CO, NO2); motore a emissioni ridotte (Stage V con filtro antiparticolato "
             "dove disponibile); terminale di scarico orientato lontano dai posti di lavoro; motore spento "
             "nelle soste",
             _DPI)


def _investimento(extra: str) -> dict:
    return r("Investimento da mezzi in manovra", 3, 4,
             "Percorsi e aree di manovra separati da quelli pedonali e delimitati; segnalatore acustico di "
             "retromarcia e girofaro attivi; specchi e telecamere puliti e regolati; nessuno nel raggio "
             "d'azione; moviere nelle manovre con visibilità ridotta; velocità a passo d'uomo vicino ai "
             f"posti di lavoro; {extra}",
             _DPI)


def _traffico(extra: str = "") -> dict:
    return r("Investimento da veicoli in transito sulla strada", 3, 4,
             "Cantiere stradale segnalato e delimitato secondo il D.M. 10/07/2002 e il D.I. 22/01/2019, con "
             "personale formato per la posa della segnaletica; luci lampeggianti e pannello a messaggio "
             "variabile o freccia luminosa sulla macchina; operatori sempre dentro l'area delimitata e mai "
             "rivolti di spalle al traffico" + (f"; {extra}" if extra else ""),
             "Indumenti ad alta visibilità classe 3, casco, calzature di sicurezza")


def _incendio_rifornimento(extra: str = "") -> dict:
    return r("Incendio ed esplosione", 1, 3,
             "Rifornimento a motore spento e freddo, lontano da fiamme e scintille, con divieto di fumare; "
             "estintore a bordo o nelle immediate vicinanze; pulizia periodica del vano motore da olio, "
             "polvere e residui vegetali; controllo di tubazioni carburante e idrauliche"
             + (f"; {extra}" if extra else ""),
             _DPI)


def _oleodinamica() -> dict:
    return r("Getti di olio idraulico in pressione", 2, 3,
             "Controllo visivo giornaliero di tubi flessibili e raccordi; sostituzione dei flessibili "
             "danneggiati con ricambi originali; nessuna ricerca di perdite con le mani (usare un cartone); "
             "scaricare la pressione residua del circuito prima di ogni intervento",
             "Guanti, occhiali protettivi")


ATTREZZATURE = {
    # ------------------------------------------------------------------ movimento terra e demolizione
    "Miniescavatore": attrezzatura(MACCHINA, rischi=[
        r("Ribaltamento della macchina", 2, 4,
          "Lavorare su terreno portante e il più possibile in piano, a distanza dal ciglio degli scavi almeno "
          "pari alla loro profondità; con la lama abbassata a terra durante lo scavo; non traslare in "
          "trasversale sui pendii né con il braccio sollevato e carico; non superare le pendenze del "
          "fabbricante; " + _ROPS + " (UNI EN 474-1 e UNI EN 474-5, UNI EN ISO 12117-2); " + _MMT_ABILITAZIONE),
        _investimento("attenzione alla rotazione della torretta: delimitare il raggio di rotazione, compresa "
                      "la sporgenza posteriore nei modelli non a raggio ridotto"),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Nessuno tra torretta e ostacoli fissi o tra benna e parete di scavo; leva di sicurezza dei "
          "comandi sollevata prima di scendere; attacco rapido con dispositivo di bloccaggio verificato a "
          "ogni cambio di benna; uso per sollevare carichi solo con gancio sulla benna, valvole di blocco "
          "dei cilindri, tabella di portata e verifiche dell'Allegato VII se la portata supera 200 kg"),
        r("Contatto con sottoservizi e linee elettriche", 2, 4,
          "Acquisire le planimetrie dei sottoservizi dagli enti gestori e segnarne il tracciato a terra; "
          "scavo a mano o con aspirazione nell'ultimo tratto vicino a cavi e tubazioni del gas; "
          + _LINEE),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Non passare con la benna carica sopra persone o sopra la cabina degli autocarri; caricare il "
          "cassone dal lato posteriore o laterale con l'autista fuori dalla zona di carico; benna non "
          "riempita oltre il colmo"),
        _rumore("80-85 dB(A) per l'operatore"),
        _wbv(2),
        _oleodinamica(),
    ], scheda_uso=scheda(
        "Escavatore idraulico compatto (fino a circa 6 t), cingolato o gommato, per scavi in spazi ristretti, "
        "trincee per sottoservizi e piccole demolizioni con attrezzi intercambiabili.",
        ["verificare l'abilitazione dell'operatore (Accordo Stato-Regioni 17 aprile 2025)",
         "controllare cingoli, tubi idraulici, comandi, leva di sicurezza, cintura e struttura ROPS/TOPS",
         "verificare l'aggancio dell'attrezzo all'attacco rapido e il perno di sicurezza",
         "individuare sottoservizi e linee elettriche aeree nell'area di scavo",
         "scaricare la macchina dal carrello su terreno piano con rampe bloccate e nessuno nei pressi",
         "delimitare la zona di rotazione della torretta"],
        ["tenere la lama abbassata a terra durante lo scavo e allacciata la cintura",
         "mantenere la distanza dal ciglio degli scavi e non scavare sotto i cingoli",
         "non far sostare persone nel raggio d'azione né nello scavo durante il lavoro del braccio",
         "traslare sui pendii in linea di massima pendenza con la benna bassa",
         "non usare la benna per trasportare o sollevare persone",
         "fermarsi e segnalare se emergono tubazioni, cavi o nastri segnalatori"],
        ["appoggiare benna e lama a terra, sollevare la leva di sicurezza e togliere la chiave",
         "pulire cingoli e gradini da fango, controllare perdite e annotare le anomalie",
         "per il trasporto ancorare la macchina al carrello negli appositi punti"],
        _SCHEDA_DPI_CONDUCENTE)),

    "Escavatore con martello demolitore": attrezzatura(MACCHINA, rischi=[
        r("Proiezione di schegge e frammenti", 3, 3,
          "Cabina con protezione frontale (griglia o vetro antisfondamento, FGPS) e FOPS idonea alla "
          "demolizione secondo UNI EN 474-5; area interdetta a terra con raggio non inferiore a quello "
          "indicato dal fabbricante e comunque di almeno 10-15 m; nessun lavoratore a terra vicino al punto "
          "di battuta; schermi o reti sul lato verso strade e edifici",
          _DPI + ", occhiali protettivi o visiera protettiva"),
        _rumore("oltre 90 dB(A) nei pressi del martello",
                "martello idraulico silenziato; operatori a terra lontani o con otoprotettori"),
        r("Vibrazioni al corpo intero", 3, 2,
          "Valutazione ai sensi dell'art. 202; sedile a sospensione regolato; evitare la battuta a vuoto e "
          "l'uso del martello come leva; pause e rotazione dei conducenti",
          "Calzature di sicurezza"),
        r("Polveri e fibre", 4, 3,
          "Abbattimento con nebulizzatori o cannoni ad acqua sul punto di demolizione; cabina pressurizzata "
          "con filtri; verifica preliminare dell'assenza di amianto; valutazione della silice cristallina "
          "respirabile (Titolo IX Capo II)",
          _DPI_POLVERI),
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Demolizione secondo il programma dei lavori di demolizione (art. 151) dall'alto verso il basso; "
          "macchina posizionata fuori dalla zona di possibile caduta delle parti demolite; non demolire "
          "elementi che sovrastano la macchina; verifica della portata dei solai e delle rampe su cui la "
          "macchina transita"),
        r("Ribaltamento della macchina", 2, 4,
          "Escavatore di massa adeguata al martello secondo le tabelle del fabbricante; lavorare su piano "
          "stabile e con la torretta allineata ai cingoli dove possibile; " + _ROPS + "; " + _MMT_ABILITAZIONE),
        _investimento("delimitare l'area di lavoro con recinzione fissa"),
        _oleodinamica(),
    ], scheda_uso=scheda(
        "Escavatore idraulico attrezzato con martello demolitore idraulico per la frantumazione di "
        "calcestruzzo, murature, pavimentazioni e roccia.",
        ["verificare l'abilitazione dell'operatore e la compatibilità tra martello ed escavatore (massa, "
         "portata e pressione dell'impianto idraulico)",
         "controllare la protezione frontale della cabina e la struttura FOPS",
         "verificare l'aggancio del martello, i perni, le tubazioni e l'usura dell'utensile",
         "accertare l'assenza di amianto e di impianti attivi nelle strutture da demolire",
         "delimitare l'area di proiezione e predisporre i nebulizzatori per la polvere",
         "verificare la portata del piano su cui opera la macchina"],
        ["battere con l'utensile perpendicolare alla superficie e senza far leva",
         "non battere a vuoto e interrompere la battuta oltre i 15-30 secondi sullo stesso punto",
         "tenere porte e finestrini chiusi con l'impianto di filtrazione in funzione",
         "fermare il lavoro se qualcuno entra nell'area interdetta",
         "non demolire elementi che sovrastano la macchina"],
        ["appoggiare il martello a terra in posizione stabile e scaricare la pressione",
         "ingrassare l'utensile come indicato dal fabbricante e controllare le boccole",
         "pulire la cabina e i filtri dell'aria dalla polvere"],
        _SCHEDA_DPI_CONDUCENTE + ["facciale filtrante FFP3"])),

    "Escavatore con pinza demolitrice": attrezzatura(MACCHINA, rischi=[
        r("Crollo o ribaltamento di strutture", 3, 4,
          "Demolizione per parti secondo il programma dell'art. 151, procedendo dall'alto e senza "
          "indebolire le strutture portanti a valle; distanza della macchina dall'edificio adeguata "
          "all'altezza dell'elemento da demolire; con edifici alti uso di escavatori a braccio lungo "
          "(high reach) con contrappeso e carreggiata allargabile; non lavorare sotto sbalzi"),
        r("Caduta di materiale dall'alto o a livello", 3, 4,
          "Cabina con FOPS di livello II e protezione frontale, tetto eventualmente inclinabile nei "
          "modelli per demolizione; area di caduta interdetta a terra per un raggio pari almeno all'altezza "
          "della struttura; non sollevare la pinza carica sopra la cabina"),
        r("Ribaltamento della macchina", 2, 4,
          "Rispettare le tabelle di stabilità per pinza e sbraccio; piano di lavoro livellato e compattato, "
          "spesso realizzato con le macerie stesse; mai tirare elementi strutturali con la pinza; "
          + _ROPS + "; " + _MMT_ABILITAZIONE),
        r("Polveri e fibre", 4, 3,
          "Nebulizzazione continua con cannone ad acqua sul fronte di demolizione; cabina pressurizzata con "
          "filtri; bonifica preventiva dei materiali contenenti amianto (Titolo IX Capo III)",
          _DPI_POLVERI),
        r("Proiezione di schegge e frammenti", 3, 3,
          "Protezione frontale della cabina; nessun lavoratore a terra nella zona di frantumazione; "
          "teli o reti di contenimento verso le aree esterne",
          _DPI + ", occhiali protettivi"),
        _rumore("85-90 dB(A) nelle vicinanze"),
        _investimento("recinzione fissa dell'area di demolizione con accesso controllato"),
        _oleodinamica(),
    ], scheda_uso=scheda(
        "Escavatore idraulico, anche a braccio lungo, attrezzato con pinza frantumatrice o cesoia per la "
        "demolizione controllata di strutture in calcestruzzo armato, murature e acciaio.",
        ["verificare abilitazione e addestramento dell'operatore sulla configurazione da demolizione",
         "verificare le protezioni FOPS e frontali e la compatibilità della pinza con il braccio",
         "conoscere il programma delle demolizioni e la sequenza prevista",
         "accertare il distacco di gas, elettricità e acqua e la bonifica dell'amianto",
         "predisporre l'area interdetta e i sistemi di abbattimento delle polveri",
         "preparare un piano di lavoro stabile e livellato"],
        ["procedere dall'alto verso il basso, per piccole porzioni",
         "tenere la macchina perpendicolare al fronte e fuori dalla zona di caduta",
         "non tirare né spingere le strutture con la pinza",
         "sospendere il lavoro con vento forte o se il fronte mostra cedimenti imprevisti",
         "mantenere i contatti con il preposto a terra via radio o con segnali convenuti"],
        ["appoggiare la pinza a terra, lontano dalle macerie instabili",
         "controllare denti e lame, perni e tubazioni della pinza",
         "pulire filtri e cabina dalla polvere"],
        _SCHEDA_DPI_CONDUCENTE + ["facciale filtrante FFP3"])),

    "Terna (escavatore-caricatore)": attrezzatura(MACCHINA, rischi=[
        r("Ribaltamento della macchina", 2, 4,
          "Scavare solo con gli stabilizzatori abbassati su terreno portante e la pala anteriore appoggiata "
          "a terra; trasportare il carico con la pala bassa; non lavorare trasversalmente sui pendii; "
          "distanza dai cigli degli scavi; " + _ROPS + " (UNI EN 474-4); " + _MMT_ABILITAZIONE),
        _investimento("attenzione al cambio di posto di guida: prima di invertire il sedile fermare la "
                      "macchina e controllare l'area dalla parte verso cui ci si volta"),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Nessuno nel raggio del braccio retro o tra stabilizzatori e terreno; blocchi meccanici del "
          "braccio e della pala inseriti durante i trasferimenti e la manutenzione; leva di sicurezza dei "
          "comandi prima di scendere"),
        r("Contatto con sottoservizi e linee elettriche", 2, 4,
          "Planimetrie dei sottoservizi e tracciamento a terra; scavo a mano nell'ultimo tratto; " + _LINEE),
        r("Incidenti nella circolazione su strada", 2, 4,
          "Trasferimenti su strada con conducente munito di patente idonea, braccio retro bloccato in "
          "posizione di trasporto, benna anteriore vuota e chiusa, luci e girofaro accesi; rispetto del "
          "Codice della strada per le macchine operatrici"),
        _rumore("80-85 dB(A)"),
        _wbv(3),
        _oleodinamica(),
    ], scheda_uso=scheda(
        "Macchina gommata che riunisce una pala caricatrice anteriore e un escavatore posteriore con "
        "stabilizzatori, per scavi, carico e piccoli movimenti terra nei cantieri urbani e stradali.",
        ["verificare l'abilitazione dell'operatore (terne, Accordo Stato-Regioni 17 aprile 2025)",
         "controllare pneumatici, freni, sterzo, luci, stabilizzatori e blocchi di trasporto",
         "verificare cintura, ROPS/FOPS, girofaro e segnalatore di retromarcia",
         "individuare sottoservizi e linee aeree nell'area di lavoro",
         "verificare il bloccaggio degli attrezzi agli attacchi rapidi"],
        ["abbassare gli stabilizzatori e la pala prima di scavare con il braccio retro",
         "fermare la macchina prima di invertire il posto di guida",
         "trasportare il carico con la pala bassa e procedere a velocità moderata",
         "non trasportare persone in pala o sui gradini",
         "inserire i blocchi del braccio per i trasferimenti"],
        ["parcheggiare in piano con pala e benna a terra e freno di stazionamento inserito",
         "togliere la chiave e chiudere la cabina",
         "controllare livelli e perdite e annotare le anomalie"],
        _SCHEDA_DPI_CONDUCENTE)),

    "Minipala (skid loader)": attrezzatura(MACCHINA, rischi=[
        r("Ribaltamento della macchina", 2, 4,
          "Salire e scendere dai pendii con il lato più pesante a monte (in salita con la benna carica "
          "avanti, in discesa in retromarcia), benna bassa durante gli spostamenti; non superare il carico "
          "operativo nominale; " + _ROPS + " (UNI EN 474-3) e barra di sicurezza del sedile abbassata; "
          "operatore abilitato come per le pale caricatrici frontali (Accordo Stato-Regioni 17 aprile 2025)"),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Mai entrare o uscire dalla cabina con i bracci sollevati; puntello di sicurezza dei bracci "
          "inserito per qualsiasi intervento sotto di essi; comandi bloccati dalla barra di sicurezza "
          "sollevata; nessuno vicino ai bracci e alle ruote durante le manovre"),
        _investimento("la sterzatura a slittamento fa ruotare la macchina su sé stessa: delimitare l'area "
                      "intorno e non farvi sostare persone"),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Griglia di protezione anteriore e FOPS; forche e pinze con carico bloccato; non sollevare "
          "carichi instabili o lunghi; non sollevare il carico durante gli spostamenti"),
        _rumore("80-88 dB(A)"),
        _wbv(3),
        _gas_scarico("la minipala"),
    ], scheda_uso=scheda(
        "Caricatore compatto a ruote o cingoli con sterzatura a slittamento e bracci di sollevamento, "
        "usato con benna, forche, spazzola o altri attrezzi per movimentazioni e pulizie di cantiere.",
        ["verificare abilitazione e addestramento dell'operatore",
         "controllare barra di sicurezza, cintura, blocco dei comandi e cabina ROPS/FOPS",
         "verificare l'aggancio dell'attrezzo e il funzionamento del puntello dei bracci",
         "controllare pneumatici o cingoli, luci e segnalatore di retromarcia",
         "verificare portata del terreno e pendenze dei percorsi"],
        ["salire a bordo e scendere solo con i bracci abbassati e l'attrezzo a terra",
         "tenere l'attrezzo basso negli spostamenti",
         "rispettare il carico operativo nominale e il diagramma dell'attrezzo",
         "non far salire persone sull'attrezzo o sulla macchina",
         "non usarla in ambienti chiusi senza ricambio d'aria"],
        ["appoggiare l'attrezzo a terra, inserire il freno e sollevare la barra di sicurezza",
         "inserire il puntello dei bracci prima di interventi di manutenzione",
         "pulire la macchina e verificare perdite di olio"],
        _SCHEDA_DPI_CONDUCENTE)),

    "Bulldozer": attrezzatura(MACCHINA, rischi=[
        r("Ribaltamento della macchina", 2, 4,
          "Lavorare preferibilmente lungo la linea di massima pendenza; non avvicinarsi al ciglio di "
          "scarpate e rilevati non consolidati; spingere il materiale verso il bordo lasciandone uno "
          "strato come arresto; " + _ROPS + " (UNI EN 474-2, UNI EN ISO 3471); formazione e addestramento "
          "specifici dell'operatore (art. 73, comma 4), non essendo il bulldozer tra le macchine elencate "
          "dall'Accordo Stato-Regioni"),
        _investimento("ampia zona cieca davanti alla lama e dietro il ripper: nessuno a terra nel raggio "
                      "di lavoro, contatto visivo o radio con il preposto"),
        r("Seppellimento e sprofondamento", 1, 4,
          "Verifica preventiva della portanza del terreno, di cavità e di sottoservizi; non operare su "
          "rilevati appena formati vicino al bordo; distanza dai cigli degli scavi"),
        r("Vibrazioni al corpo intero", 3, 3,
          "Valutazione ai sensi dell'art. 202; sedile a sospensione regolato; cingoli in buono stato e "
          "tensionati; velocità ridotta sui terreni irregolari; limitazione e rotazione dei turni",
          "Calzature di sicurezza"),
        _rumore("85-95 dB(A) in cabina aperta"),
        r("Polveri e fibre", 3, 2,
          "Bagnatura delle piste e dei materiali; cabina chiusa e pressurizzata con filtri efficienti",
          _DPI_POLVERI),
        _incendio_rifornimento(),
    ], scheda_uso=scheda(
        "Trattore cingolato con lama anteriore e, spesso, ripper posteriore, per sbancamenti, spinta e "
        "stesa del terreno e preparazione di piani di posa.",
        ["verificare formazione e addestramento dell'operatore",
         "controllare cingoli, lama, ripper, tubi idraulici, freni, luci e segnalatore di retromarcia",
         "verificare ROPS/FOPS, cintura e vetri della cabina",
         "esaminare il terreno: pendenze, cigli, cavità, sottoservizi e linee aeree",
         "concordare con il preposto i segnali e l'area di lavoro"],
        ["allacciare la cintura e lavorare con porte chiuse",
         "non avvicinarsi ai cigli e lasciare un cordolo di materiale come arresto",
         "affrontare i pendii in linea di massima pendenza",
         "fermarsi se qualcuno entra nell'area di lavoro",
         "non salire o scendere dalla macchina in movimento"],
        ["parcheggiare in piano con lama e ripper appoggiati a terra",
         "pulire i cingoli dal fango e controllare la tensione",
         "pulire il vano motore e annotare le anomalie"],
        _SCHEDA_DPI_CONDUCENTE)),

    "Grader (livellatrice)": attrezzatura(MACCHINA, rischi=[
        _investimento("la lama centrale e la lunghezza del telaio riducono la visibilità laterale: "
                      "telecamere e specchi, nessun operatore a terra vicino alla lama"),
        r("Ribaltamento della macchina", 2, 4,
          "Non lavorare in prossimità del bordo di scarpate e fossi con la lama inclinata verso valle; "
          "velocità ridotta nelle curve; ruote anteriori inclinate per contrastare la spinta laterale "
          "secondo le istruzioni; " + _ROPS + " (UNI EN 474-8); formazione e addestramento specifici "
          "dell'operatore (art. 73, comma 4)"),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Nessuno tra lama e telaio o vicino all'articolazione centrale durante la sterzatura; lama "
          "appoggiata a terra e articolazione bloccata prima di interventi"),
        _traffico("nei lavori su strade aperte movieri o semaforo a monte e a valle"),
        _wbv(3),
        _rumore("80-88 dB(A)"),
        r("Polveri e fibre", 3, 2,
          "Bagnatura del materiale prima della livellatura; cabina chiusa e filtrata", _DPI_POLVERI),
    ], scheda_uso=scheda(
        "Macchina semovente a ruote con lama centrale orientabile, per la livellatura e la profilatura di "
        "piani di posa, fondazioni stradali e scarpate.",
        ["verificare formazione e addestramento dell'operatore",
         "controllare comandi della lama, articolazione, freni, luci, girofaro e retromarcia",
         "verificare ROPS, cintura, specchi e telecamere",
         "predisporre la segnaletica se si lavora su strada aperta"],
        ["mantenere la velocità adeguata alla visibilità e al fondo",
         "non far avvicinare persone alla lama",
         "lavorare lontano dal bordo di scarpate e fossi",
         "farsi assistere da un moviere nelle inversioni di marcia"],
        ["parcheggiare in piano con lama a terra e articolazione bloccata",
         "pulire e controllare i taglienti della lama"],
        _SCHEDA_DPI_CONDUCENTE)),

    "Dumper": attrezzatura(MACCHINA, rischi=[
        r("Ribaltamento della macchina", 3, 4,
          "Percorsi con pendenze entro i limiti del fabbricante e senza bordi cedevoli; scarico a distanza "
          "dal ciglio dello scavo o con fermo di arresto delle ruote (cordolo, trave); cassone abbassato "
          "durante la marcia; in discesa marcia con il cassone carico a monte; " + _ROPS + " (UNI EN 474-6); "
          "per i dumper cingolati operatore abilitato (autoribaltabili a cingoli, Accordo Stato-Regioni "
          "17 aprile 2025), per quelli gommati formazione e addestramento (art. 73, comma 4)"),
        _investimento("con il cassone carico la visibilità anteriore è ridotta: preferire dumper con "
                      "posto di guida girevole o telecamera e procedere in retromarcia solo se assistiti"),
        r("Trasporto improprio di persone", 2, 4,
          "Divieto di trasportare persone nel cassone o sui parafanghi, da segnalare con cartello a bordo"),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Non caricare oltre la portata e il colmo del cassone; carico ben distribuito; non sostare a "
          "fianco del dumper durante il carico con escavatore o pala"),
        _wbv(3),
        _rumore("80-90 dB(A)"),
        _gas_scarico("il dumper"),
    ], scheda_uso=scheda(
        "Autoribaltabile da cantiere gommato o cingolato, con cassone ribaltabile anteriore, laterale o "
        "girevole, per il trasporto di terre, inerti e materiali di risulta sulle piste interne.",
        ["verificare abilitazione (cingolati) o addestramento (gommati) dell'operatore",
         "controllare freni, sterzo, comandi del cassone, luci, girofaro e segnalatore di retromarcia",
         "verificare la presenza di ROPS e cintura",
         "verificare pendenze e larghezza dei percorsi e predisporre i fermi di scarico vicino agli scavi"],
        ["allacciare la cintura e tenere il cassone abbassato in marcia",
         "affrontare le rampe in linea di massima pendenza e senza curvare",
         "scaricare solo in piano, con il fermo di arresto e senza persone dietro",
         "non trasportare persone",
         "farsi guidare da un moviere se il carico limita la visibilità"],
        ["parcheggiare in piano con cassone abbassato e freno inserito",
         "pulire il cassone e controllare perdite di olio"],
        _SCHEDA_DPI_CONDUCENTE)),

    # ------------------------------------------------------------------ sollevamento
    "Autocarro con cestello": attrezzatura(MACCHINA, rischi=[
        r("Caduta dall'alto", 2, 4,
          "Operatore abilitato per PLE con stabilizzatori (Accordo Stato-Regioni 17 aprile 2025); imbracatura "
          "con cordino corto agganciata al punto di ancoraggio del cestello; cancelletto chiuso; vietato "
          "salire sui parapetti o usare scale nel cestello; vietato uscire dal cestello in quota salvo "
          "procedure espressamente previste dal fabbricante",
          "Casco con sottogola, imbracatura, cordino con assorbitore o di trattenuta, calzature di sicurezza"),
        r("Ribaltamento della macchina", 2, 4,
          "Stabilizzatori completamente estesi su piastre di ripartizione e terreno portante, con verifica "
          "della bolla di livello; rispetto di portata del cestello e area di lavoro; sospensione con vento "
          "oltre il limite di targa (di solito 12,5 m/s); verifiche periodiche annuali (Allegato VII) e "
          "macchina conforme a UNI EN 280"),
        r("Elettrocuzione", 2, 4,
          _LINEE + "; nei lavori su impianti elettrici usare cestelli isolati e procedure CEI EN 50110 / "
          "CEI 11-27",
          "Casco, guanti dielettrici (lavori elettrici), calzature di sicurezza"),
        r("Urti, colpi, impatti e compressioni", 2, 4,
          "Nel muovere il cestello osservare gli ostacoli nella direzione di movimento; comandi con "
          "pulsante di abilitazione; dispositivo anti-schiacciamento dell'operatore dove presente; "
          "operatore a terra in grado di azionare la discesa di emergenza"),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Area sotto il cestello delimitata; attrezzi legati e materiali dentro il cestello; non usare la "
          "PLE per sollevare carichi appesi"),
        _traffico("la zona degli stabilizzatori e la proiezione a terra del cestello vanno incluse nell'area "
                  "delimitata"),
    ], scheda_uso=scheda(
        "Piattaforma di lavoro mobile elevabile montata su autocarro, con braccio articolato o telescopico "
        "e cestello per una o più persone, per manutenzioni e lavori in quota.",
        ["verificare abilitazione dell'operatore, verifica periodica (Allegato VII) e registro di controllo",
         "controllare comandi in cestello e a terra, discesa di emergenza, parapetti e punti di ancoraggio",
         "verificare portanza del terreno, pendenza, vento e linee elettriche vicine",
         "estendere gli stabilizzatori su piastre e livellare la macchina",
         "delimitare l'area di lavoro e segnalare l'ingombro sulla strada",
         "accertare che a terra resti una persona informata sulle manovre di emergenza"],
        ["agganciare l'imbracatura al punto di ancoraggio del cestello",
         "non superare la portata e il numero di persone di targa",
         "non sporgersi né salire sui parapetti",
         "muovere il braccio guardando nella direzione di movimento",
         "scendere se il vento supera il limite del fabbricante o in caso di temporale",
         "non spostare l'autocarro con persone nel cestello"],
        ["riportare braccio e cestello in posizione di trasporto e ritirare gli stabilizzatori",
         "togliere la chiave e annotare le anomalie nel registro"],
        ["casco con sottogola", "imbracatura", "cordino con assorbitore", "calzature di sicurezza",
         "guanti", "indumenti ad alta visibilità"])),

    "Sollevatore telescopico": attrezzatura(MACCHINA, rischi=[
        r("Ribaltamento della macchina", 3, 4,
          "Operatore abilitato per carrelli elevatori telescopici (o rotativi) secondo l'Accordo "
          "Stato-Regioni 17 aprile 2025; rispetto del diagramma di carico per altezza e sbraccio con "
          "limitatore di momento attivo (UNI EN 1459); stabilizzatori estesi dove previsti; spostamenti con "
          "braccio rientrato e carico basso; livellamento del telaio prima di sollevare; verifiche "
          "periodiche annuali (Allegato VII); " + _ROPS),
        r("Caduta di materiale dall'alto o a livello", 3, 3,
          "Forche e attrezzi riconosciuti dalla macchina e indicati nel manuale; carichi pallettizzati e "
          "legati; nessuno sotto il carico sollevato; accessori di sollevamento marcati e verificati "
          "trimestralmente quando si usa il gancio (Allegato VI punto 3.1.2)"),
        _investimento("visibilità laterale destra limitata dal braccio: specchi e telecamera, moviere "
                      "nelle manovre in spazi ristretti"),
        r("Elettrocuzione", 2, 4, _LINEE),
        r("Caduta dall'alto", 1, 4,
          "Sollevare persone solo con piattaforma porta-persone prevista dal fabbricante, riconosciuta "
          "dalla macchina e con relativa abilitazione; mai su forche o pallet",
          "Casco con sottogola, imbracatura, cordino con assorbitore"),
        _wbv(2),
        _rumore("78-85 dB(A)"),
    ], scheda_uso=scheda(
        "Carrello semovente a braccio telescopico, fisso o rotativo, per il sollevamento e la "
        "movimentazione di materiali in cantiere con forche, benna, gancio o altri attrezzi.",
        ["verificare abilitazione dell'operatore e verifica periodica annuale (Allegato VII)",
         "controllare limitatore di momento, comandi, freni, pneumatici, stabilizzatori e luci",
         "verificare il bloccaggio dell'attrezzo e il riconoscimento da parte del sistema di controllo",
         "verificare portanza e pendenza del terreno, ostacoli e linee elettriche",
         "conoscere peso e baricentro del carico"],
        ["livellare il telaio e abbassare gli stabilizzatori prima di sfilare il braccio",
         "spostarsi con braccio rientrato e carico a 30-40 cm da terra",
         "non escludere il limitatore di carico",
         "non far sostare persone sotto il carico",
         "sospendere il lavoro con vento oltre il limite del fabbricante"],
        ["rientrare il braccio e appoggiare l'attrezzo a terra",
         "parcheggiare in piano con freno inserito e chiave tolta",
         "annotare anomalie e controlli nel registro"],
        _SCHEDA_DPI_CONDUCENTE)),

    "Carrello elevatore": attrezzatura(MACCHINA, rischi=[
        r("Ribaltamento della macchina", 3, 4,
          "Operatore abilitato per carrelli industriali semoventi (Accordo Stato-Regioni 17 aprile 2025); "
          "uso su superfici piane e compatte, o carrello fuoristrada per il cantiere; marcia con forche "
          "basse e montante inclinato all'indietro; nessuna curva con il carico sollevato; rispetto della "
          "targa di portata (UNI EN ISO 3691-1); cintura o cabina chiusa sempre utilizzate"),
        _investimento("dispositivi luminosi di avvertimento a pavimento (blue spot) e segnalatore acustico; "
                      "percorsi separati da quelli pedonali; precedenza ai pedoni"),
        r("Caduta di materiale dall'alto o a livello", 3, 3,
          "Tettuccio di protezione integro; griglia reggicarico; carichi stabili, centrati e legati; "
          "nessuno sotto le forche sollevate"),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Non sporgere mani o piedi dall'ingombro del carrello; nessuno tra montante e cabina; "
          "mai usare le forche per sollevare persone"),
        _gas_scarico("carrelli a motore termico o a GPL"),
        r("Incendio ed esplosione", 1, 3,
          "Sostituzione delle bombole di GPL all'aperto, a motore spento e senza fiamme; carica delle "
          "batterie in area ventilata e lontana da fonti di innesco; estintore nei pressi",
          _DPI),
    ], scheda_uso=scheda(
        "Carrello industriale semovente a montante verticale con forche, elettrico o a motore termico, per "
        "lo scarico e la movimentazione di materiali pallettizzati nelle aree di deposito.",
        ["verificare abilitazione dell'operatore",
         "controllare forche, catene del montante, freni, sterzo, avvisatori e luci",
         "verificare che i percorsi siano piani, sgombri e di portata adeguata",
         "conoscere il peso del carico e confrontarlo con la targa di portata"],
        ["inserire le forche fino in fondo sotto il carico",
         "procedere con il carico basso e il montante inclinato indietro",
         "procedere in retromarcia se il carico limita la visibilità",
         "affrontare le rampe con il carico rivolto a monte",
         "non trasportare persone"],
        ["abbassare le forche a terra, inserire il freno e togliere la chiave",
         "mettere in carica le batterie o rifornire in area dedicata"],
        ["calzature di sicurezza", "guanti", "indumenti ad alta visibilità", "casco"])),

    "Montacarichi a cremagliera": attrezzatura(MACCHINA, rischi=[
        r("Caduta dall'alto", 2, 4,
          "Cancelli di piano con interblocco elettromeccanico che impedisce l'apertura con piattaforma "
          "assente; parapetti sui lati della piattaforma; ai piani impalcati di sbarco con parapetti; "
          "trasporto di persone solo con apparecchio per persone e materiali (UNI EN 12159), altrimenti "
          "divieto segnalato a ogni piano (UNI EN 12158-1)",
          "Casco, calzature di sicurezza, imbracatura (montaggio e smontaggio)"),
        r("Caduta di materiale dall'alto o a livello", 2, 4,
          "Recinzione alla base alta almeno 2 m con porta interbloccata; tettoia di protezione sopra i "
          "posti di carico; carichi stabili, contenuti in cassoni o legati ed entro la portata di targa"),
        r("Crollo o ribaltamento di strutture", 1, 4,
          "Montaggio da personale formato secondo le istruzioni del fabbricante; base su fondazione "
          "dimensionata; ancoraggi alla struttura agli interassi prescritti; dispositivo di sicurezza "
          "paracadute provato a ogni montaggio e periodicamente; finecorsa di extracorsa; verifiche "
          "periodiche annuali (Allegato VII) e prima verifica INAIL"),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Nessuno nel vano di corsa o sotto la piattaforma; protezioni di pignone e cremagliera; manutenzione "
          "con l'apparecchio fermo, alimentazione sezionata e piattaforma a terra"),
        r("Elettrocuzione", 1, 4,
          "Alimentazione da quadro di cantiere con interruttore differenziale; collegamento all'impianto di "
          "terra; cavo di alimentazione guidato e protetto",
          _DPI),
    ], scheda_uso=scheda(
        "Apparecchio di sollevamento da cantiere a piattaforma guidata su colonna a cremagliera ancorata "
        "all'edificio o al ponteggio, per il trasporto verticale dei materiali ai piani.",
        ["verificare l'esito della verifica periodica (Allegato VII) e il libretto con il montaggio",
         "controllare ancoraggi, recinzione di base, cancelli di piano e interblocchi",
         "provare finecorsa, pulsante di arresto di emergenza e comandi",
         "verificare che i piani di sbarco abbiano parapetti e superfici libere",
         "esporre portata e divieto di trasporto di persone ove previsto"],
        ["caricare entro la portata, con il carico distribuito e fermato",
         "azionare l'apparecchio solo con cancelli chiusi",
         "non sporgersi nel vano di corsa né salire sulla piattaforma se non consentito",
         "sospendere l'uso con vento oltre il limite del fabbricante",
         "segnalare subito ogni anomalia degli interblocchi"],
        ["riportare la piattaforma a terra e sezionare l'alimentazione",
         "chiudere i cancelli e togliere la chiave dei comandi",
         "pulire e lubrificare la cremagliera secondo il libretto"],
        ["casco", "calzature di sicurezza", "guanti"])),

    # ------------------------------------------------------------------ servizi di cantiere
    "Motocompressore": attrezzatura(MACCHINA, rischi=[
        r("Getti e schizzi", 2, 3,
          "Tubi per aria compressa adatti alla pressione massima, con raccordi a innesto di sicurezza e "
          "cavetti anti-frusta (whip check) sui collegamenti; scaricare la pressione prima di staccare gli "
          "utensili; mai dirigere il getto verso persone o per pulire indumenti e pelle",
          _DPI + ", occhiali protettivi"),
        r("Scoppio di componenti in pressione", 1, 4,
          "Valvola di sicurezza e manometro integri e non manomessi; serbatoio separatore controllato e "
          "sottoposto alle verifiche previste dal D.M. 329/2004 quando ricorrono le soglie; macchina "
          "conforme a UNI EN 1012-1"),
        _rumore("oltre 85 dB(A) a 1 m nei modelli non silenziati",
                "motocompressore silenziato con cofani chiusi, posizionato lontano dai posti di lavoro"),
        _gas_scarico("il motocompressore"),
        _incendio_rifornimento("nessun materiale infiammabile vicino allo scarico"),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Traino solo con veicolo e gancio idonei; ruote bloccate con cunei e freno di stazionamento "
          "in sosta; sollevamento solo dal golfare previsto"),
    ], scheda_uso=scheda(
        "Compressore d'aria azionato da motore a combustione, su carrello trainabile, per alimentare "
        "martelli, perforatori, sabbiatrici e altri utensili pneumatici.",
        ["posizionare il compressore in piano, all'aperto e lontano da scavi e aperture degli edifici",
         "bloccare le ruote e inserire il freno di stazionamento",
         "controllare livelli, valvola di sicurezza, manometro e tubi",
         "collegare i tubi con innesti di sicurezza e cavetti anti-frusta"],
        ["tenere chiusi i cofani fonoassorbenti",
         "non superare la pressione d'esercizio degli utensili",
         "chiudere la valvola e scaricare l'aria prima di cambiare utensile",
         "spegnere il motore per il rifornimento"],
        ["chiudere le valvole e scaricare la pressione residua",
         "scaricare la condensa dal serbatoio e controllare i filtri"],
        ["otoprotettori", "guanti", "calzature di sicurezza", "occhiali protettivi"])),

    "Gruppo elettrogeno": attrezzatura(MACCHINA, rischi=[
        r("Elettrocuzione", 2, 4,
          "Gruppo conforme a UNI ISO 8528-13; collegamento a terra o sistema di protezione secondo le "
          "istruzioni del fabbricante e la CEI 64-8 Sezione 704; prese protette da interruttore "
          "differenziale da 30 mA; cavi per posa mobile (H07RN-F o equivalenti) integri; quadro di "
          "cantiere a valle se si alimentano più utenze; collegamento a impianti fissi solo con "
          "commutatore che impedisca il ritorno in rete",
          _DPI),
        _gas_scarico("il gruppo elettrogeno"),
        _rumore("oltre 80 dB(A) nei pressi dei modelli aperti",
                "preferire gruppi insonorizzati e collocarli lontano dalle postazioni"),
        _incendio_rifornimento("eventuale serbatoio esterno in vasca di contenimento"),
        r("Ustioni", 2, 2,
          "Non toccare marmitta e testata del motore caldo; carter e cofani di protezione al loro posto",
          "Guanti"),
    ], scheda_uso=scheda(
        "Generatore di energia elettrica azionato da motore a combustione, portatile o su carrello, per "
        "alimentare utensili e impianti dove manca la rete.",
        ["posizionarlo all'aperto, in piano, lontano da aperture, scavi e materiali infiammabili",
         "eseguire il collegamento di terra o la protezione indicata dal fabbricante",
         "verificare differenziali, prese e cavi di collegamento",
         "controllare livelli di olio e carburante a motore freddo"],
        ["non sovraccaricare il gruppo oltre la potenza di targa",
         "non lasciare cavi su vie di transito senza protezione",
         "spegnere il motore per il rifornimento",
         "non coprire il gruppo né ostruire le prese d'aria"],
        ["staccare le utenze prima di spegnere",
         "lasciar raffreddare prima di coprirlo o caricarlo sul mezzo"],
        ["otoprotettori", "guanti", "calzature di sicurezza"])),

    # ------------------------------------------------------------------ macchine stradali
    "Scarificatrice (fresa stradale)": attrezzatura(MACCHINA, rischi=[
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Carter del tamburo fresante chiuso durante il lavoro; tamburo fermo e chiave tolta per il cambio "
          "dei denti; arresti di emergenza sui posti di comando e a terra (UNI EN 500-1 e UNI EN 500-2); nessuno "
          "vicino al nastro caricatore in movimento"),
        r("Polveri e fibre", 4, 3,
          "Impianto di nebulizzazione sul tamburo sempre in funzione (o aspirazione); valutazione della "
          "silice cristallina respirabile; verifica preliminare di eventuale catrame (IPA) nelle "
          "pavimentazioni vecchie",
          _DPI_POLVERI),
        _investimento("coordinare l'avanzamento con l'autocarro di carico: autista a bordo e fermo durante "
                      "il carico, segnali convenuti con l'operatore del nastro"),
        _traffico(),
        r("Proiezione di schegge e frammenti", 3, 2,
          "Paraspruzzi e bandelle al loro posto; nastro caricatore orientato sul cassone; nessuno a "
          "terra davanti al nastro o vicino al tamburo",
          _DPI + ", occhiali protettivi"),
        _rumore("90-100 dB(A) a terra vicino al tamburo"),
        _wbv(3),
    ], scheda_uso=scheda(
        "Macchina stradale semovente con tamburo fresante e nastro caricatore, per la rimozione degli "
        "strati di pavimentazione bituminosa o in calcestruzzo.",
        ["verificare carter, arresti di emergenza, nastro e impianto di nebulizzazione",
         "controllare usura e fissaggio dei denti a macchina ferma",
         "predisporre la segnaletica del cantiere stradale",
         "rilevare chiusini, cordoli e sottoservizi superficiali da evitare",
         "concordare i segnali con gli autisti degli autocarri"],
        ["tenere attiva la nebulizzazione per tutta la fresatura",
         "non avvicinarsi al tamburo o al nastro in movimento",
         "regolare l'avanzamento in base al riempimento del cassone",
         "mantenere a distanza gli operatori a terra dalla zona di proiezione"],
        ["sollevare il tamburo, arrestare la macchina e togliere la chiave",
         "pulire nastro e tamburo a macchina ferma",
         "controllare i denti e annotare le anomalie"],
        _SCHEDA_DPI_A_TERRA + ["facciale filtrante FFP3"])),

    "Spazzatrice stradale": attrezzatura(MACCHINA, rischi=[
        _investimento("velocità ridotta nelle aree con operai a terra"),
        _traffico("macchina con pannello luminoso di segnalazione nelle pulizie a fine lavori"),
        r("Polveri e fibre", 3, 2,
          "Bagnatura delle spazzole tramite impianto ad acqua; aspirazione con filtri efficienti; non "
          "spazzare a secco materiali da fresatura o demolizione",
          _DPI_POLVERI),
        r("Cesoiamenti e stritolamenti", 1, 4,
          "Spazzole e bocca di aspirazione ferme e motore spento per la rimozione di ostruzioni; "
          "contenitore ribaltato bloccato con il puntello prima di operare sotto di esso (UNI EN 13019)"),
        r("Proiezione di schegge e frammenti", 2, 2,
          "Carter e bandelle paraspruzzi integri; nessuno vicino alle spazzole laterali in rotazione",
          _DPI + ", occhiali protettivi"),
        _rumore("80-88 dB(A)"),
    ], scheda_uso=scheda(
        "Macchina semovente con spazzole e sistema di aspirazione per la pulizia della carreggiata dopo "
        "fresature, scavi e lavori stradali.",
        ["controllare spazzole, impianto ad acqua, luci, lampeggianti e retromarcia",
         "verificare il puntello del contenitore",
         "concordare percorso e segnaletica con il preposto",
         "verificare il livello dell'acqua per l'abbattimento delle polveri"],
        ["tenere l'impianto ad acqua in funzione",
         "procedere a bassa velocità vicino agli operatori",
         "fermare spazzole e motore prima di liberare ostruzioni",
         "non avvicinarsi a terra alle spazzole laterali in rotazione"],
        ["svuotare il contenitore nell'area prevista con puntello inserito",
         "lavare e controllare spazzole e filtri"],
        _SCHEDA_DPI_CONDUCENTE + ["facciale filtrante FFP2"])),

    "Macchina tracciatrice per segnaletica": attrezzatura(MACCHINA, rischi=[
        _traffico("lavorare preferibilmente con chiusura della corsia e veicolo di protezione con "
                  "segnale luminoso a seguire; nelle ore notturne illuminazione dell'area"),
        r("Rischio chimico", 3, 2,
          "Schede di sicurezza delle vernici, dei diluenti e dei prodotti bicomponenti consultate e "
          "valutate (Titolo IX); preferire vernici all'acqua; operatore sopravvento; ricarica dei serbatoi "
          "lontano da fonti di innesco; lavaggio degli ugelli in contenitori chiusi",
          "Guanti in lattice o nitrile, occhiali protettivi, maschera con filtro specifico per vapori organici"),
        r("Ustioni", 2, 3,
          "Per i termoplastici a caldo: caldaia e bruciatore integri, bombole di GPL fissate, tubi e "
          "riduttori controllati; non aprire la caldaia in temperatura; carica del materiale con guanti e "
          "visiera",
          "Guanti per saldatura, visiera protettiva, indumenti protettivi"),
        r("Incendio ed esplosione", 1, 4,
          "Bombole di GPL in posizione verticale e fissate; prova di tenuta dei raccordi; estintore a "
          "bordo; divieto di fumare; nessuna fiamma durante la ricarica dei solventi"),
        r("Getti e schizzi", 2, 2,
          "Pistole a spruzzo puntate solo sulla pavimentazione; scaricare la pressione prima di "
          "pulire gli ugelli; nessuno vicino alla barra di spruzzatura",
          "Occhiali protettivi, guanti in lattice o nitrile"),
        _rumore("75-85 dB(A)"),
    ], scheda_uso=scheda(
        "Macchina semovente o a spinta per la stesa della segnaletica orizzontale con vernici, "
        "termoplastici o bicomponenti e perline di vetro.",
        ["predisporre la chiusura della corsia e la segnaletica di cantiere",
         "consultare le schede di sicurezza dei prodotti",
         "controllare serbatoi, pistole, tubi, bombole e bruciatori",
         "verificare estintore, luci e lampeggianti"],
        ["lavorare sopravvento rispetto alle nebbie di vernice",
         "non lasciare la carreggiata fuori dall'area protetta",
         "scaricare la pressione prima di intervenire sugli ugelli",
         "non fumare e non usare fiamme durante la ricarica"],
        ["pulire pistole e circuiti con i solventi previsti, in contenitori chiusi",
         "chiudere le bombole e raccogliere i residui come rifiuti"],
        ["indumenti ad alta visibilità", "guanti in lattice o nitrile", "occhiali protettivi",
         "maschera con filtro specifico", "calzature di sicurezza"])),

    # ------------------------------------------------------------------ perforazione e fondazioni
    "Battipalo (infissione di pali e barriere)": attrezzatura(MACCHINA, rischi=[
        _rumore("oltre 95 dB(A) vicino alla massa battente",
                "battipalo con cuffia insonorizzante, area di rispetto per i non addetti"),
        r("Cesoiamenti e stritolamenti", 3, 4,
          "Posizionare e guidare il palo solo con la massa battente ferma e a fine corsa; non tenere mai "
          "le mani tra palo e guida o sotto la massa; comandi ad azione mantenuta con arresto di emergenza; "
          "conformità a UNI EN 16228-1 e -4"),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Pali sollevati con dispositivi di presa previsti dal fabbricante; nessuno sotto il palo in "
          "sollevamento; verifica del cappello di battuta e della testa del palo per evitare il distacco "
          "di frammenti"),
        r("Ribaltamento della macchina", 2, 4,
          "Macchina su terreno portante e livellato; antenna (mast) entro i limiti di inclinazione del "
          "fabbricante; spostamenti con mast abbassato o nella posizione di trasporto"),
        _traffico("posa delle barriere su strade aperte con chiusura della corsia e veicolo di protezione"),
        r("Contatto con sottoservizi e linee elettriche", 2, 4,
          "Prima dell'infissione verificare con gli enti gestori e con cercaservizi la presenza di cavi e "
          "tubazioni lungo l'asse dei pali; " + _LINEE),
        r("Vibrazioni al sistema mano-braccio", 2, 2,
          "Non tenere le mani sul palo durante la battuta; manutenzione degli smorzatori",
          "Guanti antivibrazioni"),
    ], scheda_uso=scheda(
        "Macchina semovente o montata su escavatore con massa battente o vibratore su guida, per "
        "l'infissione di pali, profilati di barriere stradali e paletti di recinzione.",
        ["individuare sottoservizi e linee aeree lungo l'allineamento",
         "predisporre la segnaletica stradale e l'area di rispetto",
         "controllare guida, massa battente, cappello, tubi idraulici e arresti di emergenza",
         "posizionare la macchina in piano su terreno portante"],
        ["avvicinare il palo e centrarlo solo con la massa ferma",
         "allontanare le mani dal palo prima di avviare la battuta",
         "tenere a distanza le persone non addette",
         "sospendere la battuta se il palo devia o incontra ostacoli"],
        ["abbassare la massa a fine corsa e riportare la guida in posizione di trasporto",
         "controllare usura del cappello e fissaggi"],
        _SCHEDA_DPI_A_TERRA)),

    "Macchina perforatrice per pali": attrezzatura(MACCHINA, rischi=[
        r("Ribaltamento della macchina", 2, 4,
          "Piano di lavoro progettato e verificato per le pressioni dei cingoli e degli stabilizzatori "
          "(piattaforma di lavoro); antenna entro i limiti di inclinazione; traslazioni con l'utensile "
          "basso e l'antenna nella configurazione di trasferimento; conformità a UNI EN 16228-1 e -2 o -4"),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Zona di esclusione intorno all'asta e all'utensile in rotazione, delimitata e controllata "
          "dall'operatore; nessuno vicino alla tavola rotary e alle aste kelly; dispositivi di arresto "
          "di emergenza e protezioni previste dal fabbricante; aggiunta di aste e utensili con rotazione "
          "ferma"),
        r("Caduta dall'alto", 2, 4,
          "Fori non in getto coperti con lamiere o protetti con parapetti; tubi camicia sporgenti dal "
          "piano; percorsi pedonali lontani dai fori",
          _DPI),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Svuotamento dell'utensile con nessuno nelle vicinanze; pulizia dell'elica dai detriti prima "
          "della risalita; funi dell'argano e ganci verificati trimestralmente; sollevamento delle gabbie "
          "d'armatura con accessori idonei"),
        r("Contatto con sottoservizi e linee elettriche", 1, 4,
          "Verifica preliminare dei sottoservizi con gli enti gestori; " + _LINEE),
        _rumore("85-95 dB(A)"),
        _oleodinamica(),
    ], scheda_uso=scheda(
        "Macchina cingolata con antenna e tavola di rotazione, per l'esecuzione di pali trivellati di "
        "grande diametro con aste kelly, elica continua o tubo forma.",
        ["verificare il progetto e la portanza della piattaforma di lavoro",
         "controllare antenna, funi, argani, tavola rotary e arresti di emergenza",
         "individuare sottoservizi e linee aeree",
         "delimitare la zona di esclusione intorno all'utensile",
         "predisporre coperture o protezioni per i fori"],
        ["non entrare nella zona di esclusione con l'utensile in rotazione",
         "pulire e scaricare l'utensile senza persone nelle vicinanze",
         "coprire il foro durante le pause e a fine turno",
         "comunicare con gli operatori a terra con segnali convenuti",
         "sospendere il lavoro con vento oltre i limiti del fabbricante"],
        ["abbassare l'utensile a terra e riportare l'antenna in posizione di riposo",
         "controllare funi e tubi idraulici e annotare le anomalie",
         "proteggere i fori aperti"],
        _SCHEDA_DPI_A_TERRA)),

    "Sonda di perforazione (micropali, tiranti, sondaggi)": attrezzatura(MACCHINA, rischi=[
        r("Cesoiamenti e stritolamenti", 3, 4,
          "Protezioni mobili interbloccate o dispositivi sensibili intorno alla testa di rotazione e alle "
          "morse (UNI EN 16228-1 e -2); arresti di emergenza raggiungibili; aggiunta e svitatura delle aste con "
          "rotazione ferma o in modalità ridotta prevista dal fabbricante; nessun indumento svolazzante; "
          "addestramento specifico degli addetti (art. 73, comma 4)"),
        r("Proiezione di schegge e frammenti", 3, 2,
          "Deviatore o preventer sul boccaforo per lo spurgo con aria; nessuno davanti al foro durante la "
          "perforazione a rotopercussione; tubi dell'aria con cavetti anti-frusta",
          _DPI + ", occhiali protettivi o visiera protettiva"),
        r("Polveri e fibre", 3, 3,
          "Perforazione ad acqua o con captazione delle polveri sul boccaforo; valutazione della silice "
          "cristallina respirabile",
          _DPI_POLVERI),
        r("Ribaltamento della macchina", 2, 4,
          "Macchina stabilizzata su terreno portante; su ponteggi o pendii, ancoraggio della sonda e "
          "verifica del supporto da parte di un tecnico; mast nella posizione di trasporto negli "
          "spostamenti"),
        _rumore("90-100 dB(A) con rotopercussione"),
        r("Getti e schizzi", 2, 2,
          "Iniezione delle miscele con tubi e raccordi idonei alla pressione; scaricare la pressione prima "
          "di aprire i circuiti; fluidi cementizi trattati come irritanti",
          "Occhiali protettivi, guanti in lattice o nitrile"),
        r("Movimentazione manuale dei carichi", 3, 2,
          "Caricatore automatico delle aste dove disponibile; sollevamento delle aste pesanti con "
          "argano; lavoro in coppia"),
    ], scheda_uso=scheda(
        "Perforatrice cingolata compatta a rotazione o rotopercussione, per micropali, tiranti, chiodi, "
        "drenaggi e sondaggi geognostici.",
        ["verificare protezioni della testa di rotazione, morse e arresti di emergenza",
         "controllare tubi idraulici e dell'aria con cavetti anti-frusta",
         "stabilizzare la macchina e verificare il terreno o il supporto",
         "verificare sottoservizi e linee elettriche",
         "predisporre l'abbattimento delle polveri"],
        ["non avvicinarsi alle aste in rotazione",
         "aggiungere le aste solo con rotazione ferma",
         "tenersi fuori dalla traiettoria del getto di spurgo",
         "comunicare con l'operatore ai comandi prima di ogni manovra"],
        ["abbassare il mast, scaricare la pressione dei circuiti e fermare il motore",
         "lavare le linee di iniezione e riporre le aste in rastrelliera"],
        _SCHEDA_DPI_A_TERRA + ["facciale filtrante FFP3"])),

    "Impianto per jet grouting": attrezzatura(MACCHINA, rischi=[
        r("Getti e schizzi", 3, 4,
          "Getto ad altissima pressione (fino a 400-600 bar): tubi, raccordi e girevoli certificati e "
          "controllati a ogni turno, con cavetti anti-frusta; zona di esclusione intorno alle linee e "
          "alla testa; nessun intervento sulle linee senza scarico della pressione; in caso di ferita da "
          "iniezione ricovero immediato anche se la lesione sembra lieve (conformità a UNI EN 16228-6)",
          "Occhiali a maschera o visiera protettiva, guanti in lattice o nitrile, indumenti impermeabili"),
        r("Rischio chimico", 3, 2,
          "Miscela cementizia alcalina: evitare il contatto con pelle e occhi, lavaocchi disponibile vicino "
          "alla centrale di miscelazione; carico dei silos con sistemi chiusi per limitare la polvere di "
          "cemento",
          "Guanti in lattice o nitrile, occhiali a maschera, facciale filtrante FFP2"),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Protezioni sulla testa di rotazione e morse della perforatrice; aggiunta delle aste con "
          "rotazione ferma; arresti di emergenza sia sulla perforatrice sia sulla pompa"),
        r("Sollevamento del terreno e danni a strutture vicine", 1, 4,
          "Monitoraggio del rifluimento dal foro e delle strutture adiacenti; interruzione del getto in "
          "caso di blocco del rifluimento; verifica preventiva di sottoservizi e cantine"),
        _rumore("85-95 dB(A) vicino alla pompa"),
        r("Scivolamenti e cadute a livello", 3, 2,
          "Raccolta e smaltimento del refluo in vasche; percorsi puliti e drenati; passerelle sulle zone "
          "fangose",
          "Stivali di sicurezza"),
    ], scheda_uso=scheda(
        "Insieme di perforatrice, pompa ad altissima pressione e centrale di miscelazione per il "
        "consolidamento del terreno con getti di miscela cementizia (colonne di jet grouting).",
        ["controllare pressostati, valvole di sicurezza, tubi e raccordi ad alta pressione",
         "installare i cavetti anti-frusta e delimitare la zona delle linee",
         "verificare la comunicazione tra operatore della pompa e della perforatrice",
         "predisporre lavaocchi, vasche di raccolta del refluo e percorsi",
         "verificare sottoservizi e strutture vicine"],
        ["mettere in pressione solo con la testa nel foro",
         "non avvicinarsi alle linee in pressione",
         "sorvegliare il rifluimento dal foro e fermare il getto se si arresta",
         "scaricare la pressione prima di ogni intervento"],
        ["lavare pompa, linee e aste con acqua",
         "gestire il refluo come rifiuto",
         "controllare usura di ugelli e tubi"],
        ["casco", "occhiali a maschera", "visiera protettiva", "guanti in lattice o nitrile",
         "indumenti impermeabili", "stivali di sicurezza", "otoprotettori"])),

    "Macchina per perforazione orizzontale controllata (TOC)": attrezzatura(MACCHINA, rischi=[
        r("Elettrocuzione", 2, 4,
          "Ricerca dei sottoservizi con gli enti gestori, cercaservizi e georadar, e saggi a vista nei "
          "punti di incrocio; macchina dotata di sistema di allarme per contatto con cavi elettrici "
          "(strike alert) e collegamento a picchetto di terra; operatori su tappetini equipotenziali "
          "collegati alla macchina; in caso di allarme restare sulla macchina o sul tappetino; conformità "
          "a UNI EN 16228-1 e -3",
          "Guanti dielettrici, calzature di sicurezza isolanti, casco"),
        r("Incendio ed esplosione", 1, 4,
          "Rischio di intercettare condotte del gas: tracciato progettato con distanze di rispetto, "
          "localizzazione continua della testa, saggi; in caso di danneggiamento arresto, allontanamento "
          "e chiamata al gestore"),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Morse e aste in rotazione protette e interdette durante la spinta e il tiro; caricatore "
          "automatico delle aste; aggiunta e svitatura con rotazione ferma"),
        r("Getti e schizzi", 2, 2,
          "Fango bentonitico in pressione: tubi e raccordi verificati, scarico della pressione prima delle "
          "aperture; vasca di raccolta all'uscita",
          "Occhiali protettivi, guanti in lattice o nitrile"),
        _rumore("85-90 dB(A) vicino al motore"),
        r("Caduta dall'alto", 2, 3,
          "Buche di partenza e di arrivo protette con parapetti o recinzioni; scavi armati se profondi "
          "oltre 1,50 m", _DPI),
    ], scheda_uso=scheda(
        "Perforatrice cingolata che esegue fori orizzontali guidati sotto strade, corsi d'acqua o "
        "edifici, tirando poi in posa le tubazioni con alesatore e fanghi di perforazione.",
        ["verificare il progetto del tracciato e i sottoservizi interferenti",
         "collegare la macchina a terra e predisporre i tappetini equipotenziali",
         "provare il sistema di allarme per contatto elettrico",
         "ancorare la macchina al terreno con i sistemi previsti",
         "proteggere le buche di partenza e di arrivo"],
        ["localizzare la testa di perforazione con continuità",
         "non avvicinarsi alle aste in rotazione",
         "in caso di allarme elettrico non scendere dalla macchina e chiamare il gestore",
         "coordinare via radio l'operatore e il localizzatore"],
        ["scaricare la pressione dei fanghi e fermare il motore",
         "raccogliere e smaltire i fanghi residui",
         "controllare aste, morse e tubi"],
        ["casco", "guanti dielettrici", "calzature di sicurezza", "indumenti ad alta visibilità",
         "otoprotettori", "occhiali protettivi"])),

    # ------------------------------------------------------------------ autospurgo, autobotte, verde
    "Autospurgo": attrezzatura(MACCHINA, rischi=[
        r("Ambienti confinati o sospetti di inquinamento", 2, 4,
          "Pulizia dall'esterno ogni volta possibile; ingresso in pozzetti e fognature solo secondo il "
          "D.P.R. 177/2011 (personale formato, procedura, misura dei gas H2S, CH4, O2, CO, ventilazione, "
          "treppiede di recupero, operatore all'esterno)",
          "Rilevatore multigas, imbracatura, autorespiratore per l'emergenza"),
        r("Getti e schizzi", 3, 3,
          "Lancia e ugello ad alta pressione inseriti nella condotta prima della messa in pressione; "
          "comando ad azione mantenuta; tubi e raccordi a norma UNI EN 1829-1 e -2; mai estrarre l'ugello in "
          "pressione",
          "Visiera protettiva, guanti in lattice o nitrile, indumenti impermeabili"),
        r("Rischio biologico", 3, 2,
          "Liquami e fanghi trattati come potenzialmente infetti: guanti impermeabili, igiene delle mani, "
          "nessun cibo durante il lavoro; vaccinazione antitetanica; disinfezione delle attrezzature",
          "Guanti in lattice o nitrile, indumenti impermeabili, stivali di sicurezza"),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Nessuno sotto il braccio portatubo in movimento; aspirazione con depressione: non avvicinare "
          "mani o indumenti alla bocca del tubo di aspirazione; portellone posteriore aperto solo con "
          "blocchi di sicurezza inseriti"),
        _traffico(),
        _rumore("85-90 dB(A) vicino alla pompa del vuoto"),
    ], scheda_uso=scheda(
        "Autocarro con cisterna, pompa del vuoto e pompa ad alta pressione per l'aspirazione di fanghi e "
        "liquami e il lavaggio di fognature, pozzetti e condotte.",
        ["predisporre la segnaletica stradale",
         "verificare tubi, raccordi, lancia, valvole e blocchi del portellone",
         "valutare se il lavoro comporta l'ingresso in ambienti confinati",
         "misurare i gas nel pozzetto prima di avvicinarsi all'apertura"],
        ["mettere in pressione la lancia solo dentro la condotta",
         "non sporgersi sull'apertura del pozzetto",
         "tenere mani e indumenti lontani dalla bocca di aspirazione",
         "non entrare nei pozzetti senza procedura e attrezzature di recupero"],
        ["scaricare il contenuto negli impianti autorizzati",
         "lavare e disinfettare attrezzature e DPI",
         "chiudere i pozzetti aperti"],
        ["guanti in lattice o nitrile", "stivali di sicurezza", "indumenti impermeabili",
         "indumenti ad alta visibilità", "visiera protettiva", "otoprotettori"])),

    "Autobotte": attrezzatura(MACCHINA, rischi=[
        _investimento("nella bagnatura delle piste procedere lentamente e con moviere vicino agli operai"),
        r("Ribaltamento della macchina", 2, 4,
          "Con cisterna parzialmente piena il liquido sposta il baricentro nelle curve e in frenata: "
          "velocità ridotta, cisterne con frangiflutti; percorsi di cantiere con pendenze e cigli "
          "adeguati"),
        r("Caduta dall'alto", 2, 4,
          "Accesso al passo d'uomo solo da passerella con parapetto o con linea di ancoraggio; scala "
          "integra e asciutta; operazioni di riempimento da terra quando possibile",
          "Casco, imbracatura, cordino con assorbitore, calzature di sicurezza"),
        r("Getti e schizzi", 2, 2,
          "Lancia o barra di bagnatura azionate solo con il mezzo fermo o dal posto di guida; tubi "
          "fissati; nessuno nella traiettoria del getto",
          "Occhiali protettivi, indumenti impermeabili"),
        r("Scivolamenti e cadute a livello", 3, 1,
          "Gradini e passerelle antiscivolo puliti; non bagnare le zone di transito pedonale",
          "Calzature di sicurezza"),
    ], scheda_uso=scheda(
        "Autocarro con cisterna e pompa per il trasporto e la distribuzione d'acqua, per la bagnatura "
        "delle piste contro la polvere, il lavaggio e l'approvvigionamento del cantiere.",
        ["controllare freni, luci, retromarcia, pompa, valvole e tubi",
         "verificare passerella, parapetti e scala di accesso alla cisterna",
         "verificare i percorsi di cantiere e le aree di manovra",
         "controllare lo stato dei frangiflutti e il fissaggio dei tubi a bordo"],
        ["moderare la velocità con cisterna parzialmente piena",
         "non salire sulla cisterna senza protezione contro le cadute",
         "dirigere il getto lontano dalle persone e dalle parti elettriche",
         "non bagnare in eccesso piste in pendenza, che diventano scivolose per i mezzi"],
        ["svuotare i circuiti nella stagione fredda",
         "parcheggiare in area stabile con freno inserito"],
        _SCHEDA_DPI_CONDUCENTE)),

    "Cippatrice": attrezzatura(MACCHINA, rischi=[
        r("Trascinamento negli organi di alimentazione e taglio", 2, 4,
          "Macchina conforme a UNI EN 13525 con barra di arresto/inversione dei rulli intorno alla bocca di "
          "alimentazione funzionante e provata a ogni avviamento; alimentare stando di lato alla bocca, "
          "con rami ripuliti dai monconi; mai spingere il materiale con mani o piedi (usare un ramo); "
          "materiale corto inserito con altro materiale; nessun indumento svolazzante"),
        r("Proiezione di schegge e frammenti", 3, 3,
          "Camino di scarico orientato verso il cassone o lontano dalle persone; nessuno nella zona di "
          "lancio; non inserire materiale con sassi, chiodi o terra",
          _DPI + ", visiera protettiva"),
        _rumore("oltre 100 dB(A) vicino alla bocca di alimentazione",
                "otoprotettori obbligatori per chi alimenta e per chi opera nei pressi"),
        r("Polveri e fibre", 2, 2,
          "Lavorare sopravvento; non cippare legno trattato o materiale ammuffito",
          "Facciale filtrante FFP2, occhiali protettivi"),
        _incendio_rifornimento("rimuovere i residui di legno dal vano motore"),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Rami lunghi alimentati in modo che non ruotino colpendo l'operatore; stazionamento della "
          "cippatrice in piano con ruote bloccate e timone appoggiato; traino conforme al Codice della "
          "strada"),
    ], scheda_uso=scheda(
        "Macchina a disco o a tamburo, trainata o semovente, che riduce in cippato rami e tronchi di "
        "piccolo diametro durante i lavori di sistemazione del verde e di disboscamento.",
        ["posizionare la macchina in piano con ruote bloccate e camino orientato in modo sicuro",
         "provare la barra di arresto e gli arresti di emergenza",
         "verificare carter, coltelli e fissaggi a macchina ferma",
         "delimitare la zona di lancio e allontanare i non addetti"],
        ["alimentare dal lato della bocca, mai di fronte",
         "lasciare la presa del ramo appena viene trascinato",
         "non spingere il materiale con mani o piedi",
         "non sporgersi sulla tramoggia",
         "fermare la macchina e attendere l'arresto del rotore prima di liberare intasamenti"],
        ["arrestare il motore, attendere il fermo del rotore e togliere la chiave",
         "pulire la macchina dai residui di legno",
         "controllare l'affilatura dei coltelli"],
        ["casco", "visiera protettiva", "otoprotettori", "guanti", "calzature di sicurezza",
         "indumenti ad alta visibilità"])),
}
