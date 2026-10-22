"""Attrezzature richieste dai moduli delle fasi e non previste nel catalogo iniziale.

Rischi generati dall'uso e schede d'uso scritti da zero per questo progetto. I testi vanno sempre
confrontati con il manuale d'uso del fabbricante dell'attrezzatura.

Fonti CONSULTATE ONLINE durante la stesura (ricerche web, ottobre 2026):
- PuntoSicuro: schede di prevenzione sulle fondazioni speciali e sui fanghi bentonitici; articolo
  sulla sicurezza nell'esecuzione dei tiranti d'ancoraggio (solo titolo e sintesi); casi di
  infortunio con getti d'acqua ad alta pressione; bonifica dell'amianto friabile e sicurezza nei
  cantieri di bonifica (estrattori con filtro HEPA in funzione continua, almeno 4 ricambi/ora);
- Regione Emilia-Romagna, documento sulla bonifica dei materiali contenenti amianto friabile
  (confinamento statico e dinamico, collaudo con fumogeni e manometro differenziale);
- testo dell'art. 153-154 D.Lgs. 81/2008 (Brocardi, Certifico): canali di scarico delle macerie;
- schede di fabbricanti: treppiedi UNI EN 795 tipo B con verricello UNI EN 1496 (Tractel, Delta
  Plus), pompe wellpoint (Atlas Copco, Infobuild), taglierine a filo caldo (temperatura del filo);
- scheda di valutazione dei rischi della Sapienza e istruzioni del Politecnico di Milano sull'uso
  del filo caldo (ustioni, fumi, aspirazione accesa durante il taglio);
- guide di settore nordamericane sui robot di idrodemolizione (zona di rispetto di circa 10 m,
  secondo addetto che può arrestare la pompa).

Riferimenti scritti A MEMORIA, non riletti sul testo durante la stesura (da verificare):
- D.Lgs. 81/2008: artt. 70-73, 80-87, 91, 104 e Allegati V, VI, VII, IX, XXXIII, XLII; Titoli VI,
  VIII (Capi II e III) e IX (Capi I, II, III); D.P.R. 177/2011; D.M. 6 settembre 1994 (punti
  diversi da quelli sopra); D.M. 82/2015 (bonifica bellica); D.M. 10 luglio 2002, D.M. 22 gennaio
  2019, D.M. 1 ottobre 2013;
- norme CEI 11-27, CEI 64-8 Parte 6, CEI EN 61010-1/-031, CEI EN 61243-3, CEI EN 61557,
  CEI EN 62841, CEI EN 60335-2-69, CEI EN 60309;
- norme UNI EN 16228-1/-2/-5, UNI EN ISO 22476-1/-2, UNI EN 1537, UNI EN ISO 22477-5,
  UNI EN 14492-2, UNI EN 818, UNI EN 1492, UNI EN 13414, UNI EN 1677, UNI EN 13155, UNI EN 360, UNI EN 361, UNI EN 1822
  (classi dei filtri HEPA), UNI EN 13020, UNI EN 12001, UNI EN 1829-1;
- valori numerici non trovati nelle fonti: temperature dell'emulsione, pressione e rumore
  dell'idrodemolizione, tensioni delle prove di isolamento, distanze dell'Allegato IX.
"""

from __future__ import annotations

from typing import Any

from sicurcantiere.archivio_dati.base import ATTREZZO, DPI_BASE, MACCHINA, OPERA, attrezzatura, r, scheda

# --- rischi ricorrenti ---------------------------------------------------------------------

def _elettrocuzione(p: int = 1, d: int = 4, extra: str = "") -> dict[str, Any]:
    return r("Elettrocuzione", p, d,
             "Attrezzatura a doppio isolamento o collegata all'impianto di terra; alimentazione da quadro "
             "di cantiere con differenziale da 30 mA (CEI 64-8, sezione 704); cavi H07RN-F integri, "
             "protetti dal passaggio di mezzi e lontani da acqua e fanghi; prese e spine industriali "
             "CEI EN 60309 con grado di protezione adeguato all'ambiente." + (" " + extra if extra else ""))


def _rumore(p: int = 3, d: int = 2, nota: str = "") -> dict[str, Any]:
    return r("Rumore", p, d,
             "Valutazione dell'esposizione secondo il Titolo VIII, Capo II; macchine silenziate e carter "
             "fonoassorbenti chiusi; postazione dell'operatore il più lontano possibile dalla sorgente; "
             "turnazione; otoprotettori obbligatori oltre il valore superiore di azione (85 dB(A)) e "
             "sorveglianza sanitaria degli esposti." + (" " + nota if nota else ""),
             DPI_BASE + ", otoprotettori")


def _vibrazioni_hav(p: int = 3, d: int = 2, nota: str = "") -> dict[str, Any]:
    return r("Vibrazioni al sistema mano-braccio", p, d,
             "Valutazione secondo il Titolo VIII, Capo III (valore d'azione 2,5 m/s², limite 5 m/s²); "
             "impugnature antivibranti integre; pause e rotazione degli addetti; sorveglianza sanitaria."
             + (" " + nota if nota else ""), DPI_BASE + ", guanti antivibrazioni")


def _silice(p: int = 3, d: int = 3, nota: str = "") -> dict[str, Any]:
    return r("Polveri e fibre", p, d,
             "Taglio di calcestruzzo, laterizio e conglomerati: polvere con silice cristallina respirabile, "
             "agente cancerogeno (Titolo IX, Capo II, Allegato XLII): lavorazione a umido o con "
             "aspirazione alla fonte; area delimitata; pulizia con aspiratore e non a secco con scope o "
             "aria compressa." + (" " + nota if nota else ""),
             DPI_BASE + ", facciale filtrante FFP3, occhiali a maschera")


def _tubi_pressione(p: int = 2, d: int = 3, fluido: str = "fluido", extra: str = "") -> dict[str, Any]:
    return r("Getti e schizzi", p, d,
             f"Tubazioni e raccordi del {fluido} con pressione nominale non inferiore a quella massima "
             "dell'impianto, ispezionati prima dell'uso e sostituiti se abrasi o rigonfi; giunti con "
             "fermi di sicurezza o catenelle anticolpo di frusta; nessun intervento su tubi e raccordi "
             "prima di aver scaricato la pressione residua." + (" " + extra if extra else ""),
             DPI_BASE + ", occhiali a maschera")


def _investimento(p: int = 2, d: int = 4, extra: str = "") -> dict[str, Any]:
    return r("Investimento da mezzi in manovra", p, d,
             "Area di lavoro della macchina delimitata e interdetta ai non addetti; percorsi e manovre "
             "concordati con il preposto; segnalatore acustico di retromarcia e girofaro attivi; "
             "operatori a terra sempre nel campo visivo del conducente, con indumenti ad alta visibilità."
             + (" " + extra if extra else ""))


_DPI_FISSI = ["casco", "calzature di sicurezza", "guanti"]

