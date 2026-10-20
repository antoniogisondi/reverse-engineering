"""Schede d'uso di macchine, attrezzi e opere provvisionali dell'archivio.

Per ogni voce: descrizione, misure prima, durante e dopo l'uso e DPI dell'operatore. Testi
redatti per questo progetto dal Titolo III del D.Lgs. 81/2008 (artt. 70-73 e Allegati V, VI e
VII) e dalla buona pratica di cantiere; vanno adattati alle istruzioni del fabbricante.
"""

from __future__ import annotations

from typing import Any


def _scheda(descrizione: str, prima: list[str], durante: list[str], dopo: list[str], dpi: list[str]) -> dict[str, Any]:
    return {"descrizione": descrizione, "prima": prima, "durante": durante, "dopo": dopo, "dpi": dpi}


_MEZZO_PRIMA = [
    "controllare freni, comandi, luci, avvisatore acustico e segnalatore di retromarcia",
    "verificare che i percorsi siano adatti al peso e all'ingombro del mezzo e lontani dai bordi degli scavi",
    "accertarsi che nessuno sosti nel raggio d'azione",
]
_MEZZO_DURANTE = [
    "segnalare la presenza con il girofaro e procedere a passo d'uomo vicino ai posti di lavoro",
    "farsi guidare da un moviere nelle manovre con scarsa visibilità",
    "non trasportare persone fuori dal posto di guida",
    "spegnere il motore durante il rifornimento",
]
_MEZZO_DOPO = [
    "parcheggiare in area stabile con freno di stazionamento inserito e attrezzi a terra",
    "eseguire pulizia e manutenzione secondo il libretto, annotando le anomalie",
]
_DPI_CONDUCENTE = ["casco (fuori dalla cabina)", "calzature di sicurezza", "guanti (fuori dalla cabina)",
                   "indumenti ad alta visibilità (fuori dalla cabina)", "otoprotettori (se il rumore lo richiede)"]

_ELETTRICO_PRIMA = [
    "verificare l'integrità di cavo, spina e involucro e l'isolamento (doppio isolamento o collegamento a terra)",
    "alimentare da quadro di cantiere con interruttore differenziale",
]
_ELETTRICO_DOPO = ["staccare l'alimentazione e riporre l'utensile pulito", "segnalare i malfunzionamenti"]

