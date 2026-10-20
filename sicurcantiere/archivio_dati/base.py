"""Struttura comune dei moduli dell'archivio: categorie, catalogo delle attrezzature, helper.

REGOLE PER CHI SCRIVE I CONTENUTI
- Testi scritti da zero, con parole proprie: niente copia da software commerciali, schede di
  altri enti o manuali (si possono consultare come fonti e citare in un commento).
- Riferimenti normativi corretti (D.Lgs. 81/2008 e allegati, norme UNI/EN, D.M.).
- Le fasi usano solo attrezzature presenti in CATALOGO; per una mancante la si aggiunge a
  MANCANTI nel proprio modulo, con tipo e motivo.
- I rischi di una fase sono quelli a cui è esposto l'addetto per la lavorazione in sé; i
  rischi di macchine e attrezzi sono già nelle loro schede e si aggiungono da soli.
- Probabilità e danno da 1 a 4 (matrice P x D del programma).
- DPI scritti con i nomi di anagrafiche.CATALOGO_DPI quando possibile.
"""

from __future__ import annotations

from typing import Any

DPI_BASE = "Casco, calzature di sicurezza, guanti, indumenti ad alta visibilità"

TIPOLOGIE = ("Nuove costruzioni", "Ristrutturazioni", "Opere infrastrutturali", "Restauri")
TUTTE = TIPOLOGIE
EDILIZIA = ("Nuove costruzioni", "Ristrutturazioni", "Restauri")

CATEGORIE = [
    "Allestimento e smobilizzo del cantiere",
    "Demolizioni e rimozioni",
    "Bonifiche (amianto, ordigni bellici, siti contaminati)",
    "Lavori di movimento terra",
    "Fondazioni speciali e indagini geotecniche",
    "Lavori strutturali",
    "Murature, tramezzi e partizioni",
    "Opere edili in copertura",
    "Opere edili in facciata",
    "Opere edili interne",
    "Impianti tecnici per edifici",
    "Impianti a fonti rinnovabili",
    "Lavori di urbanizzazione e reti",
    "Lavori stradali",
    "Impianti di pubblica illuminazione",
    "Sistemazioni esterne e aree verdi",
    "Ripristini e restauri",
    "Tagli, carotaggi e perforazioni",
]

MACCHINA, ATTREZZO, OPERA = "Macchina", "Attrezzo", "Opera provvisionale"

