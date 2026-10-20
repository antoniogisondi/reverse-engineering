"""Archivio di base delle lavorazioni, delle macchine e degli attrezzi.

Contenuti redatti per questo progetto a partire dal D.Lgs. 81/2008 e dalla
buona pratica di cantiere. Vanno sempre verificati e adattati dal
coordinatore al cantiere specifico.
"""

from __future__ import annotations

from typing import Any

from sicurcantiere.archivio_attrezzature import NUOVE as NUOVE_ATTREZZATURE
from sicurcantiere.archivio_attrezzature import SCHEDE

DPI_BASE = "Casco, scarpe antinfortunistiche, guanti, indumenti ad alta visibilità"

# Tipologie di intervento: filtrano l'archivio nella finestra di importazione.
TIPOLOGIE = ["Nuove costruzioni", "Ristrutturazioni", "Opere infrastrutturali", "Restauri"]

# Categorie (macrogruppi di lavorazioni) in ordine di presentazione.
CATEGORIE = [
    "Allestimento e smobilizzo del cantiere",
    "Demolizioni e rimozioni",
    "Lavori di movimento terra",
    "Lavori strutturali",
    "Opere edili in copertura",
    "Opere edili in facciata",
    "Opere edili interne",
    "Impianti tecnici per edifici",
    "Lavori di urbanizzazione e stradali",
    "Ripristini e restauri",
]

# Codice della lavorazione -> categoria e tipologie in cui compare.
_CLASSIFICAZIONE: dict[str, tuple[str, tuple[str, ...]]] = {
    "AL": ("Allestimento e smobilizzo del cantiere", tuple(TIPOLOGIE)),
    "SM": ("Allestimento e smobilizzo del cantiere", tuple(TIPOLOGIE)),
    "NC.01": ("Lavori di movimento terra", ("Nuove costruzioni", "Ristrutturazioni", "Opere infrastrutturali")),
    "NC.02": ("Lavori strutturali", ("Nuove costruzioni", "Ristrutturazioni")),
    "NC.03": ("Lavori strutturali", ("Nuove costruzioni", "Ristrutturazioni")),
    "NC.04": ("Lavori strutturali", ("Nuove costruzioni", "Ristrutturazioni")),
    "NC.05": ("Opere edili in facciata", ("Nuove costruzioni", "Ristrutturazioni")),
    "NC.06": ("Opere edili in copertura", ("Nuove costruzioni", "Ristrutturazioni")),
    "NC.07": ("Impianti tecnici per edifici", ("Nuove costruzioni", "Ristrutturazioni", "Restauri")),
    "NC.08": ("Impianti tecnici per edifici", ("Nuove costruzioni", "Ristrutturazioni", "Restauri")),
    "NC.09": ("Opere edili interne", ("Nuove costruzioni", "Ristrutturazioni", "Restauri")),
    "NC.10": ("Opere edili interne", ("Nuove costruzioni", "Ristrutturazioni", "Restauri")),
    "NC.11": ("Opere edili interne", ("Nuove costruzioni", "Ristrutturazioni", "Restauri")),
    "NC.12": ("Opere edili interne", ("Nuove costruzioni", "Ristrutturazioni")),
    "RI.01": ("Demolizioni e rimozioni", ("Ristrutturazioni", "Restauri")),
    "RI.02": ("Demolizioni e rimozioni", ("Ristrutturazioni", "Restauri")),
    "RI.03": ("Lavori strutturali", ("Ristrutturazioni", "Restauri")),
    "RI.04": ("Opere edili in copertura", ("Ristrutturazioni", "Restauri")),
    "RI.05": ("Opere edili in facciata", ("Ristrutturazioni",)),
    "IN.01": ("Lavori di movimento terra", ("Opere infrastrutturali", "Nuove costruzioni")),
    "IN.02": ("Lavori di urbanizzazione e stradali", ("Opere infrastrutturali", "Nuove costruzioni")),
    "IN.03": ("Lavori di urbanizzazione e stradali", ("Opere infrastrutturali",)),
    "IN.04": ("Lavori di urbanizzazione e stradali", ("Opere infrastrutturali",)),
    "RS.01": ("Ripristini e restauri", ("Restauri", "Ristrutturazioni")),
    "RS.02": ("Ripristini e restauri", ("Restauri", "Ristrutturazioni")),
    "RS.03": ("Opere edili in copertura", ("Restauri",)),
}


def _r(descrizione: str, p: int, d: int, misure: str, dpi: str = DPI_BASE) -> dict[str, Any]:
    return {"descrizione": descrizione, "probabilita": p, "danno": d, "misure": misure, "dpi": dpi}