SCHEDE: dict[str, dict[str, Any]] = {
    "Escavatore": _scheda(
        "Macchina movimento terra a braccio con benna, cingolata o gommata, per scavi e carico di materiale.",
        _MEZZO_PRIMA + ["verificare l'assenza di sottoservizi e di linee elettriche aeree nell'area di lavoro"],
        _MEZZO_DURANTE + ["non usare la benna per sollevare persone o carichi non agganciati con ganci idonei",
                          "lavorare con stabilizzatori o cingoli su terreno portante"],
        _MEZZO_DOPO + ["abbassare la benna a terra prima di scendere"],
        _DPI_CONDUCENTE),
    "Pala meccanica": _scheda(
        "Macchina movimento terra con benna frontale per scavi superficiali, carico e spostamento di materiali.",
        _MEZZO_PRIMA, _MEZZO_DURANTE + ["trasportare il carico con benna bassa", "non superare la portata"],
        _MEZZO_DOPO + ["abbassare la benna a terra prima di scendere"], _DPI_CONDUCENTE),
    "Autocarro": _scheda(
        "Mezzo per il trasporto di materiali, attrezzature e materiali di risulta.",
        _MEZZO_PRIMA, _MEZZO_DURANTE + ["caricare in modo stabile e senza superare portata e sagoma",
                                        "non azionare il cassone ribaltabile su terreno inclinato"],
        _MEZZO_DOPO, _DPI_CONDUCENTE + ["maschera antipolvere (con lavorazioni polverose)"]),
    "Autobetoniera": _scheda(
        "Mezzo per il trasporto del calcestruzzo dall'impianto di betonaggio al getto.",
        _MEZZO_PRIMA + ["verificare le protezioni degli organi di trasmissione e la scaletta"],
        _MEZZO_DURANTE + ["bloccare la canala durante gli spostamenti", "tenersi lontani dalla canala in rotazione"],
        _MEZZO_DOPO + ["lavare tamburo e canala lontano da scavi e caditoie"],
        _DPI_CONDUCENTE + ["occhiali protettivi (durante lo scarico)"]),
    "Autopompa per calcestruzzo": _scheda(
        "Mezzo con pompa e braccio articolato per il getto del calcestruzzo in quota o a distanza.",
        _MEZZO_PRIMA + ["posizionare gli stabilizzatori su piastre e terreno portante",
                        "verificare la distanza dalle linee elettriche aeree (Allegato IX)"],
        _MEZZO_DURANTE + ["comandare il braccio con l'area sottostante sgombra", "non piegare la tubazione terminale"],
        _MEZZO_DOPO + ["pulire vasca e tubazioni con la pompa ferma"],
        _DPI_CONDUCENTE + ["occhiali protettivi"]),
    "Gru a torre": _scheda(
        "Apparecchio di sollevamento fisso per la movimentazione dei materiali in cantiere.",
        ["verificare basamento, zavorre, messa a terra, limitatori e freni",
         "controllare funi, ganci con dispositivo di chiusura e verifiche periodiche (Allegato VII)",
         "accertarsi che non ci siano interferenze con altre gru o linee elettriche"],
        ["imbracare i carichi con accessori idonei e verificati", "non passare con il carico sopra le persone",
         "sospendere il lavoro con vento oltre il limite del fabbricante", "comunicare con il segnalatore a terra"],
        ["lasciare la gru libera di ruotare (bandiera) e il gancio alto senza carico", "togliere l'alimentazione"],
        ["casco", "calzature di sicurezza", "guanti"]),
    "Autogru": _scheda(
        "Gru montata su autocarro per sollevamenti e montaggi.",
        _MEZZO_PRIMA + ["estendere gli stabilizzatori su piastre e terreno portante",
                        "verificare il diagramma di carico e le linee elettriche aeree"],
        ["delimitare l'area sotto il carico", "non superare la portata per lo sbraccio usato",
         "sospendere il lavoro con vento forte"],
        _MEZZO_DOPO + ["rientrare braccio e stabilizzatori prima degli spostamenti"],
        _DPI_CONDUCENTE),
    "Rullo compattatore": _scheda(
        "Macchina per la compattazione di terreni e conglomerati.",
        _MEZZO_PRIMA, _MEZZO_DURANTE + ["tenersi lontani dai bordi di scavi e rilevati"],
        _MEZZO_DOPO, _DPI_CONDUCENTE),
    "Vibrofinitrice": _scheda(
        "Macchina per la stesa del conglomerato bituminoso.",
        _MEZZO_PRIMA + ["verificare i dispositivi di arresto d'emergenza e le protezioni delle coclee"],
        _MEZZO_DURANTE + ["non avvicinarsi alla coclea e al banco riscaldato", "lavorare sopravvento rispetto ai fumi"],
        _MEZZO_DOPO, _DPI_CONDUCENTE + ["calzature di sicurezza resistenti al calore", "facciale filtrante FFP2"]),
    "Piattaforma di lavoro elevabile": _scheda(
        "Macchina con cestello per lavori in quota (PLE).",
        ["verificare comandi, dispositivi di emergenza e parapetti del cestello",
         "posizionare la macchina su terreno piano e portante con gli stabilizzatori",
         "operatore con formazione specifica (Accordo Stato-Regioni 22/02/2012)"],
        ["agganciare l'imbracatura agli attacchi del cestello", "non sporgersi né salire sui parapetti",
         "non superare la portata e non usare la PLE come apparecchio di sollevamento",
         "delimitare l'area sottostante"],
        ["riportare il cestello a riposo", "togliere la chiave e segnalare le anomalie"],
        ["casco con sottogola", "imbracatura", "cordino con assorbitore", "calzature di sicurezza", "guanti"]),
    "Betoniera a bicchiere": _scheda(
        "Macchina per l'impasto di malte e calcestruzzi in cantiere.",
        _ELETTRICO_PRIMA + ["verificare le protezioni di pignone, corona e cinghie",
                            "posizionarla in piano, su base stabile, sotto tettoia se vicina alla gru"],
        ["non introdurre mani o attrezzi nel bicchiere in rotazione", "non rimuovere le protezioni"],
        ["pulire il bicchiere a macchina ferma e scollegata"] + _ELETTRICO_DOPO,
        ["guanti", "calzature di sicurezza", "maschera antipolvere", "otoprotettori", "occhiali protettivi"]),
    "Sega circolare": _scheda(
        "Macchina da banco per il taglio del legno.",
        _ELETTRICO_PRIMA + ["verificare cuffia registrabile, coltello divisore e spingitoio",
                            "verificare il dispositivo contro il riavvio automatico"],
        ["usare lo spingitoio per i pezzi piccoli", "non rimuovere la cuffia", "non indossare indumenti svolazzanti"],
        ["pulire il banco dalla segatura"] + _ELETTRICO_DOPO,
        ["occhiali protettivi", "otoprotettori", "maschera antipolvere", "calzature di sicurezza"]),
    "Smerigliatrice angolare": _scheda(
        "Utensile portatile a disco per tagliare e smerigliare.",
        _ELETTRICO_PRIMA + ["montare un disco adatto al materiale e al numero di giri, con il carter"],
        ["impugnare con due mani e lavorare in posizione stabile", "non usare il disco da taglio per smerigliare",
         "allontanare materiali infiammabili dalle scintille"],
        _ELETTRICO_DOPO,
        ["occhiali protettivi", "visiera protettiva", "otoprotettori", "guanti", "maschera antipolvere"]),
    "Martello demolitore": _scheda(
        "Utensile elettrico o pneumatico per demolizioni e rotture.",
        _ELETTRICO_PRIMA + ["scegliere utensili a bassa emissione di vibrazioni con impugnature antivibranti"],
        ["lavorare a umido per contenere le polveri", "alternare gli addetti per limitare l'esposizione a vibrazioni"],
        _ELETTRICO_DOPO,
        ["otoprotettori", "guanti antivibrazioni", "occhiali protettivi", "facciale filtrante FFP2",
         "calzature di sicurezza"]),
    "Trapano elettrico": _scheda(
        "Utensile portatile per forare legno, metallo e murature.",
        _ELETTRICO_PRIMA + ["verificare il fissaggio della punta"],
        ["non forzare l'utensile", "verificare l'assenza di cavi e tubazioni nel punto di foratura"],
        _ELETTRICO_DOPO, ["occhiali protettivi", "guanti", "otoprotettori"]),
    "Saldatrice": _scheda(
        "Saldatrice elettrica ad arco per carpenteria metallica.",
        _ELETTRICO_PRIMA + ["allontanare materiali infiammabili e tenere un estintore a portata di mano"],
        ["schermare la zona per proteggere gli altri lavoratori dalle radiazioni",
         "aspirare o ventilare i fumi nei luoghi chiusi"],
        ["controllare che non restino focolai"] + _ELETTRICO_DOPO,
        ["schermo per saldatura", "guanti per saldatura", "grembiule per saldatura", "calzature di sicurezza"]),
    "Cannello a gas": _scheda(
        "Cannello alimentato a GPL per guaine bituminose e lavori a caldo.",
        ["verificare tubo, raccordi e valvole antiritorno", "tenere la bombola in piedi, lontana dalla fiamma",
         "predisporre un estintore"],
        ["non lasciare il cannello acceso appoggiato", "lavorare sopravvento"],
        ["chiudere la valvola della bombola", "controllare l'assenza di focolai prima di lasciare la zona"],
        ["guanti", "calzature di sicurezza", "indumenti protettivi"]),
    "Ponteggio metallico fisso": _scheda(
        "Opera provvisionale per i lavori in quota sulle facciate, montata secondo il PiMUS.",
        ["verificare autorizzazione ministeriale, PiMUS e, se dovuto, progetto (art. 133)",
         "controllare ancoraggi, basette, impalcati, parapetti e fermapiede (Allegato XIX)"],
        ["non rimuovere parapetti o ancoraggi", "non accumulare materiali sugli impalcati",
         "salire solo dalle scale interne"],
        ["verificare il ponteggio dopo vento forte o lunga sospensione dei lavori"],
        ["casco", "calzature di sicurezza", "guanti", "attrezzatura anticaduta (montaggio e smontaggio)"]),
    "Trabattello": _scheda(
        "Ponte su ruote per lavori in quota di breve durata.",
        ["montarlo secondo le istruzioni del fabbricante, con parapetti e stabilizzatori",
         "bloccare le ruote e verificare il piano di appoggio"],
        ["non spostarlo con persone sopra", "salire dall'interno", "non usare scale o pedane sull'impalcato"],
        ["smontarlo o metterlo in sicurezza a fine lavoro"], ["casco", "calzature di sicurezza", "guanti"]),
    "Scala a mano": _scheda(
        "Scala semplice o doppia per accessi e lavori brevi in quota.",
        ["verificare piedini antiscivolo, pioli e catena di sicurezza (scale doppie)",
         "appoggiarla su piano stabile, sporgente almeno 1 m oltre il piano di arrivo"],
        ["salire e scendere con il viso verso la scala", "una persona alla volta", "non sporgersi lateralmente"],
        ["riporla in luogo asciutto e segnalare i difetti"], ["casco", "calzature di sicurezza", "guanti"]),
    "Utensili manuali": _scheda(
        "Attrezzi d'uso comune: martelli, pinze, cazzuole, badili, piccozze, seghe a mano.",
        ["verificare che manici e parti taglienti siano integri e ben fissati"],
        ["usare l'attrezzo adatto al lavoro", "tenere sgombre le zone di passaggio",
         "riporre gli attrezzi nelle apposite custodie o fissarli quando si lavora in quota"],
        ["pulire e riporre gli attrezzi", "sostituire quelli danneggiati"],
        ["casco", "occhiali protettivi", "guanti", "calzature di sicurezza"]),
}