# Catalogo unico delle attrezzature: nome -> tipo. Le prime sono già presenti nell'archivio.
CATALOGO: dict[str, str] = {
    # --- già presenti (archivio.py e archivio_attrezzature.py) ---
    "Escavatore": MACCHINA, "Pala meccanica": MACCHINA, "Autocarro": MACCHINA, "Autobetoniera": MACCHINA,
    "Autopompa per calcestruzzo": MACCHINA, "Gru a torre": MACCHINA, "Autogru": MACCHINA,
    "Rullo compattatore": MACCHINA, "Vibrofinitrice": MACCHINA, "Piattaforma di lavoro elevabile": MACCHINA,
    "Trattore": MACCHINA, "Autocarro con gru": MACCHINA,
    "Betoniera a bicchiere": ATTREZZO, "Sega circolare": ATTREZZO, "Smerigliatrice angolare": ATTREZZO,
    "Martello demolitore": ATTREZZO, "Trapano elettrico": ATTREZZO, "Saldatrice": ATTREZZO,
    "Cannello a gas": ATTREZZO, "Utensili manuali": ATTREZZO, "Motosega": ATTREZZO,
    "Decespugliatore a motore": ATTREZZO,
    "Ponteggio metallico fisso": OPERA, "Trabattello": OPERA, "Scala a mano": OPERA,
    # --- nuove macchine ---
    "Miniescavatore": MACCHINA,
    "Escavatore con martello demolitore": MACCHINA,
    "Escavatore con pinza demolitrice": MACCHINA,
    "Terna (escavatore-caricatore)": MACCHINA,
    "Minipala (skid loader)": MACCHINA,
    "Bulldozer": MACCHINA,
    "Grader (livellatrice)": MACCHINA,
    "Dumper": MACCHINA,
    "Autocarro con cestello": MACCHINA,
    "Sollevatore telescopico": MACCHINA,
    "Carrello elevatore": MACCHINA,
    "Montacarichi a cremagliera": MACCHINA,
    "Motocompressore": MACCHINA,
    "Gruppo elettrogeno": MACCHINA,
    "Scarificatrice (fresa stradale)": MACCHINA,
    "Spazzatrice stradale": MACCHINA,
    "Macchina tracciatrice per segnaletica": MACCHINA,
    "Battipalo (infissione di pali e barriere)": MACCHINA,
    "Macchina perforatrice per pali": MACCHINA,
    "Sonda di perforazione (micropali, tiranti, sondaggi)": MACCHINA,
    "Impianto per jet grouting": MACCHINA,
    "Macchina per perforazione orizzontale controllata (TOC)": MACCHINA,
    "Autospurgo": MACCHINA,
    "Autobotte": MACCHINA,
    "Cippatrice": MACCHINA,
    # --- nuovi attrezzi ---
    "Martello perforatore (tassellatore)": ATTREZZO,
    "Martello demolitore pneumatico": ATTREZZO,
    "Avvitatore elettrico": ATTREZZO,
    "Pistola sparachiodi": ATTREZZO,
    "Scanalatrice per murature": ATTREZZO,
    "Sega a disco per murature e calcestruzzo": ATTREZZO,
    "Tagliasfalto a disco": ATTREZZO,
    "Carotatrice": ATTREZZO,
    "Sega a filo diamantato": ATTREZZO,
    "Piastra vibrante": ATTREZZO,
    "Costipatore a percussione": ATTREZZO,
    "Vibratore per calcestruzzo": ATTREZZO,
    "Frattazzatrice meccanica": ATTREZZO,
    "Piegaferri": ATTREZZO,
    "Tagliaferri": ATTREZZO,
    "Saldatrice per polietilene": ATTREZZO,
    "Cannello ossiacetilenico": ATTREZZO,
    "Cesoia elettrica per lamiere": ATTREZZO,
    "Intonacatrice": ATTREZZO,
    "Impastatrice": ATTREZZO,
    "Pompa per malte e iniezioni": ATTREZZO,
    "Levigatrice per pavimenti": ATTREZZO,
    "Taglierina elettrica per piastrelle": ATTREZZO,
    "Pistola a spruzzo (airless)": ATTREZZO,
    "Sabbiatrice": ATTREZZO,
    "Idropulitrice": ATTREZZO,
    "Pompa sommersa": ATTREZZO,
    "Aspiratore con filtro HEPA": ATTREZZO,
    "Ventilatore estrattore": ATTREZZO,
    "Rilevatore multigas": ATTREZZO,
    "Argano a bandiera": ATTREZZO,
    "Argano a cavalletto": ATTREZZO,
    "Motoperforatrice (trivella a motore)": ATTREZZO,
    # --- nuove opere provvisionali ---
    "Scala doppia": OPERA,
    "Ponte su cavalletti": OPERA,
    "Parapetto provvisorio": OPERA,
    "Rete di sicurezza anticaduta": OPERA,
    "Linea vita provvisoria": OPERA,
    "Andatoie e passerelle": OPERA,
    "Armatura delle pareti di scavo (blindaggio)": OPERA,
    "Puntelli metallici": OPERA,
    "Casseforme": OPERA,
    "Unità di decontaminazione (amianto)": OPERA,
    # --- richieste dai moduli delle fasi (schede in aggiunte.py) ---
    "Canale di scarico delle macerie": OPERA,
    "Estrattore d'aria con filtro assoluto HEPA (depressore)": ATTREZZO,
    "Nebulizzatore a bassa pressione": ATTREZZO,
    "Rilevatore di masse metalliche (magnetometro)": ATTREZZO,
    "Taglierina a filo caldo per pannelli isolanti": ATTREZZO,
    "Accessori di sollevamento (brache, bilancini, ganci)": ATTREZZO,
    "Attrezzatura per scavo di diaframmi (benna mordente o idrofresa)": MACCHINA,
    "Idrodemolitrice (robot ad acqua ad alta pressione)": MACCHINA,
    "Impianto di abbassamento della falda (wellpoint)": ATTREZZO,
    "Impianto di confezionamento e dissabbiatura dei fanghi": MACCHINA,
    "Levigatrice per pareti con aspirazione (giraffa)": ATTREZZO,
    "Macchina insufflatrice per isolanti sfusi": MACCHINA,
    "Macchina per minitrincea (fresa a disco)": MACCHINA,
    "Martinetto idraulico per tesatura": ATTREZZO,
    "Paranco elettrico a catena": ATTREZZO,
    "Penetrometro statico e dinamico": MACCHINA,
    "Pompa pneumatica per massetti": ATTREZZO,
    "Sega murale su binario": ATTREZZO,
    "Sollevatore a ventose per lastre e vetri": ATTREZZO,
    "Sollevatore per lastre (alzapannelli)": ATTREZZO,
    "Spanditrice di emulsione bituminosa": MACCHINA,
    "Strumenti di misura per verifiche elettriche": ATTREZZO,
    "Treppiede con dispositivo di recupero": ATTREZZO,
}

