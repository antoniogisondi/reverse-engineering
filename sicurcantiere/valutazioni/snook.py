"""Tabelle psicofisiche di Snook e Ciriello (1991), valori per il 90% della popolazione.

Fonte: S. H. Snook, V. M. Ciriello, "The design of manual handling tasks: revised tables of
maximum acceptable weights and forces", Ergonomics 34(9), 1991, pp. 1197-1213. Sono le tavole
richiamate dal metodo 1 della UNI ISO 11228-2 (traino e spinta) e, per il trasporto, dalle
linee di indirizzo nazionali sulla UNI ISO 11228-1. Si usano solo le righe che proteggono il
90% della popolazione adulta sana, come indicato dalle norme.

Ogni riga riporta, nell'ordine delle colonne di COLONNE_*, il valore in kg (forza o peso).
"""

from __future__ import annotations

S_8H = 8 * 3600

# Distanza in metri -> intervalli tra due azioni (secondi) delle colonne della tabella.
COLONNE_SPINTA_TRAINO: tuple[tuple[float, tuple[int, ...]], ...] = (
    (2.1, (6, 12, 60, 120, 300, 1800, S_8H)),
    (7.6, (15, 22, 60, 120, 300, 1800, S_8H)),
    (15.2, (25, 35, 60, 120, 300, 1800, S_8H)),
    (30.5, (60, 120, 300, 1800, S_8H)),
    (45.7, (60, 120, 300, 1800, S_8H)),
    (61.0, (120, 300, 1800, S_8H)),
)
COLONNE_TRASPORTO: tuple[tuple[float, tuple[int, ...]], ...] = (
    (2.1, (6, 12, 60, 120, 300, 1800, S_8H)),
    (4.3, (10, 16, 60, 120, 300, 1800, S_8H)),
    (8.5, (18, 24, 60, 120, 300, 1800, S_8H)),
)

# Altezza delle mani da terra (cm) per genere.
ALTEZZE_SPINTA_TRAINO = {"M": (144, 95, 64), "F": (135, 89, 57)}
ALTEZZE_TRASPORTO = {"M": (111, 79), "F": (105, 72)}

_SPINTA_TRAINO = {
    # (azione, genere, forza): righe per altezza, nello stesso ordine di ALTEZZE_SPINTA_TRAINO
    ("spinta", "M", "iniziale"): (
        "20 22 25 25 26 26 31  14 16 21 21 22 22 26  16 18 19 19 20 21 25  15 16 19 19 24  13 14 16 16 20  12 14 14 18",
        "21 24 26 26 28 28 34  16 18 23 23 25 25 30  18 21 22 22 23 24 28  17 19 22 22 27  14 16 19 19 23  14 16 16 20",
        "19 22 24 24 25 26 31  13 14 20 20 21 21 26  15 17 19 19 20 20 24  14 16 19 19 23  12 14 16 16 20  12 14 14 17",
    ),
    ("spinta", "M", "mantenimento"): (
        "10 13 15 16 18 18 22  8 9 13 13 15 16 18  8 9 11 12 13 14 16  8 10 12 13 16  7 8 10 11 13  7 8 9 11",
        "10 13 16 17 19 19 23  8 10 13 13 15 15 18  8 10 11 12 13 13 16  8 10 12 13 16  7 8 9 11 13  7 8 9 11",
        "10 13 16 16 18 19 23  8 10 12 13 14 15 18  8 10 11 11 12 13 15  8 9 11 13 15  7 8 9 11 13  7 8 9 10",
    ),
    ("spinta", "F", "iniziale"): (
        "14 15 17 18 20 21 22  15 16 16 16 18 19 20  12 14 14 14 15 16 17  12 13 14 15 17  12 13 14 15 17  12 13 14 15",
        "14 15 17 18 20 21 22  14 15 16 17 19 19 21  11 13 14 14 16 16 17  12 14 15 16 18  12 14 15 16 18  12 13 14 16",
        "11 12 14 14 16 17 18  11 12 14 14 16 16 17  9 11 12 12 13 14 15  11 12 12 13 15  11 12 12 13 15  10 11 12 13",
    ),
    ("spinta", "F", "mantenimento"): (
        "6 8 10 10 11 12 14  6 7 7 7 8 9 11  5 6 6 6 7 7 9  5 6 6 6 8  5 5 5 6 8  4 4 4 6",
        "6 7 9 9 10 11 13  6 7 8 8 9 9 11  5 6 6 7 7 8 10  5 6 6 7 9  5 6 6 6 8  4 4 5 6",
        "5 6 8 8 9 9 12  6 7 7 7 8 9 11  5 6 6 6 7 7 9  5 6 6 6 8  5 5 5 6 7  4 4 4 6",
    ),
    ("traino", "M", "iniziale"): (
        "14 16 18 18 19 19 23  11 13 16 16 17 18 21  13 15 15 15 16 17 20  12 13 15 15 19  10 11 13 13 16  10 11 11 14",
        "19 22 25 25 27 27 32  15 18 23 23 24 24 29  18 20 21 21 23 23 28  16 18 21 21 26  14 16 18 18 23  13 16 16 19",
        "22 25 28 28 30 30 36  18 20 26 26 27 28 33  20 23 24 24 26 26 31  18 21 24 24 30  16 18 21 21 26  15 18 18 22",
    ),
    ("traino", "M", "mantenimento"): (
        "8 10 12 13 15 15 18  6 8 10 11 12 12 15  7 8 9 9 10 11 13  7 8 9 11 13  6 7 8 9 10  6 7 7 9",
        "10 13 16 17 19 20 24  8 10 13 14 16 16 19  9 10 12 12 14 14 17  9 10 12 14 17  7 9 10 12 14  7 9 10 12",
        "11 14 17 18 20 21 25  9 11 14 15 17 17 20  9 11 12 13 15 15 18  9 11 13 15 18  8 9 11 12 15  8 9 10 12",
    ),
    ("traino", "F", "iniziale"): (
        "13 16 17 18 20 21 22  13 14 16 16 18 19 20  10 12 13 14 15 16 17  12 13 14 15 17  12 13 14 15 17  12 13 14 15",
        "14 16 18 19 21 22 23  14 15 16 17 19 20 21  10 12 14 14 16 17 18  13 14 15 16 18  13 14 15 16 18  12 13 14 16",
        "15 17 19 20 22 23 24  15 16 17 18 20 21 22  11 13 15 15 17 18 19  13 14 15 17 19  13 14 15 17 19  13 14 15 17",
    ),
    ("traino", "F", "mantenimento"): (
        "6 9 10 10 11 12 15  7 8 9 9 10 11 13  6 7 7 8 8 9 11  6 7 7 8 10  6 6 7 7 9  5 5 5 7",
        "6 9 10 10 11 12 14  7 8 9 9 10 10 13  5 6 7 7 8 9 11  6 7 7 7 10  5 6 6 7 9  5 5 5 7",
        "5 8 9 9 10 11 13  6 7 8 8 9 10 12  5 6 7 7 7 8 10  6 6 6 7 9  5 6 6 6 8  4 5 5 6",
    ),
}