def _r(descrizione: str, p: int, d: int, misure: str, dpi: str) -> dict[str, Any]:
    return {"descrizione": descrizione, "probabilita": p, "danno": d, "misure": misure, "dpi": dpi}


_DPI = "Casco, scarpe antinfortunistiche, guanti, indumenti ad alta visibilità"

# Nuove macchine e attrezzi per la preparazione delle aree di cantiere.
NUOVE: dict[str, dict[str, Any]] = {
    "Trattore": {"tipo": "Macchina", "rischi": [
        _r("Ribaltamento del trattore", 2, 4, "Telaio di protezione (ROPS) e cintura allacciata; evitare pendenze "
           "trasversali e bordi di scarpate; zavorre secondo il fabbricante.", _DPI),
        _r("Investimento di persone a terra", 2, 4, "Nessuno nel raggio d'azione; segnalazione acustica e luminosa.", _DPI),
        _r("Trascinamento dall'albero cardanico", 2, 4, "Albero cardanico protetto per tutta la lunghezza; "
           "attacco e distacco di attrezzi a motore spento.", _DPI),
        _r("Rumore", 3, 2, "Valutazione dell'esposizione; cabina chiusa; manutenzione dei silenziatori.",
           _DPI + ", otoprotettori"),
        _r("Vibrazioni al corpo intero", 3, 2, "Sedile ammortizzato regolato; velocità moderata su terreni sconnessi.", _DPI),
    ]},
    "Autocarro con gru": {"tipo": "Macchina", "rischi": [
        _r("Caduta del carico sospeso", 2, 4, "Imbracature verificate; ganci con chiusura; area sotto il carico "
           "delimitata; operatore formato (Accordo Stato-Regioni 22/02/2012).", _DPI),
        _r("Ribaltamento durante il sollevamento", 2, 4, "Stabilizzatori estesi su terreno portante; rispetto del "
           "diagramma di carico.", _DPI),
        _r("Investimento di persone a terra", 2, 4, "Moviere nelle manovre; nessuno nel raggio d'azione.", _DPI),
        _r("Elettrocuzione per contatto con linee aeree", 1, 4, "Distanze dell'Allegato IX dalle linee elettriche.", _DPI),
    ]},
    "Motosega": {"tipo": "Attrezzo", "rischi": [
        _r("Tagli per contatto con la catena e contraccolpo", 3, 4, "Motosega con freno catena e fermo di "
           "sicurezza; addetto formato; impugnatura salda con due mani; mai oltre l'altezza delle spalle.",
           _DPI + ", pantaloni e guanti antitaglio, visiera protettiva"),
        _r("Caduta della pianta o dei rami", 2, 4, "Direzione di caduta pianificata, via di fuga libera, "
           "area interdetta per un raggio pari a due volte l'altezza della pianta.", _DPI),
        _r("Rumore", 4, 2, "Valutazione dell'esposizione; turnazione degli addetti.", _DPI + ", otoprotettori"),
        _r("Vibrazioni al sistema mano-braccio", 3, 2, "Motosega con sistema antivibrante; pause.",
           _DPI + ", guanti antivibrazione"),
        _r("Incendio durante il rifornimento", 1, 3, "Rifornimento a motore freddo, lontano da fiamme.", _DPI),
    ]},
    "Decespugliatore a motore": {"tipo": "Attrezzo", "rischi": [
        _r("Proiezione di sassi e frammenti", 3, 3, "Carter di protezione; nessuno entro 15 m durante l'uso.",
           _DPI + ", visiera protettiva"),
        _r("Tagli per contatto con l'organo di taglio", 2, 3, "Arresto del motore prima di liberare l'organo di "
           "taglio; imbracatura di sostegno.", _DPI + ", ghette"),
        _r("Rumore", 4, 2, "Valutazione dell'esposizione; turnazione degli addetti.", _DPI + ", otoprotettori"),
        _r("Vibrazioni al sistema mano-braccio", 3, 2, "Impugnature antivibranti; pause.",
           _DPI + ", guanti antivibrazione"),
    ]},
}

