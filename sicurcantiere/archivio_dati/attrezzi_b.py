"""Archivio: attrezzi di cantiere (seconda parte) e opere provvisionali.

Rischi generati dall'uso e schede d'uso, scritti per questo progetto. Fonti consultate:
- D.Lgs. 81/2008: Titolo III (artt. 70-73, Allegati V, VI, VII), Titolo IV, Capo II (artt. 111-
  140 e Allegati XVIII-XXII), Titolo VIII (rumore, vibrazioni), Titolo IX, Capi I-III (agenti
  chimici, cancerogeni, amianto);
- D.M. 6 settembre 1994 (bonifiche amianto, unità di decontaminazione); D.P.R. 177/2011;
- norme UNI EN 131, 13374, 1263-1/-2, 795, 1065, 12812, 12811; CEI EN 60335-2-69, 60079-29-1;
- quaderni tecnici INAIL sui lavori in quota (reti di sicurezza, parapetti provvisori,
  sistemi di ancoraggio), schede PuntoSicuro sui ponti su cavalletti, testo del D.M. 6 settembre 1994.
I testi vanno sempre confrontati con il manuale del fabbricante dell'attrezzatura.
NOTA: le ricerche in rete sono state interrotte dal limite di utilizzo durante la redazione; non
tutte le fonti elencate sono state rilette per intero e diversi riferimenti sono citati da
conoscenze normative. Prima dell'uso professionale vedere docs/verifiche-archivio.md.
"""

from __future__ import annotations

from typing import Any

from sicurcantiere.archivio_dati.base import ATTREZZO, DPI_BASE, OPERA, attrezzatura, r, scheda

# --- rischi ricorrenti ---------------------------------------------------------------------

def _elettrocuzione(p: int = 1, d: int = 4, extra: str = "") -> dict[str, Any]:
    return r("Elettrocuzione", p, d,
             "Utensile a doppio isolamento o collegato a terra; alimentazione da quadro di cantiere con "
             "differenziale da 30 mA (Allegato V, parte I, punto 6); cavi per posa mobile H07RN-F integri, "
             "sollevati da terra e lontani da acqua e spigoli; prese e spine di tipo industriale (CEI EN 60309)."
             + (" " + extra if extra else ""))


def _rumore(p: int = 3, d: int = 2, nota: str = "") -> dict[str, Any]:
    return r("Rumore", p, d,
             "Valutazione dell'esposizione secondo il Titolo VIII, Capo II; scelta di macchine silenziate; "
             "manutenzione di silenziatori e cuscinetti; turnazione degli addetti; otoprotettori obbligatori "
             "oltre il valore superiore di azione (85 dB(A))." + (" " + nota if nota else ""),
             DPI_BASE + ", otoprotettori")


def _vibrazioni(p: int = 3, d: int = 2) -> dict[str, Any]:
    return r("Vibrazioni al sistema mano-braccio", p, d,
             "Valutazione secondo il Titolo VIII, Capo III (valore d'azione 2,5 m/s², limite 5 m/s²); "
             "attrezzi con impugnature antivibranti in buono stato; pause e rotazione degli addetti; "
             "sorveglianza sanitaria degli esposti.",
             DPI_BASE + ", guanti antivibrazioni")


_DPI_OPERA = ["casco con sottogola", "calzature di sicurezza", "guanti"]

