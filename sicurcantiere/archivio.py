"""Archivio di base delle lavorazioni, delle macchine e degli attrezzi.

Contenuti redatti per questo progetto a partire dal D.Lgs. 81/2008 e dalla
buona pratica di cantiere. Vanno sempre verificati e adattati dal
coordinatore al cantiere specifico.
"""

from __future__ import annotations

from typing import Any

DPI_BASE = "Casco, scarpe antinfortunistiche, guanti, indumenti ad alta visibilità"

CATEGORIE = [
    "Allestimento e smobilizzo",
    "Nuove costruzioni",
    "Ristrutturazioni",
    "Opere infrastrutturali",
    "Restauro",
]


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


def _lav(categoria: str, codice: str, descrizione: str, incidenza: float,
         attrezzature: list[str], rischi: list[dict[str, Any]]) -> dict[str, Any]:
    for nome in attrezzature:
        assert nome in ATTREZZATURE, nome
    return {
        "categoria": categoria,
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

_A, _N, _R, _I, _S = CATEGORIE

LAVORAZIONI: list[dict[str, Any]] = [
    # --- Allestimento e smobilizzo ---
    _lav(_A, "AL.01", "Allestimento e recinzione del cantiere", 50, ["Autocarro", "Utensili manuali"], [
        _r("Investimento da mezzi in manovra", 2, 4,
           "Delimitare le aree di manovra; segnaletica; moviere a terra durante le manovre in retromarcia."),
        _MMC,
    ]),
    _lav(_A, "AL.02", "Montaggio e smontaggio di ponteggio metallico fisso", 70,
         ["Autocarro", "Utensili manuali"], [
        _r("Caduta dall'alto durante il montaggio", 3, 4,
           "Montaggio secondo PiMUS e autorizzazione ministeriale; lavoratori formati (Allegato XXI); "
           "sistemi anticaduta agganciati a punti sicuri.",
           DPI_BASE + ", imbracatura con doppio cordino e assorbitore"),
        _CADUTA_MATERIALE,
        _r("Elettrocuzione per vicinanza a linee aeree", 1, 4,
           "Rispettare le distanze dell'Allegato IX; se non possibile chiedere il distacco all'ente gestore."),
    ]),
    _lav(_A, "AL.03", "Installazione della gru a torre", 40, ["Autogru", "Utensili manuali"], [
        _CADUTA_ALTO, _CADUTA_MATERIALE,
        _r("Cedimento del basamento", 1, 4, "Basamento calcolato da tecnico abilitato; verifica del terreno."),
    ]),
    _lav(_A, "AL.04", "Impianto elettrico e di terra del cantiere", 60, ["Trapano elettrico", "Utensili manuali"], [
        _r("Elettrocuzione", 2, 4,
           "Quadri ASC certificati; interruttori differenziali; impianto di terra verificato; "
           "impresa abilitata con dichiarazione di conformità.",
           DPI_BASE + ", guanti isolanti"),
    ]),
    _lav(_A, "SM.01", "Smobilizzo del cantiere", 50, ["Autocarro", "Utensili manuali"], [
        _r("Investimento da mezzi in manovra", 2, 4, "Moviere durante le manovre; area delimitata."),
        _MMC,
    ]),
    # --- Nuove costruzioni ---
    _lav(_N, "NC.01", "Scavo di sbancamento e a sezione aperta", 25, ["Escavatore", "Autocarro"], [
        _r("Seppellimento per franamento delle pareti", 2, 4,
           "Pendenza delle pareti adeguata al terreno o armature; nessun deposito sul ciglio; verifica dopo le piogge."),
        _r("Caduta nello scavo", 3, 3, "Parapetti o delimitazione del ciglio; accessi con scale vincolate."),
        _r("Contatto con sottoservizi", 2, 4,
           "Rilievo preventivo dei sottoservizi presso gli enti gestori; scavo a mano in prossimità."),
    ]),
    _lav(_N, "NC.02", "Fondazioni in cemento armato", 35,
         ["Autobetoniera", "Autopompa per calcestruzzo", "Sega circolare", "Utensili manuali"], [
        _r("Punture e tagli da ferri di armatura", 3, 2, "Proteggere le estremità dei ferri di ripresa."),
        _r("Contatto con il calcestruzzo (dermatiti)", 3, 2, "Evitare il contatto con la pelle; lavaggio immediato.",
           DPI_BASE + ", stivali e guanti impermeabili"),
        _r("Caduta nello scavo di fondazione", 2, 3, "Passerelle con parapetto; ciglio delimitato."),
    ]),
    _lav(_N, "NC.03", "Strutture in elevazione in cemento armato", 40,
         ["Gru a torre", "Autopompa per calcestruzzo", "Sega circolare", "Ponteggio metallico fisso"], [
        _CADUTA_ALTO, _CADUTA_MATERIALE,
        _r("Crollo delle casseforme o dei puntelli", 2, 4,
           "Puntellature secondo progetto; disarmo solo dopo l'autorizzazione del direttore dei lavori."),
        _r("Vibrazioni e rumore da vibratore per calcestruzzo", 3, 2, "Rotazione degli addetti.",
           DPI_BASE + ", otoprotettori"),
    ]),
    _lav(_N, "NC.04", "Solai in latero-cemento", 45,
         ["Gru a torre", "Autopompa per calcestruzzo", "Ponteggio metallico fisso"], [
        _r("Caduta dall'alto attraverso il solaio o dai bordi", 3, 4,
           "Sottopalchi o reti anticaduta; parapetti perimetrali; non camminare sulle pignatte.",
           DPI_BASE + ", imbracatura"),
        _CADUTA_MATERIALE,
    ]),
    _lav(_N, "NC.05", "Murature di tamponamento in laterizio", 50,
         ["Betoniera a bicchiere", "Ponteggio metallico fisso", "Utensili manuali"], [
        _r("Caduta dall'alto", 2, 4, "Lavorare da ponteggio o ponti su cavalletti conformi."),
        _MMC, _POLVERI,
    ]),
    _lav(_N, "NC.06", "Copertura a falde", 45,
         ["Gru a torre", "Sega circolare", "Ponteggio metallico fisso"], [
        _r("Caduta dall'alto dal bordo e attraverso la copertura", 3, 4,
           "Ponteggio con mantovana; camminamenti sulle superfici non portanti; linee vita.",
           DPI_BASE + ", imbracatura con cordino"),
        _CADUTA_MATERIALE,
        _r("Condizioni climatiche avverse", 3, 2, "Sospendere i lavori con vento forte, pioggia o ghiaccio."),
    ]),
    _lav(_N, "NC.07", "Impianti idrico-sanitari e di riscaldamento", 45,
         ["Cannello a gas", "Trapano elettrico", "Scala a mano"], [
        _r("Incendio", 1, 4, "Allontanare i materiali infiammabili; controllo dell'area a fine lavoro."),
        _MMC,
    ]),
    _lav(_N, "NC.08", "Impianto elettrico dell'edificio", 55,
         ["Trapano elettrico", "Smerigliatrice angolare", "Scala a mano"], [
        _r("Elettrocuzione", 2, 4, "Lavorare fuori tensione; sezionamento e blocco dei quadri; verifica di assenza di tensione."),
        _POLVERI,
    ]),
    _lav(_N, "NC.09", "Intonaci interni ed esterni", 60,
         ["Betoniera a bicchiere", "Trabattello", "Ponteggio metallico fisso"], [
        _r("Caduta dall'alto da ponti su cavalletti o trabattelli", 2, 3, "Opere provvisionali conformi e verificate."),
        _r("Schizzi di malta negli occhi", 3, 2, "Non lavorare sopra la testa senza protezione degli occhi.",
           DPI_BASE + ", occhiali"),
    ]),
    _lav(_N, "NC.10", "Pavimenti e rivestimenti", 50, ["Smerigliatrice angolare", "Utensili manuali"], [
        _r("Posture incongrue (lavoro in ginocchio)", 4, 1, "Pause; alternanza delle attività.", DPI_BASE + ", ginocchiere"),
        _r("Contatto con adesivi e prodotti chimici", 2, 2, "Consultare le schede di sicurezza; aerare i locali."),
        _POLVERI,
    ]),
    _lav(_N, "NC.11", "Tinteggiature", 65, ["Trabattello", "Scala a mano"], [
        _r("Caduta dall'alto", 2, 3, "Trabattelli e scale conformi."),
        _r("Inalazione di vapori e contatto con prodotti chimici", 2, 2,
           "Consultare le schede di sicurezza; ventilazione dei locali.", DPI_BASE + ", mascherina, occhiali"),
    ]),
    _lav(_N, "NC.12", "Serramenti e opere in ferro", 40,
         ["Saldatrice", "Smerigliatrice angolare", "Trapano elettrico"], [
        _MMC, _CADUTA_ALTO,
    ]),
    # --- Ristrutturazioni ---
    _lav(_R, "RI.01", "Demolizioni parziali di murature e tramezzi", 55,
         ["Martello demolitore", "Autocarro", "Utensili manuali"], [
        _r("Crollo di strutture", 2, 4,
           "Programma delle demolizioni (art. 151); puntellamenti; procedere dall'alto verso il basso."),
        _r("Polveri", 4, 2, "Bagnare le macerie; canali di scarico chiusi.", DPI_BASE + ", mascherina FFP3, occhiali"),
        _r("Presenza di amianto", 1, 4,
           "Verifica preliminare dei materiali; se presente, rimozione da impresa iscritta all'albo con piano di lavoro."),
    ]),
    _lav(_R, "RI.02", "Rimozione di pavimenti e intonaci", 60,
         ["Martello demolitore", "Utensili manuali"], [_POLVERI, _MMC]),
    _lav(_R, "RI.03", "Consolidamento di solai esistenti", 50,
         ["Trapano elettrico", "Saldatrice", "Utensili manuali"], [
        _r("Crollo del solaio durante l'intervento", 2, 4, "Puntellare il solaio prima dell'intervento; carichi limitati."),
        _CADUTA_ALTO,
    ]),
    _lav(_R, "RI.04", "Rifacimento del manto di copertura", 45,
         ["Autogru", "Ponteggio metallico fisso", "Utensili manuali"], [
        _r("Caduta dall'alto dal bordo e attraverso la copertura", 3, 4,
           "Parapetti perimetrali o ponteggio con mantovana; camminamenti; linee vita.",
           DPI_BASE + ", imbracatura con cordino"),
        _CADUTA_MATERIALE,
    ]),
    _lav(_R, "RI.05", "Rifacimento della facciata con cappotto termico", 50,
         ["Ponteggio metallico fisso", "Trapano elettrico", "Utensili manuali"], [
        _CADUTA_ALTO, _CADUTA_MATERIALE,
        _r("Incendio dei pannelli isolanti", 1, 4, "Nessuna lavorazione a caldo vicino ai pannelli; estintori."),
    ]),
    # --- Opere infrastrutturali ---
    _lav(_I, "IN.01", "Scavo a sezione obbligata per condotte", 30, ["Escavatore", "Autocarro"], [
        _r("Seppellimento", 2, 4, "Armatura delle pareti oltre 1,50 m di profondità (art. 119)."),
        _r("Contatto con sottoservizi", 2, 4, "Rilievo preventivo; scavo a mano in prossimità."),
        _r("Investimento da traffico veicolare", 2, 4,
           "Segnaletica temporanea secondo il D.M. 10/07/2002; movieri; indumenti ad alta visibilità classe 3."),
    ]),
    _lav(_I, "IN.02", "Posa di condotte e pozzetti", 40, ["Escavatore", "Autogru"], [
        _r("Schiacciamento durante la posa", 2, 4, "Guidare i tubi con funi; nessuno nello scavo sotto il carico."),
    ]),
    _lav(_I, "IN.03", "Fresatura e pavimentazione stradale in conglomerato bituminoso", 20,
         ["Vibrofinitrice", "Rullo compattatore", "Autocarro"], [
        _r("Investimento da traffico veicolare", 3, 4,
           "Segnaletica temporanea; movieri; delimitazione dell'area di lavoro."),
        _r("Ustioni da conglomerato caldo", 2, 2, "Evitare il contatto con il materiale steso; indumenti a maniche lunghe.",
           DPI_BASE + ", scarpe con suola resistente al calore"),
    ]),
    _lav(_I, "IN.04", "Segnaletica stradale orizzontale e verticale", 50, ["Autocarro", "Utensili manuali"], [
        _r("Investimento da traffico veicolare", 3, 4, "Cantiere mobile segnalato; veicolo con pannello a messaggio."),
    ]),
    # --- Restauro ---
    _lav(_S, "RS.01", "Pulitura di superfici lapidee e intonaci storici", 70,
         ["Ponteggio metallico fisso", "Utensili manuali"], [
        _r("Inalazione di prodotti chimici e polveri", 3, 2, "Schede di sicurezza; ventilazione.",
           DPI_BASE + ", mascherina con filtri, occhiali"),
        _CADUTA_ALTO,
    ]),
    _lav(_S, "RS.02", "Consolidamento di murature con iniezioni", 55,
         ["Trapano elettrico", "Ponteggio metallico fisso"], [
        _r("Schizzi di miscela", 3, 2, "Verificare la tenuta di tubi e raccordi prima dell'iniezione.",
           DPI_BASE + ", occhiali, guanti impermeabili"),
        _VIBRAZIONI_MB,
    ]),
    _lav(_S, "RS.03", "Restauro di elementi lignei di copertura", 60,
         ["Ponteggio metallico fisso", "Sega circolare", "Utensili manuali"], [
        _CADUTA_ALTO,
        _r("Esposizione a prodotti antitarlo", 2, 2, "Applicare in ambienti ventilati; schede di sicurezza.",
           DPI_BASE + ", mascherina, guanti"),
    ]),
]


def per_categoria() -> dict[str, list[dict[str, Any]]]:
    gruppi: dict[str, list[dict[str, Any]]] = {c: [] for c in CATEGORIE}
    for lav in LAVORAZIONI:
        gruppi[lav["categoria"]].append(lav)
    return gruppi