# --- Macchine e attrezzi: i loro rischi si aggiungono a quelli della fase ---

_RUMORE = _r("Rumore", 3, 2, "Valutazione dell'esposizione; macchine silenziate; rotazione degli addetti.",
             DPI_BASE + ", otoprotettori")
_VIBRAZIONI_MB = _r("Vibrazioni al sistema mano-braccio", 3, 2,
                    "Utensili con impugnature antivibranti; pause e rotazione degli addetti.",
                    DPI_BASE + ", guanti antivibrazione")
_INVESTIMENTO = _r("Investimento di persone a terra", 2, 4,
                   "Segnalatore acustico e luminoso di retromarcia; nessuno nel raggio d'azione; percorsi separati.")
_RIBALTAMENTO = _r("Ribaltamento del mezzo", 2, 4,
                   "Operatore formato e abilitato; terreno stabile; cintura di sicurezza; cabina con protezione ROPS.")

ATTREZZATURE: dict[str, dict[str, Any]] = {
    "Escavatore": {"tipo": "Macchina", "rischi": [_INVESTIMENTO, _RIBALTAMENTO, _RUMORE]},
    "Pala meccanica": {"tipo": "Macchina", "rischi": [_INVESTIMENTO, _RIBALTAMENTO, _RUMORE]},
    "Autocarro": {"tipo": "Macchina", "rischi": [
        _INVESTIMENTO,
        _r("Caduta di materiale dal cassone", 2, 3, "Carico ben distribuito e fissato; non superare la portata."),
    ]},
    "Autobetoniera": {"tipo": "Macchina", "rischi": [
        _INVESTIMENTO,
        _r("Schizzi di calcestruzzo", 3, 1, "Mantenersi a distanza dalla canala durante lo scarico.",
           DPI_BASE + ", occhiali"),
    ]},
    "Autopompa per calcestruzzo": {"tipo": "Macchina", "rischi": [
        _INVESTIMENTO,
        _r("Ribaltamento per cedimento degli stabilizzatori", 2, 4,
           "Stabilizzatori su piastre di ripartizione e terreno portante; verifica delle linee aeree."),
        _r("Colpo di frusta della tubazione terminale", 2, 3,
           "Guidare il terminale solo con la pompa ferma; nessuno sotto il braccio."),
    ]},
    "Gru a torre": {"tipo": "Macchina", "rischi": [
        _r("Caduta del carico sospeso", 2, 4,
           "Imbracature verificate; ganci con chiusura di sicurezza; interdizione dell'area sotto i carichi; "
           "gruista abilitato; verifiche periodiche."),
        _r("Interferenza con altre gru o linee elettriche", 1, 4,
           "Limitatori di rotazione; distanze dall'Allegato IX; procedura di coordinamento tra gruisti."),
    ]},
    "Autogru": {"tipo": "Macchina", "rischi": [
        _r("Caduta del carico sospeso", 2, 4, "Imbracature verificate; interdizione dell'area sotto i carichi."),
        _r("Ribaltamento", 2, 4, "Stabilizzatori estesi su terreno portante; rispetto del diagramma di carico."),
    ]},
    "Rullo compattatore": {"tipo": "Macchina", "rischi": [_INVESTIMENTO, _RIBALTAMENTO, _RUMORE,
        _r("Vibrazioni al corpo intero", 3, 2, "Sedile ammortizzato; limitare il tempo di esposizione.")]},
    "Vibrofinitrice": {"tipo": "Macchina", "rischi": [_INVESTIMENTO,
        _r("Esposizione a fumi di bitume e calore", 3, 2,
           "Lavorare sopravvento; idratazione e pause nelle ore calde.",
           DPI_BASE + ", mascherina per vapori organici")]},
    "Piattaforma di lavoro elevabile": {"tipo": "Macchina", "rischi": [
        _r("Caduta dall'alto dal cestello", 2, 4,
           "Operatore formato (accordo Stato-Regioni); imbracatura agganciata al cestello; stabilizzatori.",
           DPI_BASE + ", imbracatura con cordino corto"),
        _RIBALTAMENTO,
    ]},
    "Betoniera a bicchiere": {"tipo": "Attrezzo", "rischi": [
        _r("Trascinamento negli organi in movimento", 2, 3, "Protezioni di pignone e corona; arresto prima della pulizia."),
        _r("Elettrocuzione", 1, 4, "Collegamento a quadro con differenziale; cavi integri e a norma."),
    ]},
    "Sega circolare": {"tipo": "Attrezzo", "rischi": [
        _r("Tagli e amputazioni", 2, 4, "Cuffia di protezione registrabile; coltello divisore; spingitoio."),
        _r("Proiezione di schegge", 3, 2, "Schermo di protezione.", DPI_BASE + ", occhiali"),
        _RUMORE,
    ]},
    "Smerigliatrice angolare": {"tipo": "Attrezzo", "rischi": [
        _r("Proiezione di schegge e rottura del disco", 3, 3,
           "Disco idoneo al materiale e al numero di giri; carter di protezione.",
           DPI_BASE + ", occhiali o visiera"),
        _RUMORE, _VIBRAZIONI_MB,
    ]},
    "Martello demolitore": {"tipo": "Attrezzo", "rischi": [
        _VIBRAZIONI_MB, _RUMORE,
        _r("Polveri", 3, 2, "Bagnatura delle superfici.", DPI_BASE + ", mascherina FFP2"),
    ]},
    "Trapano elettrico": {"tipo": "Attrezzo", "rischi": [
        _r("Elettrocuzione", 1, 3, "Utensile a doppio isolamento; cavi integri."),
        _r("Proiezione di frammenti", 2, 2, "Punte idonee al materiale; pezzo da forare bloccato.",
           DPI_BASE + ", occhiali"),
    ]},
    "Saldatrice": {"tipo": "Attrezzo", "rischi": [
        _r("Radiazioni ottiche e fumi di saldatura", 3, 2, "Aspirazione localizzata; schermi.",
           DPI_BASE + ", maschera per saldatura, guanti da saldatore"),
        _r("Incendio", 2, 3, "Allontanare i materiali combustibili; estintore a portata di mano."),
    ]},
    "Cannello a gas": {"tipo": "Attrezzo", "rischi": [
        _r("Ustioni e incendio", 2, 3, "Bombola lontana dalla fiamma; valvola contro il ritorno di fiamma; estintore."),
    ]},
    "Ponteggio metallico fisso": {"tipo": "Opera provvisionale", "rischi": [
        _r("Caduta dall'alto", 2, 4, "Parapetti completi e tavole fermapiede; impalcati senza vuoti; verifiche periodiche."),
    ]},
    "Trabattello": {"tipo": "Opera provvisionale", "rischi": [
        _r("Ribaltamento e caduta dall'alto", 2, 3,
           "Montaggio secondo il manuale del fabbricante; stabilizzatori; ruote bloccate; nessuno sopra durante lo spostamento."),
    ]},
    "Scala a mano": {"tipo": "Opera provvisionale", "rischi": [
        _r("Caduta dall'alto", 3, 3, "Scale conformi con piedini antiscivolo, vincolate in sommità; sporgere di 1 m oltre lo sbarco."),
    ]},
    "Utensili manuali": {"tipo": "Attrezzo", "rischi": [
        _r("Tagli, abrasioni, contusioni", 3, 1, "Utensili in buono stato e adatti al lavoro."),
    ]},
}