ATTREZZATURE: dict[str, dict[str, Any]] = {
    # ===================================== ATTREZZI ======================================
    "Cesoia elettrica per lamiere": attrezzatura(ATTREZZO, rischi=[
        r("Punture, tagli e abrasioni", 3, 2,
          "Bordi e sfridi di lamiera maneggiati sempre con guanti antitaglio; sfridi raccolti subito in "
          "contenitori; lamiera appoggiata e trattenuta su piano stabile; mani lontane dalla testa di taglio.",
          DPI_BASE.replace("guanti", "guanti antitaglio")),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Protezioni della lama integre (Allegato V, parte I, punto 6); interruttore a uomo presente; "
          "cambio lame e pulizia solo con spina staccata; non togliere le schermature."),
        r("Proiezione di schegge e frammenti", 2, 2,
          "Rispettare lo spessore massimo di taglio indicato dal fabbricante; non forzare l'avanzamento; "
          "trucioli e riccioli allontanati con l'utensile fermo.", DPI_BASE + ", occhiali protettivi"),
        _elettrocuzione(),
        _rumore(2, 2),
    ], scheda_uso=scheda(
        "Utensile elettrico portatile a lame o a punzone (roditrice) per tagliare lamiere sottili e "
        "pannelli metallici di lattoneria e coperture.",
        ["verificare l'integrità di cavo, spina e involucro e che lame e punzone non siano consumati",
         "controllare il serraggio delle lame e la presenza delle protezioni",
         "collegarsi a una presa del quadro di cantiere protetta da differenziale",
         "fissare o appoggiare stabilmente la lamiera da tagliare"],
        ["tenere l'utensile con entrambe le mani e avanzare senza forzare",
         "non superare lo spessore e il tipo di metallo ammessi dal fabbricante",
         "tenere il cavo lontano dalla linea di taglio e dai bordi vivi",
         "in quota lavorare solo da postazioni protette, con l'utensile assicurato contro la caduta"],
        ["staccare la spina prima di pulire o sostituire le lame",
         "raccogliere sfridi e trucioli metallici",
         "segnalare difetti o surriscaldamenti al preposto"],
        ["guanti antitaglio", "occhiali protettivi", "otoprotettori", "calzature di sicurezza"])),

    "Intonacatrice": attrezzatura(ATTREZZO, rischi=[
        r("Getti e schizzi", 3, 2,
          "Lancia sempre rivolta verso la parete; pressione regolata dal manometro; nessuno davanti alla "
          "lancia; prima di aprire raccordi e tubi scaricare la pressione residua.",
          DPI_BASE + ", occhiali a maschera"),
        r("Rischio chimico", 3, 2,
          "Premiscelati a base di calce e cemento irritanti e sensibilizzanti: consultare la scheda di "
          "sicurezza (Titolo IX, Capo I); cemento a basso tenore di cromo VI; pulizia immediata della pelle "
          "schizzata; lavaocchi in postazione.", DPI_BASE + ", guanti in lattice o nitrile, crema protettiva"),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Griglia di protezione della tramoggia con microinterruttore che arresta la coclea; mai inserire "
          "le mani o attrezzi nella vasca in movimento; pulizia e sblocco a macchina spenta e staccata."),
        r("Polveri e fibre", 3, 2,
          "Caricare i sacchi lentamente e vicino alla bocca della tramoggia; postazione di carico ventilata; "
          "facciale filtrante durante il carico.", DPI_BASE + ", facciale filtrante FFP2"),
        r("Movimentazione manuale dei carichi", 3, 2,
          "Sacchi da 25 kg posti su bancali all'altezza della tramoggia; sollevamenti a due per pesi maggiori; "
          "valutazione secondo l'Allegato XXXIII."),
        _elettrocuzione(),
        _rumore(2, 2),
    ], scheda_uso=scheda(
        "Macchina miscelatrice e pompante che impasta il premiscelato con acqua e lo spruzza a parete "
        "attraverso una tubazione con lancia.",
        ["verificare tubi, raccordi a innesto rapido, manometro e griglia di protezione della tramoggia",
         "posizionare la macchina in piano, lontana dal ciglio di scavi e solai aperti",
         "stendere i tubi senza strozzature, pieghe strette o passaggi carrabili",
         "collegarla al quadro di cantiere con differenziale e verificare il pulsante di emergenza"],
        ["dirigere la lancia solo verso la superficie da intonacare",
         "concordare con l'addetto alla macchina i segnali di avvio e arresto",
         "in caso di intasamento fermare la pompa e scaricare la pressione prima di intervenire",
         "non aprire la griglia e non introdurre le mani nella tramoggia"],
        ["svuotare e lavare tramoggia, pompa e tubi con la macchina staccata",
         "scaricare le acque di lavaggio in vasca di decantazione, non in caditoie o scavi",
         "controllare l'usura di statore e rotore e annotare le anomalie"],
        ["occhiali a maschera", "guanti in lattice o nitrile", "facciale filtrante FFP2", "casco",
         "calzature di sicurezza", "indumenti protettivi"])),

    "Impastatrice": attrezzatura(ATTREZZO, rischi=[
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Vasca con griglia o coperchio interbloccato che arresta le pale all'apertura (Allegato V); "
          "organi di trasmissione carterati; pulizia solo con alimentazione staccata."),
        r("Polveri e fibre", 3, 2,
          "Svuotare i sacchi con cautela e vicino alla vasca; preferire impastatrici con aspirazione o "
          "coperchio di carico; lavorare all'aperto o in ambiente ventilato.",
          DPI_BASE + ", facciale filtrante FFP2"),
        r("Rischio chimico", 2, 2,
          "Leganti cementizi e additivi gestiti secondo le schede di sicurezza; evitare il contatto con la "
          "pelle; acqua pulita disponibile per il lavaggio.", DPI_BASE + ", guanti in lattice o nitrile"),
        r("Movimentazione manuale dei carichi", 3, 2,
          "Materiali stoccati vicino e in alto rispetto alla bocca di carico; carrelli per il trasporto dei "
          "sacchi; impasto scaricato in contenitori di capacità maneggevole."),
        _elettrocuzione(),
    ], scheda_uso=scheda(
        "Mescolatore elettrico a vasca fissa con pale o frusta per malte, colle, autolivellanti e piccoli "
        "impasti; comprende i mescolatori portatili a frusta.",
        ["verificare la griglia di protezione e il microinterruttore di sicurezza",
         "posizionare l'impastatrice su base piana e stabile",
         "controllare cavo, spina e pulsante di arresto"],
        ["caricare acqua e materiale con le pale in moto solo attraverso la griglia",
         "non togliere o bloccare le protezioni",
         "con il mescolatore a frusta tenere l'utensile con due mani e il secchio bloccato con i piedi",
         "mantenere pulita la zona per evitare scivolamenti sull'impasto"],
        ["staccare la spina prima di lavare vasca e pale",
         "rimuovere i residui induriti con l'attrezzo fermo",
         "riporre al riparo dalla pioggia"],
        ["facciale filtrante FFP2", "guanti in lattice o nitrile", "occhiali protettivi",
         "calzature di sicurezza"])),

    "Pompa per malte e iniezioni": attrezzatura(ATTREZZO, rischi=[
        r("Getti e schizzi", 3, 3,
          "Pressione di esercizio regolata sotto il limite dei tubi e del supporto; valvola di sicurezza e "
          "manometro funzionanti; tubi con raccordi assicurati da catenelle; prima di scollegare portare a "
          "zero la pressione.", DPI_BASE + ", occhiali a maschera, schermo facciale"),
        r("Rischio chimico", 3, 3,
          "Resine epossidiche e poliuretaniche sensibilizzanti: scheda di sicurezza in cantiere, miscelazione "
          "all'aperto, contenitori chiusi ed etichettati (Titolo IX, Capo I); niente contatto con la pelle; "
          "sorveglianza sanitaria se prevista.",
          DPI_BASE + ", guanti in lattice o nitrile, maschera con filtro specifico"),
        r("Crollo o ribaltamento di strutture", 1, 4,
          "Iniezioni nelle murature e nei terreni con pressioni e quantità stabilite dal progettista; "
          "controllo continuo di lesioni e rigonfiamenti; arresto immediato in caso di fuoriuscite anomale."),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Tramoggia con griglia; organi in movimento protetti; manutenzione e sblocchi a pompa spenta."),
        _elettrocuzione(),
    ], scheda_uso=scheda(
        "Pompa a pistone, a vite o a membrana per iniettare malte, boiacche o resine in murature, "
        "fessurazioni, terreni e ancoraggi.",
        ["leggere le schede di sicurezza dei prodotti e predisporre lavaocchi e materiale assorbente",
         "verificare valvola di sicurezza, manometro, tubi e raccordi",
         "fissare i raccordi con fascette o catenelle anti-sfilamento",
         "concordare con il progettista pressioni massime e sequenza delle iniezioni"],
        ["aumentare la pressione gradualmente controllando il manometro",
         "mantenere una persona alla pompa in contatto con chi tiene l'ugello",
         "non piegare né calpestare i tubi in pressione",
         "sospendere se compaiono fuoriuscite, lesioni nuove o rigonfiamenti"],
        ["scaricare la pressione e lavare il circuito secondo il manuale",
         "smaltire residui e contenitori di resina come rifiuti",
         "riporre i prodotti chimici in luogo chiuso e ventilato"],
        ["occhiali a maschera", "schermo facciale", "guanti in lattice o nitrile", "tuta monouso",
         "maschera con filtro specifico", "calzature di sicurezza"])),

    "Levigatrice per pavimenti": attrezzatura(ATTREZZO, rischi=[
        r("Polveri e fibre", 3, 3,
          "Macchina collegata ad aspiratore di classe adeguata (polveri di calcestruzzo contenenti silice "
          "cristallina respirabile, Titolo IX, Capo II); in alternativa lavorazione a umido; ambiente "
          "ventilato e confinato rispetto alle altre squadre.", DPI_BASE + ", facciale filtrante FFP3"),
        _rumore(3, 2),
        _vibrazioni(3, 2),
        r("Urti, colpi, impatti e compressioni", 2, 2,
          "Avviamento con piatti sollevati o macchina ben impugnata; mai piedi vicino al piatto rotante; "
          "dischi e mole fissati come da manuale."),
        r("Rischio chimico", 2, 2,
          "Con levigatura di parquet e successiva verniciatura: prodotti a basso contenuto di solventi, "
          "aerazione, nessuna fiamma; polveri di legno duro (cancerogene) aspirate alla fonte.",
          DPI_BASE + ", maschera con filtro specifico"),
        _elettrocuzione(1, 4, "Con lavorazione a umido usare macchine idonee e cavi fuori dall'acqua."),
    ], scheda_uso=scheda(
        "Macchina a piatti o a nastro per levigare, lucidare o carteggiare pavimenti in calcestruzzo, "
        "pietra, piastrelle o legno.",
        ["verificare il fissaggio di dischi, mole o carta abrasiva e il carter",
         "collegare l'aspiratore e verificarne filtri e tenuta",
         "sgombrare la superficie da ostacoli e chiodi sporgenti",
         "srotolare il cavo dietro l'operatore, fuori dalla traiettoria della macchina"],
        ["impugnare saldamente la macchina prima dell'avviamento",
         "non lasciare la macchina in moto senza sorveglianza",
         "fare pause e turni per limitare rumore e vibrazioni",
         "tenere a distanza le altre persone e chiudere l'area con la lavorazione a secco"],
        ["fermare e staccare la macchina prima di cambiare gli abrasivi",
         "svuotare l'aspiratore in sacchi chiusi senza sollevare polvere",
         "pulire con aspirazione, non a secco con la scopa"],
        ["facciale filtrante FFP3", "otoprotettori", "guanti antivibrazioni", "occhiali protettivi",
         "calzature di sicurezza", "ginocchiere"])),

    "Taglierina elettrica per piastrelle": attrezzatura(ATTREZZO, rischi=[
        r("Punture, tagli e abrasioni", 3, 3,
          "Cuffia di protezione del disco registrata sul pezzo; avanzamento con carrello o spingitoio; mani "
          "fuori dalla linea del disco; disco diamantato integro e adatto al materiale.",
          DPI_BASE.replace("guanti", "guanti antitaglio")),
        r("Proiezione di schegge e frammenti", 3, 2,
          "Schermo del disco presente; pezzo appoggiato in piano sulla guida; nessuno nella direzione di "
          "rotazione.", DPI_BASE + ", occhiali protettivi"),
        _elettrocuzione(1, 4, "Macchina con raffreddamento ad acqua di grado di protezione idoneo; vaschetta "
                              "piena senza tracimazioni sui componenti elettrici."),
        r("Polveri e fibre", 2, 2,
          "Taglio ad acqua; se a secco, aspirazione alla fonte e postazione all'aperto.",
          DPI_BASE + ", facciale filtrante FFP2"),
        _rumore(3, 2),
    ], scheda_uso=scheda(
        "Banco da taglio con disco diamantato raffreddato ad acqua per piastrelle, gres e pietre di piccolo "
        "formato.",
        ["posizionarla su piano stabile e asciutto, all'altezza di lavoro",
         "verificare disco, cuffia, guida e livello dell'acqua",
         "collegarla a presa con differenziale e controllare che il cavo non passi nell'acqua"],
        ["avanzare il pezzo con il carrello senza forzare",
         "non rimuovere sfridi vicini al disco in rotazione",
         "attendere l'arresto del disco prima di togliere il pezzo"],
        ["staccare la spina, svuotare la vaschetta e pulire i fanghi",
         "verificare l'usura del disco e sostituirlo se danneggiato"],
        ["occhiali protettivi", "guanti antitaglio", "otoprotettori", "calzature di sicurezza",
         "indumenti impermeabili"])),

    "Pistola a spruzzo (airless)": attrezzatura(ATTREZZO, rischi=[
        r("Getti e schizzi", 2, 4,
          "Getto ad altissima pressione con rischio di iniezione sottocutanea: mai puntare la pistola verso "
          "persone o parti del corpo; sicura del grilletto inserita nelle pause; protezione dell'ugello "
          "montata; scarico della pressione prima di pulire o cambiare ugello; ogni ferita va trattata subito "
          "in pronto soccorso.", DPI_BASE + ", occhiali a maschera"),
        r("Rischio chimico", 3, 3,
          "Vernici e solventi valutati con le schede di sicurezza (Titolo IX, Capo I); preferire prodotti "
          "all'acqua; ventilazione forzata negli interni; nebbia trattenuta con teli.",
          DPI_BASE + ", maschera con filtro specifico, tuta monouso"),
        r("Incendio ed esplosione", 2, 4,
          "Con prodotti infiammabili: nessuna fiamma o scintilla, impianti elettrici e ventilatori idonei, "
          "messa a terra della pompa e tubi conduttivi contro le cariche elettrostatiche; estintore vicino; "
          "solvente in quantità minima e in contenitori chiusi."),
        _elettrocuzione(),
        _rumore(2, 2),
    ], scheda_uso=scheda(
        "Impianto con pompa ad alta pressione e pistola senza aria compressa per applicare pitture, "
        "smalti, impregnanti e vernici protettive.",
        ["leggere le schede di sicurezza dei prodotti e organizzare la ventilazione",
         "verificare tubi ad alta pressione, raccordi, sicura del grilletto e protezione dell'ugello",
         "collegare a terra la pompa con prodotti infiammabili",
         "proteggere con teli superfici e passaggi vicini"],
        ["non puntare mai la pistola verso persone e non toccare il getto",
         "inserire la sicura del grilletto a ogni pausa",
         "sbloccare l'ugello intasato solo dopo aver scaricato la pressione",
         "non fumare né usare fiamme in zona"],
        ["scaricare la pressione e lavare il circuito con il solvente previsto, in luogo ventilato",
         "raccogliere stracci e residui in contenitori metallici chiusi",
         "riporre vernici e solventi in deposito ventilato"],
        ["maschera con filtro specifico", "occhiali a maschera", "guanti in lattice o nitrile",
         "tuta monouso", "calzature di sicurezza"])),

    "Sabbiatrice": attrezzatura(ATTREZZO, rischi=[
        r("Polveri e fibre", 4, 3,
          "Abrasivi privi di silice cristallina libera (silice respirabile cancerogena, Titolo IX, Capo II); "
          "confinamento dell'area con teli; sabbiatura a umido dove possibile; verifica preventiva di vernici "
          "al piombo o materiali contenenti amianto.", DPI_BASE + ", autorespiratore"),
        r("Getti e schizzi", 3, 3,
          "Comando a uomo presente sulla lancia (arresto al rilascio); tubi e raccordi antisfilamento; "
          "nessuno nella direzione del getto; area delimitata e segnalata.",
          DPI_BASE + ", visiera protettiva, indumenti protettivi"),
        _rumore(4, 3, "Il rumore alla lancia supera di norma i 100 dB(A)."),
        _vibrazioni(2, 2),
        r("Proiezione di schegge e frammenti", 3, 2,
          "Distanza di sicurezza e schermature verso passaggi e altre squadre; casco da sabbiatura con visiera."),
        r("Elettrocuzione", 1, 4,
          "Messa a terra di serbatoio e tubi per disperdere le cariche elettrostatiche; collegamenti del "
          "compressore protetti da differenziale."),
    ], scheda_uso=scheda(
        "Impianto con serbatoio di abrasivo e lancia ad aria compressa per pulire superfici in muratura, "
        "pietra, calcestruzzo o metallo.",
        ["verificare che la superficie non contenga amianto o vernici al piombo",
         "scegliere un abrasivo privo di silice libera e predisporre teli di confinamento",
         "controllare tubi, raccordi, valvola a uomo presente e manometro del serbatoio",
         "fornire all'operatore casco da sabbiatura con adduzione d'aria filtrata"],
        ["delimitare e segnalare l'area, interdetta alle altre persone",
         "mantenere la lancia rivolta solo verso la superficie",
         "alternare gli operatori per limitare rumore e affaticamento",
         "interrompere con vento che disperde la polvere fuori dall'area"],
        ["scaricare la pressione del serbatoio",
         "aspirare e raccogliere l'abrasivo esausto come rifiuto",
         "pulire e ispezionare casco, filtri e tubi"],
        ["autorespiratore", "visiera protettiva", "cuffie antirumore", "indumenti protettivi", "guanti",
         "calzature di sicurezza"])),

    "Idropulitrice": attrezzatura(ATTREZZO, rischi=[
        r("Getti e schizzi", 3, 3,
          "Lancia con comando a uomo presente e sicura; getto mai rivolto a persone, prese o quadri elettrici; "
          "lancia impugnata con due mani per il contraccolpo; ugelli adatti alla superficie.",
          DPI_BASE + ", visiera protettiva, indumenti impermeabili"),
        _elettrocuzione(1, 4, "Macchina con grado di protezione adeguato; nessun getto su linee o apparecchi "
                              "in tensione; spina e prese lontane dall'acqua."),
        r("Scivolamenti e cadute a livello", 3, 2,
          "Raccolta e deflusso delle acque; calzature antiscivolo; in quota lavorare solo da postazioni "
          "protette tenendo conto della spinta della lancia."),
        _rumore(3, 2),
        r("Rischio chimico", 2, 2,
          "Detergenti usati secondo la scheda di sicurezza; con acqua calda o vapore attenzione alle "
          "ustioni; acque reflue raccolte e smaltite.", DPI_BASE + ", guanti in lattice o nitrile"),
    ], scheda_uso=scheda(
        "Macchina con pompa ad alta pressione e lancia per lavare superfici, facciate, mezzi e attrezzature.",
        ["verificare tubo, lancia, grilletto con sicura e cavo di alimentazione",
         "posizionare la macchina lontano dalla zona bagnata",
         "proteggere prese, quadri e apparecchi elettrici dal getto"],
        ["impugnare la lancia con due mani e tenere una posizione stabile",
         "non rivolgere il getto verso persone o animali",
         "inserire la sicura quando si appoggia la lancia",
         "segnalare la zona per gli spruzzi e il pavimento bagnato"],
        ["spegnere, scaricare la pressione e staccare la spina",
         "avvolgere i tubi senza pieghe e riporre la macchina al riparo dal gelo"],
        ["visiera protettiva", "indumenti impermeabili", "stivali di sicurezza", "otoprotettori", "guanti"])),

    "Pompa sommersa": attrezzatura(ATTREZZO, rischi=[
        _elettrocuzione(2, 4, "Pompa con cavo integrato per uso in immersione, collegata a presa con "
                              "differenziale dedicato; mai entrare in acqua con la pompa alimentata; "
                              "giunzioni dei cavi fuori dall'acqua."),
        r("Annegamento", 1, 4,
          "Pozzetti e vasche di aggottamento protetti con parapetto o coperchio; nessun lavoro isolato vicino "
          "a scavi allagati; salvagente o cima a disposizione."),
        r("Seppellimento e sprofondamento", 2, 4,
          "L'aggottamento può richiamare terreno fine e franare le pareti: pompa in pozzetto filtrante, "
          "controllo delle pareti di scavo e degli edifici vicini, armature come da art. 118."),
        r("Movimentazione manuale dei carichi", 2, 2,
          "Calare e sollevare la pompa con la fune o catena di sollevamento, mai con il cavo elettrico."),
        r("Scivolamenti e cadute a livello", 2, 2,
          "Tubi di mandata stesi lungo percorsi definiti e protetti negli attraversamenti; scarico delle acque "
          "lontano dalle vie di transito."),
    ], scheda_uso=scheda(
        "Elettropompa da immergere in scavi, pozzetti o locali allagati per l'aggottamento delle acque.",
        ["verificare l'integrità del cavo e del pressacavo e la presenza del galleggiante",
         "alimentare da presa con differenziale e verificarne il funzionamento con il tasto di prova",
         "predisporre un pozzetto o una base che non aspiri fango e terreno",
         "individuare un punto di scarico autorizzato"],
        ["calare e sollevare la pompa solo con la fune di manovra",
         "staccare l'alimentazione prima di qualsiasi intervento sulla pompa",
         "controllare periodicamente pareti di scavo e livello dell'acqua",
         "non lasciare che la pompa giri a secco"],
        ["staccare la spina, sollevare la pompa e lavarla con acqua pulita",
         "controllare girante e cavo e annotare le anomalie",
         "coprire o proteggere il pozzetto"],
        ["stivali di sicurezza", "guanti", "indumenti impermeabili", "casco"])),

    "Aspiratore con filtro HEPA": attrezzatura(ATTREZZO, rischi=[
        r("Polveri e fibre", 2, 4,
          "Aspiratore di classe H (CEI EN 60335-2-69, allegato AA) per amianto e polveri pericolose; filtro "
          "HEPA integro e ben alloggiato; sostituzione dei filtri e svuotamento in sacchi chiusi solo "
          "nell'area di lavoro, con DPI respiratori.", DPI_BASE + ", facciale filtrante FFP3, tuta monouso"),
        r("Esposizione ad amianto", 2, 4,
          "Con materiali contenenti amianto: uso secondo il piano di lavoro (art. 256); aspiratore dedicato "
          "e decontaminato prima di uscire dall'area; filtri e sacchi smaltiti come rifiuti contenenti "
          "amianto.", DPI_BASE + ", facciale filtrante FFP3, tuta monouso"),
        _elettrocuzione(),
        _rumore(2, 2),
    ], scheda_uso=scheda(
        "Aspiratore industriale con filtro assoluto ad alta efficienza per polveri pericolose, silice e "
        "fibre, anche nelle bonifiche e come aspirazione localizzata di utensili.",
        ["verificare che la classe dell'aspiratore (L, M, H) sia adeguata alla polvere",
         "controllare l'integrità e il corretto montaggio di filtro e guarnizioni",
         "verificare il funzionamento dell'indicatore di portata o di intasamento"],
        ["collegare il tubo direttamente alla cuffia dell'utensile quando possibile",
         "non aprire il contenitore e non battere i filtri durante l'uso",
         "interrompere se l'allarme segnala portata insufficiente"],
        ["svuotare in sacchi chiusi ed etichettati, con DPI respiratori",
         "pulire l'esterno a umido e conservare l'aspiratore con le bocche tappate",
         "far sostituire i filtri secondo il manuale e registrare la manutenzione"],
        ["facciale filtrante FFP3", "tuta monouso", "guanti in lattice o nitrile", "calzature di sicurezza"])),

    "Ventilatore estrattore": attrezzatura(ATTREZZO, rischi=[
        r("Ambienti confinati o sospetti di inquinamento", 2, 4,
          "Il ventilatore non sostituisce la procedura del D.P.R. 177/2011: misurazione dell'atmosfera prima "
          "e durante l'accesso, ventilazione continua, aria presa da zona pulita lontana da scarichi di "
          "motori, presidio esterno e piano di recupero.", DPI_BASE + ", imbracatura, autorespiratore"),
        r("Incendio ed esplosione", 1, 4,
          "In presenza possibile di gas o vapori infiammabili usare ventilatori in esecuzione ATEX e "
          "condotti antistatici; motore a scoppio mai nell'ambiente ventilato."),
        r("Cesoiamenti e stritolamenti", 1, 3,
          "Griglie di protezione su aspirazione e mandata; manutenzione a ventilatore fermo e staccato."),
        _elettrocuzione(),
        _rumore(3, 2),
    ], scheda_uso=scheda(
        "Ventilatore portatile con condotto flessibile per immettere aria pulita o estrarre aria viziata, "
        "fumi e polveri da pozzetti, cunicoli, vasche e locali chiusi.",
        ["verificare griglie, condotto e alimentazione (esecuzione ATEX se necessario)",
         "posizionare la presa d'aria in zona pulita, lontana da gas di scarico",
         "ventilare il tempo necessario e misurare l'atmosfera con il rilevatore prima dell'accesso",
         "verificare che l'accesso all'ambiente confinato sia autorizzato e presidiato (D.P.R. 177/2011)"],
        ["mantenere il ventilatore sempre acceso durante la permanenza degli addetti",
         "non schiacciare né piegare il condotto",
         "uscire subito se il ventilatore si arresta o il rilevatore dà allarme"],
        ["spegnere e staccare l'alimentazione",
         "pulire griglie e condotto e verificarne le lacerazioni"],
        ["otoprotettori", "guanti", "calzature di sicurezza", "casco"])),

    "Rilevatore multigas": attrezzatura(ATTREZZO, rischi=[
        r("Ambienti confinati o sospetti di inquinamento", 2, 4,
          "Una lettura errata espone ad asfissia o intossicazione: strumento tarato e sottoposto a prova di "
          "risposta (bump test) prima di ogni uso; sensori adatti ai gas attesi (O2, LEL, H2S, CO); misura "
          "dall'esterno prima di entrare e a più altezze; lavoratori qualificati secondo il D.P.R. 177/2011.",
          DPI_BASE + ", imbracatura, autorespiratore"),
        r("Incendio ed esplosione", 1, 4,
          "Strumento certificato ATEX per la zona di impiego; allarme LEL al 10% del limite inferiore di "
          "esplosività con immediato abbandono dell'area."),
        r("Caduta dall'alto", 1, 4,
          "Misure nei pozzetti con sonda e tubo di campionamento, senza sporgersi; aperture protette."),
    ], scheda_uso=scheda(
        "Strumento portatile con sensori e allarmi acustici e luminosi che misura ossigeno, gas "
        "infiammabili e gas tossici prima e durante il lavoro in ambienti confinati o scavi.",
        ["verificare la data di taratura e la carica della batteria",
         "eseguire la prova di risposta con gas di riferimento e l'azzeramento in aria pulita",
         "controllare che le soglie di allarme siano quelle stabilite dalla procedura"],
        ["misurare dall'esterno con la pompa e la sonda prima di entrare, a varie quote",
         "indossare lo strumento acceso vicino alle vie respiratorie per tutta la permanenza",
         "abbandonare subito l'ambiente all'allarme e non rientrare senza nuova misura",
         "registrare le letture sul permesso di lavoro"],
        ["scaricare e conservare la registrazione dei dati",
         "pulire lo strumento e ricaricarlo",
         "inviare a taratura alla scadenza o dopo urti e saturazioni dei sensori"],
        ["casco", "calzature di sicurezza", "guanti"])),

    "Argano a bandiera": attrezzatura(ATTREZZO, rischi=[
        r("Caduta di materiale dall'alto o a livello", 3, 4,
          "Portata indicata e rispettata; gancio con dispositivo di chiusura; carichi imbracati in secchioni "
          "o cassoni chiusi; zona sottostante delimitata e interdetta; fine corsa superiore efficiente; "
          "verifiche periodiche dell'Allegato VII se di portata superiore a 200 kg."),
        r("Caduta dall'alto", 2, 4,
          "Postazione di ricevimento con parapetto e cancelletto o fermo apribile (Allegato XVIII); "
          "addetto che non si sporge oltre il parapetto e, se necessario, è vincolato con imbracatura a "
          "punto fisso.", DPI_BASE + ", imbracatura, cordino con assorbitore"),
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Fissaggio al ponteggio solo se previsto dal fabbricante del ponteggio e dal PiMUS, con montante "
          "rinforzato e ancoraggi aggiuntivi; staffa o morsetti serrati e controllati; mai fissaggi di fortuna."),
        _elettrocuzione(1, 4, "Pulsantiera a bassa tensione con arresto di emergenza; cavo protetto dagli urti."),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Carico guidato da terra con fune di guida; nessuno sotto il carico durante sollevamento e "
          "discesa; rotazione del braccio solo a carico fermo."),
    ], scheda_uso=scheda(
        "Piccolo apparecchio di sollevamento elettrico con braccio girevole, fissato a ponteggio, solaio o "
        "montante, per sollevare materiali al piano di lavoro.",
        ["verificare targa di portata, fune, gancio con chiusura e fine corsa",
         "controllare il fissaggio alla struttura secondo il manuale e il PiMUS del ponteggio",
         "allestire al piano un varco con parapetto e cancelletto apribile",
         "delimitare a terra l'area di caduta dei carichi"],
        ["non superare la portata e non sollevare persone",
         "aprire il cancelletto solo per ricevere il carico, con l'addetto in posizione sicura",
         "manovrare con fune avvolta in modo regolare, senza tiri obliqui",
         "sospendere con vento forte o se il carico oscilla"],
        ["lasciare il gancio in alto senza carico e richiudere il cancelletto",
         "togliere l'alimentazione e proteggere la pulsantiera",
         "annotare sul registro i controlli trimestrali di funi e catene (Allegato VI punto 3.1.2)"],
        ["casco con sottogola", "guanti", "calzature di sicurezza", "imbracatura"])),

    "Argano a cavalletto": attrezzatura(ATTREZZO, rischi=[
        r("Caduta di materiale dall'alto o a livello", 3, 4,
          "Portata rispettata; zavorre o ancoraggi del cavalletto secondo il manuale; gancio con chiusura e "
          "fine corsa; area di sollevamento delimitata; verifiche dell'Allegato VII per portate oltre 200 kg."),
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Cavalletto appoggiato su solaio di portata verificata; zavorre fisse e non costituite da materiali "
          "sciolti; distanza dal bordo come da manuale; controllo del serraggio di tutti i giunti."),
        r("Caduta dall'alto", 2, 4,
          "Bordo del solaio o della copertura protetto con parapetto, salvo il varco di manovra; addetto al "
          "varco vincolato con imbracatura a punto di ancoraggio idoneo.",
          DPI_BASE + ", imbracatura, cordino con assorbitore"),
        _elettrocuzione(1, 4),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Carico accompagnato con fune di guida; mani lontane dal tamburo e dalla fune in movimento."),
    ], scheda_uso=scheda(
        "Argano elettrico montato su telaio a cavalletto zavorrato, appoggiato su solai o coperture piane, "
        "per il sollevamento di materiali dove non si può usare il ponteggio.",
        ["verificare portata del solaio, zavorre previste dal fabbricante e serraggio dei giunti",
         "controllare fune, gancio con chiusura, freno e fine corsa",
         "proteggere il bordo con parapetto e lasciare solo il varco necessario",
         "delimitare a terra la zona di sollevamento"],
        ["non sollevare persone e non superare la portata",
         "non rimuovere né spostare le zavorre durante l'uso",
         "ricevere il carico solo quando è fermo, tirandolo dentro con il gancio d'accompagnamento",
         "sospendere con vento forte"],
        ["mettere a terra il carico, togliere l'alimentazione e proteggere l'argano dalla pioggia",
         "richiudere il varco del parapetto",
         "registrare i controlli periodici di funi e ganci"],
        ["casco con sottogola", "guanti", "calzature di sicurezza", "imbracatura"])),

    "Motoperforatrice (trivella a motore)": attrezzatura(ATTREZZO, rischi=[
        r("Urti, colpi, impatti e compressioni", 3, 3,
          "Il blocco della punta nel terreno produce una forte reazione di torsione: macchine con frizione o "
          "barra di reazione; impugnatura a due mani e posizione stabile; uso a due operatori per i diametri "
          "maggiori; avanzamento lento in terreni con sassi e radici."),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Indumenti aderenti e niente lacci o sciarpe vicino alla coclea; motore spento per liberare la "
          "punta o cambiare la trivella."),
        r("Elettrocuzione", 1, 4,
          "Individuazione preventiva di cavi e tubazioni interrate con planimetrie degli enti e cercaservizi; "
          "perforazione sospesa al primo indizio di sottoservizi."),
        _rumore(3, 2),
        _vibrazioni(3, 2),
        r("Incendio ed esplosione", 1, 3,
          "Rifornimento a motore spento e freddo, lontano da fiamme; tanica omologata; gas di scarico lontani "
          "da scavi e pozzetti."),
    ], scheda_uso=scheda(
        "Trivella portatile con motore a scoppio e punta elicoidale per fori nel terreno destinati a pali, "
        "recinzioni, cartelli e piantumazioni.",
        ["verificare con planimetrie e cercaservizi l'assenza di sottoservizi nel punto di foro",
         "controllare impugnature, acceleratore con ritorno automatico, frizione e fissaggio della punta",
         "rifornire a motore spento e allontanarsi dal punto di rifornimento per l'avviamento"],
        ["impugnare con due mani, con piedi ben piantati e fuori dalla traiettoria della coclea",
         "avanzare gradualmente sollevando spesso la punta per scaricare il terreno",
         "rilasciare l'acceleratore subito se la punta si blocca",
         "non lasciare la macchina in moto incustodita"],
        ["spegnere il motore e pulire la punta",
         "coprire o segnalare i fori aperti",
         "riporre la macchina a motore freddo"],
        ["otoprotettori", "guanti antivibrazioni", "occhiali protettivi", "calzature di sicurezza", "casco"])),

    # ================================ OPERE PROVVISIONALI ================================
    "Scala doppia": attrezzatura(OPERA, rischi=[
        r("Caduta dall'alto", 3, 3,
          "Scala conforme alla UNI EN 131 e all'art. 113 (altezza non oltre 5 m, catena o dispositivo contro "
          "l'apertura); uso solo per lavori brevi e a basso rischio, quando un'attrezzatura più sicura non è "
          "giustificata (art. 111, comma 3); non salire sugli ultimi gradini salvo piattaforma con guardacorpo; "
          "una persona alla volta."),
        r("Crollo o ribaltamento di strutture", 2, 3,
          "Appoggio su superficie piana e portante, con piedini antiscivolo integri; scala completamente "
          "aperta e bloccata; non spostarla con persone sopra; non usarla come scala semplice."),
        r("Caduta di materiale dall'alto o a livello", 2, 2,
          "Attrezzi in borsa o fondina; nessun materiale appoggiato sulla sommità; area sottostante libera."),
        r("Posture incongrue", 2, 1,
          "Posizionare la scala vicino al punto di lavoro senza sporgersi lateralmente; lavori prolungati "
          "su ponte su cavalletti o trabattello."),
    ], scheda_uso=scheda(
        "Scala portatile a due tronchi incernierati, autostabile, a gradini o pioli, per lavori di breve "
        "durata a modesta altezza.",
        ["verificare marcatura UNI EN 131, montanti, gradini, piedini e catena o tirante contro l'apertura",
         "scegliere la lunghezza adatta senza dover usare gli ultimi gradini",
         "posizionarla su piano stabile e non scivoloso, lontano da porte, passaggi e linee elettriche"],
        ["aprirla completamente e verificare il blocco prima di salire",
         "salire con il viso rivolto alla scala mantenendo tre punti di appoggio",
         "non sporgersi lateralmente e non spostarla stando sopra",
         "usare attrezzi leggeri tenuti in borsa"],
        ["chiuderla e riporla al riparo, in posizione orizzontale o vincolata",
         "togliere dall'uso e segnalare la scala danneggiata"],
        ["casco con sottogola", "calzature di sicurezza", "guanti"])),

    "Ponte su cavalletti": attrezzatura(OPERA, rischi=[
        r("Caduta dall'alto", 2, 3,
          "Altezza dell'impalcato non oltre 2 m e mai su impalcati di ponteggi (art. 139); impalcato largo "
          "almeno 90 cm con tavole accostate, fissate ai cavalletti e sbalzi non oltre 20 cm (Allegato XVIII "
          "punto 2.2.2); parapetto se posto vicino ad aperture o bordi verso il vuoto."),
        r("Crollo o ribaltamento di strutture", 2, 3,
          "Cavalletti su piano stabile e livellato, mai su mattoni o materiali instabili; vietati ponti "
          "sovrapposti e montanti costituiti da scale a pioli; distanza tra i cavalletti adeguata allo "
          "spessore delle tavole (in genere non oltre 1,80 m con tavole da 4 cm)."),
        r("Caduta di materiale dall'alto o a livello", 2, 2,
          "Materiale sull'impalcato limitato a quello di uso immediato; tavole senza nodi passanti o fessure."),
        r("Scivolamenti e cadute a livello", 2, 2,
          "Impalcato pulito da malta e detriti; salita tramite scala e non dai cavalletti."),
    ], scheda_uso=scheda(
        "Piano di lavoro di tavole o elementi metallici appoggiati su cavalletti, per lavori interni o "
        "esterni a quota non superiore a 2 m.",
        ["verificare integrità di cavalletti e tavole e il piano di appoggio",
         "comporre un impalcato largo almeno 90 cm con tavole fissate e sbalzi entro 20 cm",
         "porre i cavalletti a interasse compatibile con lo spessore delle tavole",
         "aggiungere il parapetto vicino a vani, finestre e bordi aperti"],
        ["salire con scala, non arrampicandosi sui cavalletti",
         "non sovraccaricare l'impalcato e non concentrare il materiale in campata",
         "non sovrapporre cavalletti o altri appoggi per guadagnare altezza",
         "tenere pulito il piano di lavoro"],
        ["smontare o liberare l'impalcato da materiali a fine turno",
         "scartare tavole lesionate e cavalletti deformati"],
        ["casco", "calzature di sicurezza", "guanti"])),

    "Parapetto provvisorio": attrezzatura(OPERA, rischi=[
        r("Caduta dall'alto", 2, 4,
          "Parapetto con corrente superiore ad almeno 1 m, corrente intermedio e fermapiede di almeno 15 cm "
          "(Allegato XVIII punto 2.1.5 e art. 126); sistemi di classe A, B o C secondo la UNI EN 13374 "
          "scelti in base alla pendenza della superficie; montaggio dal lato protetto o con DPI anticaduta "
          "vincolati.", DPI_BASE + ", imbracatura, cordino con assorbitore"),
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Montanti fissati con morsetti, piastre o tasselli al supporto di resistenza verificata secondo le "
          "istruzioni del fabbricante; interasse dei montanti non superiore a quello indicato; controlli "
          "periodici del serraggio e dopo eventi atmosferici."),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Fermapiede continuo; rete o pannelli di tamponamento dove si accumula materiale; nessun deposito "
          "appoggiato al parapetto."),
        r("Movimentazione manuale dei carichi", 2, 2,
          "Elementi trasportati a mano solo se maneggevoli; pacchi sollevati al piano con mezzi meccanici."),
    ], scheda_uso=scheda(
        "Protezione collettiva temporanea dei bordi di solai, coperture, scale, aperture e scavi, composta da "
        "montanti, correnti o pannelli e fermapiede.",
        ["scegliere il sistema (classe UNI EN 13374) adatto alla pendenza e al tipo di bordo",
         "verificare la resistenza del supporto e i dispositivi di fissaggio previsti dal fabbricante",
         "pianificare il montaggio per lavorare sempre da zona già protetta o con imbracatura vincolata"],
        ["mantenere continui corrente superiore, intermedio e fermapiede",
         "non rimuovere tratti di parapetto senza protezione sostitutiva",
         "non appoggiarsi né sedersi sul parapetto e non usarlo come ancoraggio per i carichi",
         "controllare il serraggio dopo vento, urti e a inizio turno"],
        ["smontare solo quando il bordo è protetto in modo definitivo",
         "verificare gli elementi e scartare quelli deformati o corrosi"],
        ["casco con sottogola", "calzature di sicurezza", "guanti", "imbracatura", "cordino con assorbitore"])),

    "Rete di sicurezza anticaduta": attrezzatura(OPERA, rischi=[
        r("Caduta dall'alto", 2, 4,
          "Rete conforme alla UNI EN 1263-1 posata secondo la UNI EN 1263-2 e il manuale: altezza di caduta "
          "sulla rete non oltre 6 m (3 m vicino ai bordi), larghezza di raccolta oltre il bordo di lavoro, "
          "spazio libero sotto la rete sufficiente alla freccia; etichetta e maglia di prova presenti; "
          "rete sostituita dopo una caduta o oltre la durata indicata."),
        r("Caduta di materiale dall'alto o a livello", 2, 2,
          "Rimozione frequente di materiali caduti sulla rete; rete a maglia fine sovrapposta se necessario "
          "trattenere oggetti piccoli."),
        r("Crollo o ribaltamento di strutture", 1, 4,
          "Punti di ancoraggio della rete dimensionati per i carichi della UNI EN 1263-2; funi di bordo e "
          "di legatura integre; nessun elemento tagliente a contatto della rete."),
        r("Caduta dall'alto durante il montaggio", 2, 4,
          "Posa e smontaggio da piattaforme di lavoro elevabili o con imbracatura vincolata; personale "
          "formato secondo il manuale.", DPI_BASE + ", imbracatura, cordino con assorbitore"),
    ], scheda_uso=scheda(
        "Rete in fibra sintetica con fune perimetrale, tesa sotto o lungo i bordi del piano di lavoro per "
        "trattenere le persone che cadono (sistemi S, T, U, V della UNI EN 1263-1).",
        ["controllare etichetta, data di fabbricazione, maglia di prova e integrità della rete",
         "verificare la distanza tra piano di lavoro e rete e lo spazio libero sotto",
         "fissarla ai punti di ancoraggio previsti con le funi di legatura e a interassi da manuale",
         "proteggerla da spigoli vivi, fiamme e lavori a caldo"],
        ["non usarla come deposito di materiali o piano di passaggio",
         "togliere subito oggetti caduti sulla rete",
         "sospendere i lavori sopra la rete se danneggiata o allentata",
         "evitare saldature e tagli a caldo sopra la rete"],
        ["smontare con le stesse cautele del montaggio",
         "conservarla asciutta e al riparo dalla luce solare",
         "eliminarla dopo una caduta o a fine vita utile"],
        ["casco con sottogola", "imbracatura", "cordino con assorbitore", "guanti",
         "calzature di sicurezza"])),

    "Linea vita provvisoria": attrezzatura(OPERA, rischi=[
        r("Caduta dall'alto", 2, 4,
          "Dispositivo di ancoraggio temporaneo conforme alla UNI EN 795 (tipo B o C) installato secondo il "
          "manuale su struttura di resistenza verificata; tirante d'aria calcolato per evitare l'urto al "
          "suolo; uso solo con imbracatura e cordino con assorbitore (DPI di terza categoria, addestramento "
          "obbligatorio, art. 77, comma 5).", DPI_BASE + ", imbracatura, cordino con assorbitore"),
        r("Effetto pendolo e urto contro ostacoli", 2, 3,
          "Linea posizionata il più possibile sopra e in asse alla zona di lavoro; cordini regolabili o "
          "retrattili per limitare la libera caduta."),
        r("Sospensione inerte dopo l'arresto", 1, 4,
          "Piano di emergenza e salvataggio con kit di recupero e personale addestrato presente; intervento "
          "entro pochi minuti."),
        r("Crollo o ribaltamento di strutture", 1, 4,
          "Ancoraggi d'estremità non fissati su elementi di dubbia tenuta (lucernari, gronde, parapetti); "
          "tensionamento secondo il manuale; ispezione prima di ogni utilizzo."),
    ], scheda_uso=scheda(
        "Fune o nastro orizzontale tesi tra ancoraggi provvisori, a cui i lavoratori si collegano con "
        "imbracatura per i lavori in quota senza protezioni collettive.",
        ["verificare idoneità della struttura di ancoraggio e manuale di installazione",
         "calcolare il tirante d'aria disponibile con la freccia della linea e il cordino usato",
         "ispezionare fune, tenditore, ancoraggi e DPI prima dell'uso",
         "predisporre la procedura di salvataggio"],
        ["restare sempre collegati, usando due cordini nei passaggi tra campate",
         "non collegare alla linea più persone di quante ammesse dal fabbricante",
         "evitare il contatto della fune con spigoli vivi",
         "non lavorare mai da soli"],
        ["smontare la linea senza staccarsi da altri ancoraggi sicuri",
         "togliere dall'uso la linea e i DPI che hanno arrestato una caduta",
         "conservare i componenti puliti e asciutti e registrare le ispezioni"],
        ["imbracatura", "cordino con assorbitore", "dispositivo retrattile", "casco con sottogola",
         "calzature di sicurezza", "guanti"])),

    "Andatoie e passerelle": attrezzatura(OPERA, rischi=[
        r("Caduta dall'alto", 2, 4,
          "Larghezza di almeno 60 cm per il solo passaggio di persone e 120 cm con trasporto di materiali; "
          "pendenza non oltre il 25%; parapetto normale con fermapiede sui lati verso il vuoto (art. 130 e "
          "Allegato XVIII); pianerottoli di riposo nelle andatoie lunghe."),
        r("Scivolamenti e cadute a livello", 3, 2,
          "Listelli trasversali fissati sul piano di calpestio a distanza pari al passo di un uomo carico; "
          "pulizia da fango, malta e ghiaccio; illuminazione nelle ore buie."),
        r("Crollo o ribaltamento di strutture", 1, 4,
          "Appoggi stabili e lontani dal ciglio degli scavi; passerelle metalliche di portata dichiarata; "
          "tavole senza difetti fissate agli appoggi."),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Andatoie poste in zona di possibile caduta di materiali protette con impalcato sovrastante "
          "(parasassi) o spostate fuori dal raggio d'azione dei mezzi di sollevamento."),
    ], scheda_uso=scheda(
        "Percorsi provvisori in tavole o elementi metallici per superare scavi, dislivelli o raggiungere "
        "i posti di lavoro.",
        ["dimensionare larghezza e pendenza in base al tipo di passaggio",
         "montare i parapetti verso il vuoto e i listelli antiscivolo",
         "posare gli appoggi su terreno consolidato e lontano dal ciglio degli scavi"],
        ["non sostare e non depositare materiali sull'andatoia",
         "transitare una persona alla volta sulle passerelle strette",
         "segnalare subito tavole rotte, mobili o listelli mancanti"],
        ["pulire il piano di calpestio a fine turno",
         "rimuovere o interdire le passerelle non più necessarie"],
        ["casco", "calzature di sicurezza", "guanti", "indumenti ad alta visibilità"])),

    "Armatura delle pareti di scavo (blindaggio)": attrezzatura(OPERA, rischi=[
        r("Seppellimento e sprofondamento", 2, 4,
          "Armatura delle pareti oltre 1,50 m di profondità salvo pareti a scarpa sicura (art. 118), "
          "dimensionata sulla relazione geotecnica e posata via via che lo scavo procede; nessun lavoratore "
          "in zona non armata; pannelli sporgenti oltre il ciglio di almeno 30 cm; materiali e mezzi tenuti "
          "lontani dal ciglio (art. 120)."),
        r("Caduta dall'alto", 2, 3,
          "Ciglio dello scavo con parapetto o barriera; accessi con scale vincolate sporgenti 1 m oltre il "
          "bordo; vietato salire sulle traverse dei blindaggi."),
        r("Cesoiamenti e stritolamenti", 2, 4,
          "Inserimento ed estrazione dei pannelli con escavatore abilitato al sollevamento e ganci idonei; "
          "nessuno tra pannello e parete durante la posa; comunicazioni con segnalatore."),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Tavola o fascia oltre il ciglio come fermapiede; controllo delle armature dopo piogge e prima di "
          "ogni ripresa dei lavori."),
        r("Ambienti confinati o sospetti di inquinamento", 1, 4,
          "In scavi profondi e trincee vicine a reti di gas o fognature misurare l'atmosfera e ventilare "
          "(art. 121)."),
    ], scheda_uso=scheda(
        "Sistemi di sostegno delle pareti di trincee e scavi a sezione obbligata, con pannelli e puntoni "
        "metallici a cassone o a slitta, oppure con tavole e sbadacchi.",
        ["verificare progetto o schema di montaggio del fabbricante in base al terreno e alla profondità",
         "controllare pannelli, puntoni a vite e dispositivi di sollevamento",
         "individuare i sottoservizi e delimitare l'area di manovra"],
        ["calare i pannelli man mano che lo scavo avanza senza entrare in zona non armata",
         "regolare i puntoni da posizione protetta",
         "tenere terra di scavo, materiali e mezzi a distanza dal ciglio",
         "ispezionare le armature a ogni ripresa e dopo forti piogge"],
        ["estrarre i pannelli gradualmente durante il rinterro, senza persone nello scavo",
         "pulire e verificare gli elementi prima del riuso"],
        ["casco", "calzature di sicurezza", "guanti", "indumenti ad alta visibilità"])),

    "Puntelli metallici": attrezzatura(OPERA, rischi=[
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Puntelli telescopici conformi alla UNI EN 1065 impiegati entro la portata della classe e "
          "dell'estensione usata; disposizione secondo il progetto delle opere provvisionali (UNI EN 12812); "
          "appoggio su basi di ripartizione e piano portante; perni originali; controventamento dove serve."),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Regolazione dell'altezza solo con il perno di sicurezza inserito; mani lontane dai fori del tubo "
          "interno; mai sostituire il perno con chiodi o tondini."),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Puntelli accatastati legati o in ceste; in movimentazione con gru uso di ceste apposite."),
        r("Movimentazione manuale dei carichi", 2, 2,
          "Puntelli lunghi trasportati da due persone; posa a coppie per le estensioni maggiori."),
    ], scheda_uso=scheda(
        "Puntelli telescopici regolabili in acciaio per sostenere solai, casseforme e strutture durante "
        "getti, lavori di consolidamento e demolizioni.",
        ["verificare classe e portata in relazione all'estensione (UNI EN 1065)",
         "scartare puntelli piegati, corrosi o con filettature danneggiate",
         "predisporre basi di ripartizione su piano stabile e secondo lo schema di progetto"],
        ["posare i puntelli in verticale e bloccarli con perno e ghiera",
         "non sovrapporre puntelli o allungarli con spessori improvvisati",
         "controllare che nessun puntello sia allentato prima e durante i getti"],
        ["disarmare solo dopo l'autorizzazione del direttore dei lavori e nell'ordine stabilito",
         "pulire, verificare e accatastare i puntelli in ceste o legati"],
        ["casco", "calzature di sicurezza", "guanti"])),

    "Casseforme": attrezzatura(OPERA, rischi=[
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Casseforme e loro sostegni realizzati secondo progetto o schema del fabbricante (art. 140, UNI EN "
          "12812); velocità di getto compatibile con la spinta del calcestruzzo; puntelli e saette di "
          "stabilizzazione delle pareti verticali; disarmo autorizzato dal direttore dei lavori."),
        r("Caduta dall'alto", 2, 4,
          "Mensole e passerelle di getto con parapetto incorporate nelle casseforme verticali; perimetro dei "
          "solai protetto con parapetti; accessi con scale vincolate.",
          DPI_BASE + ", imbracatura, cordino con assorbitore"),
        r("Punture, tagli e abrasioni", 3, 2,
          "Chiodi ripiegati o rimossi dalle tavole di disarmo; ferri di ripresa protetti con cappellotti; "
          "ordine della zona di lavoro."),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Pannelli sollevati con gru tramite punti di aggancio previsti; nessuno sotto il carico; disarmo "
          "con zona sottostante interdetta."),
        r("Rischio chimico", 2, 2,
          "Disarmanti applicati a rullo o a bassa pressione secondo la scheda di sicurezza; evitare nebbie.",
          DPI_BASE + ", guanti in lattice o nitrile"),
    ], scheda_uso=scheda(
        "Sistemi di casseratura in legno o in pannelli metallici e plastici per il getto di pareti, pilastri, "
        "travi e solai in calcestruzzo armato.",
        ["verificare progetto o schema di montaggio e la stabilità dei sostegni",
         "controllare pannelli, morsetti, tiranti e passerelle di getto",
         "predisporre parapetti e accessi prima del getto"],
        ["montare pannelli e tiranti nella sequenza del fabbricante",
         "rispettare la velocità di getto prevista e sorvegliare le casseforme durante il getto",
         "non salire sui pannelli o sulle armature di ferro come passaggio"],
        ["disarmare dopo la maturazione e con l'autorizzazione del direttore dei lavori",
         "schiodare, pulire e accatastare gli elementi in modo stabile"],
        ["casco", "calzature di sicurezza", "guanti", "imbracatura"])),

    "Unità di decontaminazione (amianto)": attrezzatura(OPERA, rischi=[
        r("Esposizione ad amianto", 2, 4,
          "Unità composta da locale di equipaggiamento, locale doccia, chiusa d'aria e locale incontaminato "
          "(D.M. 6 settembre 1994), unico passaggio per entrare e uscire dall'area confinata; flusso d'aria "
          "dall'esterno verso la zona di lavoro mantenuto dagli estrattori; collaudo di tenuta prima dei "
          "lavori; procedura di uscita stabilita nel piano di lavoro (art. 256).",
          DPI_BASE + ", facciale filtrante FFP3, tuta monouso"),
        r("Rischio biologico", 1, 2,
          "Docce con acqua calda pulite e disinfettate; acque di lavaggio filtrate prima dello scarico; "
          "indumenti personali tenuti solo nel locale incontaminato."),
        _elettrocuzione(1, 4, "Impianti di illuminazione, docce e boiler della UDC eseguiti e certificati per "
                              "locali bagnati (grado di protezione idoneo)."),
        r("Scivolamenti e cadute a livello", 2, 2,
          "Pavimenti con pedane antiscivolo, teli integri e fissati, illuminazione adeguata nei passaggi."),
        r("Microclima", 2, 2,
          "Riscaldamento dei locali nella stagione fredda; pause per chi lavora con tute e maschere."),
    ], scheda_uso=scheda(
        "Struttura modulare con locali in sequenza (equipaggiamento, doccia, chiusa d'aria, locale "
        "incontaminato) per l'ingresso e la decontaminazione dei lavoratori nei cantieri di bonifica "
        "dell'amianto.",
        ["montarla a contatto con l'area confinata, con teli e porte a battente secondo il D.M. 6 settembre 1994",
         "verificare docce con acqua calda, filtri delle acque reflue e illuminazione",
         "eseguire il collaudo di tenuta e la prova della depressione prima di iniziare",
         "affiggere la procedura di ingresso e uscita"],
        ["entrare passando dal locale incontaminato, dove si indossano tuta e maschera",
         "all'uscita aspirare la tuta, toglierla nel locale di equipaggiamento e fare la doccia con la maschera",
         "non portare all'esterno materiali e attrezzi non decontaminati",
         "controllare ogni giorno integrità dei teli e funzionamento delle docce"],
        ["pulire a umido i locali e smaltire tute, filtri e teli come rifiuti contenenti amianto",
         "smontarla solo dopo la certificazione di restituibilità dell'area, iniziando dalla zona contaminata"],
        ["facciale filtrante FFP3", "tuta monouso", "guanti in lattice o nitrile", "stivali di sicurezza"])),
}