SCHEDE.update({
    "Trattore": _scheda(
        "Macchina agricola per il traino di rimorchi e l'uso di attrezzi portati, anche per la pulizia delle aree.",
        _MEZZO_PRIMA + ["verificare il telaio di protezione (ROPS), la cintura e le protezioni del cardano"],
        _MEZZO_DURANTE + ["non percorrere pendenze trasversali", "attaccare gli attrezzi solo a motore spento"],
        _MEZZO_DOPO + ["abbassare gli attrezzi portati a terra"],
        _DPI_CONDUCENTE),
    "Autocarro con gru": _scheda(
        "Autocarro con gru idraulica per il carico, lo scarico e il sollevamento di materiali.",
        _MEZZO_PRIMA + ["estendere gli stabilizzatori su terreno portante",
                        "verificare il diagramma di carico e le linee elettriche aeree"],
        ["delimitare l'area sotto il carico", "manovrare dalla postazione di comando con piena visibilità",
         "non sollevare persone"],
        _MEZZO_DOPO + ["richiudere la gru in posizione di trasporto prima di muoversi"],
        _DPI_CONDUCENTE),
    "Motosega": _scheda(
        "Attrezzo portatile a catena per il taglio di alberi e rami.",
        ["verificare freno catena, fermo dell'acceleratore, tensione e affilatura della catena",
         "avviare la motosega a terra, con catena libera"],
        ["impugnare con due mani, in posizione stabile, con la via di fuga libera",
         "non tagliare con la punta della barra", "non lavorare da soli né sopra le spalle"],
        ["spegnere e trasportare con il coprilama", "rifornire a motore freddo"],
        ["casco con visiera protettiva", "otoprotettori", "guanti antitaglio", "pantaloni antitaglio",
         "calzature di sicurezza"]),
    "Decespugliatore a motore": _scheda(
        "Attrezzo portatile a filo o a lama per il taglio di erba, arbusti e vegetazione.",
        ["verificare carter, organo di taglio e imbracatura di sostegno",
         "rimuovere sassi e oggetti dalla zona da trattare"],
        ["tenere a distanza le altre persone", "spegnere il motore per liberare l'organo di taglio"],
        ["pulire l'attrezzo a motore spento", "rifornire a motore freddo"],
        ["visiera protettiva", "otoprotettori", "guanti", "ghette di protezione", "calzature di sicurezza"]),
})


def testo_misure(scheda: dict[str, Any]) -> str:
    """Misure d'uso in un unico testo, divise in prima, durante e dopo l'uso."""
    parti = []
    for chiave, titolo in (("prima", "Prima dell'uso"), ("durante", "Durante l'uso"), ("dopo", "Dopo l'uso")):
        if scheda.get(chiave):
            voci = "; ".join(f"{n}) {v}" for n, v in enumerate(scheda[chiave], 1))
            parti.append(f"{titolo}: {voci}.")
    return "\n".join(parti)
