"""Fasi di lavoro degli impianti: impianti tecnici per edifici (IT), impianti a fonti rinnovabili (FR)
e impianti di pubblica illuminazione (PI).

Testi scritti da zero. Fonti consultate per verificare macchine, attrezzi e riferimenti:
- D.Lgs. 81/2008: Titolo III Capo III (artt. 80-87, impianti e lavori elettrici), artt. 83 e 117
  con Allegato IX (distanze dalle parti attive), artt. 111, 115, 119, 146, 148, Titolo VI e
  Allegato XXXIII, Titolo IX (agenti chimici e cancerogeni, silice cristallina respirabile).
- INAIL, «Lavori su impianti elettrici in bassa tensione» (2018); norma CEI 11-27 (figure PES,
  PAV, PEI e procedure per lavori fuori tensione, in prossimità e sotto tensione in BT); CEI 64-8
  (Parte 6 verifiche, Sezione 722 ricarica dei veicoli elettrici); CEI EN 62305 (protezione
  contro i fulmini); CEI 0-21 (connessione degli utenti attivi in BT); D.P.R. 462/2001.
- Suva, «Energia dal tetto in sicurezza. Montaggio e manutenzione di impianti solari» (2024) e
  schede Suva sul montaggio degli ascensori; articoli PuntoSicuro su infortuni nel montaggio di
  pannelli fotovoltaici e sui vani ascensore; Guida VV.F. per l'installazione degli impianti
  fotovoltaici (nota DCPREV 1324/2012).
- UNI 7129 (impianti gas domestici fino a 35 kW), D.M. 12/04/1996 (impianti termici a gas
  oltre 35 kW), UNI 10779 e UNI EN 12845 (idranti e sprinkler), UNI EN 81-20 e D.P.R. 162/1999
  (ascensori), Reg. (UE) 2024/573 e D.P.R. 146/2018 (gas fluorurati), CEI EN IEC 62485-2
  (locali batterie), D.M. 37/2008, D.M. 10/07/2002 e D.M. 22/01/2019 (segnaletica e cantieri
  stradali in presenza di traffico).
NOTA: le ricerche in rete sono state interrotte dal limite di utilizzo durante la redazione; non
tutte le fonti elencate sono state rilette per intero e diversi riferimenti sono citati da
conoscenze normative. Prima dell'uso professionale vedere docs/verifiche-archivio.md.
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import ATTREZZO, DPI_BASE, EDILIZIA, fase, r

IT = "Impianti tecnici per edifici"
FR = "Impianti a fonti rinnovabili"
PI = "Impianti di pubblica illuminazione"

NUOVE_RIST = ("Nuove costruzioni", "Ristrutturazioni")

# Attrezzature non presenti nel CATALOGO di base.py.
MANCANTI = {
    "Paranco elettrico a catena": (
        ATTREZZO, "Sollevamento di guide, cabina, contrappeso e macchinario dal gancio in testata del "
                  "vano ascensore, dove gru e argani a bandiera non arrivano."),
    "Strumenti di misura per verifiche elettriche": (
        ATTREZZO, "Rilevatori di tensione, multimetri, misuratori di isolamento, di terra e di "
                  "intervento dei differenziali usati nelle verifiche (CEI 64-8 Parte 6) e nella "
                  "verifica dell'assenza di tensione: rischi propri da puntali e arco."),
}

# DPI per lavori all'interno degli edifici, dove gli indumenti ad alta visibilità non servono.
DPI_INT = "Casco, calzature di sicurezza, guanti"
DPI_ELETTRICO = ("Calzature di sicurezza, guanti dielettrici, visiera protettiva, indumenti protettivi "
                 "(non propaganti la fiamma)")
DPI_ANTICADUTA = DPI_BASE + ", imbracatura, cordino con assorbitore, dispositivo retrattile"

# --- Rischi riusati ---

_ELETTRO_FT = r(
    "Elettrocuzione", 2, 4,
    "Lavori eseguiti fuori tensione secondo la CEI 11-27: individuazione del circuito, sezionamento, "
    "blocco con lucchetto e cartello «lavori in corso» sul dispositivo di sezionamento, verifica "
    "dell'assenza di tensione con rilevatore idoneo su tutti i conduttori. Lavori affidati a PES o PAV "
    "designati per iscritto dal datore di lavoro (artt. 80 e 82 D.Lgs. 81/2008); lavori sotto tensione "
    "in BT solo da personale idoneo (PEI) con procedure scritte. Attrezzi isolati CEI EN 60900.",
    DPI_ELETTRICO)
_ELETTRO_ESISTENTI = r(
    "Elettrocuzione per contatto con linee esistenti nelle murature", 2, 4,
    "Nelle ristrutturazioni sezionare e bloccare i circuiti dell'area prima di forare o tracciare; "
    "individuare il percorso di cavi e tubazioni con rilevatore e con gli schemi disponibili; non "
    "affidarsi alla sola posizione di prese e interruttori.", DPI_INT)
_MMC = r(
    "Movimentazione manuale dei carichi", 3, 2,
    "Sollevamento in due persone o con mezzi ausiliari (carrelli, paranchi) per i componenti pesanti o "
    "ingombranti; percorsi sgombri; valutazione del rischio secondo il Titolo VI e l'Allegato XXXIII "
    "del D.Lgs. 81/2008.", DPI_INT)
_MMC_EST = r(
    "Movimentazione manuale dei carichi", 3, 2,
    "Sollevamento in due persone o con mezzi ausiliari per gli elementi pesanti o ingombranti; "
    "avvicinare i materiali con i mezzi il più possibile al punto di posa (Titolo VI e Allegato XXXIII "
    "del D.Lgs. 81/2008).")
_POLVERI_FORI = r(
    "Polveri e fibre", 3, 2,
    "Utensili con aspirazione alla fonte collegata ad aspiratore con filtro HEPA; nebulizzazione "
    "d'acqua dove possibile; pulizia con aspiratore e non con scopa o aria compressa. Le polveri di "
    "calcestruzzo e laterizio contengono silice cristallina respirabile (Titolo IX Capo II e "
    "Allegato XLII del D.Lgs. 81/2008).",
    DPI_INT + ", facciale filtrante FFP3, occhiali protettivi")
_TAGLI = r(
    "Punture, tagli e abrasioni", 3, 1,
    "Guanti antitaglio nella manipolazione di lamiere, canaline, profilati e tubi tagliati; sbavare "
    "subito i bordi dei tagli; cesoie e taglierini con lama protetta.",
    DPI_INT.replace("guanti", "guanti antitaglio"))
_POSTURE = r(
    "Posture incongrue", 3, 2,
    "Alternare le lavorazioni a soffitto, in ginocchio o in spazi ristretti con pause e cambi di "
    "posizione; usare piani di lavoro alla giusta altezza invece di lavorare con le braccia sopra le "
    "spalle per lunghi periodi; ginocchiere per i lavori a pavimento.", DPI_INT + ", ginocchiere")
_CADUTA_COPERTURA = r(
    "Caduta dall'alto", 3, 4,
    "Prima dell'accesso accertare la resistenza della copertura e individuare lucernari e superfici non "
    "calpestabili (art. 148 D.Lgs. 81/2008); bordi protetti con ponteggio perimetrale o parapetti "
    "provvisori; lucernari e lastre fragili coperti o protetti con reti; dove la protezione collettiva "
    "non è attuabile, imbracatura collegata a linea vita o ancoraggi conformi UNI EN 795 (art. 115). "
    "Accesso con ponteggio o scala vincolata e sporgente di almeno 1 m; lavoro mai da soli.",
    DPI_ANTICADUTA)
_CADUTA_MAT_COPERTURA = r(
    "Caduta di materiale dall'alto o a livello", 2, 3,
    "Materiali e attrezzi in copertura vincolati o raccolti in contenitori, mai appoggiati sulle falde "
    "inclinate; area sottostante delimitata; tavole fermapiede sul perimetro; sospendere il lavoro con "
    "vento forte.")
_SCIVOLAMENTI_COPERTURA = r(
    "Scivolamenti e cadute a livello", 3, 2,
    "Non lavorare su coperture bagnate, gelate o con muschio; calzature con suola antiscivolo; "
    "camminamenti o tavole sulle falde; cavi e materiali raccolti per non creare inciampi.")
_SOLE = r(
    "Microclima", 3, 2,
    "Esposizione al sole e al caldo in copertura o in campo aperto: lavori più gravosi nelle ore fresche, "
    "pause all'ombra, acqua a disposizione, copricapo; sospensione nelle giornate di allerta per "
    "ondate di calore; con il freddo indumenti adeguati.", DPI_BASE + ", copricapo, crema protettiva")
_INVESTIMENTO = r(
    "Investimento da mezzi in manovra", 2, 4,
    "Addetti a terra fuori dal raggio d'azione dei mezzi; manovre in retromarcia assistite da moviere; "
    "percorsi pedonali separati; indumenti ad alta visibilità.")
_TRAFFICO = r(
    "Investimento da traffico veicolare", 3, 4,
    "Cantiere stradale segnalato e delimitato secondo gli schemi del D.M. 10/07/2002, installato e "
    "rimosso da personale formato ai sensi del D.M. 22/01/2019; movieri o semafori nei sensi unici "
    "alternati; mezzi con luci lampeggianti e pannelli; lavori notturni solo con illuminazione "
    "dell'area. Mai lavorare fuori dall'area delimitata.",
    "Casco, calzature di sicurezza, guanti, indumenti ad alta visibilità (classe 3)")
_SOTTOSERVIZI = r(
    "Contatto con sottoservizi e linee elettriche", 2, 4,
    "Individuare prima dello scavo reti interrate (elettriche, gas, acqua, telecomunicazioni) con gli "
    "enti gestori e con cercaservizi, segnandole sul terreno; scavo a mano in prossimità; linee aeree "
    "alle distanze dell'Allegato IX o messe fuori tensione dal gestore (art. 117 D.Lgs. 81/2008).")
_SEPPELLIMENTO = r(
    "Seppellimento e sprofondamento", 2, 4,
    "Pareti dello scavo armate o a scarpa oltre 1,50 m di profondità (art. 119 D.Lgs. 81/2008) e "
    "comunque se il terreno è instabile; materiale di risulta e mezzi a distanza dal ciglio "
    "(art. 120); scala per uscire dallo scavo; nessuno nello scavo durante le manovre dell'escavatore.")
_CEMENTO = r(
    "Rischio chimico", 2, 2,
    "Il calcestruzzo fresco è alcalino e irritante per la pelle: guanti impermeabili e maniche lunghe, "
    "lavaggio immediato della pelle e degli occhi in caso di contatto; consultare le schede di "
    "sicurezza di additivi e disarmanti.", DPI_BASE + ", guanti in lattice o nitrile, stivali di sicurezza")
_ELETTRO_DC = r(
    "Elettrocuzione in corrente continua", 3, 4,
    "I moduli esposti alla luce sono sempre in tensione e le stringhe in serie raggiungono centinaia di "
    "volt in c.c.: tenere aperti i sezionatori di stringa e lato c.c. fino al collegamento finale, "
    "coprire i moduli con teli opachi se si interviene su stringhe già chiuse; connettori dello stesso "
    "tipo e costruttore, mai scollegati sotto carico; misurare tensione e polarità prima di collegare "
    "all'inverter. Lavori eseguiti da PES/PAV secondo la CEI 11-27 con attrezzi isolati.",
    "Calzature di sicurezza, guanti dielettrici (classe 0), visiera protettiva, indumenti protettivi")
_ARCO_DC = r(
    "Incendio ed esplosione", 2, 4,
    "Un arco elettrico in corrente continua non si estingue da solo e può innescare incendi: "
    "serraggio dei connettori e dei morsetti con gli attrezzi e le coppie indicate dal costruttore; "
    "cavi protetti dagli spigoli e dalle parti calde; quadri di campo lontani da materiali combustibili "
    "(Guida VV.F. 2012 sugli impianti fotovoltaici); estintore a CO2 a portata di mano.",
    DPI_ELETTRICO)
_BIOLOGICO = r(
    "Rischio biologico", 2, 2,
    "Lavori in campo aperto: indumenti chiusi a maniche lunghe, repellenti contro zecche e insetti, "
    "controllo della pelle a fine turno; vaccinazione antitetanica in regola; cassetta di pronto "
    "soccorso in cantiere.", DPI_BASE + ", stivali di sicurezza")

LAVORAZIONI = [
    # ------------------------------------------------------------------
    # IMPIANTI TECNICI PER EDIFICI
    # ------------------------------------------------------------------
    fase("IT.01", IT, "Impianto elettrico dell'edificio",
         "Esecuzione di tracce e posa di canalizzazioni e scatole per l'impianto elettrico",
         "Tracciamento dei percorsi, apertura di tracce nelle murature con scanalatrice e martello "
         "perforatore, posa di tubi corrugati, canaline e scatole da incasso o da esterno e loro "
         "fissaggio con malta o tasselli. Nei controsoffitti e nei locali tecnici posa di passerelle "
         "portacavi a soffitto.",
         "Addetto all'esecuzione di tracce e canalizzazioni per impianti elettrici", 60, EDILIZIA,
         ["Scanalatrice per murature", "Martello perforatore (tassellatore)", "Aspiratore con filtro HEPA",
          "Trabattello", "Scala doppia", "Utensili manuali"], [
             _POLVERI_FORI, _ELETTRO_ESISTENTI,
             r("Proiezione di schegge e frammenti", 3, 2,
               "Occhiali protettivi durante la scanalatura e lo scalpellamento delle tracce; persone non "
               "addette lontane dalla zona di lavoro; non scalpellare verso il viso.",
               DPI_INT + ", occhiali protettivi"),
             r("Caduta di materiale dall'alto o a livello", 2, 2,
               "Passerelle portacavi sorrette provvisoriamente fino al fissaggio definitivo delle staffe; "
               "nessuno sotto la zona di montaggio a soffitto; attrezzi riposti nei contenitori del "
               "trabattello.", DPI_INT),
             _POSTURE, _TAGLI,
         ]),
    fase("IT.02", IT, "Impianto elettrico dell'edificio",
         "Posa di cavi e conduttori e collegamento degli apparecchi di utilizzazione",
         "Infilaggio dei conduttori nelle tubazioni con sonda tirafilo, stesura dei cavi sulle "
         "passerelle e nelle dorsali, siglatura dei circuiti. Collegamento di prese, comandi, punti "
         "luce e apparecchi, con installazione dei frutti e delle placche.",
         "Addetto alla posa di cavi e al collegamento degli apparecchi elettrici", 70, EDILIZIA,
         ["Utensili manuali", "Avvitatore elettrico", "Scala doppia", "Trabattello"], [
             _ELETTRO_FT,
             r("Movimentazione manuale dei carichi", 2, 2,
               "Bobine di cavo su svolgitori o cavalletti portabobine; tiro dei cavi lunghi in più "
               "persone, con argano tiracavi per le dorsali pesanti; evitare strappi.", DPI_INT),
             _POSTURE, _TAGLI,
             r("Urti, colpi, impatti e compressioni", 2, 2,
               "Coordinare a voce il tiro dei cavi tra gli addetti agli estremi; guanti per evitare "
               "lo scorrimento del cavo tra le mani; la sonda tirafilo non va forzata verso il viso.",
               DPI_INT),
         ]),
    fase("IT.03", IT, "Impianto elettrico dell'edificio",
         "Installazione di quadri elettrici e allacciamento alla fornitura",
         "Fissaggio a parete o a pavimento dei quadri generali e di zona, cablaggio degli interruttori e "
         "attestazione delle linee in arrivo e in partenza. Collegamento della linea montante al punto "
         "di consegna del distributore, che resta in tensione a monte del contatore.",
         "Addetto all'installazione dei quadri elettrici", 45, NUOVE_RIST + ("Restauri",),
         ["Trapano elettrico", "Martello perforatore (tassellatore)", "Avvitatore elettrico",
          "Utensili manuali"], [
             _ELETTRO_FT,
             r("Ustioni", 2, 4,
               "Rischio di arco elettrico nei lavori in prossimità del punto di consegna e dei quadri già "
               "alimentati: distanze e barriere della CEI 11-27 verso le parti attive (art. 83 "
               "D.Lgs. 81/2008), schermi isolanti sui morsetti rimasti in tensione, indumenti non "
               "propaganti la fiamma e visiera; mai lavorare da soli.", DPI_ELETTRICO),
             _MMC, _TAGLI, _POLVERI_FORI,
         ]),
    fase("IT.04", IT, "Impianto elettrico dell'edificio",
         "Verifiche, prove e messa in servizio dell'impianto elettrico",
         "Esame a vista e prove strumentali previste dalla CEI 64-8 Parte 6: continuità dei conduttori "
         "di protezione, resistenza di isolamento, prova dei differenziali, misura della resistenza di "
         "terra o dell'impedenza dell'anello di guasto. Prima messa in tensione per settori e rilascio "
         "della dichiarazione di conformità (D.M. 37/2008).",
         "Addetto alle verifiche e alla messa in servizio degli impianti elettrici", 80,
         NUOVE_RIST + ("Restauri",),
         ["Strumenti di misura per verifiche elettriche", "Utensili manuali", "Scala doppia"], [
             r("Elettrocuzione", 2, 4,
               "Misure con impianto in tensione eseguite solo da PES o PAV secondo le procedure della "
               "CEI 11-27; strumenti di categoria di misura adeguata e puntali integri con protezioni; "
               "durante la prova d'isolamento avvisare gli altri addetti e segregare i circuiti sotto "
               "prova; scaricare le capacità dei cavi al termine della prova.", DPI_ELETTRICO),
             r("Ustioni", 1, 4,
               "Prima messa in tensione per singoli circuiti, con i quadri chiusi e l'operatore di lato "
               "rispetto all'apparecchio di manovra; visiera e indumenti non propaganti la fiamma.",
               DPI_ELETTRICO),
             r("Elettrocuzione di terzi durante la messa in servizio", 2, 4,
               "Comunicare alle altre imprese presenti l'inizio della messa in tensione e le zone "
               "interessate; cartelli sui quadri; scatole e frutti chiusi prima di alimentare i circuiti.",
               DPI_INT),
         ]),
    fase("IT.05", IT, "Impianto di terra e protezione dalle scariche atmosferiche",
         "Realizzazione dell'impianto di terra",
         "Posa della corda di rame nuda nello scavo di fondazione o in trincea perimetrale, infissione "
         "dei dispersori a picchetto entro pozzetti ispezionabili e collegamento al collettore di terra "
         "e ai conduttori equipotenziali delle masse estranee. L'impianto va denunciato con la "
         "dichiarazione di conformità e verificato periodicamente (D.P.R. 462/2001, art. 86 "
         "D.Lgs. 81/2008).",
         "Addetto alla realizzazione dell'impianto di terra", 40, NUOVE_RIST,
         ["Miniescavatore", "Martello demolitore", "Utensili manuali",
          "Strumenti di misura per verifiche elettriche"], [
             _SOTTOSERVIZI,
             r("Urti, colpi, impatti e compressioni", 2, 2,
               "Infissione dei picchetti con battipicchetto o testa di battuta adatta al martello; "
               "picchetto tenuto con attrezzo reggipalo e non con le mani; mazze con manico integro.",
               DPI_BASE + ", occhiali protettivi"),
             _MMC_EST, _INVESTIMENTO,
             r("Scivolamenti e cadute a livello", 2, 2,
               "Trincee aperte segnalate e protette con barriere; passerelle per l'attraversamento; "
               "pozzetti chiusi con il chiusino appena posati."),
         ]),
    fase("IT.06", IT, "Impianto di terra e protezione dalle scariche atmosferiche",
         "Installazione dell'impianto di protezione contro le scariche atmosferiche",
         "Montaggio sulla copertura di captatori ad asta o a maglia, posa delle calate lungo le facciate "
         "con supporti distanziatori e collegamento all'impianto di terra con morsetti di sezionamento, "
         "secondo il progetto redatto in base alla CEI EN 62305 (art. 84 D.Lgs. 81/2008).",
         "Addetto all'installazione dell'impianto di protezione contro i fulmini", 50, NUOVE_RIST + ("Restauri",),
         ["Ponteggio metallico fisso", "Piattaforma di lavoro elevabile", "Linea vita provvisoria",
          "Martello perforatore (tassellatore)", "Utensili manuali"], [
             _CADUTA_COPERTURA, _CADUTA_MAT_COPERTURA,
             r("Elettrocuzione da fulminazione", 1, 4,
               "Consultare le previsioni meteo e non salire in copertura o sul ponteggio con temporali in "
               "arrivo; sospendere il lavoro al primo segno di attività temporalesca e allontanarsi dalle "
               "strutture metalliche.", DPI_BASE),
             _SCIVOLAMENTI_COPERTURA, _SOLE,
         ]),
    fase("IT.07", IT, "Impianti speciali",
         "Realizzazione di impianti speciali: rete dati, citofonico e antintrusione",
         "Posa di canalizzazioni e cavi per rete dati in rame e fibra ottica, impianto citofonico o "
         "videocitofonico, antintrusione e videosorveglianza; montaggio di armadi rack, centrali, "
         "sensori, telecamere e posti esterni; terminazione, giunzione e collaudo delle linee.",
         "Addetto alla realizzazione di impianti speciali", 65, EDILIZIA,
         ["Trapano elettrico", "Martello perforatore (tassellatore)", "Scala doppia", "Trabattello",
          "Utensili manuali"], [
             r("Radiazioni ottiche", 2, 3,
               "Non guardare mai l'estremità di una fibra o di un connettore ottico, che può essere "
               "attraversato da luce laser invisibile; tappi sulle porte non utilizzate; ispezione dei "
               "connettori solo con microscopio dotato di filtro.", DPI_INT + ", occhiali protettivi"),
             r("Punture, tagli e abrasioni", 3, 2,
               "I residui di fibra di vetro tagliata penetrano nella pelle: raccoglierli in un contenitore "
               "dedicato con tappo, lavorare su un tappetino scuro, non mangiare né fumare nella zona di "
               "giunzione e lavarsi le mani a fine lavoro.", DPI_INT + ", occhiali protettivi"),
             r("Elettrocuzione", 2, 3,
               "Alimentazioni a 230 V di centrali, rack e alimentatori collegate fuori tensione dopo "
               "sezionamento del circuito dedicato; batterie tampone collegate per ultime e con attrezzi "
               "isolati.", DPI_INT),
             _POLVERI_FORI, _POSTURE,
         ]),
    fase("IT.08", IT, "Impianto idrico-sanitario e scarichi",
         "Posa delle reti di adduzione idrica e di scarico",
         "Esecuzione di tracce e forometrie, posa delle tubazioni di adduzione in multistrato, "
         "polipropilene o acciaio con collettori di distribuzione, e delle colonne e diramazioni di "
         "scarico in PVC o polietilene con le ventilazioni. Prove di tenuta delle reti in pressione "
         "e prove di scarico.",
         "Addetto alla posa delle reti idriche e di scarico", 55, EDILIZIA,
         ["Scanalatrice per murature", "Carotatrice", "Martello perforatore (tassellatore)",
          "Saldatrice per polietilene", "Cannello a gas", "Utensili manuali"], [
             _POLVERI_FORI, _ELETTRO_ESISTENTI,
             r("Getti e schizzi", 2, 2,
               "Prove di tenuta eseguite con pompa provvista di manometro, senza superare la pressione di "
               "prova prevista; raccordi e tappi controllati prima di mettere in pressione; nessuno "
               "davanti a tappi e raccordi durante la prova; scaricare la pressione prima di intervenire.",
               DPI_INT + ", occhiali protettivi"),
             r("Rischio chimico", 2, 2,
               "Colle, primer e solventi per tubi in PVC usati in locali ventilati, lontano da fiamme, "
               "secondo le schede di sicurezza; contenitori richiusi dopo l'uso.",
               DPI_INT + ", guanti in lattice o nitrile"),
             r("Rischio biologico", 2, 2,
               "Nei collegamenti a reti di scarico esistenti: chiudere gli scarichi a monte, ventilare, "
               "guanti impermeabili e lavaggio delle mani; vaccinazione antitetanica in regola.",
               DPI_INT + ", guanti in lattice o nitrile"),
             _MMC, _POSTURE,
         ]),
    fase("IT.09", IT, "Impianto idrico-sanitario e scarichi",
         "Montaggio di apparecchi sanitari e rubinetterie",
         "Posa e fissaggio di vasi, lavabi, bidet, piatti doccia e vasche, di cassette di scarico da "
         "incasso e dei telai per sanitari sospesi; montaggio di rubinetterie, sifoni e accessori, "
         "collegamento alle reti e sigillatura con silicone.",
         "Addetto al montaggio di sanitari e rubinetterie", 40, EDILIZIA,
         ["Trapano elettrico", "Martello perforatore (tassellatore)", "Utensili manuali"], [
             r("Movimentazione manuale dei carichi", 3, 2,
               "Vasche, piatti doccia di grandi dimensioni e lavabi in ceramica movimentati in due "
               "persone o con carrello; trasporto ai piani con montacarichi o ascensore di cantiere, "
               "non a mano lungo le scale.", DPI_INT),
             r("Punture, tagli e abrasioni", 3, 2,
               "La ceramica rotta ha bordi taglienti: guanti antitaglio nella movimentazione e nella "
               "rimozione dei pezzi danneggiati; imballaggi aperti con taglierino a lama retrattile.",
               DPI_INT.replace("guanti", "guanti antitaglio")),
             r("Rischio chimico", 1, 2,
               "Siliconi, sigillanti e adesivi usati con ventilazione del bagno e secondo le schede di "
               "sicurezza; guanti in nitrile.", DPI_INT + ", guanti in lattice o nitrile"),
             _POSTURE,
             r("Urti, colpi, impatti e compressioni", 2, 2,
               "Sanitari sospesi tenuti in posizione da un secondo addetto fino al serraggio dei "
               "tiranti; mani fuori dalla zona tra apparecchio e parete durante l'accostamento.", DPI_INT),
         ]),
    fase("IT.10", IT, "Impianto termico",
         "Installazione di generatori di calore, reti di distribuzione e radiatori",
         "Posa e collegamento di caldaie murali o a basamento con lo scarico dei fumi, dei vasi di "
         "espansione e dei dispositivi di sicurezza; realizzazione delle reti di distribuzione e posa "
         "di radiatori o ventilconvettori con valvole termostatiche. Riempimento, prova idraulica e "
         "prima accensione con analisi dei fumi.",
         "Addetto all'installazione di generatori di calore e radiatori", 40, EDILIZIA,
         ["Carotatrice", "Martello perforatore (tassellatore)", "Cannello a gas", "Utensili manuali",
          "Trabattello"], [
             r("Movimentazione manuale dei carichi", 3, 2,
               "Caldaie, bollitori e radiatori in ghisa movimentati con carrello portacaldaie o in più "
               "persone; generatori a basamento posizionati con mezzi di sollevamento; percorsi sgombri.",
               DPI_INT),
             r("Rischio chimico", 2, 4,
               "Alla prima accensione verificare il tiraggio e la tenuta del condotto fumi e analizzare "
               "i prodotti della combustione; locale ventilato; mai accendere con il condotto non "
               "collegato. Rilevatore di monossido di carbonio a disposizione degli addetti.", DPI_INT),
             r("Ustioni", 2, 2,
               "Durante il riempimento e la prima accensione non toccare tubazioni, valvole di sicurezza e "
               "corpi caldi; scarichi delle valvole di sicurezza convogliati; spurgo dei radiatori con "
               "impianto freddo.", DPI_INT),
             r("Getti e schizzi", 2, 2,
               "Prova idraulica con manometro e pressione non superiore a quella di prova; nessuno "
               "davanti a raccordi e tappi; scaricare l'impianto prima di intervenire sui collegamenti.",
               DPI_INT + ", occhiali protettivi"),
             _POLVERI_FORI, _POSTURE,
         ]),
    fase("IT.11", IT, "Impianto termico",
         "Posa di pannelli radianti a pavimento",
         "Posa sul solaio di fascia perimetrale e pannelli isolanti sagomati, stesura dei circuiti in "
         "tubo di polietilene reticolato o multistrato con fissaggio ai pannelli, collegamento ai "
         "collettori di zona e prova di tenuta in pressione prima del getto del massetto.",
         "Addetto alla posa di pannelli radianti a pavimento", 40, EDILIZIA,
         ["Utensili manuali", "Avvitatore elettrico"], [
             r("Posture incongrue", 4, 2,
               "Lavoro quasi interamente in ginocchio o chinati: ginocchiere, rotazione dei compiti tra "
               "gli addetti e pause per alzarsi e cambiare posizione; svolgitore per il tubo, per non "
               "srotolarlo a mano piegati.", DPI_INT + ", ginocchiere"),
             r("Scivolamenti e cadute a livello", 3, 2,
               "Camminare sui pannelli solo dove necessario e con tavole di ripartizione sopra i tubi "
               "posati; percorsi liberi da rotoli e ritagli; segnalare i dislivelli dei collettori.",
               DPI_INT),
             r("Punture, tagli e abrasioni", 2, 1,
               "Taglio dei pannelli isolanti e dei tubi con cesoie tagliatubi e taglierini a lama "
               "retrattile, tagliando lontano dal corpo.", DPI_INT),
             r("Getti e schizzi", 1, 2,
               "Prova di tenuta con pompa e manometro alla pressione prevista dal fabbricante; raccordi "
               "dei collettori serrati e controllati prima della pressurizzazione.",
               DPI_INT + ", occhiali protettivi"),
             r("Movimentazione manuale dei carichi", 2, 1,
               "Rotoli di tubo e pacchi di pannelli distribuiti nei locali con carrelli e in quantità "
               "contenute.", DPI_INT),
         ]),
    fase("IT.12", IT, "Impianto gas",
         "Realizzazione dell'impianto di adduzione del gas",
         "Posa delle tubazioni del gas dal contatore agli apparecchi, in vista o sotto traccia, in rame, "
         "acciaio o multistrato, con le ventilazioni e le aerazioni dei locali previste dalla UNI 7129 "
         "per gli impianti domestici fino a 35 kW (oltre, D.M. 12/04/1996). Prova di tenuta e messa "
         "in servizio da impresa abilitata ai sensi del D.M. 37/2008.",
         "Addetto alla realizzazione dell'impianto gas", 50, EDILIZIA,
         ["Carotatrice", "Scanalatrice per murature", "Cannello a gas", "Rilevatore multigas",
          "Utensili manuali"], [
             r("Incendio ed esplosione", 2, 4,
               "Prima di collegarsi a una rete esistente chiudere e bloccare la valvola a monte e "
               "sfiatare il tratto verso l'esterno; nessuna fiamma libera o apparecchio elettrico non "
               "idoneo durante le operazioni con gas presente; ricerca delle perdite con rilevatore o "
               "soluzione schiumogena, mai con fiamma; prova di tenuta con esito positivo prima "
               "dell'immissione del gas.", DPI_INT),
             r("Rischio chimico", 2, 3,
               "Nella messa in servizio degli apparecchi ventilare il locale e verificare con rilevatore "
               "l'assenza di gas e di monossido di carbonio; condotti fumi collegati prima "
               "dell'accensione.", DPI_INT),
             _POLVERI_FORI, _ELETTRO_ESISTENTI, _POSTURE,
         ]),
    fase("IT.13", IT, "Impianti di climatizzazione e ventilazione meccanica",
         "Installazione di unità esterne in copertura e delle linee frigorifere",
         "Sollevamento in copertura o su terrazzo delle unità motocondensanti e delle pompe di calore "
         "con autogru o autocarro con gru, posa su basamenti antivibranti, posa e brasatura delle linee "
         "frigorifere in rame, vuoto, carica del refrigerante e collegamento delle unità interne. Le "
         "operazioni sui circuiti con gas fluorurati sono riservate a personale certificato "
         "(Reg. UE 2024/573, D.P.R. 146/2018).",
         "Addetto all'installazione di impianti di climatizzazione", 35, EDILIZIA,
         ["Autogru", "Autocarro con gru", "Carotatrice", "Cannello a gas", "Linea vita provvisoria",
          "Utensili manuali"], [
             _CADUTA_COPERTURA,
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Unità imbracate ai punti indicati dal fabbricante con accessori di portata adeguata; zona "
               "di sollevamento e area sottostante interdette; addetto in copertura che guida il carico "
               "con funi e riceve il carico solo a fine discesa; segnali concordati con il gruista.",
               DPI_ANTICADUTA),
             r("Rischio chimico", 2, 3,
               "Il refrigerante liquido provoca congelamento della pelle e, in locali chiusi, può "
               "sostituire l'ossigeno: recupero con apposita macchina, mai rilascio in ambiente; carica "
               "con locale ventilato. Con refrigeranti infiammabili (R32, R290) nessuna fiamma o "
               "scintilla durante la carica e rilevatore di gas.",
               DPI_INT + ", occhiali a maschera, guanti"),
             _MMC_EST, _SOLE,
         ]),
    fase("IT.14", IT, "Impianti di climatizzazione e ventilazione meccanica",
         "Posa di canalizzazioni per ventilazione meccanica e trattamento dell'aria",
         "Montaggio di unità di trattamento aria o di recuperatori di calore, posa a soffitto o nei "
         "controsoffitti di canali in lamiera zincata o in pannelli preisolati con staffe e pendini, "
         "foratura dei passaggi a parete e solaio e installazione di bocchette, griglie e serrande "
         "tagliafuoco.",
         "Addetto alla posa di canalizzazioni aerauliche", 50, EDILIZIA,
         ["Martello perforatore (tassellatore)", "Carotatrice", "Cesoia elettrica per lamiere",
          "Trabattello", "Piattaforma di lavoro elevabile", "Utensili manuali"], [
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Tronchi di canale sollevati con sollevatore per canali o in due persone e sostenuti fino "
               "al fissaggio di tutti i pendini; tasselli adatti al supporto e alla portata; area "
               "sottostante delimitata.", DPI_INT),
             r("Punture, tagli e abrasioni", 3, 2,
               "I bordi della lamiera tagliata sono molto taglienti: guanti antitaglio e maniche lunghe; "
               "bordi sbavati e ritagli raccolti subito.",
               DPI_INT.replace("guanti", "guanti antitaglio")),
             r("Polveri e fibre", 2, 2,
               "Taglio di pannelli isolanti in lana minerale o poliuretano con lama e non con disco; "
               "aspirazione dei residui; facciale filtrante durante il taglio e la posa a soffitto.",
               DPI_INT + ", facciale filtrante FFP2, occhiali protettivi"),
             _POSTURE, _MMC,
         ]),
    fase("IT.15", IT, "Impianto antincendio",
         "Realizzazione di impianti antincendio a idranti e sprinkler",
         "Posa delle reti in acciaio o polietilene ad alta densità, montaggio di idranti, naspi e "
         "attacchi per autopompa secondo la UNI 10779, o delle reti a soffitto con gli erogatori "
         "sprinkler secondo la UNI EN 12845; installazione del gruppo di pompaggio e prove idrauliche "
         "di collaudo.",
         "Addetto alla realizzazione di impianti antincendio", 45, NUOVE_RIST,
         ["Martello perforatore (tassellatore)", "Saldatrice", "Smerigliatrice angolare",
          "Piattaforma di lavoro elevabile", "Trabattello", "Utensili manuali"], [
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Tubazioni in acciaio pesanti sollevate con mezzi idonei e sostenute fino al serraggio dei "
               "collari; staffaggi dimensionati sul peso dei tubi pieni; nessuno sotto la zona di "
               "montaggio a soffitto.", DPI_INT),
             r("Getti e schizzi", 2, 3,
               "Prove idrauliche alla pressione di collaudo con manometro tarato, dopo il controllo di "
               "tutti i giunti; area delle prove interdetta; scaricare la pressione prima di qualunque "
               "intervento.", DPI_INT + ", occhiali protettivi"),
             r("Rischio chimico", 2, 2,
               "Oli da filettatura e prodotti per giunti usati secondo le schede di sicurezza; guanti in "
               "nitrile e pulizia delle mani; fumi di saldatura aspirati nei locali chiusi.",
               DPI_INT + ", guanti in lattice o nitrile"),
             _MMC, _POSTURE, _POLVERI_FORI,
         ]),
    fase("IT.16", IT, "Impianto ascensore",
         "Montaggio dell'impianto ascensore nel vano corsa e in fossa",
         "Montaggio, da ponteggio interno al vano o dal tetto della cabina, delle staffe e delle guide "
         "di cabina e contrappeso, delle porte di piano, della cabina, del macchinario e delle funi; "
         "posa in fossa degli ammortizzatori e dei dispositivi di estremità; cablaggi del quadro di "
         "manovra, regolazioni e prove finali (Direttiva 2014/33/UE, D.P.R. 162/1999, UNI EN 81-20).",
         "Addetto al montaggio di impianti ascensore", 35, NUOVE_RIST,
         ["Paranco elettrico a catena", "Ponteggio metallico fisso", "Martello perforatore (tassellatore)",
          "Saldatrice", "Utensili manuali"], [
             r("Caduta dall'alto", 3, 4,
               "Vani di porta ai piani chiusi con protezioni rigide e bloccate, rimosse solo per il tempo "
               "del montaggio delle porte (art. 146 D.Lgs. 81/2008); impalcati del ponteggio interno "
               "completi, con distanza dalle pareti non oltre 30 cm; sul tetto di cabina parapetto e "
               "imbracatura collegata a un ancoraggio indipendente dalla cabina.", DPI_ANTICADUTA),
             r("Caduta di materiale dall'alto o a livello", 3, 4,
               "Nessun lavoro sovrapposto nel vano: chi lavora in fossa o ai piani bassi è protetto da "
               "un impalcato di sicurezza; attrezzi vincolati; guide e componenti imbracati al paranco "
               "fissato al gancio in testata, di portata verificata.", DPI_INT + ", casco con sottogola"),
             r("Cesoiamenti e stritolamenti", 2, 4,
               "Cabina e contrappeso bloccati meccanicamente prima di entrare in fossa o sotto la cabina; "
               "movimenti solo con la manovra d'ispezione e con l'addetto in posizione protetta; arresto "
               "di emergenza in fossa e sul tetto di cabina provato prima di iniziare; nessuno tra "
               "cabina, contrappeso e pareti durante le corse di prova.", DPI_INT),
             r("Elettrocuzione", 2, 4,
               "Linea di alimentazione del quadro di manovra sezionata e bloccata durante i cablaggi; "
               "prove e regolazioni sotto tensione solo da PES/PAV secondo la CEI 11-27.", DPI_ELETTRICO),
             _MMC, _POLVERI_FORI,
         ]),

    # ------------------------------------------------------------------
    # IMPIANTI A FONTI RINNOVABILI
    # ------------------------------------------------------------------
    fase("FR.01", FR, "Impianto fotovoltaico su copertura",
         "Montaggio delle strutture di supporto dei moduli fotovoltaici in copertura",
         "Tracciamento della disposizione dei moduli, smontaggio puntuale del manto o foratura della "
         "lamiera, fissaggio di staffe, ganci o zavorre e montaggio dei binari di supporto, con "
         "ripristino della tenuta all'acqua. La portata della copertura ai nuovi carichi va accertata "
         "in progetto.",
         "Addetto al montaggio delle strutture per impianti fotovoltaici", 45, NUOVE_RIST,
         ["Ponteggio metallico fisso", "Parapetto provvisorio", "Linea vita provvisoria",
          "Rete di sicurezza anticaduta", "Avvitatore elettrico", "Smerigliatrice angolare",
          "Utensili manuali"], [
             _CADUTA_COPERTURA,
             r("Caduta attraverso superfici fragili", 2, 4,
               "Lastre in fibrocemento, policarbonato e lucernari non sono calpestabili: tavole o "
               "passerelle di ripartizione e reti sottostanti o coperture di protezione; segnalare le "
               "zone fragili. Lastre di fibrocemento sospette di contenere amianto non vanno forate: "
               "serve una bonifica preventiva.", DPI_ANTICADUTA),
             _CADUTA_MAT_COPERTURA, _SCIVOLAMENTI_COPERTURA, _SOLE, _TAGLI,
         ]),
    fase("FR.02", FR, "Impianto fotovoltaico su copertura",
         "Sollevamento e posa dei moduli fotovoltaici in copertura",
         "Sollevamento dei pallet di moduli in copertura con autocarro con gru, sollevatore telescopico "
         "o montacarichi, distribuzione sulla falda e fissaggio dei moduli ai binari con morsetti, "
         "collegando tra loro i connettori dei moduli lungo la stringa.",
         "Addetto alla posa dei moduli fotovoltaici", 30, NUOVE_RIST,
         ["Autocarro con gru", "Sollevatore telescopico", "Montacarichi a cremagliera",
          "Ponteggio metallico fisso", "Linea vita provvisoria", "Avvitatore elettrico",
          "Utensili manuali"], [
             _CADUTA_COPERTURA,
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Pallet depositati solo dove la copertura ne regge il peso e su piani di sbarco protetti; "
               "moduli trasportati uno alla volta e in due persone, mai con vento forte per l'effetto "
               "vela; moduli in attesa di posa legati o zavorrati; area sottostante interdetta.",
               DPI_ANTICADUTA),
             _ELETTRO_DC,
             r("Movimentazione manuale dei carichi", 3, 2,
               "Moduli di grandi dimensioni movimentati in due persone o con ventose a maniglia; "
               "tragitti brevi sulla falda, sui camminamenti predisposti.", DPI_ANTICADUTA),
             _SOLE, _SCIVOLAMENTI_COPERTURA,
         ]),
    fase("FR.03", FR, "Impianto fotovoltaico su copertura",
         "Cablaggi lato corrente continua dell'impianto fotovoltaico",
         "Posa dei cavi solari di stringa in canali o tubazioni dalla copertura al locale tecnico, "
         "montaggio dei quadri di campo con sezionatori, fusibili e scaricatori, collegamento delle "
         "stringhe e misura delle tensioni a vuoto e della polarità prima della connessione "
         "all'inverter.",
         "Addetto ai cablaggi in corrente continua degli impianti fotovoltaici", 55, NUOVE_RIST,
         ["Strumenti di misura per verifiche elettriche", "Ponteggio metallico fisso",
          "Linea vita provvisoria", "Trapano elettrico", "Utensili manuali"], [
             _ELETTRO_DC, _ARCO_DC, _CADUTA_COPERTURA, _POSTURE, _SOLE,
         ]),
    fase("FR.04", FR, "Impianto fotovoltaico su copertura",
         "Installazione dell'inverter e collegamento alla rete",
         "Fissaggio a parete o a basamento degli inverter, collegamento degli ingressi in corrente "
         "continua e dell'uscita in corrente alternata al quadro con le protezioni e il sistema di "
         "protezione di interfaccia previsti dalla CEI 0-21; configurazione, prove e attivazione in "
         "accordo con il distributore.",
         "Addetto all'installazione di inverter per impianti fotovoltaici", 35, NUOVE_RIST,
         ["Trapano elettrico", "Strumenti di misura per verifiche elettriche", "Utensili manuali"], [
             _ELETTRO_FT,
             r("Elettrocuzione per energia residua dell'inverter", 2, 4,
               "Dopo il sezionamento dei lati c.c. e c.a. attendere il tempo di scarica dei condensatori "
               "indicato dal fabbricante e verificare l'assenza di tensione prima di aprire l'inverter; "
               "sezionatori c.c. aperti con l'inverter spento e mai sotto carico.", DPI_ELETTRICO),
             r("Movimentazione manuale dei carichi", 3, 2,
               "Inverter pesanti sollevati in due persone o con sollevatore, appoggiati sulla staffa "
               "prima del fissaggio; attenzione alle dita tra apparecchio e staffa.", DPI_INT),
             _POLVERI_FORI,
         ]),
    fase("FR.05", FR, "Impianto fotovoltaico a terra",
         "Infissione dei pali e montaggio delle strutture dell'impianto fotovoltaico a terra",
         "Picchettamento topografico delle file, infissione dei pali in acciaio con battipalo cingolato "
         "o, su terreni duri, in prefori; montaggio delle travi, dei profili e degli eventuali "
         "inseguitori monoassiali con bulloneria serrata a coppia.",
         "Addetto all'infissione dei pali e al montaggio delle strutture a terra", 30,
         ("Opere infrastrutturali", "Nuove costruzioni"),
         ["Battipalo (infissione di pali e barriere)", "Sollevatore telescopico", "Autocarro",
          "Avvitatore elettrico", "Utensili manuali"], [
             r("Urti, colpi, impatti e compressioni", 2, 4,
               "Il palo viene posizionato e guidato dalla macchina: nessun addetto lo tiene con le mani "
               "durante la battitura; l'aiutante resta fuori dal raggio di lavoro del battipalo e in "
               "vista dell'operatore; segnali concordati.", DPI_BASE + ", otoprotettori"),
             _INVESTIMENTO, _SOTTOSERVIZI, _MMC_EST,
             _SOLE, _BIOLOGICO,
         ]),
    fase("FR.06", FR, "Impianto fotovoltaico a terra",
         "Scavo e posa dei cavidotti dell'impianto fotovoltaico a terra",
         "Scavo a sezione obbligata per i cavidotti tra le file, le cabine di campo e il punto di "
         "connessione, posa dei tubi corrugati e dei pozzetti, posa della corda di terra e rinterro "
         "con nastro segnalatore. Posa delle cabine prefabbricate con autogru su basamento predisposto.",
         "Addetto allo scavo e alla posa dei cavidotti", 35, ("Opere infrastrutturali", "Nuove costruzioni"),
         ["Escavatore", "Miniescavatore", "Autocarro", "Autogru", "Piastra vibrante", "Utensili manuali"], [
             _SEPPELLIMENTO, _INVESTIMENTO, _SOTTOSERVIZI, _MMC_EST,
             r("Polveri e fibre", 2, 2,
               "Bagnare le piste e le aree di scavo con tempo secco; mezzi a velocità ridotta.",
               DPI_BASE + ", facciale filtrante FFP2"),
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Nella posa delle cabine nessuno sotto il carico sospeso o tra il manufatto e il "
               "basamento; guida con funi; sgancio solo a cabina appoggiata e stabile."),
         ]),
    fase("FR.07", FR, "Impianto fotovoltaico a terra",
         "Posa dei moduli e cablaggi dell'impianto fotovoltaico a terra",
         "Distribuzione dei moduli lungo le file con mezzi da cantiere, fissaggio alle strutture, "
         "collegamento delle stringhe, posa dei cavi nei cavidotti fino alle cassette di parallelo e "
         "agli inverter di campo, con prove di isolamento e di tensione.",
         "Addetto alla posa dei moduli e ai cablaggi dell'impianto a terra", 35,
         ("Opere infrastrutturali", "Nuove costruzioni"),
         ["Sollevatore telescopico", "Autocarro", "Avvitatore elettrico",
          "Strumenti di misura per verifiche elettriche", "Utensili manuali"], [
             _ELETTRO_DC, _ARCO_DC,
             r("Movimentazione manuale dei carichi", 3, 2,
               "Moduli prelevati dai pallet e posati in due persone; pallet avvicinati alle file con il "
               "mezzo; rotazione degli addetti nei montaggi ripetitivi.", DPI_BASE),
             _POSTURE, _SOLE, _INVESTIMENTO,
         ]),
    fase("FR.08", FR, "Impianto solare termico",
         "Installazione di collettori solari termici e del circuito solare",
         "Montaggio in copertura delle staffe e dei collettori piani o sottovuoto, posa delle tubazioni "
         "coibentate fino al bollitore e al gruppo di circolazione, riempimento del circuito con fluido "
         "termovettore antigelo e prova di tenuta.",
         "Addetto all'installazione di impianti solari termici", 40, EDILIZIA,
         ["Autocarro con gru", "Ponteggio metallico fisso", "Linea vita provvisoria",
          "Cannello a gas", "Trapano elettrico", "Utensili manuali"], [
             _CADUTA_COPERTURA, _CADUTA_MAT_COPERTURA,
             r("Ustioni", 3, 3,
               "I collettori esposti al sole e non ancora riempiti raggiungono temperature molto elevate: "
               "tenerli coperti fino al riempimento, che va fatto al mattino presto o con cielo coperto; "
               "non aprire sfiati e valvole con il circuito caldo.",
               DPI_ANTICADUTA + ", occhiali protettivi"),
             r("Rischio chimico", 1, 2,
               "Fluido termovettore a base di glicole maneggiato secondo la scheda di sicurezza, con "
               "guanti e occhiali; raccolta degli sversamenti.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
             _MMC_EST,
         ]),
    fase("FR.09", FR, "Pompe di calore",
         "Installazione di pompe di calore",
         "Posa dell'unità esterna su basamento antivibrante a terra, su terrazzo o in copertura e "
         "dell'eventuale unità interna con accumulo; collegamento idraulico, frigorifero ed elettrico, "
         "riempimento dell'impianto e messa in funzione. Le unità con refrigerante infiammabile (R290) "
         "vanno installate rispettando le distanze dalle aperture indicate dal fabbricante.",
         "Addetto all'installazione di pompe di calore", 35, EDILIZIA,
         ["Autocarro con gru", "Carotatrice", "Martello perforatore (tassellatore)", "Cannello a gas",
          "Utensili manuali"], [
             r("Movimentazione manuale dei carichi", 3, 3,
               "Unità esterne e bollitori movimentati con carrello montascale, transpallet o mezzo di "
               "sollevamento e non a braccia lungo le scale; almeno due persone nel posizionamento.",
               DPI_BASE),
             r("Rischio chimico", 2, 3,
               "Interventi sul circuito frigorifero solo da personale certificato F-gas; recupero del "
               "refrigerante con macchina dedicata; con refrigeranti infiammabili nessuna fiamma o "
               "scintilla nella zona e rilevatore di gas; protezione dal contatto con refrigerante "
               "liquido.", DPI_BASE + ", occhiali a maschera"),
             _ELETTRO_FT, _POLVERI_FORI,
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Sollevamenti su terrazzi e coperture con area sottostante interdetta e carico guidato con "
               "funi; unità ancorata al basamento prima dello sgancio."),
         ]),
    fase("FR.10", FR, "Impianto geotermico",
         "Perforazione e posa delle sonde geotermiche verticali",
         "Perforazione a rotazione o rotopercussione con sonda montata su cingoli, gestione dei fluidi "
         "e dei detriti di perforazione, inserimento delle sonde a U in polietilene zavorrate e "
         "cementazione del foro dal fondo con miscela di bentonite e cemento.",
         "Addetto alla perforazione e alla posa di sonde geotermiche", 30, NUOVE_RIST,
         ["Sonda di perforazione (micropali, tiranti, sondaggi)", "Motocompressore",
          "Pompa per malte e iniezioni", "Escavatore", "Autocarro con gru", "Utensili manuali"], [
             r("Getti e schizzi", 3, 2,
               "Fluidi e detriti risalgono dal foro con violenza, soprattutto con l'aria compressa: "
               "deviatore a bocca foro e vasche di raccolta; nessuno davanti alla bocca del foro; in "
               "presenza di falde in pressione predisporre la chiusura della testa del foro.",
               DPI_BASE + ", occhiali a maschera, indumenti impermeabili, otoprotettori"),
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "La bobina della sonda in polietilene immagazzina energia: svolgerla con svolgitore e "
               "tagliare le reggette dalla parte opposta; nessuno tra la sonda in discesa e la macchina.",
               DPI_BASE + ", occhiali protettivi"),
             _CEMENTO,
             r("Scivolamenti e cadute a livello", 3, 2,
               "Area attorno alla macchina mantenuta pulita dai fanghi; piano di lavoro livellato; "
               "fosse e vasche di raccolta recintate.", DPI_BASE + ", stivali di sicurezza"),
             _SOTTOSERVIZI, _MMC_EST,
         ]),
    fase("FR.11", FR, "Impianto geotermico",
         "Collegamento delle sonde geotermiche e realizzazione del circuito",
         "Scavo delle trincee orizzontali, collegamento delle sonde ai collettori in pozzetto con "
         "saldatura per elettrofusione o testa a testa, posa delle linee fino alla centrale termica, "
         "prova di pressione e riempimento con fluido termovettore.",
         "Addetto al collegamento delle sonde geotermiche", 40, NUOVE_RIST,
         ["Miniescavatore", "Saldatrice per polietilene", "Piastra vibrante", "Utensili manuali"], [
             _SEPPELLIMENTO, _SOTTOSERVIZI,
             r("Getti e schizzi", 2, 3,
               "Prova di pressione con manometro e valvola di sicurezza, dopo il raffreddamento completo "
               "delle saldature; nessuno sopra le giunzioni durante la prova.",
               DPI_BASE + ", occhiali protettivi"),
             r("Rischio chimico", 1, 2,
               "Fluido termovettore antigelo maneggiato con guanti e occhiali secondo la scheda di "
               "sicurezza; sversamenti raccolti e non dispersi nel terreno.",
               DPI_BASE + ", guanti in lattice o nitrile"),
             _POSTURE, _MMC_EST,
         ]),
    fase("FR.12", FR, "Sistemi di accumulo",
         "Installazione di sistemi di accumulo elettrochimico",
         "Posizionamento dei moduli batteria e del relativo armadio o rack in locale idoneo per "
         "ventilazione, temperatura e distanze dai materiali combustibili, collegamento all'inverter "
         "ibrido o al convertitore dedicato e configurazione del sistema di gestione delle batterie.",
         "Addetto all'installazione di sistemi di accumulo", 25, NUOVE_RIST,
         ["Trapano elettrico", "Carrello elevatore", "Strumenti di misura per verifiche elettriche",
          "Utensili manuali"], [
             r("Elettrocuzione", 2, 4,
               "Le batterie non si possono mettere fuori tensione: collegamenti tra i moduli eseguiti con "
               "sezionatore o fusibili del pacco aperti, attrezzi isolati CEI EN 60900 e senza oggetti "
               "metallici indossati (anelli, orologi); morsetti protetti con le calotte; lavori da PES/PAV "
               "secondo la CEI 11-27.", DPI_ELETTRICO),
             r("Ustioni", 2, 4,
               "Un cortocircuito sui morsetti genera arco e correnti elevatissime: mai appoggiare attrezzi "
               "sulle batterie, collegare prima il polo indicato dal fabbricante, serrare a coppia.",
               DPI_ELETTRICO),
             r("Incendio ed esplosione", 1, 4,
               "Non installare moduli danneggiati, deformati o caduti; rispettare le condizioni del "
               "fabbricante; per batterie al piombo ventilazione del locale contro l'accumulo di "
               "idrogeno (CEI EN IEC 62485-2); estintore adatto in prossimità.", DPI_INT),
             r("Movimentazione manuale dei carichi", 3, 2,
               "Moduli batteria pesanti movimentati con carrello o in due persone, nell'imballo fino al "
               "punto di posa.", DPI_INT),
             r("Rischio chimico", 1, 3,
               "In caso di perdita di elettrolito evitare il contatto e l'inalazione, ventilare e seguire "
               "le istruzioni della scheda di sicurezza; occhiali e guanti in nitrile.",
               DPI_INT + ", guanti in lattice o nitrile, occhiali a maschera"),
         ]),
    fase("FR.13", FR, "Infrastrutture di ricarica dei veicoli elettrici",
         "Installazione di colonnine e stazioni di ricarica per veicoli elettrici",
         "Taglio della pavimentazione e scavo per cavidotti e basamento, getto o posa del plinto "
         "prefabbricato, montaggio della colonnina o del wallbox, posa della linea dedicata dal quadro "
         "con le protezioni previste dalla CEI 64-8 Sezione 722, collegamento e prove funzionali.",
         "Addetto all'installazione di stazioni di ricarica", 35, ("Nuove costruzioni", "Ristrutturazioni",
                                                                   "Opere infrastrutturali"),
         ["Tagliasfalto a disco", "Miniescavatore", "Autocarro con gru", "Piastra vibrante",
          "Utensili manuali"], [
             _SOTTOSERVIZI, _ELETTRO_FT,
             r("Investimento da mezzi in manovra", 2, 4,
               "Nei parcheggi aperti al pubblico area di lavoro recintata e segnalata, con percorsi "
               "pedonali alternativi; su strada cantiere segnalato secondo il D.M. 10/07/2002.",
               "Casco, calzature di sicurezza, guanti, indumenti ad alta visibilità (classe 3)"),
             _CEMENTO, _MMC_EST,
         ]),
    fase("FR.14", FR, "Impianto mini eolico",
         "Realizzazione della fondazione dell'aerogeneratore mini eolico",
         "Scavo per il plinto di fondazione, posa dei tirafondi o della dima di ancoraggio della torre "
         "con controllo topografico della posizione, armatura, getto del calcestruzzo e posa dei "
         "cavidotti verso il quadro di connessione.",
         "Addetto alla realizzazione della fondazione dell'aerogeneratore", 30,
         ("Nuove costruzioni", "Opere infrastrutturali"),
         ["Escavatore", "Autobetoniera", "Autopompa per calcestruzzo", "Vibratore per calcestruzzo",
          "Autocarro con gru", "Utensili manuali"], [
             _SEPPELLIMENTO,
             r("Caduta dall'alto", 2, 3,
               "Scavo delimitato con parapetti o barriere a distanza dal ciglio; accesso al fondo scavo "
               "con scala vincolata; armature sporgenti protette con cappellotti."),
             _CEMENTO, _INVESTIMENTO, _MMC_EST, _BIOLOGICO,
         ]),
    fase("FR.15", FR, "Impianto mini eolico",
         "Montaggio della torre e dell'aerogeneratore mini eolico",
         "Assemblaggio a terra della navicella e del rotore, sollevamento della torre tubolare o a "
         "traliccio con autogru o con sistema ribaltabile, serraggio dei tirafondi, montaggio della "
         "navicella e delle pale in quota e cablaggio fino al quadro di connessione.",
         "Addetto al montaggio di aerogeneratori mini eolici", 25, ("Nuove costruzioni", "Opere infrastrutturali"),
         ["Autogru", "Piattaforma di lavoro elevabile", "Avvitatore elettrico", "Utensili manuali"], [
             r("Caduta dall'alto", 2, 4,
               "Lavori in testa alla torre da PLE o, per salire sulla torre, con scala dotata di "
               "dispositivo anticaduta di tipo guidato (UNI EN 353-1) e imbracatura sempre collegata; "
               "piano di soccorso in quota con addetti formati.", DPI_ANTICADUTA),
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Area di montaggio interdetta per un raggio pari almeno all'altezza della torre; nessuno "
               "sotto i carichi sospesi; sollevamenti sospesi con vento oltre i limiti del fabbricante "
               "della gru e dell'aerogeneratore; attrezzi vincolati in quota.",
               DPI_BASE + ", casco con sottogola"),
             r("Urti, colpi, impatti e compressioni", 2, 4,
               "Rotore bloccato con il freno di stazionamento e il blocco meccanico durante il montaggio "
               "e i cablaggi; pale guidate con funi; mani fuori dai punti di accoppiamento.",
               DPI_ANTICADUTA),
             r("Elettrocuzione", 2, 4,
               "Il generatore produce tensione appena il rotore gira: collegamenti al quadro con "
               "aerogeneratore bloccato e linea sezionata; lavori da PES/PAV secondo la CEI 11-27.",
               DPI_ELETTRICO),
             _MMC_EST,
         ]),

    # ------------------------------------------------------------------
    # IMPIANTI DI PUBBLICA ILLUMINAZIONE
    # ------------------------------------------------------------------
    fase("PI.01", PI, "Opere civili per la pubblica illuminazione",
         "Scavo e posa di cavidotti e pozzetti per la pubblica illuminazione",
         "Taglio della pavimentazione stradale, scavo a sezione ristretta lungo marciapiedi e "
         "carreggiate, posa dei tubi corrugati e dei pozzetti prefabbricati con chiusini, rinterro "
         "compattato e ripristino provvisorio o definitivo della pavimentazione.",
         "Addetto allo scavo e alla posa di cavidotti per illuminazione pubblica", 40,
         ("Opere infrastrutturali", "Nuove costruzioni"),
         ["Tagliasfalto a disco", "Miniescavatore", "Escavatore", "Autocarro", "Piastra vibrante",
          "Utensili manuali"], [
             _TRAFFICO, _SOTTOSERVIZI, _SEPPELLIMENTO, _INVESTIMENTO,
             r("Movimentazione manuale dei carichi", 3, 2,
               "Pozzetti e chiusini posati con l'escavatore e accessori di sollevamento idonei, non a "
               "mano; chiusini pesanti movimentati con apposito sollevachiusini."),
             r("Scivolamenti e cadute a livello", 2, 2,
               "Scavi aperti protetti con barriere e illuminati di notte; passerelle per gli accessi "
               "pedonali alle abitazioni; pozzetti chiusi a fine giornata."),
         ]),
    fase("PI.02", PI, "Opere civili per la pubblica illuminazione",
         "Realizzazione dei plinti di fondazione dei pali",
         "Scavo per il plinto, posa del plinto prefabbricato con foro per il palo e pozzetto "
         "incorporato oppure getto in opera con cassero a perdere e tubo per l'alloggiamento del palo, "
         "collegamento al cavidotto e rinfianco.",
         "Addetto alla realizzazione dei plinti per pali di illuminazione", 35,
         ("Opere infrastrutturali", "Nuove costruzioni"),
         ["Miniescavatore", "Autocarro con gru", "Autobetoniera", "Vibratore per calcestruzzo",
          "Utensili manuali"], [
             _TRAFFICO, _SOTTOSERVIZI,
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Plinti prefabbricati sollevati con gli inserti di sollevamento previsti; nessuno nello "
               "scavo durante la discesa; guida con funi e sgancio a plinto appoggiato."),
             _CEMENTO,
             r("Caduta dall'alto", 2, 2,
               "Scavi dei plinti coperti o protetti con barriere quando non presidiati, anche di notte; "
               "segnalazione luminosa."),
         ]),
    fase("PI.03", PI, "Installazione di pali e corpi illuminanti",
         "Posa e rizzatura dei pali di illuminazione",
         "Scarico dei pali, imbracatura e sollevamento con autogru o autocarro con gru, inserimento nel "
         "foro del plinto, messa a piombo e bloccaggio con cunei e sabbia, sigillatura del colletto e "
         "montaggio delle morsettiere e degli sbracci.",
         "Addetto alla posa e rizzatura dei pali", 30, ("Opere infrastrutturali", "Nuove costruzioni"),
         ["Autocarro con gru", "Autogru", "Utensili manuali"], [
             r("Elettrocuzione per vicinanza a linee aeree", 2, 4,
               "Verificare prima la presenza di linee elettriche aeree: palo e braccio della gru sempre "
               "alle distanze minime dell'Allegato IX del D.Lgs. 81/2008, altrimenti linea messa fuori "
               "tensione dal gestore (artt. 83 e 117); preposto che sorveglia le distanze durante la "
               "rotazione."),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Palo sganciato dalla gru solo dopo il bloccaggio con i cunei e la verifica della "
               "verticalità; nessuno nel raggio di caduta del palo durante sollevamento e rizzatura; "
               "imbracatura sopra il baricentro con accessori di portata adeguata."),
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "Palo guidato con funi e non con le mani nella fase di inserimento; mani fuori dal foro del "
               "plinto; comunicazione a gesti o via radio con il gruista."),
             _TRAFFICO, _MMC_EST,
         ]),
    fase("PI.04", PI, "Installazione di pali e corpi illuminanti",
         "Posa dei cavi e collegamenti elettrici dell'impianto di illuminazione",
         "Infilaggio dei cavi nei cavidotti con sonda e argano tiracavi tra i pozzetti, giunzioni e "
         "derivazioni in muffola o nelle morsettiere a base palo, collegamento dei dispersori e dei "
         "conduttori di protezione per gli impianti non in classe II, prove di isolamento.",
         "Addetto alla posa dei cavi e ai collegamenti dell'illuminazione pubblica", 50,
         ("Opere infrastrutturali", "Nuove costruzioni"),
         ["Autocarro", "Strumenti di misura per verifiche elettriche", "Utensili manuali"], [
             r("Elettrocuzione", 2, 4,
               "Collegamenti a linee esistenti solo dopo sezionamento e blocco del quadro di comando e "
               "verifica dell'assenza di tensione in loco, perché le linee possono essere alimentate da "
               "più quadri o restare in tensione per errori di schema; lavori da PES/PAV secondo la "
               "CEI 11-27.", DPI_ELETTRICO),
             _TRAFFICO, _POSTURE,
             r("Movimentazione manuale dei carichi", 2, 2,
               "Bobine su cavalletto svolgitore o sul cassone dell'autocarro; tiro dei cavi lunghi con "
               "argano tiracavi o in più persone coordinate."),
             r("Rischio chimico", 1, 2,
               "Resine bicomponenti per giunzioni miscelate e colate con guanti in nitrile, secondo la "
               "scheda di sicurezza.", DPI_BASE + ", guanti in lattice o nitrile"),
         ]),
    fase("PI.05", PI, "Installazione di pali e corpi illuminanti",
         "Montaggio di armature e corpi illuminanti con piattaforma di lavoro elevabile",
         "Salita in quota con PLE o autocarro con cestello, montaggio dell'armatura sullo sbraccio o "
         "testa palo, regolazione dell'inclinazione e del puntamento, collegamento dei conduttori dalla "
         "morsettiera, anche su strada aperta al traffico.",
         "Addetto al montaggio di corpi illuminanti", 40, ("Opere infrastrutturali", "Nuove costruzioni"),
         ["Autocarro con cestello", "Piattaforma di lavoro elevabile", "Utensili manuali"], [
             _TRAFFICO,
             r("Elettrocuzione", 2, 4,
               "Linea del circuito sezionata al quadro e verificata in loco prima del collegamento; con "
               "linee aeree vicine (anche di altri gestori) cestello alle distanze dell'Allegato IX o "
               "linea messa fuori tensione (art. 117 D.Lgs. 81/2008).", DPI_ELETTRICO),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Area sotto il cestello delimitata e libera da pedoni e veicoli; attrezzi e minuteria "
               "vincolati o nel cestello; armatura fissata al cestello durante la salita.",
               DPI_BASE + ", casco con sottogola"),
             r("Radiazioni ottiche", 2, 2,
               "Non guardare direttamente le sorgenti LED accese durante le prove di funzionamento; "
               "accensioni di prova con l'addetto non affacciato all'apparecchio.", DPI_BASE),
             _SOLE,
         ]),
    fase("PI.06", PI, "Installazione di pali e corpi illuminanti",
         "Installazione dei quadri di comando dell'illuminazione pubblica",
         "Posa dell'armadio stradale su basamento, cablaggio degli interruttori, del contattore, dei "
         "regolatori di flusso e degli orologi astronomici, collegamento delle linee in partenza e "
         "allaccio al punto di consegna del distributore, con verifiche e prima messa in tensione.",
         "Addetto all'installazione dei quadri di illuminazione pubblica", 35,
         ("Opere infrastrutturali", "Nuove costruzioni"),
         ["Autocarro con gru", "Strumenti di misura per verifiche elettriche", "Utensili manuali"], [
             _ELETTRO_FT,
             r("Ustioni", 2, 4,
               "Rischio d'arco nei lavori in prossimità del punto di consegna, che resta in tensione: "
               "distanze e schermi della CEI 11-27, visiera e indumenti non propaganti la fiamma, "
               "secondo addetto presente.", DPI_ELETTRICO),
             _TRAFFICO, _MMC_EST, _CEMENTO,
         ]),
    fase("PI.07", PI, "Manutenzione e riqualificazione della pubblica illuminazione",
         "Rimozione e sostituzione di corpi illuminanti esistenti",
         "Sezionamento del circuito, smontaggio da PLE delle armature esistenti, calo a terra e "
         "conferimento come rifiuti di apparecchiature elettriche (RAEE), montaggio dei nuovi "
         "apparecchi, generalmente a LED, verifica dello stato di palo e sbraccio e prove di "
         "funzionamento.",
         "Addetto alla sostituzione di corpi illuminanti", 45, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Autocarro con cestello", "Piattaforma di lavoro elevabile", "Autocarro", "Utensili manuali"], [
             _TRAFFICO,
             r("Elettrocuzione", 2, 4,
               "Sezionamento e blocco del quadro e verifica dell'assenza di tensione a base palo e in "
               "testa; nei vecchi apparecchi scaricare i condensatori di rifasamento prima di toccare "
               "i morsetti; con linee aeree vicine, distanze dell'Allegato IX.", DPI_ELETTRICO),
             r("Rischio chimico", 2, 3,
               "Le lampade a scarica contengono mercurio: smontarle intere, imballarle e conferirle "
               "come RAEE; in caso di rottura raccogliere i frammenti con guanti, senza aspirapolvere. "
               "Condensatori di vecchi apparecchi possono contenere PCB: non aprirli e smaltirli come "
               "rifiuto pericoloso.", DPI_BASE + ", guanti in lattice o nitrile, facciale filtrante FFP2"),
             r("Crollo o ribaltamento di strutture", 1, 4,
               "Prima di salire o di caricare lo sbraccio controllare a vista la corrosione alla base e "
               "al colletto del palo; pali ammalorati non vanno usati come appoggio e si segnalano al "
               "committente.", DPI_BASE),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Apparecchi smontati deposti nel cestello e calati a terra, mai lanciati; area sotto il "
               "cestello delimitata.", DPI_BASE + ", casco con sottogola"),
             _SOLE,
         ]),
]