ATTREZZATURE.update(NUOVE_ATTREZZATURE)
for _nome, _voce in ATTREZZATURE.items():
    _voce["scheda"] = SCHEDE[_nome]


def _lav(codice: str, descrizione: str, incidenza: float,
         attrezzature: list[str], rischi: list[dict[str, Any]], gruppo: str = "", dettaglio: str = "",
         addetto: str = "") -> dict[str, Any]:
    for nome in attrezzature:
        assert nome in ATTREZZATURE, nome
    categoria, tipologie = _CLASSIFICAZIONE.get(codice) or _CLASSIFICAZIONE[codice[:2]]
    return {
        "categoria": categoria,
        "tipologie": tipologie,
        "gruppo": gruppo,
        "dettaglio": dettaglio,
        "addetto": addetto,
        "codice": codice,
        "descrizione": descrizione,
        "incidenza_manodopera": incidenza,
        "attrezzature": attrezzature,
        "rischi": rischi,
    }


_MMC = _r("Movimentazione manuale dei carichi", 3, 2,
          "Carichi oltre 25 kg movimentati da due persone o con mezzi meccanici; formazione (art. 169).")
_CADUTA_ALTO = _r("Caduta dall'alto", 3, 4,
                  "Opere provvisionali conformi; parapetti sui bordi; dove non possibili, sistemi anticaduta.",
                  DPI_BASE + ", imbracatura con cordino e assorbitore")
_CADUTA_MATERIALE = _r("Caduta di materiale dall'alto", 3, 3,
                       "Delimitare l'area sottostante; tavole fermapiede; sollevamento con mezzi idonei.")
_POLVERI = _r("Polveri", 3, 2, "Bagnatura; aspirazione; taglio a umido.",
              DPI_BASE + ", mascherina FFP2, occhiali")

