"""Fasi di lavoro: lavori strutturali; murature, tramezzi e partizioni.

Testi redatti da zero per questo progetto. Fonti consultate per verificare contenuti e riferimenti
(non copiate): D.Lgs. 81/2008, Titolo IV Capo II (artt. 111, 115, 116, 122-130 su ponteggi, ponti a
sbalzo, sottoponti, impalcature nelle costruzioni in conglomerato cementizio, andatoie; artt. 142-146
sezione VII «Costruzioni edilizie»: armature provvisorie, loro posa, resistenza e disarmo, difesa
delle aperture), Titolo VI e Allegato XXXIII (movimentazione manuale dei carichi), Titolo VIII capi
II, III e V (rumore, vibrazioni, radiazioni ottiche artificiali), Titolo IX (agenti chimici e
cancerogeni; D.Lgs. 44/2020 sulla silice cristallina respirabile, Allegato XLII), Allegati IV, VI
(punto 3, sollevamento), IX, XVIII e XXXII (segnali gestuali); Circolare del Ministero del Lavoro
n. 13 del 20/01/1982, Parte III (prevenzione infortuni nel montaggio di elementi prefabbricati in
c.a. e c.a.p.: istruzioni scritte di montaggio del fornitore e della ditta montatrice, persona
esperta, difese applicate agli elementi a piè d'opera); D.M. 17/01/2018 (NTC 2018, capp. 4.1,
4.2, 4.4, 4.5 e 11); Regolamento (UE) 1907/2006 Allegato XVII voce 47 (cromo VI idrosolubile nel
cemento, Reg. UE 301/2014); norme UNI EN 12812 (centine e opere provvisionali di sostegno),
UNI EN 12813 (torri di puntellazione), UNI EN 1065 (puntelli telescopici), UNI EN 12811-1,
UNI EN 13374 (parapetti provvisori), UNI EN 1263-1/2 (reti di sicurezza), UNI EN 795 e UNI EN 363
(ancoraggi e sistemi anticaduta), UNI EN 1090-2 (esecuzione di strutture in acciaio),
UNI EN 206 e UNI 11104 (calcestruzzo), UNI 11424 (sistemi a secco in lastre di gesso rivestito),
UNI EN 1051 (vetromattone), UNI EN 771 (elementi per muratura); materiali divulgativi INAIL
(cadute dall'alto, montaggio di prefabbricati), PuntoSicuro (montaggio dei prefabbricati e
dispositivi di protezione), manuale tecnico della Regione Emilia-Romagna sulle procedure operative
nei cantieri edili, istruzioni tipiche dei fabbricanti di casseforme, solai a predalles, lastre
alveolari, pannelli X-lam e sistemi in cartongesso.
I contenuti vanno sempre verificati e adattati dal coordinatore al cantiere specifico.
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import ATTREZZO, DPI_BASE, fase, r

_ST = "Lavori strutturali"
_MU = "Murature, tramezzi e partizioni"

_NC_RI = ("Nuove costruzioni", "Ristrutturazioni")
_NC_RI_INF = ("Nuove costruzioni", "Ristrutturazioni", "Opere infrastrutturali")
_EDILIZIA = ("Nuove costruzioni", "Ristrutturazioni", "Restauri")

# Attrezzature non presenti nel CATALOGO di base.py: nome -> (tipo, motivo).
MANCANTI: dict[str, tuple[str, str]] = {
    "Accessori di sollevamento (brache, bilancini, ganci)": (
        ATTREZZO,
        "Brache in fune, catena o fibra tessile, bilancini e ganci con cui si imbracano casseforme, "
        "fasci di ferri, travi prefabbricate, profili in acciaio ed elementi in legno: hanno rischi "
        "propri (rottura, sfilamento, scelta errata della portata e dell'angolo di tiro, UNI EN 13414, "
        "UNI EN 818, UNI EN 1492) e verifiche trimestrali di cui all'Allegato VI punto 3.1.2; non "
        "sono rappresentati dalle schede della gru o dell'autogru.",
    ),
    "Macchina insufflatrice per isolanti sfusi": (
        ATTREZZO,
        "Macchina con tramoggia, cardatore e soffiante che spinge in un tubo flessibile fiocchi di "
        "lana minerale, cellulosa o granuli per riempire le intercapedini esistenti attraverso fori "
        "praticati nella muratura: rischi propri (organi rotanti della tramoggia, tubo in pressione, "
        "polveri) diversi da quelli di una pompa per malte.",
    ),
}

# --- DPI ricorrenti ---
_DPI_ANTICADUTA = DPI_BASE + ", casco con sottogola, imbracatura, cordino con assorbitore"
_DPI_CLS = DPI_BASE + ", stivali di sicurezza, guanti in lattice o nitrile, occhiali protettivi, crema protettiva"
_DPI_FERRI = DPI_BASE + ", guanti antitaglio"
_DPI_POLVERI = DPI_BASE + ", facciale filtrante FFP3, occhiali protettivi"
_DPI_SALDATURA = (DPI_BASE + ", schermo per saldatura, guanti per saldatura, grembiule per saldatura, "
                  "ghette per saldatura, maschera con filtro specifico")

# --- Rischi riusati ---
_CADUTA_SCAVO = r("Caduta dall'alto", 2, 3,
                  "Ciglio degli scavi di fondazione delimitato con parapetto o sbarramento arretrato; "
                  "attraversamenti su andatoie con parapetti (art. 130); accesso al fondo con scale a "
                  "mano vincolate e sporgenti almeno 1 m dal ciglio; scavi profondi oltre 1,50 m con "
                  "pareti armate o a scarpa secondo la relazione geotecnica (art. 119).")
_SEPPELLIMENTO = r("Seppellimento e sprofondamento", 2, 4,
                   "Non entrare negli scavi prima della verifica della stabilità delle pareti da parte "
                   "del preposto, in particolare dopo piogge o gelo; nessun deposito di materiali, "
                   "casseforme o ferri e nessun transito di mezzi entro una fascia di rispetto dal "
                   "ciglio (art. 120); armature delle pareti mantenute fino al rinterro.")
_CADUTA_BORDO = r("Caduta dall'alto", 3, 4,
                  "Bordi di solai e impalcati protetti dal ponteggio perimetrale con parapetto o, in "
                  "sua assenza, dal ponte di sicurezza a sbalzo largo almeno 1,20 m (art. 129); aperture "
                  "nei solai, vani scala e vani ascensore chiusi con tavolati fissati o parapetti con "
                  "fermapiede (art. 146); dove la protezione collettiva non è possibile, imbracatura "
                  "agganciata a linea vita o ancoraggi (UNI EN 795).", _DPI_ANTICADUTA)
_CARICHI_SOSPESI = r("Caduta di materiale dall'alto o a livello", 2, 4,
                     "Imbracatura dei carichi con accessori di portata adeguata e controllati; "
                     "materiali minuti sollevati in cassoni o ceste chiuse, mai su forche o pallet "
                     "senza contenimento; nessuno sotto il carico sospeso; segnalazione dell'area di "
                     "tiro; comunicazione con il gruista con i gesti dell'Allegato XXXII o via radio.",
                     DPI_BASE + ", casco con sottogola")
_IMBRACATURA = r("Urti, colpi, impatti e compressioni", 2, 3,
                 "Guidare gli elementi sospesi con funi o aste, mai con le mani sotto il carico; "
                 "avvicinarsi solo a carico fermo a pochi centimetri dalla posizione di posa; sganciare "
                 "solo dopo aver verificato la stabilità o il vincolo dell'elemento; mani lontane dai "
                 "punti di appoggio.")
_MMC = r("Movimentazione manuale dei carichi", 3, 2,
         "Carichi oltre 25 kg (uomini) o 20 kg (donne) movimentati in due o con mezzi meccanici; "
         "materiali depositati vicino al punto di impiego e ad altezza comoda; valutazione con la "
         "norma UNI ISO 11228-1 (Titolo VI e Allegato XXXIII); formazione sul corretto sollevamento.")
_MMC_BLOCCHI = r("Movimentazione manuale dei carichi", 3, 3,
                 "Scelta di blocchi di peso compatibile con la posa manuale ripetuta; bancali portati "
                 "dalla gru o dal montacarichi a ridosso della postazione e sollevati su rialzi per "
                 "evitare di chinarsi; rotazione dei compiti; valutazione con UNI ISO 11228-1 e "
                 "sorveglianza sanitaria (art. 168 e Allegato XXXIII).")
_FERRI_SPORGENTI = r("Punture, tagli e abrasioni", 3, 2,
                     "Ferri di ripresa e chiamate verticali protetti con cappellotti in plastica o "
                     "piegati; filo di legatura tagliato e ripiegato; guanti antitaglio nella "
                     "manipolazione dei tondini e delle reti elettrosaldate.", _DPI_FERRI)
_CEMENTO = r("Rischio chimico", 3, 2,
             "Calcestruzzo e malte sono alcalini e contengono cromo VI (tenore limitato dal Reg. (UE) "
             "1907/2006, Allegato XVII voce 47): evitare il contatto con la pelle e gli occhi, guanti "
             "impermeabili con polsino, stivali sotto i pantaloni; lavare subito la pelle con acqua; "
             "lavaocchi in cantiere; disarmanti applicati secondo la scheda di sicurezza; "
             "sorveglianza sanitaria per le dermatiti da contatto.", _DPI_CLS)
_GETTI = r("Getti e schizzi", 3, 2,
           "Addetti fuori dalla traiettoria del getto e lontani dal terminale nelle fasi di avvio e "
           "di pulizia della tubazione; occhiali protettivi durante getto e vibratura; scarico del "
           "calcestruzzo graduale e a bassa altezza per contenere gli schizzi.", _DPI_CLS)
_SCIVOLAMENTI = r("Scivolamenti e cadute a livello", 3, 2,
                  "Piani di lavoro sgombri da ritagli, chiodi, tondini e attrezzi; percorsi sopra le "
                  "armature su tavole o passerelle; casseri trattati con disarmante e superfici bagnate "
                  "percorse con attenzione; illuminazione adeguata nelle zone in ombra.")
_POSTURE = r("Posture incongrue", 3, 2,
             "Banchi di lavoro e cavalletti ad altezza adeguata; alternanza tra lavori chinati e in "
             "piedi; ginocchiere nei lavori in ginocchio; pause programmate.",
             DPI_BASE + ", ginocchiere")
_MICROCLIMA = r("Microclima", 3, 2,
                "Nei mesi caldi lavori più pesanti nelle ore fresche, pause all'ombra e acqua a "
                "disposizione; con freddo indumenti adeguati; sospensione dei lavori all'aperto con "
                "temperature o indice di calore oltre le soglie indicate dal piano di emergenza "
                "caldo.", DPI_BASE + ", indumenti per il freddo, copricapo")
_VENTO = r("Microclima", 2, 3,
           "Sospendere sollevamenti e lavori in quota con vento oltre i limiti indicati dal "
           "fabbricante della gru o dal piano di montaggio, con pioggia, ghiaccio o scarsa "
           "visibilità; anemometro consultabile; superfici bagnate o gelate non percorse senza "
           "protezioni collettive.", DPI_BASE + ", indumenti impermeabili, indumenti per il freddo")
_INVESTIMENTO = r("Investimento da mezzi in manovra", 2, 4,
                  "Autobetoniere, autopompe e autocarri in area di sosta stabile e delimitata; manovre "
                  "in retromarcia guidate da un moviere; addetti a terra visibili e fuori dal raggio "
                  "d'azione del braccio e delle ruote.")
_CROLLO_CASSERI = r("Crollo o ribaltamento di strutture", 2, 4,
                    "Casseforme e puntellature montate secondo il progetto o gli schemi del "
                    "fabbricante (UNI EN 12812, UNI EN 1065, UNI EN 12813) e controllate dal preposto "
                    "prima del getto (artt. 142-144); puntelli su basi resistenti e non cedevoli, "
                    "controventati, mai sostituiti con mattoni o spezzoni; velocità di getto e "
                    "spinta del calcestruzzo compatibili con la portata del cassero.")
_SILICE = r("Polveri e fibre", 3, 3,
            "Taglio di laterizi, blocchi e pietre con utensili ad acqua o con aspirazione alla fonte; "
            "operazioni all'aperto o in ambienti ventilati; pulizia con aspiratore e non a secco con "
            "scope; la silice cristallina respirabile è agente cancerogeno (D.Lgs. 81/2008, Titolo IX "
            "e Allegato XLII, D.Lgs. 44/2020): valutazione dell'esposizione e sorveglianza sanitaria.",
            _DPI_POLVERI)
_RUMORE_MARTELLATURA = r("Rumore", 3, 2,
                         "Valutazione del rumore (Titolo VIII Capo II); otoprotettori sopra 85 dB(A); "
                         "lavorazioni rumorose concentrate in orari definiti e lontane dagli altri "
                         "addetti.", DPI_BASE + ", otoprotettori")
_CADUTA_PONTEGGIO = r("Caduta dall'alto", 2, 4,
                      "Lavorare dal ponteggio con impalcati completi, parapetti e fermapiede e "
                      "distanza dalla muratura non superiore a 20 cm (artt. 125-126); ponti su "
                      "cavalletti solo fino a 2 m e mai sovrapposti né sopra impalcati del ponteggio; "
                      "nessuna rimozione di parapetti o tavole per comodità di lavoro.")
_CADUTA_INTERNI = r("Caduta dall'alto", 2, 3,
                    "Ponti su cavalletti con impalcato largo almeno 90 cm e tavole ben accostate, "
                    "trabattelli con ruote bloccate e parapetti; scale doppie solo per brevi "
                    "lavorazioni e con catena o tirante di apertura; nessun piano di lavoro "
                    "improvvisato su secchi, blocchi o bancali.")
_MATERIALE_IMPALCATO = r("Caduta di materiale dall'alto o a livello", 2, 3,
                         "Sugli impalcati solo il materiale necessario alla lavorazione in corso, "
                         "senza superarne la portata (art. 124); fermapiede continui; blocchi e "
                         "malta lontani dal bordo; zona sottostante delimitata e protetta con "
                         "mantovana o segregata (art. 129, comma 3).", DPI_BASE + ", casco con sottogola")
_FIBRE_ISOLANTI = r("Polveri e fibre", 3, 2,
                    "Pannelli in lana minerale tagliati con coltello e non con utensili veloci; "
                    "maniche lunghe e guanti per evitare il prurito da fibre; ambiente ventilato e "
                    "pulizia con aspiratore; consultare la scheda informativa del fabbricante.",
                    DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi, indumenti protettivi")

LAVORAZIONI = [
    # ======================================================================================
    # LAVORI STRUTTURALI
    # ======================================================================================
    # --- Opere di fondazione in c.a. ---
    fase("ST.01", _ST, "Opere di fondazione in c.a.",
         "Getto di magrone e sottofondazioni in calcestruzzo",
         "Getto sul fondo dello scavo, già regolarizzato e compattato, di uno strato di calcestruzzo "
         "magro di pulizia di 10-15 cm per formare un piano di appoggio pulito e livellato per le "
         "armature delle fondazioni. Comprende i getti di sottofondazione e di riempimento a "
         "quote diverse, con scarico diretto dall'autobetoniera o con l'autopompa e stesura a mano "
         "con rastrelli e staggia.",
         "Addetto al getto di magrone e sottofondazioni", 20, _NC_RI_INF,
         ["Autobetoniera", "Autopompa per calcestruzzo", "Andatoie e passerelle",
          "Armatura delle pareti di scavo (blindaggio)", "Utensili manuali"], [
             _SEPPELLIMENTO, _CADUTA_SCAVO, _INVESTIMENTO, _CEMENTO, _GETTI,
             r("Posture incongrue", 3, 2,
               "Stesura e livellamento con attrezzi a manico lungo, per lavorare in piedi; turni "
               "alternati nel tiro della staggia; getto distribuito vicino al punto di posa "
               "per ridurre lo spostamento a mano del calcestruzzo.", _DPI_CLS),
         ]),
    fase("ST.02", _ST, "Opere di fondazione in c.a.",
         "Casseforme e disarmo di strutture di fondazione",
         "Tracciamento e montaggio delle casseforme in pannelli metallici o in tavole di legno per "
         "plinti, travi rovesce, cordoli e bordi di platea, con puntoni di contrasto sul terreno e "
         "applicazione del disarmante. A maturazione del getto si smontano i casseri, si "
         "puliscono e si accatastano per il riutilizzo.",
         "Addetto alla carpenteria delle fondazioni", 60, _NC_RI_INF,
         ["Casseforme", "Sega circolare", "Gru a torre", "Autocarro con gru",
          "Accessori di sollevamento (brache, bilancini, ganci)", "Utensili manuali"], [
             _SEPPELLIMENTO, _CADUTA_SCAVO, _MMC,
             r("Punture, tagli e abrasioni", 3, 2,
               "Chiodi delle tavole di recupero ribattuti o estratti subito dopo il disarmo; "
               "legname accatastato per tipo lontano dai passaggi; guanti nella manipolazione dei "
               "pannelli e dei morsetti."),
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "Pannelli di grandi dimensioni movimentati con la gru e appoggiati su terreno "
               "stabile; puntoni di contrasto messi in opera prima di sganciare il pannello; nel "
               "disarmo staccare i casseri gradualmente, senza farli cadere nello scavo."),
         ]),
    fase("ST.03", _ST, "Opere di fondazione in c.a.",
         "Lavorazione e posa dei ferri d'armatura delle fondazioni",
         "Taglio e piegatura delle barre in un'area attrezzata del cantiere oppure ricevimento di "
         "gabbie preassemblate, sollevamento con la gru e posa nello scavo sul magrone con "
         "distanziatori. Legatura con filo di ferro delle staffe, delle reti e dei ferri di attesa "
         "per i pilastri e i setti.",
         "Addetto alla lavorazione e posa dei ferri delle fondazioni", 50, _NC_RI_INF,
         ["Piegaferri", "Tagliaferri", "Gru a torre",
          "Accessori di sollevamento (brache, bilancini, ganci)", "Utensili manuali"], [
             _FERRI_SPORGENTI, _CARICHI_SOSPESI, _SEPPELLIMENTO, _CADUTA_SCAVO,
             r("Movimentazione manuale dei carichi", 3, 2,
               "Barre lunghe e reti trasportate in due o con la gru, in fasci legati in due punti; "
               "gabbie pesanti mai trascinate a mano nello scavo; accatastamento su travetti per "
               "prendere i ferri senza chinarsi."),
             _POSTURE,
         ]),
    fase("ST.04", _ST, "Opere di fondazione in c.a.",
         "Getto del calcestruzzo per le strutture di fondazione",
         "Getto del calcestruzzo di plinti, travi rovesce e platee con autopompa o direttamente "
         "dalla canala dell'autobetoniera, procedendo per strati e compattando con vibratore a "
         "immersione. Sulle platee segue la staggiatura e, se previsto, la lisciatura meccanica; "
         "la superficie è poi protetta e bagnata durante la maturazione.",
         "Addetto al getto del calcestruzzo per le fondazioni", 20, _NC_RI_INF,
         ["Autobetoniera", "Autopompa per calcestruzzo", "Vibratore per calcestruzzo",
          "Frattazzatrice meccanica", "Andatoie e passerelle", "Utensili manuali"], [
             _INVESTIMENTO, _CEMENTO, _GETTI, _SCIVOLAMENTI, _CADUTA_SCAVO,
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "Il terminale in gomma dell'autopompa è guidato da un solo addetto, che non lo tiene "
               "sotto il braccio né se lo avvolge attorno al corpo e resta in contatto visivo o "
               "radio con l'operatore; nessuno sotto il braccio della pompa in movimento."),
         ]),
    # --- Strutture in elevazione in c.a. ---
    fase("ST.05", _ST, "Strutture in elevazione in c.a.",
         "Casseforme per pilastri, setti e travi in elevazione",
         "Montaggio delle casseforme modulari o in legno per pilastri, pareti, setti e travi, con "
         "puntelli, tiranti e puntoni di stabilizzazione, previa applicazione del disarmante. Per "
         "le travi si realizza il fondo cassero sostenuto da puntelli o torri di puntellazione e "
         "si eseguono le sponde; i casseri a parete si movimentano con la gru agganciandoli ai "
         "punti indicati dal fabbricante.",
         "Addetto alla carpenteria in elevazione", 60, _NC_RI,
         ["Casseforme", "Puntelli metallici", "Gru a torre", "Sega circolare",
          "Ponteggio metallico fisso", "Trabattello", "Parapetto provvisorio",
          "Accessori di sollevamento (brache, bilancini, ganci)", "Utensili manuali"], [
             _CADUTA_BORDO, _CROLLO_CASSERI, _CARICHI_SOSPESI, _IMBRACATURA,
             r("Caduta dall'alto", 2, 4,
               "Casseri di pilastri e pareti dotati di mensole di lavoro con parapetto per il getto "
               "e la vibratura; salita in quota con scale integrate nel cassero o trabattelli, mai "
               "arrampicandosi sui tiranti o sui ferri; casseri a parete stabilizzati con i puntoni "
               "prima dello sgancio dalla gru.", _DPI_ANTICADUTA),
             _MMC, _VENTO,
         ]),
    fase("ST.06", _ST, "Strutture in elevazione in c.a.",
         "Lavorazione e posa dei ferri d'armatura di pilastri, setti e travi",
         "Preparazione delle armature di pilastri, setti e travi, con legatura delle staffe e "
         "giunzione per sovrapposizione ai ferri di attesa, oppure posa di gabbie preassemblate "
         "sollevate con la gru. Posizionamento dei distanziatori per garantire il copriferro "
         "prescritto e controllo prima della chiusura dei casseri.",
         "Addetto alla lavorazione e posa dei ferri in elevazione", 50, _NC_RI,
         ["Piegaferri", "Tagliaferri", "Gru a torre", "Trabattello", "Ponteggio metallico fisso",
          "Accessori di sollevamento (brache, bilancini, ganci)", "Utensili manuali"], [
             _CADUTA_BORDO, _FERRI_SPORGENTI, _CARICHI_SOSPESI,
             r("Crollo o ribaltamento di strutture", 2, 3,
               "Gabbie alte di pilastri e setti controventate con tiranti o vincolate ai ferri di "
               "attesa finché non sono chiusi i casseri; non salire sulle gabbie per legare le "
               "staffe superiori, ma lavorare da trabattelli o piattaforme."),
             _POSTURE,
         ]),
    fase("ST.07", _ST, "Strutture in elevazione in c.a.",
         "Getto del calcestruzzo di pilastri, setti, travi e solette con autopompa",
         "Getto del calcestruzzo nelle casseforme di pilastri, setti, travi e solette con autopompa "
         "o con benna sollevata dalla gru, a strati di altezza contenuta, e compattazione con "
         "vibratore a immersione. Gli addetti operano dalle mensole dei casseri o dal solaio "
         "protetto; al termine si staggia e si cura la maturazione delle superfici.",
         "Addetto al getto del calcestruzzo in elevazione", 25, _NC_RI,
         ["Autobetoniera", "Autopompa per calcestruzzo", "Gru a torre", "Vibratore per calcestruzzo",
          "Ponteggio metallico fisso", "Parapetto provvisorio", "Utensili manuali"], [
             _CADUTA_BORDO, _CEMENTO, _GETTI, _CROLLO_CASSERI,
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "Terminale dell'autopompa guidato da un solo addetto in posizione stabile, mai sul "
               "bordo del solaio; comunicazione via radio o a gesti con l'operatore; benna della "
               "gru aperta solo quando è ferma sopra il cassero; nessuno sotto il braccio."),
             _SCIVOLAMENTI,
         ]),
    fase("ST.08", _ST, "Strutture in elevazione in c.a.",
         "Disarmo delle casseforme e delle armature di sostegno",
         "Rimozione dei casseri di pilastri, setti, travi, solette e solai a maturazione avvenuta e "
         "solo dopo l'autorizzazione del direttore dei lavori, sotto la sorveglianza del preposto "
         "(art. 145). Allentamento graduale e progressivo dei puntelli secondo la sequenza prevista, "
         "estrazione dei pannelli, pulizia e accatastamento del materiale; eventuale ripuntellatura "
         "provvisoria dei solai.",
         "Addetto al disarmo delle casseforme", 65, _NC_RI,
         ["Casseforme", "Puntelli metallici", "Gru a torre", "Trabattello",
          "Accessori di sollevamento (brache, bilancini, ganci)", "Utensili manuali"], [
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Disarmo solo dopo il tempo di maturazione stabilito e l'autorizzazione del "
               "direttore dei lavori; mai con carichi accidentali o materiali depositati sul "
               "solaio (art. 145, comma 2); allentare i puntelli dal centro verso gli appoggi, "
               "lasciando i rompitratta previsti; nessuno sotto le zone in disarmo."),
             r("Caduta di materiale dall'alto o a livello", 3, 3,
               "Pannelli e tavole staccati in modo controllato e calati, non lasciati cadere; zona "
               "sottostante delimitata; casseri sganciati dalla gru solo quando sono a terra "
               "stabili.", DPI_BASE + ", casco con sottogola, occhiali protettivi"),
             _CADUTA_BORDO,
             r("Punture, tagli e abrasioni", 3, 2,
               "Rimozione immediata o ribattitura dei chiodi sporgenti; legname con chiodi non "
               "lasciato a terra lungo i percorsi; guanti per la manipolazione dei pannelli."),
             _RUMORE_MARTELLATURA, _MMC,
         ]),
    fase("ST.09", _ST, "Strutture in elevazione in c.a.",
         "Realizzazione di scale in c.a. gettate in opera",
         "Formazione del cassero inclinato della rampa e dei pianerottoli su puntelli, con le "
         "sponde e i frontali dei gradini, posa delle armature collegate alle travi e ai solai, "
         "getto e vibratura del calcestruzzo. Fino al montaggio delle ringhiere definitive le "
         "rampe e i vani scala restano protetti da parapetti provvisori.",
         "Addetto alla realizzazione di scale in c.a.", 55, _NC_RI,
         ["Casseforme", "Puntelli metallici", "Sega circolare", "Gru a torre", "Vibratore per calcestruzzo",
          "Autopompa per calcestruzzo", "Parapetto provvisorio", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Vano scala e lati liberi delle rampe protetti con parapetti provvisori con "
               "fermapiede (UNI EN 13374) fin dal montaggio del cassero e fino alla posa delle "
               "ringhiere (art. 146); armature provvisorie della scala realizzate secondo l'art. "
               "142, comma 2; accesso alle rampe in costruzione solo su tavole fissate.",
               _DPI_ANTICADUTA),
             _CROLLO_CASSERI, _FERRI_SPORGENTI, _CEMENTO, _SCIVOLAMENTI,
         ]),
    # --- Solai ---
    fase("ST.10", _ST, "Solai", "Solai in latero-cemento gettati in opera",
         "Montaggio dell'impalcato di sostegno con puntelli e travi rompitratta, posa dei travetti "
         "prefabbricati e delle pignatte in laterizio, delle armature aggiuntive e della rete "
         "della soletta, quindi getto e vibratura del calcestruzzo. Durante la posa delle "
         "pignatte gli addetti si spostano solo su tavole appoggiate ai travetti, perché i "
         "blocchi non sono pedonabili.",
         "Addetto alla realizzazione di solai in latero-cemento", 45, _NC_RI,
         ["Puntelli metallici", "Gru a torre", "Autopompa per calcestruzzo", "Vibratore per calcestruzzo",
          "Ponteggio metallico fisso", "Rete di sicurezza anticaduta", "Parapetto provvisorio",
          "Andatoie e passerelle", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Rischio di sfondamento delle pignatte e di caduta tra i travetti: impalcato "
               "continuo di tavole o rete di sicurezza sotto il solaio (UNI EN 1263-1) finché il "
               "getto non è indurito; camminamenti su tavole; bordi protetti dal ponteggio che "
               "supera di almeno 1,20 m il piano di lavoro; aperture e cavedi chiusi (art. 146).",
               _DPI_ANTICADUTA),
             _CROLLO_CASSERI, _CARICHI_SOSPESI, _MMC, _CEMENTO, _SCIVOLAMENTI,
         ]),
    fase("ST.11", _ST, "Solai", "Solai a lastre prefabbricate (predalles e lastre alveolari)",
         "Posa con la gru di lastre tralicciate tipo predalles su travi rompitratta e puntelli, "
         "oppure di lastre alveolari precompresse in semplice appoggio sulle travi, secondo lo "
         "schema e le istruzioni di posa del fornitore. Seguono la posa degli alleggerimenti e "
         "delle armature integrative, la sigillatura dei giunti e il getto di completamento.",
         "Addetto alla posa di solai a lastre prefabbricate", 35, _NC_RI,
         ["Gru a torre", "Autogru", "Puntelli metallici", "Autopompa per calcestruzzo",
          "Vibratore per calcestruzzo", "Parapetto provvisorio", "Linea vita provvisoria",
          "Accessori di sollevamento (brache, bilancini, ganci)", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Lastre sollevate con i ganci o le pinze indicate dal fornitore e con bilancino per "
               "le lastre lunghe; gli addetti ricevono la lastra da zone già posate o dal "
               "ponteggio, agganciati a linea vita quando il bordo non è protetto; parapetti "
               "applicati alle lastre di bordo appena posate; nessuno sulle lastre prima che siano "
               "appoggiate e puntellate.", _DPI_ANTICADUTA),
             _IMBRACATURA, _CARICHI_SOSPESI,
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Rompitratta e puntelli delle predalles disposti alle distanze del progetto prima "
               "della posa; lunghezze di appoggio minime delle lastre alveolari verificate; nessun "
               "accumulo di materiali sulle lastre prima del getto di completamento."),
             _CEMENTO, _VENTO,
         ]),
    # --- Strutture prefabbricate e metalliche ---
    fase("ST.12", _ST, "Strutture prefabbricate e metalliche",
         "Montaggio di strutture prefabbricate in c.a. e c.a.p.",
         "Scarico dagli automezzi e montaggio con autogru di pilastri nei plinti a bicchiere, travi, "
         "tegoli di copertura e pannelli di tamponamento, seguendo il piano di montaggio con le "
         "istruzioni scritte del fornitore e della ditta montatrice (Circolare Min. Lavoro 13/1982, "
         "Parte III). Gli elementi vengono stabilizzati con puntelli, cunei o controventi "
         "provvisori e collegati prima dello sgancio; i montatori lavorano da piattaforme "
         "elevabili e su elementi già dotati in stabilimento di parapetti o ancoraggi.",
         "Addetto al montaggio di strutture prefabbricate", 30, _NC_RI_INF,
         ["Autogru", "Piattaforma di lavoro elevabile", "Autocarro",
          "Accessori di sollevamento (brache, bilancini, ganci)", "Linea vita provvisoria",
          "Rete di sicurezza anticaduta", "Parapetto provvisorio", "Trapano elettrico",
          "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Protezioni previste dal piano di montaggio e applicate a piè d'opera: parapetti "
               "sugli elementi, reti di sicurezza ancorate ai punti predisposti in stabilimento, "
               "linee vita sulle travi; aggancio e sgancio degli elementi da piattaforma elevabile; "
               "nessuno cammina sulle travi senza ancoraggio continuo; montatori idonei sotto la "
               "guida di una persona esperta; piano di recupero del lavoratore sospeso.",
               _DPI_ANTICADUTA),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Sequenza di montaggio del piano rispettata; pilastri fissati con cunei e controventi "
               "provvisori prima dello sgancio; travi e tegoli appoggiati solo sui supporti "
               "previsti e subito vincolati; nessun carico sugli elementi prima del collegamento "
               "definitivo; verifica degli inserti di sollevamento prima del tiro."),
             _CARICHI_SOSPESI, _IMBRACATURA, _VENTO,
             r("Investimento da mezzi in manovra", 2, 4,
               "Area di montaggio recintata con ingresso consentito ai soli montatori; percorsi dei "
               "bilici e posizione dell'autogru definiti nel piano; terreno di appoggio degli "
               "stabilizzatori verificato; moviere nelle manovre dei mezzi di trasporto."),
         ]),
    fase("ST.13", _ST, "Strutture prefabbricate e metalliche",
         "Montaggio di strutture in acciaio (carpenteria metallica)",
         "Scarico e premontaggio a terra di colonne, travi, controventi e arcarecci in profili "
         "d'acciaio, sollevamento con autogru o gru a torre e posa secondo il piano di montaggio "
         "redatto in base alla UNI EN 1090-2. Fissaggio provvisorio con bulloni di prima posa, "
         "messa a piombo e controventatura di ogni campata prima dello sgancio; i montatori operano "
         "da piattaforme di lavoro elevabili.",
         "Addetto al montaggio di carpenteria metallica", 35, _NC_RI_INF,
         ["Autogru", "Gru a torre", "Piattaforma di lavoro elevabile", "Autocarro",
          "Accessori di sollevamento (brache, bilancini, ganci)", "Linea vita provvisoria",
          "Rete di sicurezza anticaduta", "Avvitatore elettrico", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Massimo premontaggio a terra; lavoro in quota da piattaforme elevabili o, sulle "
               "travi, con imbracatura agganciata a linee di ancoraggio orizzontali montate a terra "
               "sui profili prima del sollevamento; reti di sicurezza sotto le zone di montaggio di "
               "arcarecci e lamiere; mai camminare sulle ali delle travi senza ancoraggio continuo.",
               _DPI_ANTICADUTA),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Colonne vincolate ai tirafondi con dadi serrati prima dello sgancio; ogni campata "
               "chiusa con controventi provvisori o definitivi prima di proseguire; numero minimo "
               "di bulloni di prima posa indicato dal piano rispettato."),
             _CARICHI_SOSPESI, _IMBRACATURA, _VENTO,
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Bulloni, dadi e chiavi in quota in borse portautensili; attrezzi assicurati con "
               "cordini; zona sotto il montaggio delimitata.", DPI_BASE + ", casco con sottogola"),
         ]),
    fase("ST.14", _ST, "Strutture prefabbricate e metalliche",
         "Bullonature e saldature in quota su strutture metalliche",
         "Completamento dei collegamenti delle strutture in acciaio con serraggio controllato dei "
         "bulloni ad alta resistenza e saldature di giunti, piastre e connettori, eseguiti da "
         "piattaforme elevabili o da posizioni protette in quota. Comprende la molatura dei "
         "cordoni, il ritocco della protezione anticorrosiva e il controllo dei serraggi.",
         "Addetto alle bullonature e saldature in quota", 45, _NC_RI_INF,
         ["Piattaforma di lavoro elevabile", "Saldatrice", "Smerigliatrice angolare",
          "Avvitatore elettrico", "Linea vita provvisoria", "Utensili manuali"], [
             r("Caduta dall'alto", 2, 4,
               "Lavoro da piattaforma elevabile con imbracatura agganciata al punto previsto nel "
               "cestello o, fuori dal cestello, a linee di ancoraggio; cordini e funi di "
               "trattenuta protetti da spigoli e scorie calde.", _DPI_ANTICADUTA),
             r("Radiazioni ottiche", 3, 2,
               "Schermo con filtro adeguato al procedimento di saldatura; schermi o tende per "
               "proteggere gli altri addetti; valutazione delle radiazioni ottiche artificiali "
               "(Titolo VIII Capo V).", _DPI_SALDATURA),
             r("Rischio chimico", 3, 3,
               "I fumi di saldatura sono cancerogeni: aspirazione localizzata o lavoro all'aperto "
               "con il viso fuori dal pennacchio; rimozione di vernici e zincature dalla zona del "
               "giunto prima di saldare; valutazione secondo il Titolo IX e sorveglianza sanitaria.",
               _DPI_SALDATURA),
             r("Incendio ed esplosione", 2, 3,
               "Allontanare o coprire i materiali combustibili sotto e attorno al punto di "
               "saldatura, raccogliendo le gocce con teli ignifughi; estintore a portata di mano; "
               "controllo della zona per almeno 30 minuti dopo la fine dei lavori a caldo."),
             _MICROCLIMA,
         ]),
    # --- Strutture in legno ---
    fase("ST.15", _ST, "Strutture in legno",
         "Montaggio di strutture in legno lamellare",
         "Montaggio con autogru di pilastri, travi principali e secondarie in legno lamellare "
         "secondo il piano di montaggio e i disegni del fornitore, con fissaggio a piastre e "
         "staffe metalliche mediante viti, spinotti e bulloni. Gli elementi vengono vincolati "
         "e controventati man mano; i collegamenti in quota si eseguono da piattaforme di lavoro "
         "elevabili.",
         "Addetto al montaggio di strutture in legno lamellare", 35, _EDILIZIA,
         ["Autogru", "Piattaforma di lavoro elevabile",
          "Accessori di sollevamento (brache, bilancini, ganci)", "Avvitatore elettrico",
          "Trapano elettrico", "Linea vita provvisoria", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Connessioni in quota da piattaforma elevabile; per spostarsi sulla struttura "
               "imbracatura agganciata a linee di ancoraggio o a dispositivi retrattili fissati "
               "agli elementi già vincolati; parapetti o reti prima della posa del tavolato.",
               _DPI_ANTICADUTA),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Travi sganciate solo dopo l'inserimento dei collegamenti previsti; controventi "
               "provvisori finché non è montato l'impalcato; brache tessili con protezioni sugli "
               "spigoli per non danneggiare il legno e scivolare."),
             _CARICHI_SOSPESI, _IMBRACATURA, _VENTO,
             r("Polveri e fibre", 2, 2,
               "Le polveri di legno duro sono cancerogene: forature e tagli in opera con utensili "
               "dotati di aspirazione; pulizia con aspiratore; facciale filtrante durante le "
               "lavorazioni di taglio.", DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
         ]),
    fase("ST.16", _ST, "Strutture in legno",
         "Montaggio di pareti e solai in pannelli X-lam",
         "Posa con la gru di pannelli di legno lamellare a strati incrociati per pareti e solai, "
         "sollevati con i dispositivi di aggancio indicati dal fornitore, puntellati con puntoni "
         "regolabili e collegati tra loro e alla fondazione con viti, angolari e hold-down. I solai "
         "posati diventano piano di lavoro per il livello successivo, con i bordi protetti.",
         "Addetto al montaggio di pannelli X-lam", 35, _EDILIZIA,
         ["Gru a torre", "Autogru", "Accessori di sollevamento (brache, bilancini, ganci)",
          "Puntelli metallici", "Avvitatore elettrico", "Parapetto provvisorio",
          "Linea vita provvisoria", "Ponteggio metallico fisso", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Parapetti provvisori fissati ai pannelli di solaio prima o subito dopo la posa "
               "(UNI EN 13374) o ponteggio perimetrale; aperture nei solai chiuse (art. 146); "
               "linee di ancoraggio sui pannelli per le fasi senza protezione collettiva.",
               _DPI_ANTICADUTA),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Ogni parete puntellata con almeno due puntoni fissati prima dello sgancio dalla gru; "
               "puntoni rimossi solo dopo il collegamento a solaio e pareti adiacenti; ganci di "
               "sollevamento avvitati secondo le istruzioni del fornitore e controllati."),
             _CARICHI_SOSPESI, _IMBRACATURA, _VENTO,
         ]),

    # ======================================================================================
    # MURATURE, TRAMEZZI E PARTIZIONI
    # ======================================================================================
    # --- Murature portanti ---
    fase("MU.01", _MU, "Murature portanti",
         "Murature portanti in blocchi di laterizio",
         "Realizzazione di murature portanti in blocchi di laterizio semipieni o rettificati, posati "
         "a giunti sfalsati con malta di allettamento o colla secondo il progetto strutturale. Il "
         "materiale arriva al piano con la gru, la malta è preparata in betoniera o impastatrice; i "
         "blocchi si tagliano a misura con sega a disco.",
         "Addetto alla realizzazione di murature portanti in laterizio", 55, _EDILIZIA,
         ["Betoniera a bicchiere", "Impastatrice", "Sega a disco per murature e calcestruzzo",
          "Gru a torre", "Ponteggio metallico fisso", "Ponte su cavalletti", "Utensili manuali"], [
             _MMC_BLOCCHI, _CADUTA_PONTEGGIO, _MATERIALE_IMPALCATO, _CEMENTO, _SILICE, _POSTURE,
         ]),
    fase("MU.02", _MU, "Murature portanti",
         "Murature portanti in blocchi di calcestruzzo",
         "Posa di blocchi in calcestruzzo normale o alleggerito, pieni o forati, con malta di "
         "allettamento; nei blocchi cassero si inseriscono le armature verticali e orizzontali e si "
         "getta il calcestruzzo di riempimento. Comprende il taglio dei blocchi e la formazione "
         "delle spalle delle aperture.",
         "Addetto alla realizzazione di murature in blocchi di calcestruzzo", 50, _NC_RI_INF,
         ["Betoniera a bicchiere", "Sega a disco per murature e calcestruzzo", "Gru a torre",
          "Autopompa per calcestruzzo", "Ponteggio metallico fisso", "Ponte su cavalletti",
          "Utensili manuali"], [
             _MMC_BLOCCHI, _CADUTA_PONTEGGIO, _MATERIALE_IMPALCATO, _CEMENTO, _SILICE,
             _FERRI_SPORGENTI,
         ]),
    fase("MU.03", _MU, "Murature portanti",
         "Murature in pietra e ricostruzioni di murature in pietrame",
         "Esecuzione o ricostruzione di murature in pietra squadrata o in pietrame con malta di "
         "calce, scegliendo e sbozzando le pietre a mano e posandole a corsi con buona "
         "ammorsatura, anche nelle integrazioni di murature esistenti con la tecnica del "
         "cuci-scuci. I lavori su murature esistenti procedono per tratti brevi e con puntellature "
         "dove necessario.",
         "Addetto alla realizzazione di murature in pietra", 65, ("Ristrutturazioni", "Restauri",
                                                                  "Opere infrastrutturali"),
         ["Betoniera a bicchiere", "Sega a disco per murature e calcestruzzo", "Gru a torre",
          "Puntelli metallici", "Ponteggio metallico fisso", "Utensili manuali"], [
             _MMC_BLOCCHI, _CADUTA_PONTEGGIO, _MATERIALE_IMPALCATO,
             r("Proiezione di schegge e frammenti", 3, 2,
               "Sbozzatura delle pietre su un piano stabile e lontano dagli altri addetti; occhiali "
               "o visiera durante l'uso di mazzetta e scalpello; scalpelli con testa non "
               "slabbrata.", DPI_BASE + ", occhiali protettivi"),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Nel cuci-scuci demolire e ricostruire tratti brevi e alternati secondo le "
               "indicazioni del progettista, con puntellature dei carichi sovrastanti; nessun "
               "intervento contemporaneo su tratti adiacenti; verifica del preposto del quadro "
               "fessurativo prima di iniziare."),
             _SILICE,
         ]),
    fase("MU.04", _MU, "Murature portanti",
         "Posa di architravi e piattabande sulle aperture",
         "Posa sopra le aperture delle murature di architravi prefabbricati in laterizio armato, in "
         "calcestruzzo o in acciaio, con appoggi di lunghezza adeguata e allettamento di malta, "
         "oppure formazione di piattabande gettate in opera su cassero e puntelli. Gli elementi "
         "restano puntellati fino a maturazione della muratura o del getto.",
         "Addetto alla posa di architravi", 55, _EDILIZIA,
         ["Puntelli metallici", "Casseforme", "Gru a torre", "Ponteggio metallico fisso",
          "Ponte su cavalletti", "Utensili manuali"], [
             r("Movimentazione manuale dei carichi", 3, 3,
               "Architravi pesanti posati in due addetti o con la gru, con imbracatura adatta; "
               "elementi depositati accanto all'apertura alla quota di posa."),
             r("Crollo o ribaltamento di strutture", 2, 3,
               "Architravi e casseri delle piattabande sostenuti da puntelli fino a maturazione "
               "(art. 142, comma 2); rimozione dei sostegni solo su indicazione del preposto; nelle "
               "murature esistenti apertura del vano dopo la posa dei sostegni provvisori."),
             _IMBRACATURA, _CADUTA_PONTEGGIO, _CEMENTO,
         ]),
    # --- Murature di tamponamento e faccia a vista ---
    fase("MU.05", _MU, "Murature di tamponamento e faccia a vista",
         "Murature di tamponamento in laterizio eseguite dall'interno",
         "Realizzazione delle murature perimetrali di tamponamento in blocchi di laterizio tra i "
         "pilastri e i solai della struttura, lavorando dal solaio con ponti su cavalletti. "
         "Durante l'esecuzione il bordo del solaio resta protetto dal ponteggio o da parapetti "
         "provvisori, rimossi solo man mano che la muratura raggiunge un'altezza sufficiente.",
         "Addetto alla realizzazione di murature di tamponamento", 55, _NC_RI,
         ["Betoniera a bicchiere", "Sega a disco per murature e calcestruzzo", "Gru a torre",
          "Montacarichi a cremagliera", "Ponte su cavalletti", "Parapetto provvisorio",
          "Ponteggio metallico fisso", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Bordi del solaio protetti da ponteggio esterno o da parapetti provvisori (UNI EN "
               "13374) fino a quando la muratura non supera 1 m di altezza; parapetti tolti solo "
               "per il tratto in lavorazione e rimessi a fine giornata; i ponti su cavalletti non "
               "devono portare il piano di lavoro sopra il parapetto o il bordo del ponteggio.",
               _DPI_ANTICADUTA),
             _MMC_BLOCCHI, _MATERIALE_IMPALCATO, _CEMENTO, _SILICE,
         ]),
    fase("MU.06", _MU, "Murature di tamponamento e faccia a vista",
         "Murature di tamponamento eseguite dal ponteggio",
         "Esecuzione delle murature esterne di tamponamento o delle fodere esterne lavorando dagli "
         "impalcati del ponteggio, con approvvigionamento di blocchi e malta tramite gru o "
         "montacarichi direttamente al piano del ponteggio. Gli impalcati vengono adeguati alla "
         "quota di lavoro senza smontare parapetti e ancoraggi.",
         "Addetto alla realizzazione di murature dal ponteggio", 55, _NC_RI,
         ["Ponteggio metallico fisso", "Betoniera a bicchiere", "Montacarichi a cremagliera",
          "Gru a torre", "Sega a disco per murature e calcestruzzo", "Utensili manuali"], [
             _CADUTA_PONTEGGIO,
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Carichi sugli impalcati entro la classe del ponteggio indicata nel PiMUS; nessuna "
               "rimozione di ancoraggi o diagonali per far posto alla muratura: modifiche solo "
               "dagli addetti al montaggio e secondo il progetto del ponteggio (artt. 133-136)."),
             _MATERIALE_IMPALCATO, _MMC_BLOCCHI, _CEMENTO, _MICROCLIMA,
         ]),
    fase("MU.07", _MU, "Murature di tamponamento e faccia a vista",
         "Murature e paramenti in mattoni faccia a vista",
         "Posa di mattoni pieni o semipieni a vista, con giunti regolari e stilatura della malta, "
         "come muratura portante, paramento esterno o fodera ancorata alla muratura retrostante "
         "con connettori. Al termine si puliscono le superfici con acqua o con prodotti detergenti "
         "specifici per laterizio.",
         "Addetto alla realizzazione di murature faccia a vista", 65, _EDILIZIA,
         ["Ponteggio metallico fisso", "Betoniera a bicchiere", "Sega a disco per murature e calcestruzzo",
          "Gru a torre", "Idropulitrice", "Utensili manuali"], [
             _CADUTA_PONTEGGIO, _MATERIALE_IMPALCATO, _MMC, _SILICE, _POSTURE,
             r("Rischio chimico", 2, 3,
               "Detergenti acidi per la pulizia dei laterizi scelti tra i meno aggressivi, diluiti "
               "e applicati secondo la scheda di sicurezza, dall'alto verso il basso e su "
               "superficie prima bagnata; guanti e occhiali a maschera; acqua per il lavaggio "
               "a disposizione.", DPI_BASE + ", guanti in lattice o nitrile, occhiali a maschera, "
                                           "indumenti impermeabili"),
         ]),
    # --- Isolamenti nelle murature ---
    fase("MU.08", _MU, "Isolamenti nelle murature",
         "Posa di pannelli isolanti nelle intercapedini delle murature a cassa vuota",
         "Durante la costruzione delle murature a doppio strato si fissano al paramento interno, "
         "con tasselli o collanti, pannelli isolanti in lana minerale, polistirene o fibra di "
         "legno, sigillando i giunti, prima di chiudere con il paramento esterno. I pannelli "
         "si tagliano a misura con coltelli o seghetti.",
         "Addetto alla posa di isolanti nelle intercapedini", 50, _NC_RI,
         ["Ponteggio metallico fisso", "Ponte su cavalletti", "Trapano elettrico", "Utensili manuali"], [
             _FIBRE_ISOLANTI, _CADUTA_PONTEGGIO,
             r("Punture, tagli e abrasioni", 3, 2,
               "Taglio dei pannelli su un piano di appoggio con coltello a lama retrattile, "
               "tirando lontano dal corpo; lame sostituite quando non tagliano più.",
               DPI_BASE + ", guanti antitaglio"),
             r("Rischio chimico", 2, 2,
               "Collanti e schiume poliuretaniche usati in ambiente ventilato e secondo la scheda "
               "di sicurezza; guanti in nitrile; bombolette lontane da fonti di calore.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
             r("Incendio ed esplosione", 1, 3,
               "Isolanti combustibili (polistirene, fibra di legno) stoccati lontano da lavorazioni "
               "a caldo; nessuna saldatura o fiamma libera vicino alle intercapedini aperte; "
               "estintore a disposizione."),
         ]),
    fase("MU.09", _MU, "Isolamenti nelle murature",
         "Isolamento di intercapedini esistenti per insufflaggio",
         "Riempimento delle intercapedini di murature esistenti con isolanti sfusi (fiocchi di lana "
         "minerale, cellulosa, granuli di perlite o EPS) insufflati con macchina attraverso fori "
         "praticati nel paramento a maglia regolare. Dopo l'ispezione della cavità con "
         "endoscopio si riempie dal basso verso l'alto e si chiudono i fori con malta.",
         "Addetto all'insufflaggio di isolanti nelle intercapedini", 45, ("Ristrutturazioni", "Restauri"),
         ["Macchina insufflatrice per isolanti sfusi", "Martello perforatore (tassellatore)",
          "Ponteggio metallico fisso", "Piattaforma di lavoro elevabile", "Aspiratore con filtro HEPA",
          "Utensili manuali"], [
             r("Polveri e fibre", 3, 2,
               "Caricamento della tramoggia con sacchi aperti con cautela e in posizione "
               "sopravvento; forature con aspirazione; tubo e ugello ben fissati al foro per evitare "
               "fuoriuscite; facciale filtrante per tutta la durata dell'insufflaggio.",
               DPI_BASE + ", facciale filtrante FFP3, occhiali a maschera, tuta monouso"),
             _CADUTA_PONTEGGIO,
             r("Elettrocuzione", 1, 4,
               "Prima di forare individuare cavi e tubazioni annegati nella muratura con "
               "rilevatore e dalle planimetrie degli impianti; utensili alimentati da quadro di "
               "cantiere con differenziale."),
             _POSTURE,
         ]),
    # --- Tramezzi e partizioni interne ---
    fase("MU.10", _MU, "Tramezzi e partizioni interne",
         "Tramezzature interne in laterizio",
         "Realizzazione delle partizioni interne in mattoni forati o blocchi di laterizio di "
         "piccolo spessore, posati con malta su tracciamento a pavimento e collegati alle "
         "murature esistenti. Si lavora a terra e, per le parti alte, da ponti su cavalletti o "
         "trabattelli; il materiale arriva al piano con montacarichi o gru.",
         "Addetto alla realizzazione di tramezzature in laterizio", 55, _EDILIZIA,
         ["Betoniera a bicchiere", "Sega a disco per murature e calcestruzzo", "Montacarichi a cremagliera",
          "Ponte su cavalletti", "Trabattello", "Utensili manuali"], [
             _CADUTA_INTERNI, _MMC, _CEMENTO, _SILICE, _POSTURE,
             r("Crollo o ribaltamento di strutture", 1, 3,
               "Tramezzi alti e appena realizzati non lasciati liberi al vento nelle zone ancora "
               "senza serramenti: collegamento alle pareti laterali e puntellatura provvisoria; "
               "nessun carico appoggiato sulle pareti fresche."),
         ]),
    fase("MU.11", _MU, "Tramezzi e partizioni interne",
         "Pareti divisorie in cartongesso su orditura metallica",
         "Montaggio di pareti a secco con guide e montanti in acciaio zincato fissati a pavimento e "
         "soffitto, inserimento dell'isolante nell'orditura e chiusura con una o più lastre di "
         "gesso rivestito avvitate, secondo la UNI 11424 e le istruzioni del sistema. Comprende "
         "la stuccatura dei giunti con nastro e la carteggiatura.",
         "Addetto alla realizzazione di pareti in cartongesso", 50, _EDILIZIA,
         ["Avvitatore elettrico", "Martello perforatore (tassellatore)", "Pistola sparachiodi",
          "Trabattello", "Ponte su cavalletti", "Scala doppia", "Aspiratore con filtro HEPA",
          "Utensili manuali"], [
             _CADUTA_INTERNI,
             r("Movimentazione manuale dei carichi", 3, 2,
               "Lastre di grande formato trasportate in due tenendole in verticale, con carrelli "
               "porta lastre o sollevatori; pacchi depositati su supporti piani vicini alla zona "
               "di posa; per il soffitto uso di alzalastre.", DPI_BASE),
             r("Punture, tagli e abrasioni", 3, 2,
               "Profili tagliati con cesoie e bordi sbavati; lastre incise con coltello a lama "
               "retrattile tirando lontano dal corpo; guanti antitaglio nella manipolazione dei "
               "profili.", DPI_BASE + ", guanti antitaglio"),
             r("Polveri e fibre", 3, 2,
               "Carteggiatura dello stucco con levigatrici dotate di aspirazione o a umido; "
               "ricambio d'aria nei locali; pulizia con aspiratore.",
               DPI_BASE + ", facciale filtrante FFP2, occhiali protettivi"),
             _FIBRE_ISOLANTI,
             r("Movimenti ripetitivi degli arti superiori", 2, 2,
               "Alternanza tra avvitatura, stuccatura e taglio; avvitatori leggeri con frizione "
               "regolata e caricatori di viti; pause brevi e frequenti nelle lavorazioni a soffitto.",
               DPI_BASE),
         ]),
    fase("MU.12", _MU, "Tramezzi e partizioni interne",
         "Contropareti in cartongesso e placcaggi isolanti",
         "Realizzazione di contropareti su orditura metallica autoportante o vincolata alla parete "
         "con ganci distanziatori, oppure placcaggio diretto di lastre accoppiate a isolante "
         "incollate con malta adesiva a punti, per isolamento termico e acustico o passaggio "
         "degli impianti. Comprende la stuccatura e la finitura dei giunti.",
         "Addetto alla realizzazione di contropareti in cartongesso", 50, _EDILIZIA,
         ["Avvitatore elettrico", "Martello perforatore (tassellatore)", "Trabattello",
          "Ponte su cavalletti", "Aspiratore con filtro HEPA", "Utensili manuali"], [
             _CADUTA_INTERNI, _FIBRE_ISOLANTI,
             r("Elettrocuzione", 1, 4,
               "Prima di tassellare le pareti esistenti individuare le linee elettriche "
               "incassate con rilevatore e planimetrie; nelle ristrutturazioni circuiti "
               "interessati messi fuori tensione."),
             r("Rischio chimico", 2, 2,
               "Malte adesive e stucchi preparati secondo la scheda di sicurezza, evitando il "
               "contatto con la pelle; guanti in nitrile e occhiali durante l'impasto.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
             _MMC,
         ]),
    fase("MU.13", _MU, "Tramezzi e partizioni interne",
         "Pareti e pannelli in vetromattone",
         "Posa di diaframmi luminosi in blocchi di vetro (UNI EN 1051) con malta specifica e tondini "
         "di armatura nei giunti, oppure a secco con distanziatori e telai, entro le dimensioni "
         "massime indicate dal fabbricante e con giunti perimetrali di dilatazione. Comprende la "
         "stuccatura dei giunti e la pulizia delle facce in vetro.",
         "Addetto alla realizzazione di pareti in vetromattone", 60, _EDILIZIA,
         ["Betoniera a bicchiere", "Ponte su cavalletti", "Trabattello", "Utensili manuali"], [
             r("Punture, tagli e abrasioni", 3, 2,
               "Blocchi in vetro con spigoli scheggiati scartati e smaltiti in contenitori "
               "rigidi; manipolazione con guanti antitaglio; pulizia delle facce con spugne e non "
               "con raschietti.", DPI_BASE + ", guanti antitaglio"),
             _CADUTA_INTERNI, _CEMENTO, _MMC, _POSTURE,
         ]),
]
