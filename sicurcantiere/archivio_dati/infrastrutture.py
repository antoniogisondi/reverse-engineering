"""Fasi di lavoro per reti di urbanizzazione, lavori stradali e sistemazioni esterne.

Le fasi UR.*, SR.* e SE.* sostituiscono, con maggiore dettaglio, le fasi generiche IN.02
("Posa di condotte e pozzetti"), IN.03 ("Fresatura e pavimentazione stradale") e IN.04
("Segnaletica stradale") di archivio.py.

Testi redatti per questo progetto. Fonti consultate (solo come riferimento, nessun testo copiato):
- D.Lgs. 81/2008: Titolo IV capo II (artt. 118, 119, 120, 121 scavi; art. 117 e Allegato IX
  lavori in prossimità di parti attive), art. 66 e Allegato IV p. 3 (ambienti sospetti di
  inquinamento), art. 161 c. 2-bis (segnaletica stradale), art. 73 c. 5 (abilitazione PLE),
  Titolo IX (agenti chimici e cancerogeni), Titolo X (agenti biologici), Allegato XXXIII.
- D.M. 22/01/2019 (procedure di apposizione della segnaletica stradale in presenza di traffico,
  Allegati I e II) e sintesi delle novità rispetto al D.M. 04/03/2013 (PuntoSicuro);
  D.M. 10/07/2002 (disciplinare degli schemi segnaletici temporanei); D.P.R. 495/1992 art. 42.
- D.P.R. 177/2011 (qualificazione delle imprese in ambienti confinati), manuale illustrato INAIL
  per i lavori in ambienti sospetti di inquinamento o confinati (art. 3 c. 3), scheda INAIL 2020,
  schede InforMO della Regione Emilia-Romagna sugli infortuni in ambienti confinati.
- INAIL, "Asfaltatori - profili di rischio nei comparti produttivi" (fumi di bitume, IPA).
- UNI EN 1610 (posa e collaudo delle fognature), UNI EN 805 (reti idriche esterne agli edifici),
  UNI 10520 e UNI 10521 (saldatura del polietilene), UNI 9737 (qualifica dei saldatori PE),
  D.M. 16/04/2008 e UNI EN 12007 (reti di distribuzione del gas), UNI/PdR 26.01:2017 (tecnologie
  a basso impatto per infrastrutture interrate), D.M. 01/10/2013 (scavo e ripristino per
  infrastrutture digitali, minitrincea), UNI EN 1317 e D.M. 21/06/2004 (barriere di sicurezza),
  UNI EN 1436 e UNI EN 12899-1 (segnaletica), UNI EN 1176 e UNI EN 1177 (aree gioco),
  UNI EN ISO 20471 (alta visibilità), D.Lgs. 150/2012 (prodotti fitosanitari), Accordo
  Stato-Regioni 22/02/2012 (abilitazione degli operatori di PLE).
Contenuti da verificare e adattare dal coordinatore al cantiere specifico.
NOTA: le ricerche in rete sono state interrotte dal limite di utilizzo durante la redazione; non
tutte le fonti elencate sono state rilette per intero e diversi riferimenti sono citati da
conoscenze normative. Prima dell'uso professionale vedere docs/verifiche-archivio.md.
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import ATTREZZO, DPI_BASE, MACCHINA, TUTTE, fase, r

UR = "Lavori di urbanizzazione e reti"
SR = "Lavori stradali"
SE = "Sistemazioni esterne e aree verdi"

INFRA = ("Opere infrastrutturali", "Nuove costruzioni")
INFRA_RISTR = ("Opere infrastrutturali", "Nuove costruzioni", "Ristrutturazioni")
ESTERNI = ("Nuove costruzioni", "Ristrutturazioni", "Opere infrastrutturali")

MANCANTI: dict[str, tuple[str, str]] = {
    "Spanditrice di emulsione bituminosa": (
        MACCHINA, "Autocarro con cisterna coibentata e barra di spruzzatura per la mano d'attacco; "
                  "non rappresentabile con «Autocarro» per i rischi propri (getti caldi, barra, lancia)."),
    "Macchina per minitrincea (fresa a disco)": (
        MACCHINA, "Fresatrice a disco diamantato con aspirazione per tagli stretti e profondi nella "
                  "pavimentazione (D.M. 01/10/2013); diversa dal tagliasfalto per potenza e profondità."),
    "Treppiede con dispositivo di recupero": (
        ATTREZZO, "Sistema di accesso e recupero (treppiede con verricello o arrotolatore) per la "
                  "discesa e l'evacuazione da pozzetti e camerette; l'argano da cantiere non è un "
                  "dispositivo di salvataggio per persone."),
}

# --- DPI ricorrenti ---
DPI_STRADA = "Casco, calzature di sicurezza, guanti, indumenti ad alta visibilità in classe 3"
DPI_FOGNA = ("Casco, stivali di sicurezza, guanti in lattice o nitrile, indumenti impermeabili, "
             "indumenti ad alta visibilità, occhiali protettivi")
DPI_CONFINATI = ("Casco con sottogola, stivali di sicurezza, guanti in lattice o nitrile, imbracatura, "
                 "indumenti protettivi, autorespiratore (per l'emergenza)")
DPI_CEMENTO = DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"
DPI_BITUME = ("Casco, calzature di sicurezza, guanti, indumenti ad alta visibilità in classe 3, "
              "indumenti protettivi, occhiali protettivi")
DPI_VERDE = DPI_BASE + ", copricapo, crema protettiva"

# --- Rischi riusati ---
INV_TRAFFICO = r(
    "Investimento da veicoli in transito", 3, 4,
    "Area di lavoro delimitata e presegnalata con gli schemi del D.M. 10/07/2002 e posata con le "
    "procedure del D.M. 22/01/2019 (art. 161 c. 2-bis D.Lgs. 81/2008); squadra composta solo da "
    "addetti formati secondo l'Allegato II del decreto; non uscire mai dalla zona delimitata; "
    "spostamenti a piedi ridotti al minimo, rivolti verso il traffico; lavoro sospeso con nebbia, "
    "neve o visibilità ridotta; illuminazione e luci gialle lampeggianti nelle ore notturne.",
    DPI_STRADA)
INV_MEZZI = r(
    "Investimento da mezzi in manovra", 3, 4,
    "Nessuno nel raggio d'azione degli escavatori e dietro gli autocarri in retromarcia; manovre "
    "guidate da un addetto a terra in contatto visivo con il conducente; avvisatori acustici e "
    "luminosi di retromarcia efficienti; percorsi pedonali separati da quelli dei mezzi; "
    "indumenti ad alta visibilità.")
SEPPELLIMENTO = r(
    "Seppellimento e sprofondamento", 2, 4,
    "Scavi più profondi di 1,50 m armati con blindaggi o sagomati con pareti a scarpa adeguate al "
    "terreno (art. 119 D.Lgs. 81/2008), con l'armatura posata man mano che lo scavo avanza; "
    "materiali di risulta, tubi e mezzi lontani dal ciglio (art. 120); verifica delle pareti dopo "
    "piogge, gelo o vibrazioni e prima di ogni ripresa; si lavora solo all'interno del tratto armato; "
    "il blindaggio si toglie dal basso verso l'alto senza persone nello scavo.")
CADUTA_SCAVO = r(
    "Caduta dall'alto nello scavo", 2, 3,
    "Bordi degli scavi aperti protetti con parapetto provvisorio o delimitati a distanza con "
    "barriere; attraversamenti solo su passerelle con parapetti; discesa con scale a mano "
    "vincolate che sporgono almeno 1 m oltre il ciglio; scavo coperto o recintato a fine turno.")
SOTTOSERVIZI = r(
    "Contatto con sottoservizi in esercizio (cavi elettrici, gas, acqua)", 2, 4,
    "Planimetrie degli enti gestori acquisite prima dello scavo e reti localizzate con "
    "cercaservizi e saggi a mano; tracciati segnati sul terreno; a meno di circa 50 cm dalle reti "
    "si scava solo a mano o per aspirazione; in caso di danno a una condotta gas si allontanano le "
    "persone, si spengono i motori e si avvisano il gestore e i Vigili del Fuoco (art. 117 e "
    "Allegato IX D.Lgs. 81/2008).")
CARICO_SOSPESO = r(
    "Caduta di materiale dall'alto o a livello", 2, 4,
    "Tubi e manufatti imbracati con fasce tessili, bilancini o ganci dedicati di portata adeguata, "
    "controllati prima dell'uso; nessuno sotto il carico né nello scavo durante la calata; guida "
    "con funi; gli addetti si avvicinano solo a carico quasi fermo, fuori dalla traiettoria; "
    "elementi a terra bloccati con cunei contro il rotolamento.")
SCHIACCIAMENTO_GIUNTI = r(
    "Urti, colpi, impatti e compressioni", 2, 3,
    "Innesto dei tubi con tirfor, leva o benna a velocità ridotta e su comando dell'addetto; mani "
    "mai tra bicchiere e punta o tra tubo e parete dello scavo; segnali convenuti tra addetto e "
    "manovratore.")
MMC = r(
    "Movimentazione manuale dei carichi", 3, 2,
    "Elementi pesanti movimentati con mezzi di sollevamento o carrelli; sollevamenti manuali in "
    "due per i pezzi più pesanti, valutati con i criteri dell'Allegato XXXIII (UNI ISO 11228); "
    "prese sicure, carico vicino al corpo, pause e rotazione dei compiti.")
BIOLOGICO_FOGNA = r(
    "Rischio biologico", 3, 3,
    "Reflui e fanghi considerati infetti (Titolo X D.Lgs. 81/2008); guanti impermeabili, stivali e "
    "indumenti dedicati, lavati separatamente; divieto di mangiare, bere e fumare durante il "
    "lavoro; acqua e detergente per le mani sul posto; profilassi antitetanica e valutazione di "
    "altre vaccinazioni con il medico competente; disinfezione immediata di ogni ferita.", DPI_FOGNA)
GAS_FOGNA = r(
    "Ambienti confinati o sospetti di inquinamento", 2, 4,
    "Possibile presenza di idrogeno solforato, metano e carenza di ossigeno nei collettori e negli "
    "scavi vicini (art. 121 D.Lgs. 81/2008): misura con rilevatore multigas prima e durante il "
    "lavoro; nessuno si affaccia o scende in pozzetti aperti senza la procedura degli ambienti "
    "confinati; tappi o palloni otturatori sulle immissioni attive; ventilazione forzata se "
    "necessario.", DPI_FOGNA)
MICROCLIMA = r(
    "Microclima", 3, 2,
    "Con il caldo: lavori pesanti nelle ore fresche, pause all'ombra, acqua fresca disponibile, "
    "sorveglianza reciproca dei segni di colpo di calore, rispetto delle ordinanze regionali; con "
    "il freddo e la pioggia: indumenti protettivi, pause in ambiente riscaldato.",
    DPI_BASE + ", copricapo, indumenti per il freddo")
SOLE = r(
    "Radiazioni ottiche", 3, 2,
    "Radiazione solare naturale: copricapo con falda o paranuca, indumenti a maniche lunghe, "
    "crema solare ad alta protezione sulle parti scoperte, occhiali con filtro UV; turni che "
    "riducano l'esposizione nelle ore centrali.", DPI_VERDE)
SCIVOLAMENTI = r(
    "Scivolamenti e cadute a livello", 2, 2,
    "Area di lavoro ordinata, senza attrezzi e materiali sparsi; fango e acqua drenati; percorsi "
    "illuminati di notte; calzature con suola antiscivolo.")
CEMENTO = r(
    "Rischio chimico", 2, 2,
    "Malte e calcestruzzi alcalini e sensibilizzanti per la pelle: guanti in nitrile, maniche "
    "lunghe, occhiali; lavaggio immediato con acqua in caso di contatto; prodotti con cromo VI "
    "ridotto come previsto dal REACH; schede di sicurezza disponibili.", DPI_CEMENTO)
FUMI_BITUME = r(
    "Rischio chimico", 3, 3,
    "Fumi e vapori del bitume caldo con tracce di IPA (Titolo IX D.Lgs. 81/2008): stare sopravento "
    "rispetto a vibrofinitrice e cassoni; temperature di stesa non superiori a quelle indicate dal "
    "fornitore; preferire conglomerati tiepidi a bassa emissione; non mangiare né fumare durante "
    "la stesa; lavaggio della pelle con detergenti specifici, mai con gasolio o solventi.", DPI_BITUME)
USTIONI_BITUME = r(
    "Ustioni", 2, 3,
    "Conglomerato a 140-180 °C: non toccare il materiale né le parti calde della vibrofinitrice; "
    "stesa manuale con rastrelli e badili a manico lungo; indumenti a maniche lunghe e calzature "
    "con suola resistente al calore; acqua e kit per ustioni nel cantiere.", DPI_BITUME)
ELETTRICO_AEREO = r(
    "Elettrocuzione", 1, 4,
    "Prima del lavoro verificare la presenza di linee elettriche aeree e mantenere da esse, con "
    "persone, carichi e bracci, le distanze della tabella 1 dell'Allegato IX (art. 83 D.Lgs. "
    "81/2008); in caso contrario chiedere al gestore la messa fuori tensione o la protezione "
    "della linea.")
BIOLOGICO_VERDE = r(
    "Rischio biologico", 2, 2,
    "Terreno e vegetazione con possibili spore del tetano, zecche, insetti e larve urticanti: "
    "profilassi antitetanica; indumenti chiusi ai polsi e alle caviglie; repellenti; controllo della "
    "pelle a fine turno; segnalare allergie al medico competente; cassetta di primo soccorso.",
    DPI_BASE + ", stivali di sicurezza")


LAVORAZIONI = [
    # ===================================================================================
    # LAVORI DI URBANIZZAZIONE E RETI
    # ===================================================================================
    # --- Reti fognarie ---
    fase("UR.01", UR, "Reti fognarie", "Scavo a sezione obbligata con blindaggio per la posa di condotte",
         "Scavo in trincea per la posa di collettori fognari, con escavatore e rifinitura a mano del fondo "
         "secondo le livellette di progetto. Le pareti sono sostenute man mano con pannelli di blindaggio "
         "calati dall'escavatore; le acque di falda o di pioggia vengono allontanate con pompe. Il "
         "materiale di risulta è caricato su autocarro o accumulato lontano dal ciglio.",
         "Addetto allo scavo a sezione obbligata per la posa di condotte", 25, INFRA,
         ["Escavatore", "Autocarro", "Armatura delle pareti di scavo (blindaggio)", "Pompa sommersa",
          "Scala a mano", "Parapetto provvisorio", "Utensili manuali"],
         [SEPPELLIMENTO, CADUTA_SCAVO, SOTTOSERVIZI, INV_MEZZI,
          r("Annegamento", 1, 4,
            "Scavi sotto falda o vicino a canali solo con aggottamento continuo e pompa di riserva; "
            "sospendere il lavoro con forti piogge e uscire subito dallo scavo se l'acqua sale; mai "
            "lavorare da soli nello scavo.", DPI_FOGNA)]),
    fase("UR.02", UR, "Reti fognarie", "Posa di tubazioni fognarie in PVC o in PEAD corrugato",
         "Formazione del letto di posa in sabbia o pietrischetto, calata dei tubi in PVC (UNI EN 1401) o in "
         "polietilene corrugato a doppia parete (UNI EN 13476) e innesto a bicchiere con guarnizione "
         "elastomerica lubrificata. Controllo di pendenza e allineamento con livello laser, rinfianco e "
         "ricoprimento compattato a strati secondo UNI EN 1610.",
         "Addetto alla posa di tubazioni fognarie in materiale plastico", 45, INFRA,
         ["Escavatore", "Autocarro con gru", "Armatura delle pareti di scavo (blindaggio)", "Piastra vibrante",
          "Scala a mano", "Utensili manuali"],
         [SEPPELLIMENTO, CARICO_SOSPESO, SCHIACCIAMENTO_GIUNTI, MMC,
          r("Posture incongrue", 3, 2,
            "Lavoro chinato sul fondo dello scavo per letto di posa e giunzioni: alternanza dei compiti, "
            "pause, ginocchiere; larghezza dello scavo sufficiente a lavorare ai lati del tubo.",
            DPI_BASE + ", ginocchiere")]),
    fase("UR.03", UR, "Reti fognarie", "Posa di tubazioni in calcestruzzo di grande diametro",
         "Posa di collettori in calcestruzzo armato o vibrocompresso a incastro con guarnizione, del peso "
         "anche di alcune tonnellate per elemento, calati con autogru o escavatore idoneo al sollevamento. "
         "Gli elementi sono accostati con tirfor o con la benna su un sottofondo in calcestruzzo magro o "
         "misto e poi rinfiancati.",
         "Addetto alla posa di tubazioni in calcestruzzo", 35, INFRA,
         ["Autogru", "Escavatore", "Autocarro", "Armatura delle pareti di scavo (blindaggio)",
          "Scala a mano", "Utensili manuali"],
         [CARICO_SOSPESO, SEPPELLIMENTO, SCHIACCIAMENTO_GIUNTI,
          r("Cesoiamenti e stritolamenti", 2, 4,
            "Mai interporsi tra il tubo in calata e la parete dello scavo o il tubo già posato; "
            "accostamento finale comandato da un solo addetto con segnali convenuti; elementi "
            "sganciati solo dopo l'appoggio stabile sul letto di posa."),
          r("Crollo o ribaltamento di strutture", 2, 3,
            "Tubi in deposito accatastati su terreno piano, su travetti e bloccati con cunei; altezza "
            "delle cataste secondo le indicazioni del fabbricante; nessuno sale sulle cataste.")]),
    fase("UR.04", UR, "Reti fognarie", "Posa di pozzetti e camerette prefabbricate di ispezione",
         "Posa su platea di base di pozzetti e camerette prefabbricate in calcestruzzo, con elementi di "
         "rialzo, cono o soletta di copertura e chiusini in ghisa sferoidale (UNI EN 124). I giunti sono "
         "sigillati con malta o guarnizioni e i tubi raccordati con giunti elastici; gli elementi sono "
         "sollevati con i ganci o gli inserti previsti dal produttore.",
         "Addetto alla posa di pozzetti e camerette prefabbricate", 40, INFRA,
         ["Autogru", "Escavatore", "Autocarro con gru", "Armatura delle pareti di scavo (blindaggio)",
          "Scala a mano", "Utensili manuali"],
         [CARICO_SOSPESO,
          r("Caduta dall'alto", 2, 3,
            "Aperture dei pozzetti chiuse con coperture provvisorie resistenti o protette con "
            "parapetto fino alla posa del chiusino; nessun accesso all'interno durante il montaggio "
            "degli elementi superiori."),
          SEPPELLIMENTO, CEMENTO,
          r("Movimentazione manuale dei carichi", 3, 2,
            "Chiusini e telai in ghisa (anche oltre 50 kg) movimentati con il mezzo o con apposite "
            "pinze o leve solleva chiusini, in due; mai sollevarli con le dita sotto il bordo.")]),
    fase("UR.05", UR, "Reti fognarie", "Realizzazione di allacci alla rete fognaria esistente",
         "Scavo localizzato fino al collettore in esercizio, foratura della tubazione con carotatrice o "
         "attacco su pozzetto esistente e inserimento di braga o sella con guarnizione. L'allaccio è "
         "condotto in accordo con il gestore, con eventuale deviazione o tamponamento temporaneo dei "
         "reflui, e la sede stradale è presegnalata.",
         "Addetto alla realizzazione di allacci fognari", 55, INFRA_RISTR,
         ["Miniescavatore", "Carotatrice", "Armatura delle pareti di scavo (blindaggio)", "Rilevatore multigas",
          "Scala a mano", "Utensili manuali"],
         [BIOLOGICO_FOGNA, GAS_FOGNA, SEPPELLIMENTO, INV_TRAFFICO, SOTTOSERVIZI,
          r("Getti e schizzi", 2, 2,
            "Foratura del collettore con portata ridotta o con by-pass concordato con il gestore; "
            "posizionarsi di lato rispetto al foro; visiera durante l'apertura.",
            DPI_FOGNA + ", visiera protettiva")]),
    fase("UR.06", UR, "Reti fognarie", "Prove di tenuta e collaudo delle condotte fognarie",
         "Prova di tenuta ad aria o ad acqua dei tratti di condotta e dei pozzetti secondo UNI EN 1610, con "
         "otturatori pneumatici ai pozzetti di estremità, e videoispezione interna con telecamera. Le "
         "prove sono condotte dall'esterno; l'accesso ai pozzetti per inserire gli otturatori avviene con "
         "la procedura degli ambienti confinati.",
         "Addetto alle prove di tenuta e al collaudo delle condotte", 60, INFRA,
         ["Motocompressore", "Rilevatore multigas", "Treppiede con dispositivo di recupero", "Scala a mano",
          "Utensili manuali"],
         [r("Proiezione di schegge e frammenti", 2, 3,
            "Otturatori adatti al diametro e gonfiati alla pressione del fabbricante; puntellati o "
            "vincolati contro lo spostamento; nessuno davanti all'otturatore o dentro il pozzetto "
            "durante la messa in pressione; scarico della pressione prima di toglierli."),
          GAS_FOGNA, BIOLOGICO_FOGNA,
          r("Caduta dall'alto", 2, 3,
            "Pozzetti aperti protetti con transenne o parapetto per tutta la prova e richiusi al "
            "termine; discesa con scala fissata e imbracatura collegata al treppiede.")]),
    # --- Reti idriche ---
    fase("UR.07", UR, "Reti idriche (acquedotti)", "Posa di tubazioni in ghisa sferoidale per acquedotto",
         "Posa di tubi in ghisa sferoidale (UNI EN 545) con giunto a bicchiere e guarnizione, calati con "
         "escavatore o autogru e innestati con apposito attrezzo di tiro. I tubi sono tagliati a misura "
         "con troncatrice e smussati; nei cambi di direzione si realizzano blocchi di ancoraggio in "
         "calcestruzzo o giunti antisfilamento.",
         "Addetto alla posa di tubazioni in ghisa per acquedotto", 40, INFRA,
         ["Escavatore", "Autogru", "Autocarro con gru", "Smerigliatrice angolare",
          "Armatura delle pareti di scavo (blindaggio)", "Scala a mano", "Utensili manuali"],
         [CARICO_SOSPESO, SCHIACCIAMENTO_GIUNTI, SEPPELLIMENTO, MMC,
          r("Rischio chimico", 1, 2,
            "Lubrificanti per guarnizioni e vernici di ritocco del rivestimento usati secondo le "
            "schede di sicurezza, con guanti in nitrile; solo prodotti idonei al contatto con acqua "
            "potabile.", DPI_BASE + ", guanti in lattice o nitrile")]),
    fase("UR.08", UR, "Reti idriche (acquedotti)", "Posa di tubazioni in PEAD con saldatura per termofusione o elettrofusione",
         "Posa di tubi in polietilene ad alta densità (UNI EN 12201) in barre o in rotoli, giuntati fuori "
         "scavo o sul fondo con saldatura testa a testa (UNI 10520) o con raccordi elettrosaldabili "
         "(UNI 10521) da saldatori qualificati secondo UNI 9737. Le superfici sono raschiate e sgrassate "
         "prima della saldatura e la colonna è calata nello scavo con più punti di presa.",
         "Addetto alla posa e saldatura di tubazioni in polietilene", 45, INFRA,
         ["Escavatore", "Autocarro con gru", "Saldatrice per polietilene", "Gruppo elettrogeno",
          "Armatura delle pareti di scavo (blindaggio)", "Utensili manuali"],
         [r("Urti, colpi, impatti e compressioni", 2, 3,
            "Rotoli srotolati con aspo o svolgitore; reggette tagliate una alla volta stando di lato, "
            "perché il tubo si distende di colpo; estremità libere trattenute; calata della colonna "
            "saldata con più mezzi coordinati e nessuno tra tubo e scavo."),
          r("Ustioni", 2, 2,
            "Tubi e raccordi appena saldati non toccati fino al termine del raffreddamento indicato "
            "nei parametri di saldatura; termoelemento riposto nel suo supporto.",
            DPI_BASE + ", guanti per saldatura"),
          r("Rischio chimico", 1, 2,
            "Detergenti per lo sgrassaggio (alcol isopropilico o simili) infiammabili e irritanti: "
            "panni monouso, contenitori chiusi, nessuna fiamma vicina, guanti in nitrile.",
            DPI_BASE + ", guanti in lattice o nitrile"),
          SEPPELLIMENTO, MMC]),
    fase("UR.09", UR, "Reti idriche (acquedotti)", "Montaggio di pezzi speciali, prova idraulica e disinfezione delle condotte",
         "Montaggio di saracinesche, sfiati, scarichi, idranti e raccordi flangiati, con serraggio dei "
         "bulloni e realizzazione dei pozzetti di manovra. Prova idraulica in pressione dei tronchi "
         "secondo UNI EN 805 e il capitolato del gestore, quindi lavaggio e disinfezione della condotta "
         "con soluzione di ipoclorito e risciacquo prima della messa in servizio.",
         "Addetto ai pezzi speciali, al collaudo idraulico e alla disinfezione delle condotte", 55, INFRA,
         ["Autocarro con gru", "Miniescavatore", "Utensili manuali", "Scala a mano"],
         [r("Getti e schizzi", 2, 3,
            "Tappi e fondelli ancorati e controspinti prima della prova; pressione portata per gradi "
            "e controllata a distanza dal manometro; nessuno davanti ai fondelli o nei pozzetti in "
            "pressione; scarico completo prima di intervenire.", DPI_BASE + ", visiera protettiva"),
          r("Rischio chimico", 2, 3,
            "Ipoclorito di sodio corrosivo: travaso con pompa dosatrice, mai a mano; contenitori "
            "etichettati; mai mescolarlo con acidi (sviluppo di cloro); acqua per il lavaggio "
            "oculare disponibile; scarico dell'acqua clorata come concordato con il gestore.",
            DPI_BASE + ", guanti in lattice o nitrile, occhiali a maschera, indumenti impermeabili"),
          CARICO_SOSPESO, MMC]),
    # --- Reti gas ---
    fase("UR.10", UR, "Reti gas", "Posa di condotte e allacci della rete di distribuzione del gas",
         "Posa di tubazioni in polietilene o in acciaio rivestito per la distribuzione del gas naturale "
         "secondo D.M. 16/04/2008 e UNI EN 12007, con nastro di segnalazione, prove di tenuta e "
         "realizzazione delle prese. Gli inserimenti sulla rete in esercizio sono eseguiti solo da "
         "personale autorizzato dal distributore con attrezzature di foratura sotto pressione.",
         "Addetto alla posa di reti di distribuzione del gas", 50, INFRA,
         ["Escavatore", "Miniescavatore", "Saldatrice per polietilene", "Rilevatore multigas",
          "Armatura delle pareti di scavo (blindaggio)", "Utensili manuali"],
         [r("Incendio ed esplosione", 2, 4,
            "Durante gli inserimenti e la messa in gas: rilevatore di esplosività acceso nello scavo, "
            "divieto di fiamme e fumo, motori spenti o lontani, attrezzi antiscintilla, estintori "
            "pronti; sfiato del gas in alto e lontano dagli addetti; scavo con via di fuga sempre "
            "libera.", DPI_BASE + ", indumenti protettivi"),
          SOTTOSERVIZI, SEPPELLIMENTO, INV_TRAFFICO]),
    # --- Cavidotti ---
    fase("UR.11", UR, "Cavidotti per reti elettriche e di telecomunicazione", "Posa di cavidotti in trincea",
         "Scavo a sezione ristretta e posa di tubi corrugati a doppia parete (CEI EN 61386-24) o di "
         "polifore, con letto e rinfianco in sabbia o bauletto in calcestruzzo, nastro monitore e "
         "pozzetti di derivazione. Profondità di posa secondo CEI 11-17 e le prescrizioni dell'ente "
         "proprietario della strada; successivo tiro dei cavi con sonda o argano.",
         "Addetto alla posa di cavidotti in trincea", 40, INFRA_RISTR,
         ["Miniescavatore", "Escavatore", "Autocarro", "Piastra vibrante", "Utensili manuali"],
         [SOTTOSERVIZI, INV_TRAFFICO, MMC, CADUTA_SCAVO,
          r("Urti, colpi, impatti e compressioni", 2, 2,
            "Tiro dei cavi con argano dotato di limitatore di forza e comunicazione via radio tra i "
            "due pozzetti; mani lontane da bobine, rulli e imbocchi; bobine bloccate sul cavalletto.")]),
    fase("UR.12", UR, "Cavidotti per reti elettriche e di telecomunicazione", "Posa di condotte con perforazione orizzontale controllata (TOC)",
         "Realizzazione di un foro pilota guidato sotto strade, corsi d'acqua o ferrovie, successivo "
         "alesaggio e tiro della tubazione in polietilene, secondo UNI/PdR 26.01:2017. Si usano fanghi di "
         "perforazione a base di bentonite raccolti in vasche, e la traiettoria è seguita in superficie "
         "con un sistema di localizzazione.",
         "Addetto alla perforazione orizzontale controllata", 30, ("Opere infrastrutturali",),
         ["Macchina per perforazione orizzontale controllata (TOC)", "Miniescavatore", "Autobotte",
          "Pompa sommersa", "Utensili manuali"],
         [r("Contatto con sottoservizi in esercizio (cavi elettrici, gas, acqua)", 2, 4,
            "Mappatura preventiva delle reti con gli enti gestori e georadar; saggi a vista nei punti "
            "di incrocio; distanze minime dalla traiettoria fissate nel progetto; macchina con sistema "
            "di allarme per contatto elettrico e tappeti equipotenziali per gli operatori; "
            "sospensione immediata a ogni anomalia di spinta o di fango."),
          r("Getti e schizzi", 2, 2,
            "Pozzetti di ingresso e uscita delimitati; fango in pressione e risalite in superficie "
            "controllate dall'addetto alla localizzazione; nessuno vicino all'aste in rotazione o "
            "all'alesatore in uscita.", DPI_BASE + ", occhiali protettivi, indumenti impermeabili"),
          INV_MEZZI, SCIVOLAMENTI]),
    fase("UR.13", UR, "Cavidotti per reti elettriche e di telecomunicazione", "Posa di infrastrutture in minitrincea",
         "Taglio stretto e poco profondo della pavimentazione stradale con fresa a disco e aspirazione dei "
         "detriti, posa di minitubi o microcavi per fibra ottica e riempimento con malta cementizia "
         "fluida a rapido indurimento, secondo D.M. 01/10/2013. Il lavoro procede per tratti brevi in "
         "cantiere mobile.",
         "Addetto alla posa di infrastrutture in minitrincea", 30, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Macchina per minitrincea (fresa a disco)", "Autocarro", "Spazzatrice stradale", "Utensili manuali"],
         [INV_TRAFFICO,
          r("Contatto con sottoservizi in esercizio (cavi elettrici, gas, acqua)", 2, 4,
            "Profondità di taglio limitata a quella di progetto e verificata con gli enti gestori; "
            "attenzione a cavi superficiali e allacci; saggi a mano agli incroci con chiusini e "
            "pozzetti; arresto del taglio a ogni resistenza anomala."),
          CEMENTO, MMC]),
    # --- Ambienti confinati e reti in esercizio ---
    fase("UR.14", UR, "Lavori in ambienti confinati e su reti in esercizio", "Lavori all'interno di pozzetti, camerette e vasche",
         "Ingresso in pozzetti, camerette, collettori e vasche per ispezioni, raccordi o riparazioni. "
         "L'intervento è affidato solo a imprese qualificate ai sensi del D.P.R. 177/2011, con procedura "
         "scritta, permesso di lavoro, misura dell'atmosfera, ventilazione, sorveglianza esterna continua "
         "e piano di recupero provato.",
         "Addetto ai lavori in ambienti confinati", 70, INFRA_RISTR,
         ["Rilevatore multigas", "Ventilatore estrattore", "Treppiede con dispositivo di recupero",
          "Pompa sommersa", "Scala a mano", "Utensili manuali"],
         [r("Ambienti confinati o sospetti di inquinamento", 3, 4,
            "Rispetto di artt. 66 e 121 e Allegato IV p. 3 D.Lgs. 81/2008 e del D.P.R. 177/2011: almeno "
            "il 30% della squadra, compreso il preposto, con esperienza triennale; formazione e "
            "addestramento specifici; informazione dal committente sui rischi dell'ambiente. Prima "
            "dell'accesso: isolamento delle immissioni, misura di ossigeno, gas tossici ed "
            "esplosività a più altezze, ventilazione forzata; rilevatore indossato per tutta la "
            "durata; operatore all'esterno sempre presente e in contatto; uscita immediata "
            "all'allarme.", DPI_CONFINATI),
          r("Caduta dall'alto", 2, 4,
            "Discesa con scala fissata o integrata nel pozzetto e imbracatura collegata al "
            "dispositivo di recupero del treppiede; apertura protetta durante il lavoro.",
            DPI_CONFINATI),
          r("Annegamento", 1, 4,
            "Verificare con il gestore orari e portate; tamponare o deviare le immissioni; non entrare "
            "con pioggia in atto o prevista; collegamento al dispositivo di recupero in ogni momento.",
            DPI_CONFINATI),
          BIOLOGICO_FOGNA,
          r("Posture incongrue", 3, 2,
            "Spazi ristretti: pause frequenti all'esterno, rotazione degli addetti, attrezzi leggeri "
            "calati con secchio e fune.", DPI_CONFINATI)]),
    fase("UR.15", UR, "Lavori in ambienti confinati e su reti in esercizio", "Manutenzione e riparazione di reti idriche e fognarie in esercizio",
         "Interventi su condotte in servizio: spurgo e lavaggio ad alta pressione dei collettori, "
         "videoispezione, riparazione di perdite con manicotti o sostituzione di tratti, con by-pass "
         "provvisorio dei reflui mediante pompe o chiusura dei tronchi idrici concordata con il gestore. "
         "Le lavorazioni si svolgono di norma su strada aperta al traffico.",
         "Addetto alla manutenzione di reti in esercizio", 50, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Autospurgo", "Miniescavatore", "Pompa sommersa", "Rilevatore multigas", "Ventilatore estrattore",
          "Armatura delle pareti di scavo (blindaggio)", "Utensili manuali"],
         [BIOLOGICO_FOGNA, GAS_FOGNA, INV_TRAFFICO,
          r("Annegamento", 1, 4,
            "Rischio di arrivo improvviso di acqua o reflui: chiusura e verifica delle valvole a "
            "monte, pompe di by-pass con riserva, controllo delle previsioni meteo; scavo con via di "
            "uscita sempre libera; mai da soli.", DPI_FOGNA),
          SEPPELLIMENTO]),
    fase("UR.16", UR, "Impianti di sollevamento", "Realizzazione e allestimento di impianti di sollevamento delle acque",
         "Posa della vasca di accumulo prefabbricata o getto in opera nello scavo, montaggio di pompe "
         "sommergibili con guide e catene di sollevamento, tubazioni di mandata, valvole e quadro "
         "elettrico di comando. Le prove di funzionamento e i collegamenti elettrici sono eseguiti da "
         "personale qualificato secondo CEI 11-27.",
         "Addetto alla realizzazione di impianti di sollevamento", 35, INFRA,
         ["Autogru", "Escavatore", "Autocarro con gru", "Rilevatore multigas",
          "Treppiede con dispositivo di recupero", "Scala a mano", "Utensili manuali"],
         [CARICO_SOSPESO,
          r("Ambienti confinati o sospetti di inquinamento", 2, 4,
            "Vasche già allacciate alla rete trattate come ambienti confinati (D.P.R. 177/2011): "
            "isolamento delle immissioni, misura dell'atmosfera, ventilazione, sorveglianza esterna; "
            "montaggio delle pompe dall'esterno con le guide, senza scendere.", DPI_CONFINATI),
          r("Elettrocuzione", 2, 4,
            "Lavori sul quadro e sulle pompe solo fuori tensione, con sezionamento, blocco e cartello "
            "(CEI 11-27, persone PES/PAV); verifica dell'assenza di tensione prima di toccare i "
            "conduttori.", DPI_BASE + ", guanti dielettrici"),
          r("Caduta dall'alto", 2, 4,
            "Aperture della vasca chiuse con grigliati o protette con parapetto; accesso solo con "
            "imbracatura collegata al dispositivo di recupero."),
          SEPPELLIMENTO]),

    # ===================================================================================
    # LAVORI STRADALI
    # ===================================================================================
    # --- Cantieri in presenza di traffico ---
    fase("SR.01", SR, "Cantieri stradali in presenza di traffico", "Posa, spostamento e rimozione della segnaletica temporanea di cantiere",
         "Installazione, mantenimento e rimozione di coni, delineatori, barriere, cartelli e lampeggianti "
         "per delimitare l'area di lavoro, secondo lo schema scelto tra quelli del D.M. 10/07/2002 e con "
         "le procedure del D.M. 22/01/2019. Le operazioni procedono nel senso di marcia per la posa e in "
         "senso inverso per la rimozione, con veicolo di supporto dotato di pannello luminoso.",
         "Addetto alla posa della segnaletica temporanea di cantiere", 80, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Autocarro", "Utensili manuali"],
         [INV_TRAFFICO,
          r("Investimento da mezzi in manovra", 2, 4,
            "Veicolo di supporto fermo a distanza di sicurezza a monte degli operatori a terra, con "
            "ruote sterzate verso la banchina; discesa e salita dal lato opposto al traffico; nessun "
            "operatore tra veicolo e traffico né sul cassone in movimento.", DPI_STRADA),
          r("Movimentazione manuale dei carichi", 2, 2,
            "Sacchi di zavorra e basi dei cartelli caricati a bordo in modo da prelevarli senza "
            "sporgersi; sollevamento con la schiena dritta; basi pesanti movimentate in due.", DPI_STRADA),
          MICROCLIMA]),
    fase("SR.02", SR, "Cantieri stradali in presenza di traffico", "Regolazione del traffico con movieri e senso unico alternato",
         "Regolazione manuale del transito in senso unico alternato con palette (art. 42 D.P.R. 495/1992) "
         "o gestione di impianti semaforici provvisori, ai due estremi del cantiere, con comunicazione "
         "radio tra i movieri. Il moviere si posiziona in banchina o in area protetta e mantiene la "
         "presegnalazione efficiente per tutta la durata del lavoro.",
         "Addetto alla regolazione del traffico (moviere)", 95, ("Opere infrastrutturali", "Ristrutturazioni"),
         [],
         [INV_TRAFFICO,
          r("Rischio chimico", 2, 2,
            "Gas di scarico dei veicoli in coda: posizionarsi sopravento e non a ridosso dei veicoli "
            "fermi; rotazione periodica tra movieri e altri compiti.", DPI_STRADA),
          r("Posture incongrue", 3, 1,
            "Stazione eretta prolungata: pause e cambi programmati, seduta disponibile nelle pause.",
            DPI_STRADA),
          MICROCLIMA]),
    # --- Fresatura ---
    fase("SR.03", SR, "Demolizione e fresatura delle pavimentazioni", "Taglio e fresatura della pavimentazione in conglomerato bituminoso",
         "Taglio dei bordi con tagliasfalto e fresatura a freddo degli strati bituminosi con scarificatrice, "
         "con carico diretto del fresato sull'autocarro tramite nastro e pulizia finale con spazzatrice. "
         "Chiusini e caditoie sono individuati prima e rialzati o protetti; il fresato è gestito come "
         "materiale da recuperare.",
         "Addetto alla fresatura della pavimentazione stradale", 15, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Scarificatrice (fresa stradale)", "Tagliasfalto a disco", "Autocarro", "Spazzatrice stradale",
          "Utensili manuali"],
         [INV_TRAFFICO,
          r("Investimento da mezzi in manovra", 3, 4,
            "Addetti a terra sempre visibili al fresatore e mai tra fresa e autocarro in fase di "
            "accostamento; autocarri guidati con segnali convenuti; distanza dal tamburo e dal nastro "
            "in moto.", DPI_STRADA),
          r("Contatto con sottoservizi in esercizio (cavi elettrici, gas, acqua)", 1, 3,
            "Profondità di fresatura controllata; segnalazione preventiva di chiusini, cavi in "
            "minitrincea e spire semaforiche; rimozione o protezione dei manufatti prima del passaggio."),
          r("Polveri e fibre", 2, 2,
            "Fresa con impianto di nebulizzazione efficiente; pulizia con spazzatrice a umido e non "
            "a secco a mano; stare sopravento.", DPI_STRADA + ", facciale filtrante FFP2")]),
    # --- Sovrastruttura stradale ---
    fase("SR.04", SR, "Sovrastruttura stradale", "Formazione della fondazione stradale in misto granulare",
         "Stesa a strati del misto granulare stabilizzato con grader o pala, umidificazione e compattazione "
         "con rullo vibrante fino alla densità prescritta, con controllo delle quote e prove di carico su "
         "piastra. Il materiale è scaricato da autocarri in retromarcia lungo il tracciato.",
         "Addetto alla formazione della fondazione stradale", 15, INFRA,
         ["Autocarro", "Grader (livellatrice)", "Pala meccanica", "Rullo compattatore", "Autobotte",
          "Utensili manuali"],
         [INV_MEZZI,
          r("Polveri e fibre", 2, 2, "Bagnatura del materiale e delle piste con autobotte; stare sopravento "
            "durante lo scarico.", DPI_BASE + ", facciale filtrante FFP2"),
          MICROCLIMA, SCIVOLAMENTI]),
    fase("SR.05", SR, "Sovrastruttura stradale", "Formazione di strato in misto cementato",
         "Stesa del misto granulare confezionato con cemento in impianto, con vibrofinitrice o grader, e "
         "compattazione entro i tempi di lavorabilità, seguita dalla protezione superficiale con "
         "emulsione bituminosa o sabbia. Taglio di giunti di ripresa e controllo delle quote.",
         "Addetto alla formazione di strati in misto cementato", 15, INFRA,
         ["Autocarro", "Vibrofinitrice", "Grader (livellatrice)", "Rullo compattatore", "Utensili manuali"],
         [INV_MEZZI, CEMENTO,
          r("Polveri e fibre", 2, 2, "Bagnatura delle superfici; nessuna lavorazione manuale a secco del "
            "materiale; stare sopravento.", DPI_BASE + ", facciale filtrante FFP2"),
          MICROCLIMA]),
    fase("SR.06", SR, "Sovrastruttura stradale", "Spruzzatura della mano d'attacco in emulsione bituminosa",
         "Pulizia del piano di posa e spruzzatura di emulsione bituminosa, normale o modificata, con barra "
         "della spanditrice e con lancia nei punti non raggiungibili, nel dosaggio previsto. La superficie "
         "trattata è lasciata asciugare e interdetta al passaggio non necessario prima della stesa.",
         "Addetto alla spruzzatura della mano d'attacco", 20, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Spanditrice di emulsione bituminosa", "Spazzatrice stradale", "Utensili manuali"],
         [r("Rischio chimico", 2, 3,
            "Emulsione irritante per pelle e occhi e vapori dal prodotto riscaldato: schede di "
            "sicurezza a bordo, spruzzatura sopravento, nessuno nel ventaglio della barra o della "
            "lancia; lavaggio della pelle con detergenti specifici.", DPI_BITUME),
          r("Getti e schizzi", 2, 3,
            "Tubazioni e raccordi della lancia controllati prima dell'uso; lancia mai rivolta verso "
            "persone; visiera durante la spruzzatura manuale e lo sblocco degli ugelli.",
            DPI_BITUME + ", visiera protettiva"),
          r("Scivolamenti e cadute a livello", 3, 2,
            "Evitare di camminare sull'emulsione fresca; percorsi a piedi ai margini della striscia "
            "trattata; calzature con suola pulita.", DPI_STRADA),
          INV_TRAFFICO]),
    fase("SR.07", SR, "Sovrastruttura stradale", "Stesa e compattazione dello strato di collegamento (binder)",
         "Scarico del conglomerato bituminoso caldo dagli autocarri nella tramoggia della vibrofinitrice, "
         "stesa a spessore costante e compattazione con rulli tandem e gommati. A terra gli addetti "
         "regolano lo spessore, rifiniscono a mano bordi e raccordi e controllano la temperatura del "
         "materiale.",
         "Addetto alla stesa del conglomerato bituminoso per strato di collegamento", 15, INFRA,
         ["Vibrofinitrice", "Rullo compattatore", "Autocarro", "Utensili manuali"],
         [FUMI_BITUME, USTIONI_BITUME,
          r("Investimento da mezzi in manovra", 3, 4,
            "Accostamento degli autocarri alla vibrofinitrice guidato da un solo addetto ben visibile; "
            "nessuno tra autocarro e tramoggia; distanza dai rulli che invertono la marcia; "
            "indumenti in classe 3.", DPI_STRADA),
          MICROCLIMA, SOLE]),
    fase("SR.08", SR, "Sovrastruttura stradale", "Stesa e compattazione del tappeto di usura",
         "Stesa dello strato superficiale in conglomerato bituminoso chiuso, drenante o con bitume "
         "modificato, con particolare cura dei giunti longitudinali e trasversali, rifilatura dei bordi e "
         "messa in quota di chiusini e caditoie. La lavorazione avviene spesso a corsie alterne con la "
         "strada parzialmente aperta al traffico.",
         "Addetto alla stesa del tappeto di usura", 18, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Vibrofinitrice", "Rullo compattatore", "Autocarro", "Tagliasfalto a disco", "Utensili manuali"],
         [INV_TRAFFICO, FUMI_BITUME, USTIONI_BITUME,
          r("Movimentazione manuale dei carichi", 2, 2,
            "Chiusini e telai movimentati con leve e pinze in due o con il mezzo; materiale per i "
            "raccordi a mano trasportato con carriola, non a badilate ripetute.", DPI_BITUME),
          SOLE]),
    fase("SR.09", SR, "Sovrastruttura stradale", "Realizzazione di pavimentazioni stradali in calcestruzzo",
         "Posa di casseri o guide, eventuale rete o barrotti nei giunti, getto del calcestruzzo da "
         "autobetoniera, vibrazione con staggia o vibratori, finitura superficiale (spazzolata o "
         "frattazzata) e spruzzatura del prodotto di stagionatura. Taglio dei giunti di contrazione con "
         "sega a disco entro le prime ore.",
         "Addetto alla realizzazione di pavimentazioni in calcestruzzo", 30, INFRA_RISTR,
         ["Autobetoniera", "Autopompa per calcestruzzo", "Vibratore per calcestruzzo", "Frattazzatrice meccanica",
          "Sega a disco per murature e calcestruzzo", "Casseforme", "Utensili manuali"],
         [CEMENTO,
          r("Getti e schizzi", 2, 2,
            "Scarico dalla canala a velocità ridotta, addetti lateralmente; occhiali durante getto e "
            "vibrazione.", DPI_CEMENTO),
          r("Rischio chimico", 2, 2,
            "Prodotti di stagionatura e disarmanti spruzzati sopravento, secondo le schede di "
            "sicurezza; nessuno nella zona di nebulizzazione.", DPI_CEMENTO + ", facciale filtrante FFP2"),
          r("Posture incongrue", 3, 2,
            "Finiture a mano con attrezzi a manico lungo; ginocchiere per i lavori a terra; rotazione "
            "dei compiti.", DPI_BASE + ", ginocchiere"),
          INV_MEZZI]),
    fase("SR.10", SR, "Sovrastruttura stradale", "Posa di pavimentazioni in masselli autobloccanti",
         "Formazione del letto di sabbia livellato a staggia su fondazione compattata, posa dei masselli "
         "in calcestruzzo secondo lo schema previsto, a mano o con pinza meccanica, tagli di "
         "completamento, intasamento dei giunti con sabbia fine e vibrocompattazione finale con piastra.",
         "Addetto alla posa di masselli autobloccanti", 50, ESTERNI,
         ["Minipala (skid loader)", "Piastra vibrante", "Sega a disco per murature e calcestruzzo",
          "Autocarro con gru", "Utensili manuali"],
         [r("Movimentazione manuale dei carichi", 3, 3,
            "Pallet scaricati con gru o minipala vicino al fronte di posa; posa meccanizzata per "
            "superfici estese; nella posa manuale, masselli prelevati all'altezza del bacino, pause e "
            "turnazione (Allegato XXXIII)."),
          r("Movimenti ripetitivi degli arti superiori", 3, 2,
            "Alternare posa, tagli e stesa della sabbia; pause programmate; pinze manuali per la "
            "presa dei masselli."),
          r("Posture incongrue", 3, 2,
            "Lavoro in ginocchio: ginocchiere o cuscinetti, cambi frequenti di posizione.",
            DPI_BASE + ", ginocchiere"),
          r("Urti, colpi, impatti e compressioni", 2, 2,
            "Assestamento dei masselli con mazzuolo in gomma; mani fuori dai giunti durante "
            "l'accostamento; guanti con buona presa.")]),
    # --- Opere complementari ---
    fase("SR.11", SR, "Opere stradali complementari", "Posa di cordoli e formazione di marciapiedi",
         "Scavo e getto della fondazione in calcestruzzo, posa di cordoli prefabbricati o in pietra "
         "allettati con malta, tagli a misura e stuccatura dei giunti; formazione del massetto del "
         "marciapiede e della finitura, con rampe e scivoli per il superamento delle barriere "
         "architettoniche.",
         "Addetto alla posa di cordoli e alla formazione di marciapiedi", 50, ESTERNI,
         ["Miniescavatore", "Autocarro con gru", "Betoniera a bicchiere", "Sega a disco per murature e calcestruzzo",
          "Utensili manuali"],
         [r("Movimentazione manuale dei carichi", 3, 3,
            "Cordoli posati con pinza a gancio sul mezzo o con apposito carrello posacordoli; "
            "spostamenti manuali solo in due e per brevi tratti."),
          r("Urti, colpi, impatti e compressioni", 2, 3,
            "Mani fuori dalla zona di contatto tra cordolo e cordolo o fondazione durante "
            "l'accostamento; cordolo sganciato solo dopo l'appoggio stabile."),
          CEMENTO, INV_TRAFFICO]),
    fase("SR.12", SR, "Opere stradali complementari", "Esecuzione della segnaletica orizzontale",
         "Premarcatura a mano e stesa di strisce, frecce e scritte con vernice a solvente o all'acqua, "
         "termoplastico o colato plastico bicomponente, con macchina tracciatrice e perline di vetro "
         "rifrangenti (UNI EN 1436). Si opera in cantiere mobile con veicolo di protezione e pannello "
         "a messaggio.",
         "Addetto alla segnaletica orizzontale", 45, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Macchina tracciatrice per segnaletica", "Autocarro", "Utensili manuali"],
         [INV_TRAFFICO,
          r("Rischio chimico", 3, 2,
            "Vernici e bicomponenti contenenti solventi o resine sensibilizzanti: preferire prodotti "
            "all'acqua, travasi all'aperto sopravento, contenitori chiusi, schede di sicurezza a "
            "bordo; maschera con filtro per vapori organici in caso di spruzzatura manuale.",
            DPI_STRADA + ", guanti in lattice o nitrile, maschera con filtro specifico"),
          r("Ustioni", 2, 3,
            "Termoplastico fuso a circa 200 °C: caricamento della caldaia senza schizzi, coperchi "
            "chiusi, guanti e visiera per il travaso.", DPI_STRADA + ", guanti per saldatura, visiera protettiva"),
          r("Incendio ed esplosione", 1, 3,
            "Solventi e bombole di gas della caldaia lontani da fonti di calore, fissati e chiusi a fine "
            "lavoro; estintore sul mezzo; divieto di fumo.", DPI_STRADA)]),
    fase("SR.13", SR, "Opere stradali complementari", "Installazione della segnaletica verticale",
         "Realizzazione dei plinti di fondazione o dei fori nella pavimentazione, posa di pali e sostegni, "
         "montaggio di cartelli, pannelli e delineatori conformi a UNI EN 12899-1 e al Regolamento del "
         "Codice della Strada, con orientamento e altezze di progetto. Per portali e cartelli alti si "
         "lavora da piattaforma elevabile.",
         "Addetto all'installazione della segnaletica verticale", 55, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Autocarro con gru", "Motoperforatrice (trivella a motore)", "Martello perforatore (tassellatore)",
          "Betoniera a bicchiere", "Piattaforma di lavoro elevabile", "Scala doppia", "Utensili manuali"],
         [INV_TRAFFICO, SOTTOSERVIZI, ELETTRICO_AEREO,
          r("Caduta di materiale dall'alto o a livello", 2, 3,
            "Pannelli grandi movimentati con la gru e con funi di guida; area sottostante interdetta "
            "durante il sollevamento e il fissaggio; attrezzi legati in quota."),
          MMC]),
    fase("SR.14", SR, "Opere stradali complementari", "Installazione di barriere di sicurezza stradali",
         "Infissione dei paletti con battipalo o fissaggio su cordolo con tasselli, montaggio di "
         "distanziatori, nastri, terminali e transizioni secondo il manuale di installazione del "
         "dispositivo certificato (UNI EN 1317, D.M. 21/06/2004). Il lavoro si svolge di norma a "
         "margine della carreggiata aperta al traffico.",
         "Addetto all'installazione di barriere di sicurezza stradali", 40, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Battipalo (infissione di pali e barriere)", "Autocarro con gru", "Avvitatore elettrico",
          "Martello perforatore (tassellatore)", "Utensili manuali"],
         [INV_TRAFFICO, SOTTOSERVIZI,
          r("Movimentazione manuale dei carichi", 3, 3,
            "Nastri e paletti scaricati con la gru lungo il tracciato; sollevamento e accostamento "
            "dei nastri sempre in due; supporti di appoggio provvisori durante l'imbullonatura."),
          r("Urti, colpi, impatti e compressioni", 2, 3,
            "Dita mai nei fori per allinearli: usare punteruoli o spine; bordi dei nastri presi con "
            "guanti antitaglio; serraggio con chiave dinamometrica secondo il manuale.",
            DPI_STRADA + ", guanti antitaglio")]),
    # --- Ripristini ---
    fase("SR.15", SR, "Ripristini stradali", "Ripristino della pavimentazione stradale dopo scavi",
         "Rifilatura dei bordi dello scavo con tagliasfalto, riempimento e compattazione a strati del "
         "materiale, getto dell'eventuale strato in misto cementato o calcestruzzo e chiusura con "
         "conglomerato bituminoso a caldo steso a mano o con piccola finitrice, secondo le prescrizioni "
         "dell'ente proprietario della strada; successivo tappeto di usura a fondo assestato.",
         "Addetto ai ripristini stradali", 40, ("Opere infrastrutturali", "Ristrutturazioni"),
         ["Tagliasfalto a disco", "Miniescavatore", "Piastra vibrante", "Rullo compattatore", "Autocarro",
          "Utensili manuali"],
         [INV_TRAFFICO, USTIONI_BITUME, FUMI_BITUME,
          r("Movimentazione manuale dei carichi", 3, 2,
            "Materiale scaricato direttamente nello scavo dal mezzo; stesa manuale limitata alla "
            "rifinitura, con attrezzi a manico lungo e turnazione.", DPI_BITUME),
          MICROCLIMA]),

    # ===================================================================================
    # SISTEMAZIONI ESTERNE E AREE VERDI
    # ===================================================================================
    fase("SE.01", SE, "Opere murarie esterne", "Realizzazione di muri di contenimento in calcestruzzo armato",
         "Scavo di sbancamento a ridosso del terreno da sostenere, getto della fondazione, posa delle "
         "armature e dei casseri del paramento, getto e vibrazione del calcestruzzo, quindi "
         "realizzazione del drenaggio a tergo con tubo forato e materiale arido e rinterro a strati.",
         "Addetto alla realizzazione di muri di contenimento", 45, ESTERNI,
         ["Escavatore", "Autobetoniera", "Autopompa per calcestruzzo", "Vibratore per calcestruzzo",
          "Casseforme", "Piegaferri", "Ponte su cavalletti", "Parapetto provvisorio", "Utensili manuali"],
         [r("Seppellimento e sprofondamento", 2, 4,
            "Fronte di sbancamento con inclinazione adeguata al terreno o sostenuto con opere "
            "provvisionali (art. 118 D.Lgs. 81/2008), verificato prima di ogni turno; nessun "
            "accumulo di materiale sul ciglio; lavoro a tergo del muro solo con fronte stabile."),
          r("Caduta dall'alto", 2, 4,
            "Casseri oltre 2 m con passerelle di getto munite di parapetto; parapetto provvisorio "
            "sul ciglio dello sbancamento; accesso con scale vincolate."),
          r("Punture, tagli e abrasioni", 3, 2,
            "Ferri di ripresa sporgenti protetti con cappucci a fungo; guanti durante la "
            "legatura delle armature."),
          CARICO_SOSPESO, CEMENTO]),
    fase("SE.02", SE, "Opere murarie esterne", "Posa di recinzioni e cancelli definitivi",
         "Esecuzione di cordoli o plinti di fondazione, posa di pannelli in rete elettrosaldata, "
         "grigliati o elementi metallici su piantane, montaggio di cancelli pedonali e carrai, a battente "
         "o scorrevoli, con eventuale motorizzazione. L'automazione è installata e collaudata secondo "
         "UNI EN 12453 e le istruzioni del fabbricante.",
         "Addetto alla posa di recinzioni e cancelli definitivi", 50, ESTERNI,
         ["Motoperforatrice (trivella a motore)", "Miniescavatore", "Autocarro con gru", "Betoniera a bicchiere",
          "Saldatrice", "Smerigliatrice angolare", "Trapano elettrico", "Utensili manuali"],
         [r("Crollo o ribaltamento di strutture", 2, 4,
            "Ante dei cancelli sostenute con la gru o con supporti fino al fissaggio di cerniere, "
            "guide e fermi di fine corsa; cancello scorrevole mai lasciato sulla guida senza ritegni "
            "antiribaltamento."),
          MMC, SOTTOSERVIZI,
          r("Punture, tagli e abrasioni", 3, 2,
            "Bordi e punte di pannelli e grigliati maneggiati con guanti antitaglio; estremità della "
            "rete ripiegate o protette.", DPI_BASE + ", guanti antitaglio")]),
    fase("SE.03", SE, "Opere murarie esterne", "Realizzazione di pavimentazioni esterne in pietra e lastre",
         "Formazione del sottofondo e del massetto, posa di lastre e cubetti in pietra naturale o "
         "ricomposta su malta o letto di sabbia, tagli di adattamento, battitura e stuccatura dei giunti "
         "per piazzali, vialetti e percorsi pedonali, con pendenze per lo smaltimento delle acque.",
         "Addetto alla posa di pavimentazioni esterne", 55, TUTTE,
         ["Minipala (skid loader)", "Betoniera a bicchiere", "Sega a disco per murature e calcestruzzo",
          "Piastra vibrante", "Utensili manuali"],
         [r("Movimentazione manuale dei carichi", 3, 3,
            "Lastre pesanti movimentate con ventose o pinze e in due; pallet avvicinati con la "
            "minipala; turnazione nella posa manuale."),
          r("Posture incongrue", 3, 2, "Ginocchiere e cuscinetti per la posa a terra; pause e cambi di "
            "posizione.", DPI_BASE + ", ginocchiere"),
          CEMENTO, MICROCLIMA]),
    fase("SE.04", SE, "Formazione di aree verdi", "Preparazione del terreno e formazione di tappeti erbosi",
         "Stesa e modellazione del terreno vegetale, lavorazione con fresa o erpice portati dal trattore, "
         "rimozione di sassi e radici, concimazione di fondo e semina a spaglio o con seminatrice, "
         "rullatura e prima irrigazione; in alternativa posa di tappeto erboso in rotoli o idrosemina "
         "sulle scarpate.",
         "Addetto alla preparazione del terreno e alla semina", 35, ESTERNI,
         ["Trattore", "Minipala (skid loader)", "Autobotte", "Utensili manuali"],
         [BIOLOGICO_VERDE,
          r("Rischio chimico", 2, 2,
            "Concimi e ammendanti distribuiti secondo le schede di sicurezza, sopravento, con guanti e "
            "facciale filtrante per i prodotti polverulenti; lavaggio delle mani prima di mangiare.",
            DPI_BASE + ", guanti in lattice o nitrile, facciale filtrante FFP2"),
          r("Polveri e fibre", 2, 2, "Lavorazione del terreno non troppo asciutto; nessuno nella "
            "nuvola di polvere dietro le macchine.", DPI_BASE + ", facciale filtrante FFP2"),
          SOLE, MMC]),
    fase("SE.05", SE, "Formazione di aree verdi", "Messa a dimora di alberi e arbusti",
         "Apertura delle buche con miniescavatore o trivella, posa di alberi in zolla o in vaso con "
         "autocarro con gru, sistemazione con terra vegetale e ammendanti, ancoraggio con pali tutori o "
         "sistemi sotterranei e formazione della conca per l'irrigazione; per gli arbusti, piantagione "
         "a mano in file o gruppi.",
         "Addetto alla messa a dimora di alberi e arbusti", 55, ESTERNI,
         ["Miniescavatore", "Autocarro con gru", "Motoperforatrice (trivella a motore)", "Utensili manuali"],
         [r("Caduta di materiale dall'alto o a livello", 2, 3,
            "Alberi in zolla sollevati con fasce sul colletto o reti della zolla, mai con catene sul "
            "tronco; nessuno sotto il carico; posizionamento nella buca con funi di guida."),
          SOTTOSERVIZI, MMC,
          r("Punture, tagli e abrasioni", 3, 2, "Piante spinose maneggiate con guanti robusti e maniche "
            "lunghe; occhiali vicino a rami all'altezza del viso.", DPI_BASE + ", occhiali protettivi"),
          BIOLOGICO_VERDE]),
    fase("SE.06", SE, "Formazione di aree verdi", "Realizzazione di impianti di irrigazione",
         "Scavo di piccole trincee, posa di tubazioni in polietilene con raccordi a compressione o "
         "saldati, ali gocciolanti, irrigatori a scomparsa, elettrovalvole in pozzetti e centralina di "
         "programmazione, con collegamento al punto di presa idrica e prova di funzionamento.",
         "Addetto alla realizzazione di impianti di irrigazione", 50, ESTERNI,
         ["Miniescavatore", "Saldatrice per polietilene", "Utensili manuali"],
         [SOTTOSERVIZI,
          r("Elettrocuzione", 1, 3,
            "Collegamento della centralina e delle eventuali pompe alla rete solo da personale "
            "qualificato e fuori tensione; elettrovalvole a bassissima tensione di sicurezza; "
            "giunzioni dei cavi interrati in muffole stagne."),
          r("Rischio chimico", 1, 2, "Collanti e primer per PVC usati in ambiente aerato, lontano da "
            "fiamme, con guanti in nitrile.", DPI_BASE + ", guanti in lattice o nitrile"),
          r("Posture incongrue", 3, 2, "Lavori nei pozzetti e a terra con ginocchiere; pause e rotazione.",
            DPI_BASE + ", ginocchiere")]),
    fase("SE.07", SE, "Arredo urbano e aree gioco", "Posa di elementi di arredo urbano",
         "Posa e fissaggio di panchine, cestini, fioriere, portabiciclette, dissuasori e fontanelle su "
         "plinti o su pavimentazione esistente con tasselli meccanici o ancoranti chimici, con "
         "allineamento e messa in quota secondo il progetto, spesso in aree pubbliche frequentate.",
         "Addetto alla posa di arredo urbano", 50, TUTTE,
         ["Autocarro con gru", "Martello perforatore (tassellatore)", "Carotatrice", "Miniescavatore",
          "Utensili manuali"],
         [r("Caduta di materiale dall'alto o a livello", 2, 3,
            "Elementi pesanti (fioriere, panchine in pietra o ghisa) scaricati con gru e funi di guida; "
            "area di scarico transennata e interdetta ai passanti."),
          r("Rischio chimico", 2, 2, "Ancoranti chimici bicomponenti sensibilizzanti: estrusione con "
            "pistola, guanti in nitrile, occhiali; nessun contatto con la pelle.",
            DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
          MMC,
          r("Investimento da veicoli in transito", 2, 4,
            "Area di lavoro recintata o transennata con percorsi alternativi per i pedoni; "
            "presegnalazione sulla carreggiata secondo il D.M. 10/07/2002 se si occupa la sede "
            "stradale.", DPI_STRADA)]),
    fase("SE.08", SE, "Arredo urbano e aree gioco", "Installazione di attrezzature per aree gioco e pavimentazioni antitrauma",
         "Montaggio di giochi (altalene, scivoli, strutture multifunzione) secondo le istruzioni del "
         "fabbricante e UNI EN 1176, con fondazioni dimensionate, e realizzazione delle superfici "
         "antitrauma in gomma colata, piastre o materiale sciolto con l'altezza di caduta critica "
         "verificata secondo UNI EN 1177. Ispezione di installazione prima dell'apertura al pubblico.",
         "Addetto all'installazione di attrezzature per aree gioco", 50, ESTERNI,
         ["Autocarro con gru", "Motoperforatrice (trivella a motore)", "Miniescavatore", "Avvitatore elettrico",
          "Trabattello", "Scala doppia", "Utensili manuali"],
         [r("Caduta dall'alto", 2, 3,
            "Montaggio delle parti alte da trabattello o scala doppia stabile, non arrampicandosi "
            "sulla struttura incompleta; struttura controventata fino al getto delle fondazioni."),
          r("Rischio chimico", 2, 3,
            "Leganti poliuretanici delle pavimentazioni colate contenenti isocianati: miscelazione "
            "all'aperto, guanti in nitrile, occhiali, maschera con filtro specifico se previsto dalla "
            "scheda di sicurezza; formazione specifica sugli isocianati come richiesto dal REACH.",
            DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi, maschera con filtro specifico"),
          CARICO_SOSPESO, MMC]),
    fase("SE.09", SE, "Manutenzione del verde", "Potatura di alberature in quota con piattaforma elevabile",
         "Potatura di contenimento, rimonda del secco e messa in sicurezza di alberi lungo strade, viali "
         "e parchi, con operatore nel cestello della PLE e tagli eseguiti con motosega da potatura o "
         "attrezzi manuali; i rami sono calati in modo controllato e cippati a terra.",
         "Addetto alla potatura in quota con PLE", 70, TUTTE,
         ["Piattaforma di lavoro elevabile", "Motosega", "Cippatrice", "Autocarro", "Utensili manuali"],
         [r("Caduta dall'alto", 2, 4,
            "Operatore abilitato alla PLE (art. 73 c. 5 D.Lgs. 81/2008, Accordo Stato-Regioni "
            "22/02/2012); imbracatura con cordino di trattenuta corto agganciato al punto del "
            "cestello indicato dal fabbricante; mai uscire dal cestello per salire sulla pianta; "
            "stabilizzatori su base solida.", DPI_BASE + ", imbracatura, cordino con assorbitore, "
            "otoprotettori, visiera protettiva"),
          r("Caduta di materiale dall'alto o a livello", 3, 3,
            "Area sotto la chioma delimitata e interdetta, con addetto a terra che sorveglia; rami "
            "grossi calati con funi e carrucole; tagli che evitino il rimbalzo del ramo sul cestello."),
          ELETTRICO_AEREO, INV_TRAFFICO,
          r("Rischio biologico", 2, 2,
            "Controllo preventivo di nidi di processionaria, vespe e altri insetti; peli urticanti "
            "rimossi da ditte specializzate; viso e polsi coperti; profilassi antitetanica.",
            DPI_BASE + ", occhiali a maschera, facciale filtrante FFP2")]),
    fase("SE.10", SE, "Manutenzione del verde", "Sfalcio, diserbo e manutenzione ordinaria delle aree verdi",
         "Taglio dell'erba con trattorino o decespugliatore, rifilature, raccolta del materiale, "
         "potature basse di siepi e arbusti, eventuali trattamenti fitosanitari e controllo delle "
         "infestanti. Le aree pubbliche restano spesso aperte e i margini stradali sono presegnalati.",
         "Addetto alla manutenzione delle aree verdi", 75, TUTTE,
         ["Decespugliatore a motore", "Trattore", "Autocarro", "Utensili manuali"],
         [r("Proiezione di schegge e frammenti", 2, 3,
            "Ispezione preventiva dell'area e rimozione di sassi, vetri e rifiuti; persone tenute a "
            "distanza di sicurezza (almeno 15 m per il decespugliatore) con transenne e cartelli; "
            "sospendere il taglio se qualcuno si avvicina.", DPI_BASE + ", visiera protettiva, otoprotettori"),
          r("Rischio chimico", 2, 3,
            "Fitosanitari usati solo da addetti con certificato di abilitazione (D.Lgs. 150/2012), "
            "secondo etichetta e scheda di sicurezza; aree trattate segnalate e chiuse per il tempo di "
            "rientro; preparazione della miscela all'aperto; lavaggio dei DPI dopo l'uso.",
            DPI_BASE + ", guanti in lattice o nitrile, maschera con filtro specifico, tuta monouso"),
          r("Scivolamenti e cadute a livello", 2, 3,
            "Su scarpate ripide e terreno bagnato usare calzature con suola scolpita e attrezzature "
            "adatte alla pendenza; non lavorare in salita sotto il trattore."),
          BIOLOGICO_VERDE, SOLE]),
]