LAVORAZIONI: list[dict[str, Any]] = [
    # --- Allestimento e smobilizzo ---
    _lav("AL.01", "Allestimento e recinzione del cantiere", 50, ["Autocarro", "Utensili manuali"], [
        _r("Investimento da mezzi in manovra", 2, 4,
           "Delimitare le aree di manovra; segnaletica; moviere a terra durante le manovre in retromarcia."),
        _MMC,
    ]),
    _lav("AL.02", "Montaggio e smontaggio di ponteggio metallico fisso", 70,
         ["Autocarro", "Utensili manuali"], [
        _r("Caduta dall'alto durante il montaggio", 3, 4,
           "Montaggio secondo PiMUS e autorizzazione ministeriale; lavoratori formati (Allegato XXI); "
           "sistemi anticaduta agganciati a punti sicuri.",
           DPI_BASE + ", imbracatura con doppio cordino e assorbitore"),
        _CADUTA_MATERIALE,
        _r("Elettrocuzione per vicinanza a linee aeree", 1, 4,
           "Rispettare le distanze dell'Allegato IX; se non possibile chiedere il distacco all'ente gestore."),
    ]),
    _lav("AL.03", "Installazione della gru a torre", 40, ["Autogru", "Utensili manuali"], [
        _CADUTA_ALTO, _CADUTA_MATERIALE,
        _r("Cedimento del basamento", 1, 4, "Basamento calcolato da tecnico abilitato; verifica del terreno."),
    ]),
    _lav("AL.04", "Impianto elettrico e di terra del cantiere", 60, ["Trapano elettrico", "Utensili manuali"], [
        _r("Elettrocuzione", 2, 4,
           "Quadri ASC certificati; interruttori differenziali; impianto di terra verificato; "
           "impresa abilitata con dichiarazione di conformità.",
           DPI_BASE + ", guanti isolanti"),
    ]),
    _lav("SM.01", "Smobilizzo del cantiere", 50, ["Autocarro", "Utensili manuali"], [
        _r("Investimento da mezzi in manovra", 2, 4, "Moviere durante le manovre; area delimitata."),
        _MMC,
    ]),
    # --- Nuove costruzioni ---
    _lav("NC.01", "Scavo di sbancamento e a sezione aperta", 25, ["Escavatore", "Autocarro"], [
        _r("Seppellimento per franamento delle pareti", 2, 4,
           "Pendenza delle pareti adeguata al terreno o armature; nessun deposito sul ciglio; verifica dopo le piogge."),
        _r("Caduta nello scavo", 3, 3, "Parapetti o delimitazione del ciglio; accessi con scale vincolate."),
        _r("Contatto con sottoservizi", 2, 4,
           "Rilievo preventivo dei sottoservizi presso gli enti gestori; scavo a mano in prossimità."),
    ]),
    _lav("NC.02", "Fondazioni in cemento armato", 35,
         ["Autobetoniera", "Autopompa per calcestruzzo", "Sega circolare", "Utensili manuali"], [
        _r("Punture e tagli da ferri di armatura", 3, 2, "Proteggere le estremità dei ferri di ripresa."),
        _r("Contatto con il calcestruzzo (dermatiti)", 3, 2, "Evitare il contatto con la pelle; lavaggio immediato.",
           DPI_BASE + ", stivali e guanti impermeabili"),
        _r("Caduta nello scavo di fondazione", 2, 3, "Passerelle con parapetto; ciglio delimitato."),
    ]),
    _lav("NC.03", "Strutture in elevazione in cemento armato", 40,
         ["Gru a torre", "Autopompa per calcestruzzo", "Sega circolare", "Ponteggio metallico fisso"], [
        _CADUTA_ALTO, _CADUTA_MATERIALE,
        _r("Crollo delle casseforme o dei puntelli", 2, 4,
           "Puntellature secondo progetto; disarmo solo dopo l'autorizzazione del direttore dei lavori."),
        _r("Vibrazioni e rumore da vibratore per calcestruzzo", 3, 2, "Rotazione degli addetti.",
           DPI_BASE + ", otoprotettori"),
    ]),
    _lav("NC.04", "Solai in latero-cemento", 45,
         ["Gru a torre", "Autopompa per calcestruzzo", "Ponteggio metallico fisso"], [
        _r("Caduta dall'alto attraverso il solaio o dai bordi", 3, 4,
           "Sottopalchi o reti anticaduta; parapetti perimetrali; non camminare sulle pignatte.",
           DPI_BASE + ", imbracatura"),
        _CADUTA_MATERIALE,
    ]),
    _lav("NC.05", "Murature di tamponamento in laterizio", 50,
         ["Betoniera a bicchiere", "Ponteggio metallico fisso", "Utensili manuali"], [
        _r("Caduta dall'alto", 2, 4, "Lavorare da ponteggio o ponti su cavalletti conformi."),
        _MMC, _POLVERI,
    ]),
    _lav("NC.06", "Copertura a falde", 45,
         ["Gru a torre", "Sega circolare", "Ponteggio metallico fisso"], [
        _r("Caduta dall'alto dal bordo e attraverso la copertura", 3, 4,
           "Ponteggio con mantovana; camminamenti sulle superfici non portanti; linee vita.",
           DPI_BASE + ", imbracatura con cordino"),
        _CADUTA_MATERIALE,
        _r("Condizioni climatiche avverse", 3, 2, "Sospendere i lavori con vento forte, pioggia o ghiaccio."),
    ]),
    _lav("NC.07", "Impianti idrico-sanitari e di riscaldamento", 45,
         ["Cannello a gas", "Trapano elettrico", "Scala a mano"], [
        _r("Incendio", 1, 4, "Allontanare i materiali infiammabili; controllo dell'area a fine lavoro."),
        _MMC,
    ]),
    _lav("NC.08", "Impianto elettrico dell'edificio", 55,
         ["Trapano elettrico", "Smerigliatrice angolare", "Scala a mano"], [
        _r("Elettrocuzione", 2, 4, "Lavorare fuori tensione; sezionamento e blocco dei quadri; verifica di assenza di tensione."),
        _POLVERI,
    ]),
    _lav("NC.09", "Intonaci interni ed esterni", 60,
         ["Betoniera a bicchiere", "Trabattello", "Ponteggio metallico fisso"], [
        _r("Caduta dall'alto da ponti su cavalletti o trabattelli", 2, 3, "Opere provvisionali conformi e verificate."),
        _r("Schizzi di malta negli occhi", 3, 2, "Non lavorare sopra la testa senza protezione degli occhi.",
           DPI_BASE + ", occhiali"),
    ]),
    _lav("NC.10", "Pavimenti e rivestimenti", 50, ["Smerigliatrice angolare", "Utensili manuali"], [
        _r("Posture incongrue (lavoro in ginocchio)", 4, 1, "Pause; alternanza delle attività.", DPI_BASE + ", ginocchiere"),
        _r("Contatto con adesivi e prodotti chimici", 2, 2, "Consultare le schede di sicurezza; aerare i locali."),
        _POLVERI,
    ]),
    _lav("NC.11", "Tinteggiature", 65, ["Trabattello", "Scala a mano"], [
        _r("Caduta dall'alto", 2, 3, "Trabattelli e scale conformi."),
        _r("Inalazione di vapori e contatto con prodotti chimici", 2, 2,
           "Consultare le schede di sicurezza; ventilazione dei locali.", DPI_BASE + ", mascherina, occhiali"),
    ]),
    _lav("NC.12", "Serramenti e opere in ferro", 40,
         ["Saldatrice", "Smerigliatrice angolare", "Trapano elettrico"], [
        _MMC, _CADUTA_ALTO,
    ]),
    # --- Ristrutturazioni ---
    _lav("RI.01", "Demolizioni parziali di murature e tramezzi", 55,
         ["Martello demolitore", "Autocarro", "Utensili manuali"], [
        _r("Crollo di strutture", 2, 4,
           "Programma delle demolizioni (art. 151); puntellamenti; procedere dall'alto verso il basso."),
        _r("Polveri", 4, 2, "Bagnare le macerie; canali di scarico chiusi.", DPI_BASE + ", mascherina FFP3, occhiali"),
        _r("Presenza di amianto", 1, 4,
           "Verifica preliminare dei materiali; se presente, rimozione da impresa iscritta all'albo con piano di lavoro."),
    ]),
    _lav("RI.02", "Rimozione di pavimenti e intonaci", 60,
         ["Martello demolitore", "Utensili manuali"], [_POLVERI, _MMC]),
    _lav("RI.03", "Consolidamento di solai esistenti", 50,
         ["Trapano elettrico", "Saldatrice", "Utensili manuali"], [
        _r("Crollo del solaio durante l'intervento", 2, 4, "Puntellare il solaio prima dell'intervento; carichi limitati."),
        _CADUTA_ALTO,
    ]),
    _lav("RI.04", "Rifacimento del manto di copertura", 45,
         ["Autogru", "Ponteggio metallico fisso", "Utensili manuali"], [
        _r("Caduta dall'alto dal bordo e attraverso la copertura", 3, 4,
           "Parapetti perimetrali o ponteggio con mantovana; camminamenti; linee vita.",
           DPI_BASE + ", imbracatura con cordino"),
        _CADUTA_MATERIALE,
    ]),
    _lav("RI.05", "Rifacimento della facciata con cappotto termico", 50,
         ["Ponteggio metallico fisso", "Trapano elettrico", "Utensili manuali"], [
        _CADUTA_ALTO, _CADUTA_MATERIALE,
        _r("Incendio dei pannelli isolanti", 1, 4, "Nessuna lavorazione a caldo vicino ai pannelli; estintori."),
    ]),
    # --- Opere infrastrutturali ---
    _lav("IN.01", "Scavo a sezione obbligata per condotte", 30, ["Escavatore", "Autocarro"], [
        _r("Seppellimento", 2, 4, "Armatura delle pareti oltre 1,50 m di profondità (art. 119)."),
        _r("Contatto con sottoservizi", 2, 4, "Rilievo preventivo; scavo a mano in prossimità."),
        _r("Investimento da traffico veicolare", 2, 4,
           "Segnaletica temporanea secondo il D.M. 10/07/2002; movieri; indumenti ad alta visibilità classe 3."),
    ]),
    _lav("IN.02", "Posa di condotte e pozzetti", 40, ["Escavatore", "Autogru"], [
        _r("Schiacciamento durante la posa", 2, 4, "Guidare i tubi con funi; nessuno nello scavo sotto il carico."),
    ]),
    _lav("IN.03", "Fresatura e pavimentazione stradale in conglomerato bituminoso", 20,
         ["Vibrofinitrice", "Rullo compattatore", "Autocarro"], [
        _r("Investimento da traffico veicolare", 3, 4,
           "Segnaletica temporanea; movieri; delimitazione dell'area di lavoro."),
        _r("Ustioni da conglomerato caldo", 2, 2, "Evitare il contatto con il materiale steso; indumenti a maniche lunghe.",
           DPI_BASE + ", scarpe con suola resistente al calore"),
    ]),
    _lav("IN.04", "Segnaletica stradale orizzontale e verticale", 50, ["Autocarro", "Utensili manuali"], [
        _r("Investimento da traffico veicolare", 3, 4, "Cantiere mobile segnalato; veicolo con pannello a messaggio."),
    ]),
    # --- Restauro ---
    _lav("RS.01", "Pulitura di superfici lapidee e intonaci storici", 70,
         ["Ponteggio metallico fisso", "Utensili manuali"], [
        _r("Inalazione di prodotti chimici e polveri", 3, 2, "Schede di sicurezza; ventilazione.",
           DPI_BASE + ", mascherina con filtri, occhiali"),
        _CADUTA_ALTO,
    ]),
    _lav("RS.02", "Consolidamento di murature con iniezioni", 55,
         ["Trapano elettrico", "Ponteggio metallico fisso"], [
        _r("Schizzi di miscela", 3, 2, "Verificare la tenuta di tubi e raccordi prima dell'iniezione.",
           DPI_BASE + ", occhiali, guanti impermeabili"),
        _VIBRAZIONI_MB,
    ]),
    _lav("RS.03", "Restauro di elementi lignei di copertura", 60,
         ["Ponteggio metallico fisso", "Sega circolare", "Utensili manuali"], [
        _CADUTA_ALTO,
        _r("Esposizione a prodotti antitarlo", 2, 2, "Applicare in ambienti ventilati; schede di sicurezza.",
           DPI_BASE + ", mascherina, guanti"),
    ]),
]