# Nomi dei rischi più comuni: usarli così come sono, per avere un archivio uniforme.
RISCHI_COMUNI = [
    "Caduta dall'alto", "Caduta di materiale dall'alto o a livello", "Seppellimento e sprofondamento",
    "Investimento da mezzi in manovra", "Elettrocuzione", "Movimentazione manuale dei carichi",
    "Rumore", "Vibrazioni al sistema mano-braccio", "Vibrazioni al corpo intero", "Polveri e fibre",
    "Rischio chimico", "Punture, tagli e abrasioni", "Urti, colpi, impatti e compressioni",
    "Scivolamenti e cadute a livello", "Incendio ed esplosione", "Ustioni", "Microclima",
    "Rischio biologico", "Esposizione ad amianto", "Radiazioni ottiche", "Annegamento",
    "Ambienti confinati o sospetti di inquinamento", "Cesoiamenti e stritolamenti",
    "Proiezione di schegge e frammenti", "Crollo o ribaltamento di strutture", "Getti e schizzi",
    "Posture incongrue", "Movimenti ripetitivi degli arti superiori",
]


def r(descrizione: str, p: int, d: int, misure: str, dpi: str = DPI_BASE) -> dict[str, Any]:
    """Rischio: descrizione, probabilità e danno (1-4), misure di prevenzione e protezione, DPI."""
    return {"descrizione": descrizione, "probabilita": p, "danno": d, "misure": misure, "dpi": dpi}


def fase(codice: str, categoria: str, gruppo: str, descrizione: str, dettaglio: str, addetto: str,
         incidenza: float, tipologie: tuple[str, ...], attrezzature: list[str],
         rischi: list[dict[str, Any]]) -> dict[str, Any]:
    """Fase di lavoro dell'archivio.

    codice: prefisso del modulo e numero (es. "DM.01"); categoria: una di CATEGORIE;
    gruppo: la lavorazione di cui la fase fa parte (es. "Demolizione di edifici");
    dettaglio: descrizione dell'attività (2-4 frasi); addetto: «Addetto alla ...»;
    incidenza: percentuale tipica della manodopera sull'importo (0-100).
    """
    return {"codice": codice, "categoria": categoria, "gruppo": gruppo, "descrizione": descrizione,
            "dettaglio": dettaglio, "addetto": addetto, "incidenza_manodopera": incidenza,
            "tipologie": tuple(tipologie), "attrezzature": list(attrezzature), "rischi": list(rischi)}


def scheda(descrizione: str, prima: list[str], durante: list[str], dopo: list[str], dpi: list[str]) -> dict[str, Any]:
    """Scheda d'uso: descrizione, misure prima/durante/dopo l'uso (frasi brevi), DPI dell'operatore."""
    return {"descrizione": descrizione, "prima": prima, "durante": durante, "dopo": dopo, "dpi": dpi}


def attrezzatura(tipo: str, rischi: list[dict[str, Any]], scheda_uso: dict[str, Any]) -> dict[str, Any]:
    """Voce del catalogo: tipo (MACCHINA, ATTREZZO, OPERA), rischi generati dall'uso, scheda d'uso."""
    return {"tipo": tipo, "rischi": list(rischi), "scheda": scheda_uso}
