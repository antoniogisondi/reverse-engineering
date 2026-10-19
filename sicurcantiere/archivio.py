"""Archivio di base delle lavorazioni con i relativi rischi.

Contenuti redatti per questo progetto a partire dal D.Lgs. 81/2008 e dalla
buona pratica di cantiere. Vanno sempre verificati e adattati dal
coordinatore al cantiere specifico.
"""

from __future__ import annotations

from typing import Any

DPI_BASE = "Casco, scarpe antinfortunistiche, guanti, indumenti ad alta visibilità"


def _r(descrizione: str, p: int, d: int, misure: str, dpi: str = DPI_BASE) -> dict[str, Any]:
    return {"descrizione": descrizione, "probabilita": p, "danno": d, "misure": misure, "dpi": dpi}


LAVORAZIONI: list[dict[str, Any]] = [
    {
        "codice": "AL.01",
        "descrizione": "Allestimento e recinzione del cantiere",
        "rischi": [
            _r("Investimento da mezzi in manovra", 2, 4,
               "Delimitare le aree di manovra, segnaletica, moviere a terra durante le manovre in retromarcia."),
            _r("Movimentazione manuale dei carichi", 3, 2,
               "Carichi oltre 25 kg movimentati da due persone o con mezzi meccanici; formazione art. 169."),
            _r("Tagli e abrasioni", 3, 1, "Uso di guanti; attrezzi in buono stato e riposti dopo l'uso."),
        ],
    },
    {
        "codice": "AL.02",
        "descrizione": "Montaggio e smontaggio di ponteggio metallico fisso",
        "rischi": [
            _r("Caduta dall'alto", 3, 4,
               "Montaggio secondo PiMUS e schema di autorizzazione ministeriale; lavoratori formati "
               "(Allegato XXI); uso di sistemi anticaduta agganciati a punti sicuri.",
               DPI_BASE + ", imbracatura con doppio cordino e assorbitore"),
            _r("Caduta di materiale dall'alto", 3, 3,
               "Interdire l'area sottostante; tavole fermapiede; sollevamento con carrucola e gancio di sicurezza."),
            _r("Elettrocuzione per vicinanza a linee aeree", 1, 4,
               "Rispettare le distanze dell'Allegato IX; se non possibile chiedere il distacco all'ente gestore."),
        ],
    },
    {
        "codice": "SC.01",
        "descrizione": "Scavo a sezione aperta con mezzi meccanici",
        "rischi": [
            _r("Seppellimento per franamento delle pareti", 2, 4,
               "Pendenza delle pareti adeguata al terreno o armature; non depositare materiale sul ciglio; "
               "verifica dopo piogge."),
            _r("Caduta nello scavo", 3, 3, "Parapetti o delimitazione del ciglio; accessi con scale vincolate."),
            _r("Investimento e ribaltamento del mezzo", 2, 4,
               "Mezzo condotto da operatore abilitato; nessuno nel raggio d'azione dell'escavatore."),
            _r("Contatto con sottoservizi", 2, 4,
               "Rilievo preventivo dei sottoservizi presso gli enti gestori; scavo a mano in prossimità."),
        ],
    },
    {
        "codice": "ST.01",
        "descrizione": "Getto di fondazioni e strutture in cemento armato",
        "rischi": [
            _r("Caduta dall'alto", 3, 4,
               "Parapetti sui bordi dei solai e sulle aperture; ponteggio o trabattelli conformi.",
               DPI_BASE + ", imbracatura dove non sono presenti protezioni collettive"),
            _r("Punture e tagli da ferri di armatura", 3, 2, "Proteggere le estremità dei ferri di ripresa con cappucci."),
            _r("Contatto con il calcestruzzo (dermatiti)", 3, 2,
               "Evitare il contatto con la pelle; lavaggio immediato.",
               DPI_BASE + ", stivali e guanti impermeabili"),
            _r("Vibrazioni e rumore da vibratore", 3, 2,
               "Rotazione degli addetti; manutenzione dell'attrezzatura.",
               DPI_BASE + ", otoprotettori"),
        ],
    },
    {
        "codice": "MU.01",
        "descrizione": "Murature in laterizio",
        "rischi": [
            _r("Caduta dall'alto", 2, 4, "Lavorare da ponteggio o ponti su cavalletti conformi; mai su elementi instabili."),
            _r("Movimentazione manuale dei carichi", 3, 2, "Approvvigionamento dei materiali vicino al posto di lavoro."),
            _r("Polveri durante il taglio", 3, 2,
               "Taglio a umido o con aspirazione.",
               DPI_BASE + ", mascherina FFP2, occhiali"),
        ],
    },
    {
        "codice": "CO.01",
        "descrizione": "Rifacimento del manto di copertura",
        "rischi": [
            _r("Caduta dall'alto dal bordo e attraverso la copertura", 3, 4,
               "Parapetti perimetrali o ponteggio con mantovana; camminamenti su superfici non portanti; "
               "linee vita.",
               DPI_BASE + ", imbracatura con cordino"),
            _r("Caduta di materiale dall'alto", 3, 3, "Delimitare l'area sottostante; sollevamento con mezzi idonei."),
            _r("Esposizione a condizioni climatiche", 3, 2, "Sospendere i lavori con vento forte, pioggia o ghiaccio."),
        ],
    },
    {
        "codice": "IM.01",
        "descrizione": "Impianto elettrico di cantiere",
        "rischi": [
            _r("Elettrocuzione", 2, 4,
               "Quadri ASC certificati; interruttori differenziali; impianto di terra verificato; "
               "esecuzione da impresa abilitata con dichiarazione di conformità.",
               DPI_BASE + ", guanti isolanti"),
        ],
    },
    {
        "codice": "IM.02",
        "descrizione": "Impianti idrico-sanitari e termici",
        "rischi": [
            _r("Ustioni durante le saldature", 2, 3,
               "Bombole in posizione verticale e incatenate; valvole contro il ritorno di fiamma; estintore vicino.",
               DPI_BASE + ", occhiali o schermo per saldatura"),
            _r("Incendio", 1, 4, "Allontanare i materiali infiammabili; controllo dell'area a fine lavoro."),
        ],
    },
    {
        "codice": "FI.01",
        "descrizione": "Intonaci e tinteggiature",
        "rischi": [
            _r("Caduta dall'alto da ponti su cavalletti o trabattelli", 2, 3,
               "Trabattelli con stabilizzatori e ruote bloccate; nessuno sopra durante lo spostamento."),
            _r("Inalazione e contatto con prodotti chimici", 2, 2,
               "Consultare le schede di sicurezza; ventilazione dei locali.",
               DPI_BASE + ", mascherina, occhiali"),
        ],
    },
    {
        "codice": "DM.01",
        "descrizione": "Demolizioni parziali",
        "rischi": [
            _r("Crollo di strutture", 2, 4,
               "Programma delle demolizioni (art. 151); puntellamenti; procedere dall'alto verso il basso."),
            _r("Polveri", 4, 2, "Bagnare le macerie; canali di scarico chiusi.", DPI_BASE + ", mascherina FFP3, occhiali"),
            _r("Rumore", 4, 2, "Valutazione del rumore; limitare l'esposizione.", DPI_BASE + ", otoprotettori"),
            _r("Presenza di amianto", 1, 4,
               "Verifica preliminare dei materiali; se presente, rimozione da impresa iscritta all'albo con piano di lavoro."),
        ],
    },
    {
        "codice": "SM.01",
        "descrizione": "Smobilizzo del cantiere",
        "rischi": [
            _r("Investimento da mezzi in manovra", 2, 4, "Moviere durante le manovre; area delimitata."),
            _r("Movimentazione manuale dei carichi", 3, 2, "Uso di mezzi di sollevamento per i carichi pesanti."),
        ],
    },
]