# --- Preparazione delle aree di cantiere ---

_PREP = "Preparazione delle aree di cantiere"
_PUNTURE = _r("Punture, tagli e abrasioni", 3, 2, "Attrezzi integri con impugnature sicure; guanti adatti al lavoro.")
_BIOLOGICO_VERDE = _r("Rischio biologico (punture di insetti, zecche, morsi di animali)", 2, 2,
                      "Indumenti a maniche lunghe e chiusi alle caviglie; repellenti; controllo della cute a fine "
                      "turno; segnalare al medico competente eventuali allergie; cassetta di pronto soccorso.",
                      DPI_BASE + ", stivali di sicurezza")
_SOLE = _r("Microclima: esposizione al sole e al caldo", 3, 2,
           "Lavori più pesanti nelle ore fresche; pause all'ombra; acqua a disposizione; copricapo.",
           DPI_BASE + ", copricapo")
_INVESTIMENTO_A_TERRA = _r("Investimento da mezzi in manovra", 2, 4,
                           "Addetti a terra fuori dal raggio d'azione dei mezzi; moviere nelle manovre; "
                           "indumenti ad alta visibilità.")
_SOTTOSERVIZI = _r("Contatto con sottoservizi e linee elettriche", 1, 4,
                   "Individuare in anticipo reti interrate e linee aeree con gli enti gestori; segnalarle sul "
                   "terreno; distanze dell'Allegato IX.")