_TRASPORTO = {
    # genere: righe per altezza, nello stesso ordine di ALTEZZE_TRASPORTO
    "M": (
        "10 14 17 17 19 21 25  9 11 15 15 17 19 22  10 11 13 13 15 17 20",
        "13 17 21 21 23 26 31  11 14 18 19 21 23 27  13 15 17 18 20 22 26",
    ),
    "F": (
        "11 12 13 13 13 13 18  9 10 13 13 13 13 18  10 11 12 12 12 12 16",
        "13 14 16 16 16 16 22  10 11 14 14 14 14 20  12 12 14 14 14 14 19",
    ),
}


def _righe(testi: tuple[str, ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(x) for x in t.split()) for t in testi)


SPINTA_TRAINO = {k: _righe(v) for k, v in _SPINTA_TRAINO.items()}
TRASPORTO = {k: _righe(v) for k, v in _TRASPORTO.items()}


class FuoriTabella(ValueError):
    """La frequenza è più alta di quelle studiate per la distanza indicata."""


def _colonna(colonne: tuple[tuple[float, tuple[int, ...]], ...], distanza: float,
             azioni_ora: float) -> tuple[int, float, int, bool]:
    """Indice di colonna, distanza e intervallo di tabella usati, e se la distanza supera la tabella.

    Scelta prudenziale: la distanza di tabella uguale o immediatamente superiore e la
    frequenza di tabella uguale o immediatamente più alta di quella reale.
    """
    oltre = distanza > colonne[-1][0]
    inizio = 0
    for dist, intervalli in colonne:
        if distanza <= dist or dist == colonne[-1][0]:
            reale = 3600 / azioni_ora if azioni_ora > 0 else S_8H
            # Tolleranza del 10%: «una volta per turno» non deve cadere nella colonna dei 30 minuti.
            validi = [i for i, t in enumerate(intervalli) if t <= reale * 1.1]
            if not validi:
                raise FuoriTabella(f"frequenza superiore a un'azione ogni {intervalli[0]} s, "
                                   f"la più alta studiata per {str(dist).replace('.', ',')} m")
            j = validi[-1]
            return inizio + j, dist, intervalli[j], oltre
        inizio += len(intervalli)
    raise AssertionError("tabella vuota")


def _altezza(altezze: tuple[int, ...], cm: float) -> int:
    return min(range(len(altezze)), key=lambda i: abs(altezze[i] - cm))


def forza_raccomandata(azione: str, genere: str, forza: str, altezza_cm: float, distanza_m: float,
                       azioni_ora: float) -> tuple[float, dict]:
    """Forza (kg) accettabile per il 90% della popolazione e parametri di tabella usati."""
    r = _altezza(ALTEZZE_SPINTA_TRAINO[genere], altezza_cm)
    c, dist, intervallo, oltre = _colonna(COLONNE_SPINTA_TRAINO, distanza_m, azioni_ora)
    valore = SPINTA_TRAINO[(azione, genere, forza)][r][c]
    return float(valore), {"altezza": ALTEZZE_SPINTA_TRAINO[genere][r], "distanza": dist,
                           "intervallo": intervallo, "oltre": oltre}


def peso_trasporto(genere: str, altezza: str, distanza_m: float, azioni_ora: float) -> tuple[float, dict]:
    """Peso (kg) trasportabile accettabile per il 90% della popolazione; altezza 'alta' o 'bassa'."""
    r = 0 if altezza == "alta" else 1
    c, dist, intervallo, oltre = _colonna(COLONNE_TRASPORTO, distanza_m, azioni_ora)
    return float(TRASPORTO[genere][r][c]), {"altezza": ALTEZZE_TRASPORTO[genere][r], "distanza": dist,
                                            "intervallo": intervallo, "oltre": oltre}


def intervallo_testo(secondi: int) -> str:
    if secondi >= S_8H:
        return "una volta ogni 8 ore"
    if secondi >= 60:
        minuti = secondi // 60
        return "una volta al minuto" if minuti == 1 else f"una volta ogni {minuti} minuti"
    return f"una volta ogni {secondi} secondi"
