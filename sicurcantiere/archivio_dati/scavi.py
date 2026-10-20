"""Archivio: lavori di movimento terra (MT) e fondazioni speciali e indagini geotecniche (FS).

Testi scritti da zero. Fonti consultate (solo come riferimento tecnico):
- D.Lgs. 81/2008, Titolo IV Capo II Sezione III (artt. 118 splateamento e sbancamento, 119 pozzi,
  scavi e cunicoli, 120 deposito di materiali presso gli scavi, 121 presenza di gas negli scavi),
  art. 66 e D.P.R. 177/2011 (ambienti confinati), art. 83 e Allegato IX (distanze da parti attive),
  art. 108 e Allegato XVIII punto 1 (viabilità, rampe di accesso al fondo degli scavi),
  artt. 28 e 91 c. 2-bis (valutazione del rischio bellico, L. 177/2012), Titolo IX Capo II
  (agenti cancerogeni, silice cristallina respirabile dopo il D.Lgs. 44/2020).
- INAIL, «Sistemi di protezione degli scavi a cielo aperto» (Quaderni tecnici per i cantieri) e
  «Riduzione del rischio nelle attività di scavo»; INAIL-ANCE, guida sulla sicurezza delle
  macchine perforatrici; schede divulgative PuntoSicuro sulla serie EN 16228.
- UNI EN 13331-1/-2 (sistemi di puntellazione per scavi); UNI EN 16228-1...7 (attrezzature per
  perforazioni e fondazioni, che sostituisce UNI EN 791 e UNI EN 996); norme di esecuzione dei
  lavori geotecnici speciali: UNI EN 1536 (pali trivellati), UNI EN 12699 (pali a spostamento),
  UNI EN 14199 (micropali), UNI EN 1537 (tiranti), UNI EN 1538 (diaframmi), UNI EN 12063
  (palancole), UNI EN 12715 (iniezioni), UNI EN 12716 (jet grouting); UNI EN ISO 22475-1
  (campionamento) e UNI EN ISO 22476 (prove in sito); UNI 9916 (vibrazioni sugli edifici).
- D.P.R. 120/2017 (terre e rocce da scavo), D.Lgs. 152/2006 parte IV (rifiuti), D.I. 22/01/2019
  (segnaletica per attività in presenza di traffico veicolare).
"""

from __future__ import annotations

from sicurcantiere.archivio_dati.base import ATTREZZO, DPI_BASE, MACCHINA, fase, r

MT = "Lavori di movimento terra"
FS = "Fondazioni speciali e indagini geotecniche"

NC_RI_IN = ("Nuove costruzioni", "Ristrutturazioni", "Opere infrastrutturali")
NC_IN = ("Nuove costruzioni", "Opere infrastrutturali")

# Attrezzature necessarie non presenti nel CATALOGO di base.py: nome -> (tipo, motivo).
MANCANTI: dict[str, tuple[str, str]] = {
    "Penetrometro statico e dinamico": (
        MACCHINA, "Macchina semovente o autocarrata per prove CPT, CPTU e DPSH: la sonda di perforazione "
                  "non la rappresenta (spinta idraulica con ancoraggi a elica o maglio a caduta libera)."),
    "Impianto di abbassamento della falda (wellpoint)": (
        ATTREZZO, "Aggottamento con aghi filtranti, collettore e pompa aspirante a vuoto: diverso dalla "
                  "pompa sommersa per rischi (tubazioni in pressione, rumore continuo, impianto elettrico)."),
    "Martinetto idraulico per tesatura": (
        ATTREZZO, "Necessario per la tesatura e il collaudo dei tiranti di ancoraggio: rischio specifico "
                  "di rilascio improvviso del trefolo o della barra e di rottura dei tubi ad alta pressione."),
    "Attrezzatura per scavo di diaframmi (benna mordente o idrofresa)": (
        MACCHINA, "Macchina base con benna mordente a funi o idraulica, o con idrofresa, per i pannelli "
                  "dei diaframmi (UNI EN 16228-5): non coincide con la perforatrice per pali."),
    "Impianto di confezionamento e dissabbiatura dei fanghi": (
        MACCHINA, "Miscelatori, silos, vasche e dissabbiatori per i fanghi bentonitici o polimerici di "
                  "pali trivellati e diaframmi: rischi di vasche aperte, polveri e prodotti chimici."),
}

# --- Rischi ricorrenti ---

_SEPPELLIMENTO = r(
    "Seppellimento e sprofondamento", 2, 4,
    "Pareti con inclinazione adeguata alla natura del terreno secondo la relazione geotecnica, o armate man "
    "mano che lo scavo avanza oltre 1,50 m (artt. 118 e 119); nessun deposito di terra o materiali sul "
    "ciglio (art. 120) e mezzi a distanza dal bordo pari almeno alla profondità dello scavo; controllo "
    "delle pareti da parte del preposto a inizio turno e dopo piogge, gelo o disgelo, con sospensione "
    "dei lavori in caso di fessure o distacchi.")
_CADUTA_SCAVO = r(
    "Caduta dall'alto", 3, 3,
    "Ciglio dello scavo protetto con parapetto provvisorio o, se a più di 1,50 m dal bordo, delimitato "
    "con barriera continua e segnaletica; attraversamenti solo su passerelle con parapetti; discesa e "
    "risalita con scale a mano vincolate che sporgono almeno 1 m oltre il ciglio; illuminazione nelle "
    "ore serali.")
_INVESTIMENTO = r(
    "Investimento da mezzi in manovra", 2, 4,
    "Nessun addetto nel raggio d'azione dell'escavatore né alla base del fronte di scavo (art. 118); "
    "percorsi pedonali separati da quelli dei mezzi (Allegato XVIII punto 1); comunicazione a vista o "
    "via radio con l'operatore prima di avvicinarsi; moviere nelle retromarce; indumenti ad alta "
    "visibilità.")
_SOTTOSERVIZI = r(
    "Elettrocuzione", 2, 4,
    "Prima dello scavo, planimetrie delle reti interrate dagli enti gestori e rilievo con cercaservizi; "
    "tracciati segnati sul terreno; in prossimità delle reti procedere con saggi a mano o per aspirazione; "
    "in caso di contatto con un cavo o una condotta del gas allontanarsi, non toccare il mezzo e avvisare "
    "subito il gestore; linee aeree con le distanze minime dell'Allegato IX (art. 83).")
_POLVERI = r(
    "Polveri e fibre", 3, 2,
    "Bagnatura delle piste e dei cumuli; sospensione con vento forte; cabine dei mezzi chiuse e "
    "pressurizzate; facciale filtrante per gli addetti a terra.",
    DPI_BASE + ", facciale filtrante FFP2")