LAVORAZIONI[:0] = [
    _lav("AL.10", "Scavo di pulizia generale dell'area di cantiere", 25,
         ["Pala meccanica", "Autocarro", "Utensili manuali"], [
             _INVESTIMENTO_A_TERRA, _MMC, _PUNTURE, _SOTTOSERVIZI,
             _r("Polveri", 3, 2, "Bagnare le superfici prima e durante lo scavo; non lavorare con vento forte.",
                DPI_BASE + ", facciale filtrante FFP2"),
         ], gruppo=_PREP, addetto="Addetto allo scavo di pulizia generale dell'area di cantiere",
         dettaglio="Rimozione con mezzi meccanici e a mano di rifiuti, macerie, radici e materiali "
                   "superficiali dall'area destinata al cantiere, con carico su autocarro."),
    _lav("AL.11", "Taglio di alberi ed estirpazione delle ceppaie", 45,
         ["Motosega", "Trattore", "Utensili manuali"], [
             _r("Caduta della pianta o dei rami durante l'abbattimento", 2, 4,
                "Valutare in anticipo direzione di caduta, inclinazione e stato della pianta; tacca di "
                "direzione e cerniera; via di fuga libera; area interdetta; mai abbattere con vento forte."),
             _r("Schiacciamento durante l'estirpazione delle ceppaie", 2, 3,
                "Tiro con fune o catena di portata adeguata; nessuno nella zona di possibile rinculo o rottura."),
             _MMC, _PUNTURE, _BIOLOGICO_VERDE,
         ], gruppo=_PREP, addetto="Addetto al taglio di alberi ed estirpazione delle ceppaie",
         dettaglio="Abbattimento di alberi presenti nell'area di cantiere, sramatura e depezzatura del "
                   "tronco ed estirpazione delle ceppaie con mezzo meccanico."),
    _lav("AL.12", "Taglio di arbusti e vegetazione in genere", 55,
         ["Decespugliatore a motore", "Utensili manuali"], [
             _PUNTURE, _BIOLOGICO_VERDE, _SOLE,
             _r("Scivolamenti e cadute a livello", 2, 2, "Calzature con suola antiscivolo; procedere con "
                "attenzione su terreni in pendenza o bagnati; segnalare buche e ostacoli."),
         ], gruppo=_PREP, addetto="Addetto al taglio di arbusti e vegetazione in genere",
         dettaglio="Taglio di erba, arbusti e vegetazione infestante con decespugliatore e attrezzi manuali, "
                   "con raccolta del materiale tagliato."),
    _lav("AL.13", "Trasporto a recupero di legna e frascame", 40,
         ["Autocarro con gru", "Utensili manuali"], [
             _MMC, _PUNTURE,
             _r("Caduta di materiale durante il carico", 2, 3, "Carico imbracato o caricato con la gru; "
                "nessuno sotto il carico sospeso; carico fissato sul cassone."),
         ], gruppo=_PREP, addetto="Addetto al trasporto a recupero di legna e frascame",
         dettaglio="Raccolta, carico e trasporto del legname e del frascame derivanti dal taglio della "
                   "vegetazione verso i luoghi di recupero o smaltimento."),
    _lav("AL.14", "Realizzazione della recinzione e degli accessi al cantiere", 55,
         ["Autocarro", "Trapano elettrico", "Utensili manuali"], [
             _MMC, _PUNTURE, _SOTTOSERVIZI,
             _r("Investimento da veicoli lungo la strada", 2, 4, "Lavori sul lato strada protetti con "
                "segnaletica temporanea (D.M. 22/01/2019); indumenti ad alta visibilità."),
             _r("Urti e colpi durante l'infissione dei paletti", 2, 2, "Battipalo o mazza con impugnatura "
                "integra; reggere i paletti con apposito attrezzo e non con le mani."),
         ], gruppo=_PREP, addetto="Addetto alla realizzazione della recinzione e degli accessi al cantiere",
         dettaglio="Posa della recinzione di cantiere per impedire l'accesso ai non addetti e realizzazione "
                   "degli accessi separati per mezzi e lavoratori, con la relativa segnaletica."),
    _lav("AL.15", "Realizzazione della viabilità di cantiere", 30,
         ["Pala meccanica", "Autocarro", "Rullo compattatore", "Utensili manuali"], [
             _INVESTIMENTO_A_TERRA, _MMC,
             _r("Polveri", 3, 2, "Bagnatura periodica dei percorsi.", DPI_BASE + ", facciale filtrante FFP2"),
         ], gruppo=_PREP, addetto="Addetto alla realizzazione della viabilità di cantiere",
         dettaglio="Realizzazione di piste e percorsi per mezzi e persone, separati dove possibile, con "
                   "stesa e compattazione del misto e posa della segnaletica di cantiere."),
    _lav("AL.16", "Scotico di terreno vegetale dall'area di cantiere", 20,
         ["Escavatore", "Pala meccanica", "Autocarro"], [
             _INVESTIMENTO_A_TERRA, _SOTTOSERVIZI,
             _r("Polveri", 3, 2, "Bagnatura delle superfici di lavoro.", DPI_BASE + ", facciale filtrante FFP2"),
         ], gruppo=_PREP, addetto="Addetto allo scotico di terreno vegetale dall'area di cantiere",
         dettaglio="Asportazione con mezzi meccanici dello strato superficiale di terreno vegetale e suo "
                   "accumulo in area dedicata per il successivo riutilizzo."),
]