ATTREZZATURE: dict[str, dict[str, Any]] = {
    # ===================================== ATTREZZI ======================================
    "Sega murale su binario": attrezzatura(ATTREZZO, rischi=[
        r("Proiezione di schegge e frammenti", 2, 4,
          "Carter di protezione del disco sempre montato e regolato (Allegato V, parte I, punto 6); disco "
          "diamantato idoneo al materiale e al numero di giri, senza segmenti mancanti o crepe; zona di "
          "taglio delimitata su entrambi i lati della parete; nessuno sul prolungamento del piano del disco.",
          DPI_BASE + ", visiera protettiva"),
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Sequenza di taglio e puntellamento stabiliti prima dell'inizio, con verifica di un tecnico "
          "sulla stabilità della parete o della soletta residua; blocchi tagliati imbracati o sostenuti "
          "prima del distacco; cunei nel taglio per evitare il pizzicamento del disco."),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Binario fissato con tasselli di tipo e numero indicati dal fabbricante, su supporto sano; "
          "verifica del serraggio prima di montare il carrello; testa motore movimentata con mezzi di "
          "sollevamento o in due; mani lontane dal carrello durante l'avanzamento."),
        _silice(2, 3, "Taglio ad acqua con recupero dei fanghi."),
        _elettrocuzione(2, 4, "Con il raffreddamento ad acqua: macchina con protezione contro i getti, "
                              "trasformatore o differenziale dedicato e cavi lontani dai fanghi di taglio."),
        _rumore(4, 2),
        r("Scivolamenti e cadute a livello", 3, 2,
          "Fanghi di taglio raccolti con aspiratore per liquidi o canalizzati; pavimento asciutto nelle "
          "vie di passaggio; tubi e cavi ordinati lungo il bordo della zona di lavoro.",
          DPI_BASE.replace("calzature di sicurezza", "stivali di sicurezza")),
    ], scheda_uso=scheda(
        "Sega a disco diamantato di grande diametro che scorre su un binario tassellato alla parete o alla "
        "soletta, azionata da motore elettrico ad alta frequenza o idraulico e comandata a distanza; "
        "esegue tagli rettilinei profondi nel calcestruzzo armato.",
        ["far verificare da un tecnico la sequenza dei tagli e i puntellamenti necessari",
         "individuare con rilievi o scansione impianti e armature annegati nella parete",
         "fissare il binario con i tasselli prescritti e controllarne il serraggio",
         "montare disco e carter, verificare l'integrità del disco e l'alimentazione dell'acqua",
         "delimitare la zona di taglio su entrambi i lati e sotto le solette"],
        ["comandare la sega dalla pulsantiera a distanza, fuori dal piano del disco",
         "non rimuovere il carter e non sostare dietro il disco in rotazione",
         "sostenere o imbracare i blocchi prima di completare il taglio",
         "fermare la macchina se il disco si blocca o vibra in modo anomalo"],
        ["arrestare il motore e sezionare l'alimentazione prima di smontare il disco",
         "smontare binario e tasselli e chiudere i fori",
         "raccogliere e smaltire i fanghi di taglio secondo le indicazioni ambientali"],
        ["casco", "visiera protettiva", "otoprotettori", "facciale filtrante FFP3", "guanti",
         "stivali di sicurezza", "indumenti impermeabili"])),

    "Paranco elettrico a catena": attrezzatura(ATTREZZO, rischi=[
        r("Caduta di materiale dall'alto o a livello", 2, 4,
          "Paranco conforme alla UNI EN 14492-2 con portata targata non inferiore al carico; gancio di "
          "sospensione o trave in testata del vano di portata verificata e certificata; catena "
          "(UNI EN 818) e brache (UNI EN 1492) idonee e controllate; ganci con dispositivo di chiusura; "
          "nessuno sotto il carico e vano interdetto ai piani durante il sollevamento (Allegato VI punto 3).",
          DPI_BASE + ", casco con sottogola"),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Carico guidato con funi e non con le mani; velocità ridotta in prossimità di guide e pareti; "
          "comunicazione con radio o segnali convenzionali tra manovratore e addetti ai piani."),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Mani lontane da catena, rinvii e noce di sollevamento; finecorsa superiore e inferiore "
          "funzionanti; pulsantiera con arresto d'emergenza e comandi ad azione mantenuta."),
        r("Caduta dall'alto", 2, 4,
          "Aperture del vano ai piani chiuse con parapetti o sbarramenti; chi opera presso il vano "
          "aperto è trattenuto con imbracatura e cordino agganciati a punto di ancoraggio indipendente "
          "dal paranco.", DPI_BASE + ", imbracatura, cordino con assorbitore"),
        _elettrocuzione(),
    ], scheda_uso=scheda(
        "Paranco con motore elettrico e catena calibrata, appeso a un gancio o a una trave, usato per "
        "sollevare guide, cabine, contrappesi e macchinari nei vani ascensore e in spazi ristretti.",
        ["verificare targa, portata, data dell'ultima verifica trimestrale di funi e catene (Allegato VI punto 3.1.2)",
         "controllare il punto di sospensione e la sua portata dichiarata",
         "provare a vuoto finecorsa, freno e pulsante di arresto d'emergenza",
         "controllare catena, gancio e chiusura di sicurezza, scartando gli elementi usurati o deformati",
         "chiudere o presidiare le aperture del vano ai piani"],
        ["non superare la portata e non tirare carichi in obliquo",
         "imbracare il carico in modo stabile e sollevarlo prima di pochi centimetri per verificarlo",
         "non sostare né transitare sotto il carico sospeso",
         "non lasciare carichi appesi senza sorveglianza"],
        ["appoggiare il carico prima di sganciarlo e riavvolgere la catena",
         "togliere l'alimentazione e riporre la pulsantiera",
         "annotare anomalie e far eseguire la manutenzione periodica"],
        ["casco con sottogola", "guanti", "calzature di sicurezza", "imbracatura",
         "cordino con assorbitore"])),

    "Strumenti di misura per verifiche elettriche": attrezzatura(ATTREZZO, rischi=[
        r("Elettrocuzione", 2, 4,
          "Strumenti conformi alla CEI EN 61010-1 con categoria di misura (CAT III o CAT IV) e tensione "
          "adeguate al punto di misura; puntali e cavetti CEI EN 61010-031 con dita di guardia e parte "
          "metallica scoperta ridotta; rilevatori bipolari CEI EN 61243-3 provati su sorgente nota prima "
          "e dopo la verifica di assenza di tensione; misure eseguite da PES o PAV secondo la CEI 11-27.",
          "Calzature di sicurezza, guanti dielettrici, visiera protettiva, indumenti protettivi"),
        r("Ustioni", 2, 4,
          "Arco elettrico da cortocircuito tra i puntali: selettore e boccole controllati prima del "
          "contatto, mai misure di tensione con lo strumento predisposto in amperometro; fusibili "
          "interni originali ad alto potere di interruzione; indumenti non propaganti la fiamma.",
          "Guanti dielettrici, visiera protettiva, indumenti protettivi"),
        r("Elettrocuzione da tensione di prova", 2, 3,
          "Le prove di isolamento (CEI EN 61557-2) applicano fino a 500-1000 V: circuito sezionato e "
          "segnalato, utilizzatori scollegati, nessuno a contatto con le parti in prova; scarica delle "
          "capacità a fine misura; nelle prove dei differenziali (CEI EN 61557-6) avvertire chi è "
          "alimentato dal circuito.", "Guanti dielettrici, calzature di sicurezza"),
        r("Posture incongrue", 2, 1,
          "Strumento appoggiato o appeso con cinghia, a mani libere; quadri accessibili da posizione "
          "stabile, senza sporgersi; illuminazione sufficiente sul punto di misura.", "Guanti"),
    ], scheda_uso=scheda(
        "Rilevatori di tensione, multimetri, pinze amperometriche e strumenti multifunzione per la misura "
        "di isolamento, continuità, resistenza di terra e intervento dei differenziali (CEI EN 61557), "
        "usati nelle verifiche iniziali CEI 64-8 Parte 6 e nella verifica di assenza di tensione.",
        ["controllare la categoria di misura dello strumento rispetto al punto di misura",
         "ispezionare involucro, puntali e cavetti, scartando quelli con isolamento danneggiato",
         "verificare lo stato della batteria e la data di taratura dello strumento",
         "provare il rilevatore di tensione su una sorgente nota",
         "concordare con il preposto il piano di lavoro e i circuiti da sezionare"],
        ["collegare prima il puntale di riferimento e scollegarlo per ultimo",
         "tenere le dita dietro le guardie dei puntali",
         "non cambiare funzione o portata con i puntali collegati",
         "eseguire le prove di isolamento solo su circuiti sezionati e segnalati",
         "ripetere la prova del rilevatore su sorgente nota dopo la verifica di assenza di tensione"],
        ["scaricare il circuito dopo la prova di isolamento e ripristinare i collegamenti",
         "riporre lo strumento e gli accessori nella custodia",
         "registrare i risultati e segnalare guasti o danni allo strumento"],
        ["guanti dielettrici", "visiera protettiva", "indumenti protettivi", "calzature di sicurezza"])),

    "Treppiede con dispositivo di recupero": attrezzatura(ATTREZZO, rischi=[
        r("Caduta dall'alto", 2, 4,
          "Treppiede certificato come ancoraggio mobile UNI EN 795 tipo B, con piedi bloccati da catena "
          "o cinghia e appoggiati su terreno stabile, centrato sull'apertura; discesa e risalita con "
          "imbracatura UNI EN 361 collegata al dispositivo retrattile UNI EN 360 con funzione di "
          "recupero o al verricello UNI EN 1496; apertura protetta quando nessuno è in discesa.",
          DPI_BASE + ", imbracatura, dispositivo retrattile"),
        r("Ambienti confinati o sospetti di inquinamento", 2, 4,
          "Uso secondo il D.P.R. 177/2011: personale formato e addestrato, procedura scritta di accesso "
          "ed emergenza, misura dell'atmosfera prima e durante l'accesso con rilevatore multigas, "
          "ventilazione forzata, operatore esterno sempre presente al verricello e prova periodica del "
          "recupero dell'infortunato senza ingresso dei soccorritori.",
          "Casco con sottogola, imbracatura, autorespiratore (per l'emergenza)"),
        r("Movimentazione manuale dei carichi", 3, 2,
          "Recupero con verricello demoltiplicato e frizione o freno automatico; treppiede trasportato "
          "chiuso e montato in due; manovella con impugnatura comoda e altezza di lavoro idonea."),
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Attrezzi calati in secchi o borse legate e non lanciati; zona attorno al chiusino libera da "
          "materiali; nessun carico sul verricello di recupero diverso dalla persona.",
          DPI_BASE + ", casco con sottogola"),
        r("Urti, colpi, impatti e compressioni", 2, 2,
          "Gambe del treppiede regolate con i perni di bloccaggio inseriti; mani lontane dal tamburo del "
          "verricello e dalla carrucola di testa; casco per chi scende e chi assiste."),
    ], scheda_uso=scheda(
        "Treppiede telescopico in alluminio con carrucola di testa e verricello o dispositivo retrattile "
        "con recupero, usato per accedere a pozzetti, camerette e serbatoi e per estrarre in emergenza "
        "l'operatore.",
        ["verificare la marcatura UNI EN 795 tipo B del treppiede e UNI EN 1496 o UNI EN 360 del dispositivo",
         "controllare cavo, moschettoni, freno e manovella e la data dell'ultima verifica periodica",
         "montare il treppiede su base stabile, bloccando piedi e gambe come da manuale",
         "misurare l'atmosfera nel pozzetto e avviare la ventilazione",
         "assegnare l'operatore esterno e verificare il funzionamento dei mezzi di comunicazione"],
        ["agganciare l'imbracatura all'attacco dorsale o sternale indicato dal fabbricante",
         "mantenere il cavo sempre in tensione durante discesa e risalita",
         "l'operatore esterno resta alla manovella per tutta la durata dell'accesso",
         "in emergenza recuperare l'infortunato con il verricello, senza scendere a soccorrerlo"],
        ["chiudere l'apertura prima di smontare il treppiede",
         "pulire e asciugare cavo e componenti e riporli nella sacca",
         "togliere dall'uso il dispositivo che abbia arrestato una caduta fino al controllo"],
        ["casco con sottogola", "imbracatura", "dispositivo retrattile", "guanti",
         "stivali di sicurezza", "autorespiratore"])),

    "Pompa pneumatica per massetti": attrezzatura(ATTREZZO, rischi=[
        r("Getti e schizzi", 3, 3,
          "Tubazioni in gomma e giunti con pressione nominale adeguata e fermi di sicurezza (UNI EN 12001); "
          "tubo terminale fissato o trattenuto e dotato di deviatore o diffusore; nessuno davanti allo "
          "sbocco; in caso di intasamento chiudere l'aria e scaricare la pressione dalla valvola del "
          "serbatoio prima di aprire i giunti.", DPI_BASE + ", occhiali a maschera"),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Colpo di frusta delle tubazioni: percorso con curve ampie, tubo ancorato ogni pochi metri e "
          "nei cambi di direzione, soprattutto lungo le verticali in facciata o nei vani scala."),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Griglia sulla bocca di carico con interblocco dell'aspo o della pala di carico; mani mai "
          "nella vasca con il mescolatore in moto; manutenzione a motore spento."),
        _silice(3, 2, "Durante lo svuotamento dei sacchi e il carico di sabbia e cemento."),
        r("Rischio chimico", 2, 2,
          "Cemento a basso tenore di cromo VI, gestito secondo la scheda di sicurezza (Titolo IX, Capo I); "
          "evitare il contatto con la pelle; acqua pulita e lavaocchi in postazione.",
          DPI_BASE + ", guanti in lattice o nitrile"),
        _rumore(3, 2, "Il compressore va posizionato all'esterno e lontano dalle postazioni."),
    ], scheda_uso=scheda(
        "Macchina a serbatoio in pressione che miscela sabbia, cemento e acqua e spinge l'impasto con aria "
        "compressa lungo una tubazione fino ai piani di posa del massetto.",
        ["verificare tubi, giunti, guarnizioni e valvola di sicurezza del serbatoio",
         "posizionare macchina e compressore su base piana, all'esterno, con i bracci di carico protetti",
         "stendere e ancorare la tubazione, fissando il tratto finale",
         "verificare la griglia della bocca di carico e il pulsante di arresto",
         "concordare i segnali tra l'addetto alla macchina e l'addetto allo sbocco"],
        ["non aprire il coperchio del serbatoio quando è in pressione",
         "tenere persone lontane dallo sbocco durante la spinta",
         "fermare la spinta e scaricare la pressione prima di intervenire su un tappo",
         "non introdurre mani o attrezzi nella vasca con il mescolatore in moto"],
        ["scaricare la pressione, svuotare e lavare serbatoio e tubazioni",
         "scaricare le acque di lavaggio in vasca di decantazione",
         "controllare l'usura dei giunti e annotare le anomalie"],
        ["casco", "occhiali a maschera", "otoprotettori", "facciale filtrante FFP2",
         "guanti in lattice o nitrile", "calzature di sicurezza"])),

    "Sollevatore per lastre (alzapannelli)": attrezzatura(ATTREZZO, rischi=[
        r("Caduta di materiale dall'alto o a livello", 2, 3,
          "Rispettare portata, dimensione massima e altezza di sollevamento indicate dal fabbricante; "
          "lastra centrata sul piano di appoggio e trattenuta dai fermi; freno o arpionismo dell'argano "
          "efficiente; lastra fissata con le prime viti prima di abbassare il sollevatore; nessuno sotto la "
          "lastra non ancora fissata."),
        r("Crollo o ribaltamento di strutture", 2, 3,
          "Sollevatore usato solo su pavimento piano e portante, con le ruote bloccate durante il "
          "sollevamento; non spostarlo con la lastra in quota; gambe del treppiede completamente aperte."),
        r("Cesoiamenti e stritolamenti", 2, 2,
          "Mani lontane dagli elementi telescopici e dalla fune durante la salita e la discesa; manovella "
          "rilasciata solo con il dispositivo di blocco inserito."),
        r("Movimentazione manuale dei carichi", 2, 2,
          "Lastre caricate sul piano inclinato in due; carrello portalastre per il trasporto in piano; "
          "riduzione delle operazioni sopra la testa grazie al sollevatore."),
    ], scheda_uso=scheda(
        "Sollevatore manuale a manovella e montante telescopico su base con ruote, con piano inclinabile, "
        "per sollevare e tenere in posizione lastre di cartongesso a soffitto o a parete durante il "
        "fissaggio.",
        ["controllare montanti, fune, argano e freno e la presenza dei fermi della lastra",
         "verificare che pavimento e percorso siano liberi, piani e portanti",
         "verificare che peso e dimensioni della lastra rientrino nei limiti indicati sulla targa"],
        ["caricare la lastra in posizione orizzontale e bloccarla con i fermi",
         "bloccare le ruote prima di sollevare e salire lentamente fino a contatto",
         "fissare la lastra con le prime viti prima di abbassare il piano",
         "non usare il sollevatore come appoggio o sostegno per persone"],
        ["abbassare completamente i montanti e chiudere il sollevatore",
         "riporlo in posizione stabile, fuori dai percorsi"],
        ["casco", "guanti", "calzature di sicurezza", "occhiali protettivi"])),

    "Sollevatore a ventose per lastre e vetri": attrezzatura(ATTREZZO, rischi=[
        r("Caduta di materiale dall'alto o a livello", 2, 4,
          "Ventose conformi alla UNI EN 13155 con indicatore del vuoto ben visibile, allarme ottico o "
          "acustico di perdita del vuoto e riserva di vuoto o pompa di emergenza; portata ridotta secondo "
          "inclinazione della lastra e numero di ventose; superficie della lastra pulita, asciutta e non "
          "porosa; nessuno sotto o sul percorso del carico.", DPI_BASE + ", casco con sottogola"),
        r("Punture, tagli e abrasioni", 3, 3,
          "Bordi di vetri e lastre ceramiche taglienti: guanti antitaglio e protezione degli avambracci; "
          "lastre con spigoli protetti; rottura del vetro prevista dalla procedura con allontanamento "
          "degli addetti.", DPI_BASE.replace("guanti", "guanti antitaglio")),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Rotazione e inclinazione del carico solo a velocità ridotta e con le leve di blocco; "
          "guida del carico con impugnature o funi; mani e piedi fuori dalla zona di appoggio."),
        r("Movimentazione manuale dei carichi", 2, 2,
          "Ventose manuali usate solo per carichi compatibili con il sollevamento a mano in due o più "
          "addetti (Allegato XXXIII); per le lastre di grande formato telai a ventose su gru o carrello."),
        _elettrocuzione(1, 3, "Per i modelli a pompa elettrica: batteria carica e controllata prima dell'uso."),
    ], scheda_uso=scheda(
        "Telaio con ventose a vuoto, manuali o a pompa elettrica, montato su gru, carrello o miniescavatore "
        "o maneggiato a mano, per movimentare e posare vetrate, serramenti e lastre di grande formato.",
        ["pulire le superfici di contatto e controllare che le guarnizioni delle ventose siano integre",
         "verificare la portata in funzione dell'inclinazione e del numero di ventose",
         "provare il vuoto e l'allarme di perdita, controllare la carica della batteria",
         "delimitare il percorso del carico e la zona di posa"],
        ["attendere che l'indicatore del vuoto sia nella zona di sicurezza prima di sollevare",
         "sollevare di pochi centimetri e verificare la tenuta prima della movimentazione",
         "non sostare sotto il carico e non trasportarlo sopra le persone",
         "appoggiare subito il carico se scatta l'allarme di perdita del vuoto"],
        ["sganciare il vuoto solo con la lastra appoggiata e assicurata",
         "pulire le ventose e riporle con le coperture protettive",
         "segnalare guarnizioni usurate o anomalie dell'impianto del vuoto"],
        ["guanti antitaglio", "casco con sottogola", "calzature di sicurezza", "occhiali protettivi"])),

    "Levigatrice per pareti con aspirazione (giraffa)": attrezzatura(ATTREZZO, rischi=[
        r("Polveri e fibre", 3, 2,
          "Polveri di stucchi e rasanti, con possibile presenza di silice e carbonati: levigatrice "
          "collegata ad aspiratore di classe M o H (CEI EN 60335-2-69) con tubo integro; pulizia del filtro "
          "secondo il fabbricante; ambiente ventilato; pulizia finale ad aspirazione.",
          "Casco, calzature di sicurezza, guanti, facciale filtrante FFP2, occhiali a maschera"),
        r("Posture incongrue", 3, 2,
          "Asta regolata alla lunghezza minima utile; lavoro a soffitto alternato con lavoro a parete e "
          "pause frequenti; uso di trabattello o ponte su cavalletti per le parti alte invece di "
          "sporgersi."),
        _vibrazioni_hav(2, 2),
        r("Urti, colpi, impatti e compressioni", 2, 2,
          "Disco fermo prima di appoggiare l'attrezzo; asta tenuta con due mani; protezione del disco "
          "integra e mani lontane dal piatto rotante.",
          "Casco, calzature di sicurezza, guanti"),
        _elettrocuzione(1, 4, "Utensile conforme alla CEI EN 62841."),
    ], scheda_uso=scheda(
        "Levigatrice elettrica a disco montata su asta telescopica e collegata a un aspiratore, per "
        "carteggiare rasature e stuccature su pareti e soffitti senza ponteggi bassi.",
        ["verificare integrità di asta, testa snodata, cavo e tubo di aspirazione",
         "collegare l'aspiratore e controllare filtro e indicatore di flusso",
         "montare il disco abrasivo adatto e verificarne il fissaggio",
         "proteggere arredi e impianti e ventilare l'ambiente"],
        ["avviare prima l'aspiratore, poi la levigatrice",
         "tenere l'asta con entrambe le mani e non premere eccessivamente",
         "alternare lavoro a soffitto e a parete e fare pause",
         "fermare l'utensile se l'aspirazione si riduce"],
        ["staccare la spina prima di cambiare l'abrasivo",
         "svuotare l'aspiratore con il sacco chiuso, evitando di sollevare polvere",
         "pulire l'ambiente con l'aspiratore"],
        ["facciale filtrante FFP2", "occhiali a maschera", "guanti", "calzature di sicurezza"])),

    "Impianto di abbassamento della falda (wellpoint)": attrezzatura(ATTREZZO, rischi=[
        r("Seppellimento e sprofondamento", 2, 4,
          "Impianto dimensionato da un tecnico in base a permeabilità e profondità; funzionamento "
          "continuo garantito da pompa di riserva o gruppo elettrogeno di emergenza; controllo dei "
          "livelli con piezometri e del vuoto con vacuometri; in caso di arresto dell'impianto uscita "
          "immediata dallo scavo; monitoraggio dei cedimenti di edifici e reti vicine."),
        _tubi_pressione(2, 3, "circuito di infissione e del collettore",
                        "Durante l'infissione degli aghi con lancia ad acqua tenere la lancia con due mani "
                        "e mai rivolta verso le persone."),
        _rumore(3, 2, "Funzionamento continuo anche di notte: pompe insonorizzate o carenate e lontane "
                      "da abitazioni e postazioni."),
        _elettrocuzione(2, 4, "Quadro della pompa con grado di protezione adeguato all'esterno, "
                              "collegamento a terra e cavi protetti dal passaggio dei mezzi."),
        r("Scivolamenti e cadute a livello", 3, 2,
          "Collettori e tubi flessibili disposti lungo il ciglio dello scavo, fuori dai percorsi o "
          "protetti con passerelle; area attorno alle pompe drenata.",
          DPI_BASE.replace("calzature di sicurezza", "stivali di sicurezza")),
        r("Incendio ed esplosione", 1, 3,
          "Per le pompe con motore diesel: rifornimento a motore spento e freddo, estintore in "
          "postazione, serbatoi con bacino di contenimento; gas di scarico lontani da scavi e locali chiusi."),
        r("Movimentazione manuale dei carichi", 3, 2,
          "Aghi e collettori movimentati in due o con mezzo di sollevamento; tratti di collettore di "
          "lunghezza e peso contenuti."),
    ], scheda_uso=scheda(
        "Impianto di drenaggio formato da aghi filtranti infissi nel terreno, collettore e pompa "
        "aspirante a vuoto, che abbassa la falda per eseguire scavi all'asciutto.",
        ["acquisire il progetto dell'impianto e le indicazioni di monitoraggio della falda",
         "posizionare pompe e quadro su base stabile, lontano dal ciglio dello scavo",
         "verificare tubi, raccordi, valvole, vacuometro e collegamenti elettrici",
         "predisporre la pompa o la fonte di energia di riserva",
         "delimitare la zona di infissione degli aghi"],
        ["infiggere gli aghi con la lancia ad acqua tenendo le persone a distanza",
         "controllare più volte al giorno vuoto, portata e livelli piezometrici",
         "far uscire tutti dallo scavo in caso di arresto o di risalita della falda",
         "scaricare le acque nel recapito autorizzato, senza erosioni"],
        ["spegnere la pompa solo quando lo scavo è richiuso o messo in sicurezza",
         "estrarre gli aghi e chiudere i fori",
         "pulire e controllare pompa e collettori prima del deposito"],
        ["casco", "stivali di sicurezza", "guanti", "otoprotettori", "indumenti impermeabili",
         "indumenti ad alta visibilità"])),

    "Martinetto idraulico per tesatura": attrezzatura(ATTREZZO, rischi=[
        r("Proiezione di schegge e frammenti", 2, 4,
          "Rilascio improvviso di trefoli, cunei o barre in caso di rottura: zona sul prolungamento "
          "dell'asse del tirante, dietro e davanti al martinetto, interdetta durante la tesatura; schermo "
          "di protezione dietro al martinetto; operatore alla centralina in posizione laterale; cunei e "
          "piastre di ancoraggio idonei e puliti (UNI EN 1537).", DPI_BASE + ", visiera protettiva"),
        _tubi_pressione(2, 4, "circuito oleodinamico",
                        "Tubi oleodinamici ad alta pressione (centinaia di bar) senza pieghe, protetti da "
                        "urti, con valvola di massima tarata; mai individuare perdite con le mani: "
                        "l'olio in pressione può iniettarsi sotto la pelle."),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Martinetto sostenuto da mezzo di sollevamento o supporto durante l'inserimento sui trefoli; "
          "mani lontane da pistone e piastre in movimento; corsa massima indicata dal fabbricante."),
        r("Movimentazione manuale dei carichi", 3, 2,
          "Martinetti pesanti movimentati con paranco, gru o carrello; sollevamento manuale solo in due "
          "per pesi compatibili con l'Allegato XXXIII."),
        r("Caduta dall'alto", 2, 4,
          "Tesatura su paratie e fronti di scavo da piattaforma o ponteggio con parapetti, o da PLE con "
          "imbracatura; nessun appoggio precario su terreno o strutture.",
          DPI_BASE + ", imbracatura, cordino con assorbitore"),
    ], scheda_uso=scheda(
        "Martinetto oleodinamico a pistone cavo, alimentato da centralina con manometro tarato, che tende "
        "trefoli o barre dei tiranti di ancoraggio fino al carico di progetto e ne esegue il collaudo.",
        ["verificare il certificato di taratura di martinetto e manometro",
         "controllare tubi, raccordi rapidi, valvola di massima e livello dell'olio della centralina",
         "pulire testata, piastra e cunei e verificarne l'integrità",
         "delimitare la zona di rispetto sull'asse del tirante e montare lo schermo di protezione",
         "concordare con il direttore dei lavori il programma di carico"],
        ["mettere in carico per gradini secondo il programma e registrare letture e allungamenti",
         "stare in posizione laterale, mai sull'asse del tirante",
         "interrompere la tesatura se il manometro o gli allungamenti mostrano valori anomali",
         "non avvicinarsi al martinetto in pressione e non scollegare i tubi sotto carico"],
        ["scaricare la pressione prima di sfilare il martinetto e scollegare i tubi",
         "proteggere le teste dei tiranti con cappellotti",
         "pulire il martinetto e riporre i tubi arrotolati e tappati"],
        ["casco", "visiera protettiva", "guanti", "calzature di sicurezza", "indumenti ad alta visibilità"])),

    # ===================================== MACCHINE ======================================
    "Spanditrice di emulsione bituminosa": attrezzatura(MACCHINA, rischi=[
        r("Ustioni", 2, 3,
          "Emulsione spruzzata a temperatura fino a 60-80 °C e bitumi modificati anche più caldi: cisterna "
          "coibentata con termometro e valvole di sicurezza; bruciatori o riscaldatori accesi solo da "
          "personale addestrato, mai durante il trasferimento; nessuno vicino a barra e lancia durante "
          "lo spruzzo; ugelli disostruiti a impianto fermo e depressurizzato.",
          "Casco, calzature di sicurezza, guanti, indumenti ad alta visibilità in classe 3, "
          "indumenti protettivi, occhiali protettivi"),
        r("Getti e schizzi", 3, 2,
          "Barra con protezioni laterali e altezza regolata; lancia manuale rivolta sempre verso la "
          "superficie; vento e mezzi in transito considerati prima dello spruzzo (UNI EN 13020).",
          DPI_BASE + ", occhiali a maschera"),
        r("Rischio chimico", 2, 2,
          "Emulsioni cationiche con additivi irritanti e fumi di bitume: scheda di sicurezza consultata "
          "(Titolo IX, Capo I); postazione sopravvento; lavaggio della pelle senza solventi.",
          DPI_BASE + ", guanti in lattice o nitrile"),
        _investimento(2, 4, "In presenza di traffico: segnaletica secondo il D.M. 10 luglio 2002 e "
                            "addetti formati secondo il D.M. 22 gennaio 2019."),
        r("Incendio ed esplosione", 1, 4,
          "Riscaldatori a gas o gasolio con valvole e tubazioni integre; estintore a bordo; nessuna "
          "fiamma libera vicino alla cisterna aperta; flussaggio con solventi vietato vicino a fonti di "
          "calore."),
        r("Scivolamenti e cadute a livello", 3, 2,
          "Mano d'attacco fresca molto scivolosa: percorsi pedonali fuori dalla striscia spruzzata; "
          "pedane e scalette della macchina pulite e dotate di corrimano."),
    ], scheda_uso=scheda(
        "Autocarro con cisterna coibentata, pompa e barra di spruzzatura posteriore, con lancia manuale, "
        "che distribuisce l'emulsione bituminosa per la mano d'attacco prima della stesa dei conglomerati.",
        ["verificare valvole, termometro, tubazioni, barra e ugelli e il dispositivo di riscaldamento",
         "controllare luci, segnalatori acustici e girofaro del mezzo",
         "posare la segnaletica di cantiere stradale prima dell'inizio",
         "allontanare veicoli e persone dalla zona di spruzzo"],
        ["procedere a velocità costante e ridotta, con un addetto a terra che segnala ostacoli",
         "non sostare dietro la barra durante lo spruzzo",
         "usare la lancia solo per i ritocchi, rivolta verso la superficie",
         "spegnere il riscaldamento durante i trasferimenti"],
        ["chiudere le valvole e pulire barra e ugelli secondo il fabbricante",
         "raccogliere eventuali sversamenti con materiale assorbente",
         "segnalare perdite o anomalie dell'impianto"],
        ["indumenti ad alta visibilità", "indumenti protettivi", "guanti", "occhiali protettivi",
         "calzature di sicurezza"])),

    "Macchina per minitrincea (fresa a disco)": attrezzatura(MACCHINA, rischi=[
        _silice(3, 3, "La macchina va usata con aspirazione dei detriti o raffreddamento ad acqua."),
        r("Proiezione di schegge e frammenti", 2, 3,
          "Carter del disco chiuso fino alla superficie; nessuno davanti o di lato al disco; disco "
          "diamantato idoneo al conglomerato e senza segmenti danneggiati.",
          DPI_BASE + ", visiera protettiva"),
        _rumore(4, 2),
        _investimento(2, 4, "Lavoro in sede stradale con segnaletica secondo il D.M. 10 luglio 2002 e "
                            "personale formato secondo il D.M. 22 gennaio 2019."),
        r("Elettrocuzione", 2, 4,
          "Prima del taglio individuare i sottoservizi con le cartografie dei gestori e con georadar o "
          "cercaservizi (D.M. 1 ottobre 2013); profondità del taglio regolata e controllata; arresto "
          "immediato al contatto con cavi o tubazioni.",
          DPI_BASE),
        _vibrazioni_hav(2, 2, "Per i modelli con conducente a bordo valutare anche le vibrazioni al corpo intero."),
    ], scheda_uso=scheda(
        "Macchina semovente con disco diamantato e sistema di aspirazione dei detriti che apre nella "
        "pavimentazione stradale trincee strette e profonde per la posa di cavi e microtubi.",
        ["acquisire le planimetrie dei sottoservizi e tracciare il percorso con il cercaservizi",
         "verificare disco, carter, aspirazione o impianto ad acqua e comandi di arresto",
         "posare la segnaletica di cantiere stradale e delimitare la zona di lavoro"],
        ["regolare profondità e velocità di avanzamento secondo il fabbricante",
         "tenere le persone lontane dal disco e dal tubo di scarico dei detriti",
         "arrestare la macchina se il disco incontra elementi metallici o cavi",
         "controllare continuamente il funzionamento dell'aspirazione"],
        ["sollevare il disco e arrestare il motore prima di scendere",
         "pulire macchina e strada dai detriti con aspirazione",
         "chiudere la trincea o proteggerla prima di riaprire al traffico"],
        ["otoprotettori", "facciale filtrante FFP3", "visiera protettiva", "indumenti ad alta visibilità",
         "guanti", "calzature di sicurezza"])),

    "Idrodemolitrice (robot ad acqua ad alta pressione)": attrezzatura(MACCHINA, rischi=[
        r("Getti e schizzi", 2, 4,
          "Getto a oltre 1000 bar capace di penetrare tessuti e indumenti: macchina conforme alla "
          "UNI EN 1829-1; robot comandato a distanza con arresto d'emergenza e funzione di uomo presente; "
          "zona di rispetto di almeno 10 m (o quella del fabbricante) delimitata e interdetta, anche ai "
          "piani sottostanti per le solette passanti; schermi in gomma o lamiera attorno alla lancia; "
          "persona addetta all'arresto della pompa in contatto con l'operatore.",
          DPI_BASE + ", visiera protettiva, indumenti impermeabili"),
        r("Proiezione di schegge e frammenti", 3, 3,
          "Detriti di calcestruzzo proiettati anche a distanza: schermatura della zona di lavoro, "
          "protezione di vetri, impianti e percorsi; aperture verso l'esterno chiuse con teli o pannelli.",
          DPI_BASE + ", visiera protettiva"),
        _tubi_pressione(2, 4, "circuito ad altissima pressione",
                        "Collegamenti eseguiti solo a pompa ferma; tubi non trascinati su spigoli e "
                        "detriti; sostituzione secondo le scadenze del fabbricante."),
        _rumore(4, 3, "Livelli molto elevati (anche oltre 110 dB(A)): doppia protezione con inserti e "
                      "cuffie, gruppo pompa insonorizzato e lontano dalle postazioni."),
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Profondità di asportazione stabilita dal progetto di ripristino; verifica della stabilità "
          "della struttura e puntellamenti preventivi; robot posizionato su superficie portante e "
          "con stabilizzatori aperti."),
        r("Scivolamenti e cadute a livello", 3, 2,
          "Acque e fanghi alcalini raccolti, decantati e trattati prima dello scarico; percorsi "
          "liberi e drenati.", DPI_BASE.replace("calzature di sicurezza", "stivali di sicurezza")),
    ], scheda_uso=scheda(
        "Robot cingolato radiocomandato con lancia oscillante alimentata da una pompa ad altissima "
        "pressione, che asporta in modo selettivo il calcestruzzo degradato senza danneggiare le "
        "armature.",
        ["verificare con il tecnico la stabilità della struttura e la profondità di asportazione",
         "delimitare la zona di rispetto e i piani sottostanti, chiudere aperture e vetri",
         "controllare tubi, raccordi, ugello, schermi e arresto d'emergenza",
         "predisporre la raccolta e la decantazione delle acque di lavorazione",
         "provare il radiocomando e il collegamento con l'addetto alla pompa"],
        ["comandare il robot da fuori della zona di rispetto e in vista della lancia",
         "fermare la pompa prima di avvicinarsi alla macchina",
         "non indirizzare mai il getto verso persone o parti del corpo",
         "sospendere il lavoro se qualcuno entra nella zona interdetta"],
        ["arrestare la pompa e scaricare la pressione prima di scollegare i tubi",
         "rimuovere detriti e fanghi e trattare le acque prima dello scarico",
         "pulire e controllare ugelli, tubi e schermi"],
        ["casco", "visiera protettiva", "otoprotettori", "cuffie antirumore", "indumenti impermeabili",
         "stivali di sicurezza", "guanti"])),

    "Macchina insufflatrice per isolanti sfusi": attrezzatura(MACCHINA, rischi=[
        r("Polveri e fibre", 3, 2,
          "Fibre di cellulosa, lane minerali e granuli: materiali scelti con scheda di sicurezza "
          "consultata (lane minerali non classificate cancerogene secondo la nota Q o R); caricamento "
          "dei sacchi in modo lento; macchina posta fuori dal locale da isolare; foro di insufflaggio "
          "sigillato attorno al tubo e locale ventilato.",
          "Casco, calzature di sicurezza, guanti, facciale filtrante FFP2, occhiali a maschera, "
          "tuta monouso"),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Tramoggia con griglia e interblocco che arresta sfibratore e coclea all'apertura; mai mani o "
          "attrezzi nella tramoggia con la macchina in moto; disintasamento a macchina spenta e staccata."),
        r("Getti e schizzi", 2, 2,
          "Tubo collegato e fissato prima dell'avvio; bocchetta non rivolta verso le persone; "
          "arresto della soffiante prima di scollegare il tubo.", DPI_BASE + ", occhiali a maschera"),
        _elettrocuzione(),
        _rumore(3, 2),
        r("Caduta dall'alto", 2, 4,
          "Insufflaggio di sottotetti e intercapedini da postazioni stabili: passerelle sui solai non "
          "praticabili, parapetti o imbracatura agganciata a punto sicuro.",
          DPI_BASE + ", imbracatura, cordino con assorbitore"),
    ], scheda_uso=scheda(
        "Macchina con tramoggia, sfibratore e soffiante che disgrega gli isolanti sfusi e li spinge con "
        "aria attraverso un tubo nelle intercapedini, nei sottotetti e nei solai.",
        ["consultare la scheda di sicurezza dell'isolante",
         "verificare griglia, interblocco, tubo, cavo e comando a distanza",
         "posizionare la macchina all'esterno o in locale ventilato",
         "predisporre postazioni sicure per l'addetto alla bocchetta"],
        ["svuotare i sacchi lentamente nella tramoggia, senza comprimerli",
         "non introdurre mani o attrezzi nella tramoggia",
         "mantenere il contatto con l'addetto alla bocchetta e arrestare la macchina a fine carica",
         "sigillare il foro di insufflaggio per limitare la dispersione delle fibre"],
        ["spegnere e staccare la macchina prima della pulizia",
         "aspirare i residui con aspiratore a filtro",
         "togliere la tuta monouso e smaltirla prima di lasciare la zona di lavoro"],
        ["facciale filtrante FFP2", "occhiali a maschera", "tuta monouso", "guanti", "otoprotettori",
         "calzature di sicurezza"])),

    "Penetrometro statico e dinamico": attrezzatura(MACCHINA, rischi=[
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Macchina posizionata su terreno piano e portante, con stabilizzatori o ancoraggi a elica "
          "dimensionati per la spinta; verifica della pendenza massima indicata dal fabbricante; "
          "torre abbassata durante gli spostamenti (UNI EN 16228-1/-2)."),
        r("Urti, colpi, impatti e compressioni", 2, 4,
          "Prova dinamica: maglio a caduta libera dentro guida protetta, comando dalla postazione "
          "laterale; nessuno nella zona della torre durante la battitura; aste aggiunte o tolte solo a "
          "maglio fermo e bloccato."),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Morse e testa di spinta idraulica protette; comandi ad azione mantenuta e arresto "
          "d'emergenza; mani lontane da morse e aste in movimento durante la spinta CPT."),
        r("Elettrocuzione", 1, 4,
          "Verifica dei sottoservizi prima di infiggere le aste; distanza dalle linee elettriche aeree "
          "secondo l'Allegato IX (almeno 3 m fino a 1 kV, di più per tensioni maggiori) con torre alzata."),
        _rumore(3, 2, "Il rumore è rilevante soprattutto nella prova dinamica (DPSH)."),
        r("Movimentazione manuale dei carichi", 3, 2,
          "Aste e attrezzi di estrazione movimentati con argano o pinza della macchina; carico manuale "
          "ripetuto ridotto con rastrelliere vicine alla postazione."),
    ], scheda_uso=scheda(
        "Macchina cingolata o autocarrata che esegue prove penetrometriche: statiche (CPT/CPTU) con spinta "
        "idraulica e ancoraggi, o dinamiche (DPSH) con maglio a caduta libera (UNI EN ISO 22476-1/-2).",
        ["verificare l'assenza di sottoservizi e linee aeree nel punto di prova",
         "posizionare la macchina in piano, stabilizzata o ancorata",
         "controllare tubi oleodinamici, morse, maglio e arresto d'emergenza",
         "delimitare la zona di lavoro attorno alla torre"],
        ["comandare la prova dalla postazione prevista, fuori dalla zona del maglio",
         "inserire o togliere le aste solo a macchina ferma",
         "interrompere la spinta se la macchina tende a sollevarsi o inclinarsi",
         "tenere le persone estranee fuori dall'area delimitata"],
        ["abbassare la torre e chiudere gli stabilizzatori prima di spostarsi",
         "estrarre le aste e chiudere il foro di prova",
         "pulire e controllare aste, punta e morse"],
        ["casco", "otoprotettori", "guanti", "calzature di sicurezza", "indumenti ad alta visibilità"])),

    "Attrezzatura per scavo di diaframmi (benna mordente o idrofresa)": attrezzatura(MACCHINA, rischi=[
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Macchina base conforme alla UNI EN 16228-1/-5, su piano di lavoro livellato e portante con "
          "eventuale materasso di ghiaia; rispetto del diagramma dei carichi; muretti guida eseguiti "
          "prima dello scavo; distanza da scavi e cigli secondo il fabbricante."),
        r("Caduta di materiale dall'alto o a livello", 2, 4,
          "Benna o fresa sospesa: nessuno sotto o vicino all'utensile in movimento; funi e attacchi "
          "verificati (Allegati VI e VII); distanza di sicurezza durante lo scarico dello smarino; gabbie "
          "d'armatura sollevate con bilancini.", DPI_BASE + ", casco con sottogola"),
        r("Annegamento", 2, 4,
          "Pannello aperto pieno di fango: muretti guida sporgenti dal piano di lavoro, chiusura con "
          "grigliati o parapetti a fine turno, giubbotti e salvagenti disponibili presso lo scavo.",
          DPI_BASE + ", giubbotto di salvataggio"),
        _investimento(2, 4, "Raggio di rotazione della torretta delimitato; movimenti di autocarri e "
                            "betoniere regolati da un moviere."),
        _rumore(3, 2),
        r("Elettrocuzione", 1, 4,
          "Distanze dalle linee elettriche aeree secondo l'Allegato IX con braccio alzato; sottoservizi "
          "individuati e deviati prima dello scavo dei muretti guida."),
    ], scheda_uso=scheda(
        "Macchina base cingolata con benna mordente a funi o idraulica, o con idrofresa a tamburi rotanti, "
        "che scava pannelli di diaframma in presenza di fango bentonitico o polimerico.",
        ["verificare la portanza del piano di lavoro e l'esecuzione dei muretti guida",
         "controllare funi, attacchi, tubi oleodinamici e strumenti di verticalità",
         "delimitare il raggio di azione della macchina e le vie dei mezzi",
         "verificare distanze da linee aeree e sottoservizi"],
        ["mantenere il livello del fango nel pannello secondo progetto",
         "non sostare sotto o vicino alla benna in manovra",
         "chiudere o proteggere il pannello aperto durante le pause",
         "comunicare con radio o gesti convenzionali con gli addetti a terra"],
        ["appoggiare l'utensile a terra e arrestare la macchina",
         "proteggere i pannelli aperti con grigliati e segnaletica",
         "pulire e controllare funi e utensili"],
        ["casco con sottogola", "otoprotettori", "stivali di sicurezza", "guanti",
         "indumenti ad alta visibilità", "indumenti impermeabili"])),

    "Impianto di confezionamento e dissabbiatura dei fanghi": attrezzatura(MACCHINA, rischi=[
        r("Polveri e fibre", 3, 2,
          "Bentonite e polimeri in polvere: carico da silo con filtro o con caricatore chiuso; sacchi "
          "svuotati lentamente; postazione all'aperto e sopravvento.",
          DPI_BASE + ", facciale filtrante FFP2, occhiali a maschera"),
        r("Rischio chimico", 2, 2,
          "Fanghi alcalini e polimeri: schede di sicurezza consultate (Titolo IX, Capo I); evitare il "
          "contatto con pelle e occhi; lavaocchi e acqua pulita in postazione.",
          DPI_BASE + ", guanti in lattice o nitrile, occhiali a maschera"),
        r("Annegamento", 2, 4,
          "Vasche di stoccaggio e maturazione con parapetti normali su tutti i lati accessibili; "
          "passerelle con parapetti per le ispezioni; salvagente con cima presso le vasche.",
          DPI_BASE + ", giubbotto di salvataggio"),
        _tubi_pressione(2, 3, "circuito dei fanghi"),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Vagli vibranti, pompe e agitatori con organi in moto protetti (Allegato V); manutenzione "
          "e disintasamento solo a impianto fermo e sezionato con lucchetto."),
        _rumore(3, 2, "Vagli e pompe sono le sorgenti principali."),
        _elettrocuzione(2, 4, "Quadri con grado di protezione adeguato al getto d'acqua e collegamento a terra."),
    ], scheda_uso=scheda(
        "Impianto con silo, miscelatore, vasche, pompe e dissabbiatore a vagli vibranti e idrocicloni, che "
        "prepara il fango bentonitico o polimerico e lo ricicla separando sabbia e detriti.",
        ["verificare parapetti di vasche e passerelle e la presenza dei salvagenti",
         "controllare tubi, raccordi, protezioni dei vagli e arresti d'emergenza",
         "consultare le schede di sicurezza di bentonite e additivi",
         "verificare collegamenti elettrici e messa a terra dell'impianto"],
        ["caricare la bentonite evitando la dispersione di polvere",
         "non salire sulle vasche al di fuori delle passerelle protette",
         "intervenire su vagli e pompe solo a impianto fermo e sezionato",
         "controllare densità e livello dei fanghi secondo il programma"],
        ["svuotare e lavare le linee secondo il fabbricante",
         "gestire fanghi esausti e sabbie come rifiuti o sottoprodotti secondo le norme ambientali",
         "annotare anomalie e manutenzioni"],
        ["casco", "stivali di sicurezza", "guanti in lattice o nitrile", "occhiali a maschera",
         "facciale filtrante FFP2", "indumenti impermeabili", "otoprotettori"])),

    # =============================== RICHIESTE SUCCESSIVE ================================
    "Canale di scarico delle macerie": attrezzatura(OPERA, rischi=[
        r("Caduta dall'alto", 2, 4,
          "Imboccatura superiore costruita in modo che nessuno possa cadervi accidentalmente (art. 153, "
          "comma 3): tramoggia di carico con parapetto o sponde alte e apertura ridotta; caricamento dal "
          "piano protetto, senza sporgersi; aperture di solaio o di facciata chiuse attorno all'imbocco.",
          DPI_BASE + ", casco con sottogola"),
        r("Caduta di materiale dall'alto o a livello", 3, 3,
          "Macerie mai gettate dall'alto ma convogliate nel canale (art. 153, comma 1), con estremo inferiore "
          "a non più di 2 m dal piano di raccolta; zona di sbocco recintata e segnalata; accesso allo sbocco "
          "per il carico solo dopo la sospensione dello scarico dall'alto (art. 154); pezzi pesanti o "
          "ingombranti calati con mezzi di sollevamento (art. 153, comma 4).",
          DPI_BASE + ", casco con sottogola"),
        r("Crollo o ribaltamento di strutture", 2, 4,
          "Tronchi imboccati l'uno nell'altro e collegati con catene o funi di sostegno, con i raccordi "
          "rinforzati (art. 153, comma 2); ancoraggio al ponteggio o all'edificio come da istruzioni del "
          "fabbricante e, se appeso al ponteggio, carico considerato nel progetto o nello schema del "
          "ponteggio; controllo dei sostegni a inizio turno."),
        r("Polveri e fibre", 3, 2,
          "Macerie bagnate prima dello scarico; sbocco in cassone coperto con telo o in contenitore chiuso; "
          "canale integro senza fessure; nessuno scarico di materiali contenenti amianto.",
          DPI_BASE + ", facciale filtrante FFP2"),
        r("Rumore", 2, 2,
          "Tronchi in polietilene o con rivestimento interno smorzante; caricamento a piccole quantità; "
          "otoprotettori per chi lavora allo sbocco durante lo scarico.", DPI_BASE + ", otoprotettori"),
        r("Movimentazione manuale dei carichi", 3, 2,
          "Carriole e contenitori portati fino alla tramoggia su percorsi piani; tronchi montati in due o "
          "con argano; peso dei tronchi riportato dal fabbricante (Allegato XXXIII)."),
    ], scheda_uso=scheda(
        "Condotto verticale formato da tronchi tronco-conici in plastica o metallo imboccati l'uno "
        "nell'altro, con tramoggia di carico ai piani, che convoglia le macerie di demolizione fino a un "
        "cassone o a un'area di raccolta.",
        ["verificare con il fabbricante il sistema di sostegno e i punti di ancoraggio",
         "montare i tronchi collegandoli con le catene e controllare i raccordi",
         "posizionare l'estremo inferiore a non più di 2 m dal piano di raccolta, sopra il cassone",
         "proteggere l'imboccatura con tramoggia e parapetto",
         "recintare e segnalare la zona di sbocco"],
        ["caricare piccole quantità alla volta, senza pezzi più grandi della sezione del canale",
         "bagnare le macerie per limitare la polvere",
         "sospendere lo scarico prima di accedere allo sbocco per caricare o spostare il cassone",
         "in caso di intasamento fermare il carico e liberare il canale dall'alto, mai da sotto"],
        ["svuotare il canale e smontarlo dall'alto verso il basso",
         "pulire e controllare tronchi, catene e ganci prima del deposito",
         "rimuovere la recinzione solo a canale smontato"],
        ["casco con sottogola", "facciale filtrante FFP2", "otoprotettori", "guanti",
         "calzature di sicurezza"])),

    "Estrattore d'aria con filtro assoluto HEPA (depressore)": attrezzatura(ATTREZZO, rischi=[
        r("Esposizione ad amianto", 2, 4,
          "Confinamento dinamico secondo il D.M. 6 settembre 1994: estrattori con filtro assoluto HEPA in funzione "
          "continua per tutta la bonifica, con capacità di almeno 4 ricambi d'aria all'ora del volume "
          "confinato; depressione controllata con manometro differenziale e registrata; collaudo "
          "dell'area con fumogeni prima dell'inizio; macchina di riserva o alimentazione di emergenza; "
          "sostituzione dei prefiltri e del filtro HEPA solo dall'interno dell'area o in condizioni di "
          "confinamento, con filtri insaccati e smaltiti come rifiuto contenente amianto.",
          "Maschera con filtro specifico, tuta monouso, guanti, calzature di sicurezza"),
        _elettrocuzione(1, 4, "Alimentazione su linea dedicata, con cavi che attraversano il confinamento "
                              "senza comprometterne la tenuta."),
        _rumore(3, 2, "Estrattori in funzione continua: posizionarli dove non disturbano le postazioni "
                      "e silenziare lo scarico."),
        r("Movimentazione manuale dei carichi", 2, 2,
          "Macchina su ruote; condotti e filtri movimentati in due nei tratti in quota; posizionamento con "
          "carrello o mezzo di sollevamento."),
        r("Ambienti confinati o sospetti di inquinamento", 1, 3,
          "Scarico dell'aria filtrata all'esterno, lontano da prese d'aria, finestre e persone; mai verso "
          "spazi chiusi occupati."),
    ], scheda_uso=scheda(
        "Unità di estrazione con ventilatore, prefiltri e filtro assoluto HEPA che mantiene in depressione "
        "l'area confinata di bonifica dell'amianto friabile e filtra l'aria espulsa all'esterno.",
        ["verificare il certificato del filtro HEPA e il corretto montaggio delle guarnizioni",
         "calcolare il numero di estrattori necessario per il volume dell'area confinata",
         "installare il manometro differenziale con le sonde all'interno e all'esterno dell'area",
         "collaudare il confinamento con fumogeni e prova di depressione",
         "predisporre l'estrattore di riserva o la fonte di energia di emergenza"],
        ["tenere gli estrattori in funzione continua, anche fuori dall'orario di lavoro",
         "controllare e registrare più volte al giorno la depressione",
         "sospendere la rimozione se la depressione cala o scatta l'allarme",
         "sostituire i prefiltri quando aumenta la perdita di carico"],
        ["mantenere gli estrattori accesi fino alla restituibilità dell'area",
         "rimuovere i filtri in condizioni di confinamento e insaccarli come rifiuto contenente amianto",
         "decontaminare la macchina e sigillarne le aperture prima di trasportarla"],
        ["maschera con filtro specifico", "tuta monouso", "guanti", "calzature di sicurezza",
         "otoprotettori"])),

    "Nebulizzatore a bassa pressione": attrezzatura(ATTREZZO, rischi=[
        r("Esposizione ad amianto", 2, 4,
          "Bagnatura e impregnazione dei materiali con acqua o incapsulante a bassa pressione, come previsto "
          "dal D.M. 6 settembre 1994 che esclude getti in pressione su materiali contenenti amianto; ugello "
          "regolato a nebbia e avvicinato senza colpire il materiale; impregnazione completata prima "
          "della rimozione.",
          "Maschera con filtro specifico, tuta monouso, guanti, calzature di sicurezza"),
        r("Rischio chimico", 2, 2,
          "Incapsulanti e fissativi usati secondo la scheda di sicurezza (Titolo IX, Capo I); prodotti a "
          "base acqua preferiti; ventilazione o confinamento attivo; nessuna nebulizzazione verso il viso.",
          DPI_BASE + ", guanti in lattice o nitrile, occhiali a maschera"),
        r("Getti e schizzi", 2, 2,
          "Pressione regolata sul valore minimo efficace; lancia chiusa e pressione scaricata prima di "
          "cambiare ugelli o tubi; tubi integri e raccordi serrati.",
          DPI_BASE + ", occhiali a maschera"),
        r("Scivolamenti e cadute a livello", 3, 2,
          "Quantità di liquido dosata per non formare ristagni; teli del confinamento puliti; calzature "
          "con suola antiscivolo.",
          DPI_BASE.replace("calzature di sicurezza", "stivali di sicurezza")),
        _elettrocuzione(1, 4, "Pompa elettrica lontana dalle zone bagnate o alimentata a bassissima tensione."),
    ], scheda_uso=scheda(
        "Pompa manuale, elettrica o airless regolata a bassa pressione, con lancia e ugello a nebbia, per "
        "bagnare e impregnare con acqua o incapsulante i materiali contenenti amianto prima e durante la "
        "rimozione.",
        ["consultare la scheda di sicurezza dell'incapsulante e preparare la miscela secondo il fabbricante",
         "verificare tubi, raccordi, ugello e regolatore di pressione",
         "regolare la pressione al valore minimo e provare il getto a nebbia fuori dal materiale"],
        ["nebulizzare senza colpire direttamente il materiale e senza staccarne parti",
         "attendere l'impregnazione completa prima di iniziare la rimozione",
         "mantenere bagnati i materiali e i rifiuti per tutta la lavorazione",
         "non usare mai acqua in pressione per pulire o staccare i materiali"],
        ["scaricare la pressione e lavare la pompa all'interno dell'area di lavoro",
         "decontaminare il nebulizzatore prima di portarlo fuori dall'area",
         "smaltire residui e acque come previsto dal piano di lavoro"],
        ["maschera con filtro specifico", "tuta monouso", "guanti in lattice o nitrile",
         "occhiali a maschera", "stivali di sicurezza"])),

    "Rilevatore di masse metalliche (magnetometro)": attrezzatura(ATTREZZO, rischi=[
        r("Incendio ed esplosione", 1, 4,
          "Lo strumento è usato solo da personale brevettato di impresa iscritta all'albo per la bonifica "
          "bellica (art. 104, comma 4-bis; D.M. 82/2015), secondo le prescrizioni dell'autorità militare; "
          "taratura e prova su massa campione all'inizio di ogni giornata; ricerca per strisce delimitate; "
          "anomalie segnalate con picchetti e scoperte a mano; nessuna sonda spinta in foro oltre lo "
          "strato già verificato."),
        r("Posture incongrue", 3, 2,
          "Strumento con asta e bracciolo regolabili e cinghia a tracolla per il peso dell'elettronica; "
          "alternanza tra ricerca e altre attività; pause regolari."),
        r("Microclima", 3, 2,
          "Lavoro prolungato all'aperto: pause all'ombra, acqua, indumenti adatti alla stagione; "
          "sospensione in caso di temporale con fulmini, anche per lo strumento metallico tenuto in mano.",
          DPI_BASE + ", copricapo"),
        r("Scivolamenti e cadute a livello", 2, 2,
          "Strisce di ricerca liberate dalla vegetazione; attenzione allo strumento e al terreno insieme; "
          "calzature prive di parti metalliche che non disturbino la lettura, con suola profonda.",
          DPI_BASE.replace("calzature di sicurezza", "stivali di sicurezza")),
        r("Rischio biologico", 2, 2,
          "Indumenti chiusi a maniche lunghe, repellenti contro zecche e insetti, controllo della pelle a "
          "fine turno; vaccinazione antitetanica.", DPI_BASE),
    ], scheda_uso=scheda(
        "Magnetometro o gradiometro portatile, con sonda di superficie o sonda da calare nei fori, che "
        "rileva le masse ferrose sepolte nella ricerca di ordigni bellici in superficie e in profondità.",
        ["verificare carica delle batterie, integrità di sonde e cavi",
         "tarare lo strumento e provarlo su una massa campione",
         "togliere oggetti metallici dagli indumenti che possano disturbare la misura",
         "delimitare con picchetti le strisce di ricerca"],
        ["procedere a velocità costante tenendo la sonda alla distanza indicata dal terreno",
         "segnalare ogni anomalia senza colpire il terreno con attrezzi",
         "in profondità calare la sonda solo in fori eseguiti in strati già verificati",
         "sospendere la ricerca e allontanarsi se si individua un ordigno, avvisando il preposto"],
        ["registrare le anomalie sulla planimetria della bonifica",
         "pulire lo strumento e riporlo nella custodia con le batterie cariche"],
        ["casco", "guanti", "stivali di sicurezza", "indumenti ad alta visibilità", "copricapo"])),

    "Taglierina a filo caldo per pannelli isolanti": attrezzatura(ATTREZZO, rischi=[
        r("Ustioni", 3, 2,
          "Filo incandescente non protetto durante il taglio: mani lontane dal filo, pannello spinto con "
          "guide o battute; taglierina spenta e filo raffreddato prima di regolarlo o sostituirlo; "
          "appoggio su supporto stabile e non infiammabile.", DPI_BASE),
        r("Rischio chimico", 2, 2,
          "Il taglio termico di EPS e XPS libera fumi con stirene e prodotti di decomposizione: "
          "temperatura del filo regolata sul minimo che permette il taglio; postazione all'aperto o "
          "con aspirazione localizzata accesa per tutto il taglio; nessun taglio di pannelli vecchi senza "
          "conoscerne la composizione (possibile presenza di ritardanti di fiamma alogenati); scheda di "
          "sicurezza dei pannelli consultata (Titolo IX, Capo I).",
          DPI_BASE + ", maschera con filtro specifico"),
        r("Incendio ed esplosione", 2, 3,
          "Polistirene combustibile: taglierina lontana da sfridi accumulati, colle a solvente e bombole; "
          "spegnimento a fine uso e nelle pause; estintore nella postazione."),
        _elettrocuzione(1, 3, "Trasformatore e telaio integri; filo alimentato a bassa tensione come da "
                              "fabbricante."),
        r("Punture, tagli e abrasioni", 2, 1,
          "Filo teso che può rompersi: tensionatore regolato secondo il fabbricante; fili di ricambio "
          "maneggiati con guanti.", DPI_BASE),
    ], scheda_uso=scheda(
        "Attrezzo da banco o manuale con un filo metallico teso, riscaldato elettricamente, che taglia "
        "per fusione i pannelli in polistirene espanso o estruso per cappotti e isolamenti.",
        ["posizionare la taglierina in piano, all'aperto o sotto aspirazione localizzata",
         "verificare cavo, trasformatore, tensione del filo e guide di taglio",
         "allontanare sfridi, colle e materiali infiammabili dalla postazione",
         "consultare la scheda tecnica del pannello per la temperatura di taglio consigliata"],
        ["regolare la temperatura al minimo che consente un taglio regolare",
         "accompagnare il pannello lungo le guide senza avvicinare le mani al filo",
         "non respirare i fumi di taglio e mantenere l'aspirazione accesa",
         "spegnere la taglierina nelle pause e non lasciarla accesa incustodita"],
        ["spegnere e scollegare la taglierina e lasciare raffreddare il filo",
         "raccogliere gli sfridi in sacchi per il recupero o lo smaltimento",
         "pulire il filo dai residui fusi quando è freddo"],
        ["guanti", "occhiali protettivi", "maschera con filtro specifico", "calzature di sicurezza"])),

    "Accessori di sollevamento (brache, bilancini, ganci)": attrezzatura(ATTREZZO, rischi=[
        r("Caduta di materiale dall'alto o a livello", 2, 4,
          "Accessori marcati CE con portata e identificazione leggibili: brache di fune d'acciaio "
          "UNI EN 13414, brache di catena UNI EN 818, brache tessili piatte e tonde UNI EN 1492 (con "
          "etichetta e colore della portata), ganci e componenti UNI EN 1677, bilancini UNI EN 13155; "
          "portata scelta tenendo conto del modo di imbracatura e dell'angolo tra i bracci (angolo al "
          "vertice non oltre 120°); ganci con chiusura di sicurezza; verifica trimestrale di funi e "
          "catene registrata (Allegato VI punto 3.1.2); scarto degli accessori con fili rotti, maglie "
          "allungate, tagli o etichetta illeggibile.", DPI_BASE + ", casco con sottogola"),
        r("Urti, colpi, impatti e compressioni", 2, 3,
          "Carico guidato con funi e mai con le mani; imbracatore fuori dalla traiettoria e mai tra "
          "carico e ostacoli fissi; carico sollevato di pochi centimetri per verificarne l'equilibrio "
          "prima della movimentazione."),
        r("Cesoiamenti e stritolamenti", 2, 3,
          "Mani tolte dalle brache prima della messa in tiro; brache sfilate solo con il carico appoggiato "
          "su spessori stabili; nessun aggancio di persone ai carichi."),
        r("Punture, tagli e abrasioni", 3, 2,
          "Funi d'acciaio con fili spezzati maneggiate con guanti; brache tessili protette sugli spigoli "
          "vivi con paraspigoli o guaine; nessuna braca annodata.",
          DPI_BASE.replace("guanti", "guanti antitaglio")),
        r("Movimentazione manuale dei carichi", 2, 2,
          "Bilancini e brache di catena pesanti movimentati con il gancio dell'apparecchio di "
          "sollevamento; deposito su rastrelliere a portata di mano."),
    ], scheda_uso=scheda(
        "Brache di fune, catena o tessili, bilancini, grilli, ganci e anelli che collegano il carico al "
        "gancio della gru o di altri apparecchi di sollevamento.",
        ["controllare marcatura, portata e data dell'ultima verifica trimestrale",
         "esaminare a vista ogni accessorio e scartare quelli danneggiati o senza etichetta",
         "scegliere il tipo e la portata in base al peso del carico, al modo di imbracatura e "
         "all'angolo dei bracci",
         "predisporre paraspigoli e spessori per l'appoggio del carico"],
        ["imbracare il carico in modo equilibrato, con i ganci chiusi e i bracci in tensione uniforme",
         "comunicare con il manovratore con i gesti convenzionali dell'Allegato XXXII o via radio",
         "allontanarsi dal carico prima del sollevamento e non sostare sotto di esso",
         "non trascinare le brache sotto il carico appoggiato"],
        ["riporre gli accessori puliti e asciutti su rastrelliere, al riparo da sole e agenti chimici",
         "segnalare e togliere dall'uso gli accessori danneggiati",
         "aggiornare il registro delle verifiche di funi e catene"],
        ["casco con sottogola", "guanti", "calzature di sicurezza", "indumenti ad alta visibilità"])),
}