_MMC = r(
    "Movimentazione manuale dei carichi", 3, 2,
    "Carichi pesanti o ingombranti movimentati con il mezzo di sollevamento; sollevamento in due per gli "
    "elementi oltre i limiti della valutazione (UNI ISO 11228-1); pause e rotazione dei compiti.")
_FANGO = r(
    "Scivolamenti e cadute a livello", 3, 2,
    "Piano di lavoro mantenuto drenato e sgombro da tubi e attrezzi; passerelle o pedane sulle zone "
    "fangose; calzature con suola antiscivolo; nessun lavoro al buio.",
    DPI_BASE + ", stivali di sicurezza")
_ORDIGNI = r(
    "Esplosione di ordigni bellici inesplosi", 1, 4,
    "Valutazione del rischio bellico residuo nel PSC (artt. 28 e 91 c. 2-bis); se prevista, bonifica "
    "preventiva da impresa specializzata; al ritrovamento di un oggetto sospetto fermare i lavori, "
    "allontanare tutti e avvisare le autorità senza toccarlo.")
_CARICHI_SOSPESI = r(
    "Caduta di materiale dall'alto o a livello", 2, 4,
    "Imbracature verificate e adatte al carico; nessuno sotto il carico sospeso o nello scavo durante la "
    "calata; guida del carico con funi o aste, mai a mano sotto il carico; segnalazioni codificate con il "
    "gruista (Allegato XXXII).")