# Lavorazione di appartenenza e addetto delle fasi di base.
_GRUPPI = {
    "AL.01": ("Apprestamenti del cantiere", "Addetto all'allestimento e alla recinzione del cantiere"),
    "AL.02": ("Apprestamenti del cantiere", "Addetto al montaggio e smontaggio del ponteggio"),
    "AL.03": ("Apprestamenti del cantiere", "Addetto all'installazione della gru a torre"),
    "AL.04": ("Impianti di servizio del cantiere", "Addetto alla realizzazione dell'impianto elettrico di cantiere"),
    "SM.01": ("Smobilizzo del cantiere", "Addetto allo smobilizzo del cantiere"),
    "NC.01": ("Scavi e movimenti di terra", "Addetto allo scavo"),
    "NC.02": ("Strutture in fondazione in c.a.", "Addetto alla realizzazione delle fondazioni"),
    "NC.03": ("Strutture in elevazione in c.a.", "Addetto alla realizzazione di pilastri e travi"),
    "NC.04": ("Solai", "Addetto alla realizzazione dei solai"),
    "NC.05": ("Murature e tamponamenti", "Addetto alla realizzazione delle murature"),
    "NC.06": ("Coperture", "Addetto alla realizzazione della copertura"),
    "NC.07": ("Impianti meccanici", "Addetto alla posa degli impianti idrico-sanitari e termici"),
    "NC.08": ("Impianti elettrici", "Addetto alla posa dell'impianto elettrico"),
    "NC.09": ("Intonaci", "Addetto alla formazione degli intonaci"),
    "NC.10": ("Pavimenti e rivestimenti", "Addetto alla posa di pavimenti e rivestimenti"),
    "NC.11": ("Pitturazioni", "Addetto alle tinteggiature"),
    "NC.12": ("Serramenti e opere in ferro", "Addetto alla posa di serramenti e opere in ferro"),
    "RI.01": ("Demolizioni", "Addetto alle demolizioni"),
    "RI.02": ("Rimozioni", "Addetto alla rimozione di pavimenti e intonaci"),
    "RI.03": ("Consolidamenti strutturali", "Addetto al consolidamento dei solai"),
    "RI.04": ("Rifacimento di coperture", "Addetto al rifacimento del manto di copertura"),
    "RI.05": ("Isolamento delle facciate", "Addetto alla posa del cappotto termico"),
    "IN.01": ("Scavi e movimenti di terra", "Addetto allo scavo a sezione obbligata"),
    "IN.02": ("Reti di sottoservizi", "Addetto alla posa di condotte e pozzetti"),
    "IN.03": ("Pavimentazioni stradali", "Addetto alla pavimentazione stradale"),
    "IN.04": ("Segnaletica stradale", "Addetto alla segnaletica stradale"),
    "RS.01": ("Restauro delle superfici", "Addetto alla pulitura delle superfici"),
    "RS.02": ("Consolidamento delle murature", "Addetto al consolidamento con iniezioni"),
    "RS.03": ("Restauro di strutture lignee", "Addetto al restauro degli elementi lignei"),
}
for _l in LAVORAZIONI:
    if _l["codice"] in _GRUPPI and not _l["gruppo"]:
        _l["gruppo"], _l["addetto"] = _GRUPPI[_l["codice"]]


def per_categoria(tipologia: str | None = None) -> dict[str, list[dict[str, Any]]]:
    """Lavorazioni raggruppate per categoria, eventualmente solo quelle di una tipologia di intervento."""
    gruppi: dict[str, list[dict[str, Any]]] = {c: [] for c in CATEGORIE}
    for lav in LAVORAZIONI:
        if tipologia is None or tipologia in lav["tipologie"]:
            gruppi[lav["categoria"]].append(lav)
    return {c: l for c, l in gruppi.items() if l}