_CEMENTO = r(
    "Rischio chimico", 3, 2,
    "Miscele cementizie con cromo VI ridotto; evitare il contatto con la pelle; lavaggio immediato degli "
    "schizzi; crema protettiva e indumenti puliti; sorveglianza sanitaria per le dermatiti.",
    DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi")
_SCHIZZI_INIEZIONE = r(
    "Getti e schizzi", 3, 3,
    "Tubi, raccordi e manometri controllati prima di mettere in pressione; tubi ad alta pressione con "
    "dispositivi anti-colpo di frusta ai raccordi; nessuno vicino alla testa di iniezione durante la "
    "pressurizzazione; scarico della pressione prima di aprire o pulire i circuiti.",
    DPI_BASE + ", visiera protettiva, guanti in lattice o nitrile")
_PERFORAZIONE = r(
    "Cesoiamenti e stritolamenti", 2, 4,
    "Perforatrice conforme alla UNI EN 16228 con ripari o dispositivi di arresto sull'organo rotante; "
    "zona pericolosa attorno all'asta delimitata; aggiunta e smontaggio delle aste solo a rotazione "
    "ferma; un solo operatore ai comandi, in vista dell'aiutante; indumenti aderenti, senza parti "
    "svolazzanti.")
_ACQUA_FALDA = r(
    "Annegamento", 1, 4,
    "Controllo del livello della falda e dell'acqua piovana; aggottamento continuo con pompa di riserva; "
    "nessuno nello scavo durante l'allagamento; vie di risalita sempre libere.",
    DPI_BASE + ", stivali di sicurezza")
_SILICE = r(
    "Polveri e fibre (silice cristallina respirabile)", 3, 3,
    "Abbattimento a umido alla fonte; cabine chiuse con filtrazione; addetti a terra sopravento e lontani "
    "dal punto di frantumazione; valutazione dell'esposizione come agente cancerogeno (Titolo IX Capo II, "
    "Allegato XLII) e sorveglianza sanitaria.",
    DPI_BASE + ", facciale filtrante FFP3")
_FABBRICATI = r(
    "Crollo o ribaltamento di strutture", 2, 4,
    "Verifica preventiva delle fondazioni dei fabbricati e dei manufatti vicini; scavo per campioni o "
    "con opere di sostegno come da progetto (art. 119 c. 4); monitoraggio di fessure e cedimenti con "
    "fessurimetri e capisaldi; sospensione dei lavori ai primi segni di dissesto.")
_TRAFFICO = r(
    "Investimento da veicoli lungo la strada", 2, 4,
    "Cantiere stradale segnalato e delimitato secondo il D.M. 10/07/2002; posa e rimozione della "
    "segnaletica da personale formato (D.I. 22/01/2019); indumenti ad alta visibilità di classe 3.",
    DPI_BASE + " di classe 3")
_MICROCLIMA = r(
    "Microclima", 2, 2,
    "Pause in zona ombreggiata o riparata; acqua a disposizione; lavori più pesanti nelle ore fresche; "
    "indumenti adatti a freddo e pioggia.",
    DPI_BASE + ", indumenti impermeabili")
_URTI = r(
    "Urti, colpi, impatti e compressioni", 2, 3,
    "Movimenti dei mezzi e delle attrezzature coordinati dal preposto; nessuno tra l'elemento in "
    "movimento e parti fisse; guida degli elementi con funi; mani lontane dai punti di schiacciamento.")


LAVORAZIONI = [
    # ---------------------------------------------------------------- Movimento terra
    # --- Scavi di sbancamento e splateamento ---
    fase("MT.01", MT, "Scavi di sbancamento e splateamento",
         "Scavo di sbancamento a cielo aperto con mezzi meccanici",
         "Asportazione del terreno su vaste superfici con escavatore e pala, fino alle quote di progetto, "
         "con pareti modellate secondo l'angolo di scarpa indicato dalla relazione geotecnica o gradonate. "
         "Il materiale è caricato direttamente sugli autocarri o accumulato nelle aree di deposito previste. "
         "Il preposto controlla l'avanzamento del fronte e la stabilità delle scarpate.",
         "Addetto allo scavo di sbancamento", 15, NC_RI_IN,
         ["Escavatore", "Pala meccanica", "Autocarro", "Dumper"], [
             _SEPPELLIMENTO, _CADUTA_SCAVO, _INVESTIMENTO, _SOTTOSERVIZI, _POLVERI, _ORDIGNI,
         ]),
    fase("MT.02", MT, "Scavi di sbancamento e splateamento",
         "Scavo di splateamento in roccia o terreno compatto con demolitore idraulico",
         "Frantumazione di banchi rocciosi o terreni molto compatti con martello idraulico montato "
         "sull'escavatore e successiva rimozione dei frammenti. Le pareti vengono disgaggiate dai blocchi "
         "instabili prima dell'accesso degli addetti al fondo. Gli addetti a terra si occupano di "
         "segnalazioni, rilievi di quota e pulizia del fondo a lavorazione ferma.",
         "Addetto allo scavo di splateamento in roccia", 15, NC_IN,
         ["Escavatore con martello demolitore", "Escavatore", "Autocarro"], [
             _SILICE,
             r("Proiezione di schegge e frammenti", 3, 3,
               "Zona di frantumazione interdetta per un raggio stabilito dal preposto (almeno 15-20 m in "
               "roccia); avvicinamento solo a martello fermo e con il consenso dell'operatore; protezione "
               "frontale della cabina.",
               DPI_BASE + ", occhiali protettivi"),
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Disgaggio meccanico dei blocchi instabili dal ciglio prima di scendere; nessuno al piede "
               "della parete rocciosa; reti o pendenze di sicurezza dove la roccia è fratturata."),
             _INVESTIMENTO, _SEPPELLIMENTO,
         ]),
    fase("MT.03", MT, "Scavi di sbancamento e splateamento",
         "Formazione di rampe e piste di accesso al fondo dello scavo",
         "Realizzazione delle rampe che collegano il piano campagna al fondo dello sbancamento, con "
         "pendenza compatibile con i mezzi che le percorrono e fondo compattato e portante. L'accesso "
         "pedonale è separato da quello dei mezzi oppure si lascia un franco di almeno 70 cm oltre la "
         "sagoma del veicolo, con nicchie di rifugio ogni 20 m se il franco è da un solo lato "
         "(Allegato XVIII punto 1). Sul lato a valle si posano cordoli o barriere contro lo sviamento.",
         "Addetto alla formazione delle rampe di accesso allo scavo", 20, NC_RI_IN,
         ["Escavatore", "Pala meccanica", "Rullo compattatore", "Autocarro"], [
             r("Ribaltamento e sviamento dei mezzi dalla rampa", 2, 4,
               "Pendenza e larghezza da progetto; bordo libero rinforzato con cordolo di terra o "
               "barriera; manutenzione del fondo dopo le piogge; velocità ridotta e segnaletica."),
             _INVESTIMENTO, _CADUTA_SCAVO, _POLVERI,
         ]),
    # --- Scavi a sezione obbligata ---
    fase("MT.04", MT, "Scavi a sezione obbligata",
         "Scavo a sezione obbligata per plinti e travi di fondazione",
         "Scavo a sezione ristretta per plinti, travi rovesce e cordoli di fondazione, eseguito con "
         "escavatore o miniescavatore secondo il tracciamento, con rifinitura a mano del fondo e delle "
         "pareti. Gli scavi oltre 1,50 m in terreni non stabili vanno armati o profilati a scarpa prima "
         "dell'accesso. La terra è allontanata o depositata lontano dal ciglio.",
         "Addetto allo scavo a sezione obbligata per fondazioni", 20, NC_RI_IN,
         ["Escavatore", "Miniescavatore", "Autocarro", "Utensili manuali", "Scala a mano"], [
             _SEPPELLIMENTO, _CADUTA_SCAVO, _INVESTIMENTO, _SOTTOSERVIZI, _MMC,
         ]),
    fase("MT.05", MT, "Scavi a sezione obbligata",
         "Scavo in trincea per la posa di condotte e sottoservizi",
         "Scavo lineare a sezione obbligata per tubazioni, cavidotti e collettori, con avanzamento per "
         "tratti brevi e immediata armatura delle pareti con blindaggi o casseri a binario oltre 1,50 m. "
         "Il fondo è regolarizzato per il letto di posa. Se lo scavo è su sede stradale, l'area è "
         "delimitata e segnalata verso il traffico.",
         "Addetto allo scavo in trincea", 25, NC_IN,
         ["Escavatore", "Miniescavatore", "Autocarro", "Armatura delle pareti di scavo (blindaggio)",
          "Scala a mano"], [
             r("Seppellimento e sprofondamento", 3, 4,
               "Nessun ingresso nel tratto non armato; blindaggio posato dall'esterno e calato man mano "
               "con l'avanzamento (art. 119); pannelli oltre il ciglio di almeno 30 cm; terra di scavo "
               "sul lato opposto e a distanza dal bordo; scale di risalita entro 7-8 m da ogni addetto."),
             _CADUTA_SCAVO, _INVESTIMENTO, _SOTTOSERVIZI, _TRAFFICO,
         ]),
    fase("MT.06", MT, "Scavi a sezione obbligata",
         "Scavo a mano e rifinitura del fondo e delle pareti",
         "Scavo eseguito con pala, piccone e martello demolitore leggero dove i mezzi non possono "
         "operare o in prossimità di reti e strutture, con sollevamento del materiale in secchi o con "
         "argano. Comprende la regolarizzazione del fondo scavo e la pulizia prima dei getti. Oltre "
         "1,50 m di altezza del fronte non si scava per scalzamento alla base (art. 118).",
         "Addetto allo scavo a mano", 80, NC_RI_IN + ("Restauri",),
         ["Utensili manuali", "Martello demolitore", "Scala a mano", "Argano a cavalletto"], [
             _SEPPELLIMENTO, _MMC,
             r("Posture incongrue", 3, 2,
               "Alternanza dei compiti; attrezzi con manico di lunghezza adeguata; spazio di lavoro nello "
               "scavo sufficiente a stare in piedi; pause."),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Secchi e benne con ganci di sicurezza; nessuno sotto il carico in risalita; fermapiede o "
               "tavola al ciglio contro la caduta di sassi e attrezzi nello scavo."),
             _SOTTOSERVIZI, _MICROCLIMA,
         ]),
    fase("MT.07", MT, "Scavi a sezione obbligata",
         "Scavo in prossimità di sottoservizi e di fondazioni esistenti",
         "Saggi di individuazione e scavo controllato vicino a reti interrate (gas, elettricità, acqua, "
         "telecomunicazioni) e a fondazioni di edifici, eseguiti a mano, con miniescavatore a benna "
         "liscia o per aspirazione con autospurgo. Le reti scoperte sono sostenute e protette; le "
         "fondazioni vicine sono monitorate e scavate solo per campioni o dopo le opere di sostegno.",
         "Addetto allo scavo in prossimità di sottoservizi e fabbricati", 55, TUTTE_MT := NC_RI_IN + ("Restauri",),
         ["Miniescavatore", "Autospurgo", "Utensili manuali", "Scala a mano"], [
             r("Elettrocuzione", 2, 4,
               "Mappatura delle reti con gli enti gestori e cercaservizi; ultimi 50 cm sopra la rete "
               "scoperti a mano o per aspirazione; utensili con impugnature isolanti; cavi scoperti "
               "segnalati e protetti; in caso di danneggiamento fermarsi e avvisare il gestore.",
               DPI_BASE + ", guanti dielettrici"),
             r("Incendio ed esplosione", 1, 4,
               "Condotte del gas individuate e segnalate; divieto di fiamme libere; in caso di fuga "
               "allontanare tutti, spegnere i motori e chiamare il gestore e i vigili del fuoco; "
               "rilevatore multigas nello scavo vicino alle reti."),
             _FABBRICATI, _SEPPELLIMENTO, _MMC,
         ]),
    # --- Sostegno delle pareti e controllo delle acque ---
    fase("MT.08", MT, "Sostegno delle pareti e controllo delle acque",
         "Armatura delle pareti dello scavo con blindaggi prefabbricati",
         "Posa di sistemi di puntellazione modulari (pannelli in acciaio o alluminio con puntoni "
         "regolabili, conformi alla UNI EN 13331) secondo il manuale del fabbricante: montaggio del modulo "
         "a piano campagna, calata con l'escavatore e infissione progressiva con lo scavo, eventuali "
         "moduli di sopralzo. L'estrazione avviene dal basso verso l'alto in parallelo al rinterro.",
         "Addetto all'armatura delle pareti dello scavo", 40, NC_RI_IN,
         ["Escavatore", "Armatura delle pareti di scavo (blindaggio)", "Scala a mano", "Utensili manuali"], [
             r("Seppellimento e sprofondamento", 2, 4,
               "Montaggio e regolazione dei puntoni solo dall'esterno o dall'interno del tratto già "
               "protetto; sequenza di posa ed estrazione del fabbricante; nessuno nello scavo durante "
               "l'estrazione dei pannelli; verifica giornaliera di puntoni e spinotti."),
             _CARICHI_SOSPESI, _URTI, _CADUTA_SCAVO,
             r("Cesoiamenti e stritolamenti", 2, 3,
               "Mani fuori dagli spazi tra pannelli e puntoni durante la calata; uso di spine e "
               "dispositivi di sicurezza previsti; segnali concordati con l'escavatorista."),
         ]),
    fase("MT.09", MT, "Sostegno delle pareti e controllo delle acque",
         "Armatura delle pareti dello scavo con tavole e puntelli (sbadacchiatura)",
         "Rivestimento delle pareti con tavole verticali o orizzontali, correnti e puntelli regolabili, "
         "posati man mano che lo scavo procede, per scavi brevi, irregolari o dove il blindaggio non entra. "
         "Le tavole sporgono almeno 30 cm sopra il ciglio (art. 119 c. 2) e i puntelli sono bloccati contro "
         "lo scorrimento. Lo smontaggio procede dal basso verso l'alto con il rinterro.",
         "Addetto alla sbadacchiatura delle pareti dello scavo", 70, NC_RI_IN + ("Restauri",),
         ["Armatura delle pareti di scavo (blindaggio)", "Puntelli metallici", "Sega circolare",
          "Utensili manuali", "Scala a mano"], [
             _SEPPELLIMENTO, _MMC, _URTI,
             r("Punture, tagli e abrasioni", 3, 2,
               "Tavolame privo di chiodi sporgenti; chiodi ribattuti dopo il disarmo; guanti adatti."),
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Tavole e puntelli calati con fune o con il mezzo, mai lanciati nello scavo; fermapiede "
               "costituito dalla sporgenza delle tavole sul ciglio."),
         ]),
    fase("MT.10", MT, "Sostegno delle pareti e controllo delle acque",
         "Infissione ed estrazione di palancole metalliche",
         "Realizzazione di paratie provvisorie in palancole d'acciaio infisse con vibroinfissore o "
         "battipalo, eventualmente contrastate da travi di ripartizione e puntoni man mano che si "
         "scava (UNI EN 12063). L'addetto a terra guida l'aggancio e l'innesto della palancola nel giunto "
         "della precedente. A fine lavori le palancole sono estratte con lo stesso vibratore.",
         "Addetto all'infissione di palancole", 30, NC_IN,
         ["Battipalo (infissione di pali e barriere)", "Autogru", "Escavatore", "Saldatrice"], [
             _CARICHI_SOSPESI,
             r("Urti, colpi, impatti e compressioni", 2, 4,
               "Palancola sollevata con grillo o morsa di presa adeguata; innesto guidato con fune e asta "
               "a distanza; nessuno tra la palancola sospesa e quelle già infisse."),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Valutazione preventiva delle vibrazioni sugli edifici e sulle reti vicine (art. 119 c. 5, "
               "UNI 9916); preferire la vibroinfissione ad alta frequenza o l'infissione a pressione "
               "vicino ai fabbricati; monitoraggio durante l'infissione."),
             r("Caduta dall'alto", 2, 4,
               "Lavori di saldatura e montaggio delle travi di contrasto da piattaforma o da passerella "
               "con parapetto; nessuna salita sulle palancole.",
               DPI_BASE + ", imbracatura, cordino con assorbitore"),
             _SOTTOSERVIZI,
         ]),
    fase("MT.11", MT, "Sostegno delle pareti e controllo delle acque",
         "Aggottamento delle acque e abbassamento della falda",
         "Allontanamento dell'acqua di falda o piovana dallo scavo con pompe sommerse in pozzetti di "
         "raccolta, oppure con impianto wellpoint perimetrale di aghi filtranti collegati a un collettore "
         "e a una pompa a vuoto. Le acque sono scaricate nei recapiti autorizzati, previa decantazione. "
         "L'impianto funziona in continuo, con controllo dei livelli e pompa di riserva.",
         "Addetto all'aggottamento delle acque", 45, NC_RI_IN,
         ["Pompa sommersa", "Impianto di abbassamento della falda (wellpoint)", "Gruppo elettrogeno",
          "Utensili manuali"], [
             r("Elettrocuzione", 2, 4,
               "Pompe con grado di protezione IPX8 e cavo integro senza giunzioni in acqua; alimentazione "
               "da quadro di cantiere con differenziale da 30 mA; pompa sollevata e scollegata prima di "
               "ogni intervento.",
               DPI_BASE + ", stivali di sicurezza"),
             _ACQUA_FALDA,
             r("Seppellimento e sprofondamento", 2, 4,
               "Controllo dei sifonamenti e del trascinamento di fini al fondo scavo; filtri adeguati "
               "al terreno; nessun abbassamento rapido dell'acqua senza verifica delle pareti."),
             _FANGO, _MMC,
         ]),
    # --- Rinterri, rilevati e drenaggi ---
    fase("MT.12", MT, "Rinterri, rilevati e drenaggi",
         "Rinterro e riempimento di scavi con compattazione a strati",
         "Riempimento di scavi di fondazione e trincee con terra di risulta o materiale arido, steso in "
         "strati di spessore limitato e compattato con piastra vibrante o costipatore, fino alle quote "
         "di progetto. Il rinterro procede in parallelo alla rimozione delle armature delle pareti.",
         "Addetto al rinterro e alla compattazione", 30, NC_RI_IN,
         ["Escavatore", "Pala meccanica", "Piastra vibrante", "Costipatore a percussione", "Utensili manuali"], [
             _INVESTIMENTO, _SEPPELLIMENTO, _POLVERI, _MMC,
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "Scarico del materiale nello scavo solo con addetti fuori dalla zona di caduta; segnali "
               "concordati con l'operatore della pala."),
         ]),
    fase("MT.13", MT, "Rinterri, rilevati e drenaggi",
         "Formazione di rilevati con stesa e compattazione",
         "Costruzione di rilevati stradali, arginali o di piazzali con materiale idoneo scaricato dagli "
         "autocarri, steso con apripista e livellatrice e compattato a strati con rullo, previa umidificazione. "
         "Gli addetti a terra eseguono controlli di quota e prove di carico su piastra.",
         "Addetto alla formazione dei rilevati", 15, NC_IN,
         ["Autocarro", "Bulldozer", "Grader (livellatrice)", "Rullo compattatore", "Autobotte"], [
             _INVESTIMENTO, _POLVERI, _MICROCLIMA,
             r("Ribaltamento dei mezzi dal ciglio del rilevato", 2, 4,
               "Fascia di rispetto dal bordo del rilevato non compattato; cordolo di terra di riferimento; "
               "scarico degli autocarri a distanza dal ciglio con moviere."),
         ]),
    fase("MT.14", MT, "Rinterri, rilevati e drenaggi",
         "Realizzazione di drenaggi e vespai",
         "Posa a ridosso delle murature controterra o sotto le platee di tubi drenanti, geotessili e "
         "strati di ghiaia o ciottoli, oppure di vespai aerati con elementi in plastica. Il materiale è "
         "scaricato con il mezzo e sistemato a mano; i tubi sono collegati ai pozzetti di raccolta.",
         "Addetto alla realizzazione di drenaggi e vespai", 45, TUTTE_MT,
         ["Escavatore", "Miniescavatore", "Pala meccanica", "Piastra vibrante", "Utensili manuali"], [
             _SEPPELLIMENTO, _CADUTA_SCAVO, _MMC,
             r("Posture incongrue", 3, 2,
               "Stesa a mano limitata alle rifiniture; rastrelli e pale a manico lungo; ginocchiere per "
               "la posa a terra degli elementi; rotazione dei compiti.",
               DPI_BASE + ", ginocchiere"),
             _URTI,
         ]),
    # --- Gestione delle terre e rocce da scavo ---
    fase("MT.15", MT, "Gestione delle terre e rocce da scavo",
         "Carico e trasporto delle terre a deposito, a sito di destinazione o a impianto",
         "Carico su autocarro del materiale scavato e trasporto, come sottoprodotto al sito di destinazione "
         "indicato nel piano di utilizzo o nella dichiarazione (D.P.R. 120/2017), oppure come rifiuto a "
         "impianto autorizzato con formulario. Il cassone è coperto con telone; le ruote sono pulite "
         "prima dell'uscita sulla viabilità pubblica.",
         "Addetto al carico e trasporto delle terre", 10, NC_RI_IN,
         ["Escavatore", "Pala meccanica", "Autocarro", "Spazzatrice stradale"], [
             _INVESTIMENTO, _POLVERI,
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Nessuno vicino al cassone durante il carico; autista in cabina o in posizione protetta; "
               "carico non oltre le sponde e coperto prima della partenza."),
             r("Caduta dall'alto", 2, 3,
               "Telone steso da terra con sistema a manovella o da pedana; niente salite sul carico; "
               "scalette del cassone integre.",
               DPI_BASE + ", calzature di sicurezza"),
             _TRAFFICO,
         ]),
    fase("MT.16", MT, "Gestione delle terre e rocce da scavo",
         "Deposito intermedio e campionamento delle terre e rocce da scavo",
         "Formazione di cumuli separati per provenienza e qualità nell'area di deposito intermedio, con "
         "cartelli di identificazione, e prelievo dei campioni per la caratterizzazione ambientale "
         "prevista dal D.P.R. 120/2017. I cumuli sono stabili, a pendenza contenuta e coperti se "
         "polverulenti. Il terreno con indizi di contaminazione è isolato e segnalato al direttore dei lavori.",
         "Addetto al deposito e campionamento delle terre", 30, NC_RI_IN,
         ["Pala meccanica", "Escavatore", "Utensili manuali"], [
             _INVESTIMENTO, _POLVERI,
             r("Seppellimento e sprofondamento", 1, 4,
               "Cumuli con altezza e pendenza limitate; prelievo al piede del cumulo solo a mezzi fermi; "
               "divieto di salire sui cumuli instabili o scalzarli alla base."),
             r("Rischio chimico", 2, 3,
               "In presenza di odori, colori anomali o rifiuti interrati fermare lo scavo e avvisare; "
               "campionamento con guanti e senza contatto con la pelle; lavaggio delle mani prima dei pasti.",
               DPI_BASE + ", guanti in lattice o nitrile, facciale filtrante FFP2"),
         ]),

    # ---------------------------------------------------------------- Fondazioni speciali
    # --- Indagini geotecniche ---
    fase("FS.01", FS, "Indagini geotecniche",
         "Sondaggi geognostici a carotaggio continuo con prelievo di campioni",
         "Perforazione verticale o inclinata con sonda a rotazione, carotiere e rivestimento provvisorio, "
         "estrazione delle carote e loro sistemazione nelle cassette catalogatrici, prelievo di campioni "
         "indisturbati (UNI EN ISO 22475-1) e prove SPT in foro. Al termine il foro è cementato o "
         "attrezzato. L'aiutante sondatore movimenta aste, carotieri e cassette.",
         "Addetto ai sondaggi geognostici", 45, TUTTE_MT,
         ["Sonda di perforazione (micropali, tiranti, sondaggi)", "Autocarro con gru", "Utensili manuali"], [
             _PERFORAZIONE, _MMC, _SOTTOSERVIZI, _FANGO,
             r("Caduta di materiale dall'alto o a livello", 2, 3,
               "Aste e carotieri sollevati con il verricello e il gancio di sicurezza; nessuno sotto la "
               "testa della sonda durante la manovra; stoccaggio delle aste su rastrelliera."),
             _MICROCLIMA,
         ]),
    fase("FS.02", FS, "Indagini geotecniche",
         "Prove penetrometriche statiche e dinamiche",
         "Esecuzione di prove penetrometriche statiche con punta elettrica o piezocono (CPT, CPTU) e "
         "dinamiche superpesanti (DPSH), secondo la UNI EN ISO 22476, con macchina ancorata al terreno "
         "o zavorrata. L'operatore assembla le aste, registra i dati ed estrae la batteria a fine prova.",
         "Addetto alle prove penetrometriche", 50, TUTTE_MT,
         ["Penetrometro statico e dinamico", "Utensili manuali"], [
             r("Cesoiamenti e stritolamenti", 2, 3,
               "Aggiunta delle aste solo a spinta o maglio fermi; mani lontane dalla zona di battuta e "
               "dalla morsa; ripari del maglio chiusi."),
             _MMC, _SOTTOSERVIZI,
             r("Urti, colpi, impatti e compressioni", 2, 3,
               "Verifica degli ancoraggi o della zavorra prima della spinta per evitare il sollevamento "
               "della macchina; nessuno a ridosso del telaio durante la prova."),
         ]),
    fase("FS.03", FS, "Indagini geotecniche",
         "Installazione di piezometri e tubi inclinometrici di monitoraggio",
         "Posa nei fori di sondaggio di piezometri a tubo aperto o elettrici e di tubi inclinometrici, "
         "con riempimento dell'intercapedine con ghiaietto, tappi di bentonite e miscela cementizia. "
         "La testa del foro è protetta con pozzetto e chiusino. Seguono le letture periodiche.",
         "Addetto all'installazione della strumentazione geotecnica", 50, TUTTE_MT,
         ["Sonda di perforazione (micropali, tiranti, sondaggi)", "Pompa per malte e iniezioni",
          "Utensili manuali"], [
             _CEMENTO, _MMC, _FANGO,
             r("Polveri e fibre", 2, 2,
               "Bentonite e cemento versati da sacchi con poca altezza di caduta e sopravento; facciale "
               "filtrante durante la preparazione della miscela.",
               DPI_BASE + ", facciale filtrante FFP2"),
         ]),
    # --- Pali di fondazione ---
    fase("FS.04", FS, "Pali di fondazione",
         "Perforazione di pali trivellati di grande diametro",
         "Perforazione del terreno con macchina a rotazione dotata di asta telescopica (kelly) e utensili "
         "a elica o bucket, con camicia metallica provvisoria o fanghi di sostegno (UNI EN 1536). Il "
         "materiale estratto è scaricato a terra e allontanato con la pala. I fori aperti sono coperti o "
         "protetti fino al getto.",
         "Addetto alla perforazione dei pali trivellati", 25, NC_IN,
         ["Macchina perforatrice per pali", "Escavatore", "Pala meccanica", "Autocarro",
          "Impianto di confezionamento e dissabbiatura dei fanghi"], [
             _PERFORAZIONE,
             r("Caduta dall'alto", 2, 4,
               "Fori aperti coperti con piastre o protetti con parapetto o con la camicia sporgente "
               "almeno 1 m dal piano; nessuno vicino al foro senza necessità.",
               DPI_BASE + ", imbracatura, cordino con assorbitore"),
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Piano di lavoro livellato e portante, verificato per la pressione dei cingoli della "
               "macchina (UNI EN 16228); nessuno nella zona di possibile ribaltamento; spostamenti con "
               "antenna abbassata come da manuale."),
             r("Proiezione di schegge e frammenti", 2, 3,
               "Distanza dal punto di scarico dell'elica, che centrifuga il terreno; pulizia dell'utensile "
               "solo a rotazione ferma.",
               DPI_BASE + ", occhiali protettivi"),
             _FANGO, _INVESTIMENTO,
         ]),
    fase("FS.05", FS, "Pali di fondazione",
         "Posa delle gabbie di armatura e getto dei pali trivellati",
         "Sollevamento della gabbia metallica preassemblata con due punti di presa, rotazione in verticale "
         "e calata nel foro, con eventuale giunzione dei tronchi sopra la bocca del foro. Il getto avviene "
         "dal basso con tubo convogliatore (tremie) alimentato dall'autobetoniera, sollevato man mano, "
         "seguito dall'estrazione della camicia provvisoria.",
         "Addetto all'armatura e al getto dei pali trivellati", 35, NC_IN,
         ["Autogru", "Autobetoniera", "Saldatrice", "Utensili manuali"], [
             _CARICHI_SOSPESI,
             r("Cesoiamenti e stritolamenti", 2, 4,
               "Gabbia sostenuta alla bocca del foro con traverse di appoggio prima di sganciarla o di "
               "giuntarla; mani fuori dagli spazi tra gabbia e camicia; tubo getto manovrato a distanza."),
             r("Punture, tagli e abrasioni", 3, 2,
               "Guanti antitaglio nella movimentazione delle gabbie; ferri sporgenti protetti con cappucci.",
               DPI_BASE + ", guanti antitaglio"),
             _CEMENTO,
             r("Caduta dall'alto", 2, 4,
               "Lavoro alla bocca del foro su piattaforma con parapetto; foro protetto subito dopo il getto.",
               DPI_BASE + ", imbracatura, cordino con assorbitore"),
         ]),
    fase("FS.06", FS, "Pali di fondazione",
         "Scapitozzatura delle teste dei pali",
         "Demolizione della parte superiore del palo, contaminata dal fango o dal calcestruzzo di scarsa "
         "qualità, fino alla quota di imposta del plinto o del cordolo, mettendo a nudo i ferri di "
         "attesa. Si usano martelli demolitori o, in alternativa, sistemi di frantumazione idraulica "
         "ad anello; i ferri vengono ripuliti e raddrizzati.",
         "Addetto alla scapitozzatura dei pali", 60, NC_IN,
         ["Martello demolitore pneumatico", "Motocompressore", "Escavatore con martello demolitore",
          "Utensili manuali"], [
             _SILICE,
             r("Proiezione di schegge e frammenti", 3, 3,
               "Area attorno al palo interdetta ai non addetti; schermi tra posti di lavoro vicini; "
               "occhiali o visiera.",
               DPI_BASE + ", visiera protettiva"),
             r("Movimentazione manuale dei carichi", 3, 2,
               "Martello sostenuto da braccio o carrello di supporto dove possibile; testa del palo "
               "rimossa in blocco con il mezzo; rotazione degli addetti."),
             r("Posture incongrue", 3, 2,
               "Lavoro alla quota di comodo ribassando il piano attorno al palo; pause frequenti."),
             _SEPPELLIMENTO,
         ]),
    fase("FS.07", FS, "Pali di fondazione",
         "Infissione di pali prefabbricati battuti o vibroinfissi",
         "Infissione di pali prefabbricati in c.a.c., in acciaio o in legno con battipalo a maglio o con "
         "vibroinfissore (UNI EN 12699), previa disposizione del palo sulla guida e centratura. I tronchi "
         "di palo possono essere giuntati con saldatura o giunti meccanici; la testa è tagliata alla quota "
         "di progetto.",
         "Addetto all'infissione di pali prefabbricati", 30, NC_IN,
         ["Battipalo (infissione di pali e barriere)", "Autogru", "Saldatrice", "Smerigliatrice angolare"], [
             _CARICHI_SOSPESI,
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Valutazione preventiva delle vibrazioni trasmesse a edifici e reti (art. 119 c. 5, UNI 9916) "
               "con monitoraggio; piano di posa del battipalo portante e livellato."),
             r("Proiezione di schegge e frammenti", 2, 3,
               "Zona di battuta interdetta; cuscino della cuffia efficiente per limitare le rotture della "
               "testa del palo; nessun avvicinamento durante la battitura.",
               DPI_BASE + ", occhiali protettivi"),
             _URTI,
         ]),
    # --- Micropali e tiranti ---
    fase("FS.08", FS, "Micropali e tiranti",
         "Perforazione e armatura di micropali",
         "Perforazione di piccolo diametro a rotazione o rotopercussione, con rivestimento o fluido di "
         "circolazione, e inserimento nel foro dell'armatura tubolare in acciaio valvolata, a tronchi "
         "filettati o manicottati (UNI EN 14199). Spesso si opera in spazi ridotti, anche in interrati "
         "o a ridosso di murature da consolidare.",
         "Addetto alla perforazione dei micropali", 40, TUTTE_MT,
         ["Sonda di perforazione (micropali, tiranti, sondaggi)", "Motocompressore", "Autocarro con gru",
          "Utensili manuali"], [
             _PERFORAZIONE, _MMC,
             r("Polveri e fibre (silice cristallina respirabile)", 3, 3,
               "Perforazione ad acqua o con aspirazione e abbattimento delle polveri alla bocca del foro "
               "con circolazione ad aria; addetti sopravento; ventilazione forzata nei locali chiusi.",
               DPI_BASE + ", facciale filtrante FFP3"),
             r("Getti e schizzi", 2, 3,
               "Preventer o deviatore alla bocca del foro; scarichi del fluido convogliati; tubi dell'aria "
               "e dell'acqua con fermi anti-colpo di frusta.",
               DPI_BASE + ", visiera protettiva"),
             _FANGO, _SOTTOSERVIZI,
         ]),
    fase("FS.09", FS, "Micropali e tiranti",
         "Iniezione di micropali con miscele cementizie",
         "Confezionamento della miscela cementizia in miscelatore e iniezione nel micropalo: prima la "
         "guaina di riempimento dal fondo, poi le iniezioni ripetute e selettive valvola per valvola con "
         "doppio packer, a pressione e volume controllati. I dati sono registrati per ciascuna valvola.",
         "Addetto all'iniezione dei micropali", 45, TUTTE_MT,
         ["Pompa per malte e iniezioni", "Impastatrice", "Utensili manuali"], [
             _SCHIZZI_INIEZIONE, _CEMENTO,
             r("Polveri e fibre", 3, 2,
               "Carico del cemento da silo con filtro o da sacchi con apertura a bassa altezza; facciale "
               "filtrante per l'addetto al miscelatore.",
               DPI_BASE + ", facciale filtrante FFP2"),
             _MMC, _FANGO,
         ]),
    fase("FS.10", FS, "Micropali e tiranti",
         "Realizzazione, iniezione e tesatura di tiranti di ancoraggio",
         "Perforazione inclinata, inserimento del tirante a trefoli o a barra con guaina, iniezione del "
         "bulbo di ancoraggio e, a maturazione, tesatura con martinetto idraulico e bloccaggio sulla "
         "piastra e sulla trave di ripartizione (UNI EN 1537). Le prove di collaudo seguono il progetto. "
         "Spesso si lavora sulla parete della paratia o del fronte, da banchina di scavo o piattaforma.",
         "Addetto alla realizzazione dei tiranti di ancoraggio", 45, NC_IN + ("Ristrutturazioni",),
         ["Sonda di perforazione (micropali, tiranti, sondaggi)", "Pompa per malte e iniezioni",
          "Martinetto idraulico per tesatura", "Piattaforma di lavoro elevabile"], [
             r("Proiezione di schegge e frammenti", 2, 4,
               "Durante la tesatura nessuno davanti o dietro all'asse del martinetto; schermo di protezione; "
               "manometro tarato e pressioni di progetto; cunei e piastre puliti e integri.",
               DPI_BASE + ", visiera protettiva"),
             _SCHIZZI_INIEZIONE, _PERFORAZIONE,
             r("Caduta dall'alto", 2, 4,
               "Banchine di lavoro in testa alla paratia con parapetto; lavoro da piattaforma con "
               "imbracatura agganciata al cestello.",
               DPI_BASE + ", imbracatura, cordino con assorbitore"),
             _CEMENTO,
         ]),
    # --- Paratie e diaframmi ---
    fase("FS.11", FS, "Paratie e diaframmi",
         "Scavo per fasi di paratie tipo berlinese con posa delle travi di ripartizione",
         "Dopo la realizzazione di micropali o pali accostati e del cordolo di testa, lo scavo a valle "
         "procede per ribassi successivi fino alla quota di ogni ordine di tiranti; si posano le travi di "
         "ripartizione in acciaio, si tesano i tiranti e si protegge il terreno tra i pali con rete e "
         "calcestruzzo proiettato. Si scende al ribasso successivo solo dopo il completamento del precedente.",
         "Addetto allo scavo e al presidio delle paratie berlinesi", 35, NC_RI_IN,
         ["Escavatore", "Miniescavatore", "Saldatrice", "Cannello ossiacetilenico",
          "Piattaforma di lavoro elevabile"], [
             r("Seppellimento e sprofondamento", 2, 4,
               "Rispetto rigoroso della sequenza e delle quote di ribasso di progetto; nessun sovrascavo "
               "sotto l'ordine di tiranti non ancora tesato; distacchi di terreno tra i pali protetti "
               "subito; monitoraggio degli spostamenti della paratia."),
             _FABBRICATI,
             r("Caduta di materiale dall'alto o a livello", 2, 4,
               "Cordolo di testa con parapetto e fermapiede; nessun deposito a monte della paratia; "
               "nessuno al piede durante lavori sopra."),
             r("Radiazioni ottiche", 2, 2,
               "Schermi attorno ai posti di saldatura e taglio; addetti vicini protetti.",
               DPI_BASE + ", schermo per saldatura"),
             _CARICHI_SOSPESI,
         ]),
    fase("FS.12", FS, "Paratie e diaframmi",
         "Diaframmi in c.a. gettati in opera con fanghi di sostegno",
         "Realizzazione dei muretti guida, scavo dei pannelli con benna mordente o idrofresa in presenza "
         "di fanghi bentonitici o polimerici, posa delle gabbie di armatura e dei giunti, getto con tubo "
         "convogliatore e recupero del fango (UNI EN 1538). Il fango è confezionato, dissabbiato e "
         "riciclato in un impianto dedicato.",
         "Addetto alla realizzazione dei diaframmi", 25, NC_IN,
         ["Attrezzatura per scavo di diaframmi (benna mordente o idrofresa)",
          "Impianto di confezionamento e dissabbiatura dei fanghi", "Autogru", "Autobetoniera"], [
             r("Annegamento", 1, 4,
               "Pannelli aperti e vasche del fango protetti con parapetti o coperture; nessun passaggio "
               "lungo i muretti guida senza protezione; salvagente a portata di mano vicino alle vasche.",
               DPI_BASE + ", giubbotto di salvataggio"),
             r("Rischio chimico", 2, 2,
               "Schede di sicurezza di bentonite, polimeri e additivi; dosaggio in circuito chiuso; "
               "lavaggio della pelle a contatto con il fango.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali protettivi"),
             _CARICHI_SOSPESI, _FANGO, _INVESTIMENTO,
         ]),
    # --- Consolidamento dei terreni e sottofondazioni ---
    fase("FS.13", FS, "Consolidamento dei terreni e sottofondazioni",
         "Consolidamento del terreno con jet grouting",
         "Formazione di colonne di terreno consolidato: perforazione fino alla quota di progetto e "
         "risalita dell'asta in rotazione con getti di miscela cementizia ad altissima pressione, anche "
         "con aria o acqua (UNI EN 12716). Il refluo che risale dal foro è convogliato in una fossa di "
         "raccolta e smaltito. Pressioni, portate e velocità di risalita sono registrate.",
         "Addetto al jet grouting", 35, NC_RI_IN,
         ["Impianto per jet grouting", "Escavatore", "Pompa per malte e iniezioni", "Utensili manuali"], [
             r("Getti e schizzi", 2, 4,
               "Nessuno vicino all'ugello fuori terra durante la pressurizzazione: avvio del getto solo "
               "con il monitor nel terreno; tubi ad alta pressione certificati e con fermi anti-colpo di "
               "frusta; arresto di emergenza accessibile; zona interdetta attorno alle linee in pressione. "
               "Un'iniezione cutanea ad alta pressione richiede pronto soccorso chirurgico immediato.",
               DPI_BASE + ", visiera protettiva, indumenti impermeabili"),
             _PERFORAZIONE, _CEMENTO, _FANGO,
             r("Crollo o ribaltamento di strutture", 2, 3,
               "Controllo continuo dello sfogo del refluo per evitare sollevamenti del terreno e delle "
               "strutture vicine; monitoraggio topografico; sospensione al primo segno di sollevamento."),
         ]),
    fase("FS.14", FS, "Consolidamento dei terreni e sottofondazioni",
         "Consolidamento del terreno con iniezioni di miscele o resine",
         "Iniezione nel terreno, attraverso tubi valvolati o lance, di miscele cementizie, silicati o "
         "resine poliuretaniche espandenti, per permeazione o per fratturazione, sotto fondazioni o "
         "pavimentazioni esistenti (UNI EN 12715). Le quantità e le pressioni sono controllate e i "
         "movimenti delle strutture sono monitorati con strumenti di livellazione.",
         "Addetto al consolidamento del terreno con iniezioni", 45, TUTTE_MT,
         ["Sonda di perforazione (micropali, tiranti, sondaggi)", "Martello perforatore (tassellatore)",
          "Pompa per malte e iniezioni", "Utensili manuali"], [
             r("Rischio chimico", 3, 3,
               "Resine e catalizzatori (isocianati) usati secondo le schede di sicurezza, in ambienti "
               "ventilati; nessun addetto sensibilizzato; contenitori chiusi ed etichettati; travasi con "
               "sistemi a circuito chiuso.",
               DPI_BASE + ", guanti in lattice o nitrile, occhiali a maschera, maschera con filtro specifico"),
             _SCHIZZI_INIEZIONE,
             r("Crollo o ribaltamento di strutture", 2, 3,
               "Pressioni di iniezione limitate come da progetto; monitoraggio in tempo reale dei "
               "sollevamenti; nessuno all'interno dei locali soprastanti durante le iniezioni a fratturazione."),
             r("Incendio ed esplosione", 1, 3,
               "Resine lontane da fiamme e fonti di calore; estintore a portata di mano; divieto di fumo."),
         ]),
    fase("FS.15", FS, "Consolidamento dei terreni e sottofondazioni",
         "Sottomurazione di fondazioni esistenti per campioni",
         "Approfondimento o allargamento delle fondazioni di un edificio esistente scavando sotto la "
         "muratura per tratti brevi e alternati, secondo la sequenza di progetto, con puntellatura delle "
         "strutture sovrastanti e getto dei nuovi conci prima di aprire i tratti adiacenti "
         "(art. 119 c. 4). Lo scavo sotto la fondazione è eseguito a mano.",
         "Addetto alla sottomurazione delle fondazioni", 65, ("Ristrutturazioni", "Restauri"),
         ["Miniescavatore", "Utensili manuali", "Martello demolitore", "Puntelli metallici",
          "Casseforme", "Betoniera a bicchiere"], [
             r("Crollo o ribaltamento di strutture", 2, 4,
               "Campioni di lunghezza e sequenza stabilite dal progettista, mai adiacenti contemporaneamente; "
               "puntellature delle murature prima di scavare; getto del concio in giornata o protezione "
               "dello scavo; spie e fessurimetri sulle murature controllati a ogni turno."),
             _SEPPELLIMENTO,
             r("Posture incongrue", 3, 2,
               "Scavo sotto la fondazione con attrezzi a manico corto e spazio sufficiente; pause e "
               "alternanza degli addetti.",
               DPI_BASE + ", ginocchiere"),
             _MMC, _CEMENTO, _SOTTOSERVIZI,
         ]),
]
