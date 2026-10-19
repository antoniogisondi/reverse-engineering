"""Sollevamento manuale di carichi: equazione NIOSH (UNI ISO 11228-1, Allegato XXXIII D.Lgs. 81/2008).

Peso limite raccomandato  RWL = CP x HM x VM x DM x AM x FM x CM
Indice di sollevamento    LI  = peso sollevato / RWL

Per più compiti di sollevamento nello stesso turno si usa l'indice composto
(CLI): i compiti si ordinano per indice di sollevamento decrescente e a ogni
compito successivo si somma il contributo dovuto all'aumento di frequenza.
"""

from __future__ import annotations

import math
from typing import Any

from sicurcantiere.valutazioni.base import (
    GIALLO,
    ROSSO,
    VERDE,
    VIOLA,
    Campo,
    Esito,
    Metodo,
    interpola,
    numero_it,
)

# Costante di peso (kg) per genere ed età, come in uso in Italia (ISO 11228-1, ISO/TR 12295).
COSTANTI_PESO = {
    "M18-45": 25.0,
    "F18-45": 20.0,
    "M-giovani-anziani": 20.0,
    "F-giovani-anziani": 15.0,
}
SCELTE_LAVORATORI = (
    ("M18-45", "Maschi 18-45 anni (25 kg)"),
    ("F18-45", "Femmine 18-45 anni (20 kg)"),
    ("M-giovani-anziani", "Maschi <18 o >45 anni (20 kg)"),
    ("F-giovani-anziani", "Femmine <18 o >45 anni (15 kg)"),
)
SCELTE_DURATA = (
    ("breve", "Breve: fino a 1 ora (con recupero adeguato)"),
    ("media", "Media: da 1 a 2 ore"),
    ("lunga", "Lunga: da 2 a 8 ore"),
)
SCELTE_PRESA = (("buona", "Buona"), ("discreta", "Discreta"), ("scarsa", "Scarsa"))

# Fattore frequenza: frequenza (atti/min) -> {durata: (V < 75 cm, V >= 75 cm)}.
TABELLA_FM: list[tuple[float, dict[str, tuple[float, float]]]] = [
    (0.2, {"breve": (1.00, 1.00), "media": (0.95, 0.95), "lunga": (0.85, 0.85)}),
    (0.5, {"breve": (0.97, 0.97), "media": (0.92, 0.92), "lunga": (0.81, 0.81)}),
    (1, {"breve": (0.94, 0.94), "media": (0.88, 0.88), "lunga": (0.75, 0.75)}),
    (2, {"breve": (0.91, 0.91), "media": (0.84, 0.84), "lunga": (0.65, 0.65)}),
    (3, {"breve": (0.88, 0.88), "media": (0.79, 0.79), "lunga": (0.55, 0.55)}),
    (4, {"breve": (0.84, 0.84), "media": (0.72, 0.72), "lunga": (0.45, 0.45)}),
    (5, {"breve": (0.80, 0.80), "media": (0.60, 0.60), "lunga": (0.35, 0.35)}),
    (6, {"breve": (0.75, 0.75), "media": (0.50, 0.50), "lunga": (0.27, 0.27)}),
    (7, {"breve": (0.70, 0.70), "media": (0.42, 0.42), "lunga": (0.22, 0.22)}),
    (8, {"breve": (0.60, 0.60), "media": (0.35, 0.35), "lunga": (0.18, 0.18)}),
    (9, {"breve": (0.52, 0.52), "media": (0.30, 0.30), "lunga": (0.00, 0.15)}),
    (10, {"breve": (0.45, 0.45), "media": (0.26, 0.26), "lunga": (0.00, 0.13)}),
    (11, {"breve": (0.41, 0.41), "media": (0.00, 0.23), "lunga": (0.00, 0.00)}),
    (12, {"breve": (0.37, 0.37), "media": (0.00, 0.21), "lunga": (0.00, 0.00)}),
    (13, {"breve": (0.00, 0.34), "media": (0.00, 0.00), "lunga": (0.00, 0.00)}),
    (14, {"breve": (0.00, 0.31), "media": (0.00, 0.00), "lunga": (0.00, 0.00)}),
    (15, {"breve": (0.00, 0.28), "media": (0.00, 0.00), "lunga": (0.00, 0.00)}),
]

# Fattore presa: (V < 75 cm, V >= 75 cm).
TABELLA_CM = {"buona": (1.00, 1.00), "discreta": (0.95, 1.00), "scarsa": (0.90, 0.90)}


def hm(h: float) -> float:
    """Distanza orizzontale del carico dal corpo (cm)."""
    if h <= 25:
        return 1.0
    return 0.0 if h > 63 else 25.0 / h


def vm(v: float) -> float:
    """Altezza delle mani da terra all'inizio del sollevamento (cm)."""
    return 0.0 if v > 175 else max(0.0, 1 - 0.003 * abs(v - 75))


def dm(d: float) -> float:
    """Dislocazione verticale del carico (cm)."""
    if d <= 25:
        return 1.0
    return 0.0 if d > 175 else 0.82 + 4.5 / d


def am(a: float) -> float:
    """Angolo di asimmetria (gradi)."""
    return 0.0 if a > 135 else 1 - 0.0032 * a


def fm(frequenza: float, durata: str, v: float) -> float:
    """Fattore frequenza; tra i valori di tabella si interpola linearmente."""
    if frequenza > 15:
        return 0.0
    colonna = 0 if v < 75 else 1
    tabella = [(f, valori[durata][colonna]) for f, valori in TABELLA_FM]
    return interpola(tabella, max(frequenza, 0.2))


def cm(presa: str, v: float) -> float:
    return TABELLA_CM[presa][0 if v < 75 else 1]


def classe(indice: float) -> tuple[str, str]:
    if indice <= 0.85:
        return "Rischio accettabile", VERDE
    if indice <= 1.0:
        return "Livello di attenzione", GIALLO
    if indice <= 3.0:
        return "Rischio presente", ROSSO
    return "Rischio elevato", VIOLA


MISURE_PER_FATTORE = {
    "HM": "Avvicinare il carico al corpo (distanza orizzontale ≤ 25 cm): eliminare ostacoli, usare piani di appoggio vicini.",
    "VM": "Portare l'altezza di presa vicino a 75 cm da terra: rialzare i carichi depositati a terra con pallet o supporti.",
    "DM": "Ridurre il dislivello tra presa e deposito, con piani di lavoro regolabili o carrelli a piattaforma.",
    "AM": "Eliminare le torsioni del tronco riorganizzando le posizioni di prelievo e deposito.",
    "FM": "Ridurre la frequenza dei sollevamenti, introdurre pause e rotazione su compiti diversi.",
    "CM": "Migliorare la presa: maniglie, contenitori con impugnature, guanti adatti.",
}
MISURE_GENERALI = {
    VERDE: ["Nessun intervento specifico; mantenere informazione e formazione (art. 169)."],
    GIALLO: [
        "Attivare formazione e addestramento specifici sulle corrette modalità di sollevamento (art. 169).",
        "Valutare la sorveglianza sanitaria dei lavoratori esposti.",
    ],
    ROSSO: [
        "Ridurre il rischio con interventi tecnici e organizzativi (art. 168); priorità ai fattori più penalizzanti.",
        "Sorveglianza sanitaria dei lavoratori esposti (art. 168 c. 2 lett. d).",
        "Valutare l'uso di ausili meccanici: carrelli, sollevatori, paranchi, manipolatori.",
    ],
    VIOLA: [
        "Interventi di riprogettazione prioritari e immediati: il compito non è sostenibile con la sola formazione.",
        "Introdurre ausili meccanici o la movimentazione in coppia, ridurre il peso dei singoli carichi.",
        "Sorveglianza sanitaria dei lavoratori esposti (art. 168 c. 2 lett. d).",
    ],
}


def _fattori(c: dict[str, Any], durata: str) -> dict[str, float]:
    return {
        "HM": hm(c["h"]), "VM": vm(c["v"]), "DM": dm(c["d"]), "AM": am(c["a"]),
        "FM": fm(c["frequenza"], durata, c["v"]), "CM": cm(c["presa"], c["v"]),
    }


def _misure(fattori: dict[str, float], colore: str) -> list[str]:
    misure = list(MISURE_GENERALI[colore])
    if colore != VERDE:
        peggiori = sorted((v, k) for k, v in fattori.items() if v < 0.9)
        misure += [MISURE_PER_FATTORE[k] for _, k in peggiori]
    return misure


def calcola_semplice(dati: dict[str, Any]) -> Esito:
    cp = COSTANTI_PESO[dati["lavoratori"]]
    fattori = _fattori(dati, dati["durata"])
    rwl = cp * math.prod(fattori.values())
    peso = dati["peso"]
    if rwl <= 0:
        indice = math.inf
        testo = "> 3 (fattore nullo)"
    else:
        indice = peso / rwl
        testo = numero_it(indice)
    nome, colore = classe(indice)
    dettagli = [
        ("Costante di peso (CP)", f"{numero_it(cp, 0)} kg"),
        ("Fattore altezza (VM)", numero_it(fattori["VM"])),
        ("Fattore dislocazione verticale (DM)", numero_it(fattori["DM"])),
        ("Fattore distanza orizzontale (HM)", numero_it(fattori["HM"])),
        ("Fattore asimmetria (AM)", numero_it(fattori["AM"])),
        ("Fattore frequenza (FM)", numero_it(fattori["FM"])),
        ("Fattore presa (CM)", numero_it(fattori["CM"])),
        ("Peso limite raccomandato (RWL)", f"{numero_it(rwl)} kg"),
        ("Peso effettivamente sollevato", f"{numero_it(peso, 1)} kg"),
        ("Indice di sollevamento (LI)", testo),
    ]
    note = []
    zero = [k for k, v in fattori.items() if v == 0]
    if zero:
        note.append(f"Fattori nulli ({', '.join(zero)}): i parametri sono fuori dai limiti del metodo, "
                    "il compito va riprogettato.")
    return Esito(indice, testo, nome, colore, dettagli, misure=_misure(fattori, colore), note=note)


def calcola_composto(dati: dict[str, Any]) -> Esito:
    cp = COSTANTI_PESO[dati["lavoratori"]]
    durata = dati["durata"]
    compiti = [c for c in dati["compiti"] if c["peso"] > 0 and c["frequenza"] > 0]
    if not compiti:
        return Esito(None, "-", "Dati insufficienti", GIALLO, note=["Inserire almeno un compito con peso e frequenza."])
    # Il fattore frequenza dei compiti combinati si legge, prudenzialmente,
    # nella colonna V < 75 cm se almeno un compito parte da sotto 75 cm.
    v_rif = min(c["v"] for c in compiti)
    righe = []
    calcoli = []
    for c in compiti:
        f = _fattori(c, durata)
        firwl = cp * f["HM"] * f["VM"] * f["DM"] * f["AM"] * f["CM"]
        strwl = firwl * f["FM"]
        fili = c["peso"] / firwl if firwl > 0 else math.inf
        stli = c["peso"] / strwl if strwl > 0 else math.inf
        calcoli.append((stli, fili, c))
        righe.append([c["nome"] or "Compito", numero_it(c["peso"], 1), numero_it(c["frequenza"], 1),
                      numero_it(firwl), numero_it(strwl), numero_it(fili), numero_it(stli)])
    calcoli.sort(key=lambda x: x[0], reverse=True)

    indice = calcoli[0][0]
    frequenza_cumulata = calcoli[0][2]["frequenza"]
    for _, fili, c in calcoli[1:]:
        fm_prima = fm(frequenza_cumulata, durata, v_rif)
        frequenza_cumulata += c["frequenza"]
        fm_dopo = fm(frequenza_cumulata, durata, v_rif)
        if fm_dopo <= 0 or fm_prima <= 0:
            indice = math.inf
            break
        indice += fili * (1 / fm_dopo - 1 / fm_prima)
    testo = numero_it(indice) if math.isfinite(indice) else "> 3 (frequenza oltre i limiti)"
    nome, colore = classe(indice)
    peggiore = calcoli[0][2]
    dettagli = [
        ("Costante di peso (CP)", f"{numero_it(cp, 0)} kg"),
        ("Numero di compiti", str(len(compiti))),
        ("Frequenza complessiva", f"{numero_it(sum(c['frequenza'] for c in compiti), 1)} atti/min"),
        ("Compito con indice più alto", peggiore["nome"] or "Compito"),
        ("Indice di sollevamento composto (CLI)", testo),
    ]
    misure = _misure(_fattori(peggiore, durata), colore)
    return Esito(indice, testo, nome, colore, dettagli,
                 ["Compito", "Peso kg", "Freq. atti/min", "FIRWL kg", "STRWL kg", "FILI", "STLI"],
                 righe, misure)


_CAMPI_COMUNI = (
    Campo("lavoratori", "Lavoratori esposti", "scelta", scelte=SCELTE_LAVORATORI, predefinito="M18-45"),
    Campo("durata", "Durata del compito nel turno", "scelta", scelte=SCELTE_DURATA, predefinito="lunga"),
)
_GEOMETRIA = (
    Campo("peso", "Peso sollevato", minimo=0, massimo=100, decimali=1, suffisso=" kg", predefinito=10),
    Campo("h", "Distanza orizzontale (H)", minimo=0, massimo=100, suffisso=" cm", predefinito=40,
          aiuto="Distanza tra il punto medio delle caviglie e il centro della presa."),
    Campo("v", "Altezza delle mani all'inizio (V)", minimo=0, massimo=200, suffisso=" cm", predefinito=75),
    Campo("d", "Dislocazione verticale (D)", minimo=0, massimo=200, suffisso=" cm", predefinito=50),
    Campo("a", "Angolo di asimmetria (A)", minimo=0, massimo=180, suffisso="°", predefinito=0),
    Campo("frequenza", "Frequenza", minimo=0, massimo=20, decimali=1, suffisso=" atti/min", predefinito=1),
    Campo("presa", "Qualità della presa", "scelta", scelte=SCELTE_PRESA, predefinito="discreta"),
)

DESCRIZIONE = (
    "Il metodo NIOSH, ripreso dalla norma UNI ISO 11228-1 richiamata dall'Allegato XXXIII del "
    "D.Lgs. 81/2008, calcola per il compito di sollevamento il peso limite raccomandato (RWL), "
    "riducendo la costante di peso con fattori che tengono conto di altezza e dislocazione del carico, "
    "distanza dal corpo, asimmetria, frequenza e qualità della presa. Il rapporto tra il peso "
    "sollevato e il peso limite è l'indice di sollevamento: fino a 0,85 il rischio è accettabile, "
    "tra 0,85 e 1 è richiesta attenzione, oltre 1 il rischio è presente e oltre 3 è elevato."
)

NIOSH_SEMPLICE = Metodo(
    chiave="niosh",
    nome="Sollevamento manuale - compito semplice (NIOSH)",
    norma="UNI ISO 11228-1",
    descrizione=DESCRIZIONE,
    campi=_CAMPI_COMUNI + _GEOMETRIA,
    calcola=calcola_semplice,
)

NIOSH_COMPOSTO = Metodo(
    chiave="niosh_composto",
    nome="Sollevamento manuale - compito composto (NIOSH, CLI)",
    norma="UNI ISO 11228-1",
    descrizione=DESCRIZIONE + " Con più compiti di sollevamento si calcola l'indice composto (CLI).",
    campi=_CAMPI_COMUNI,
    colonne_compiti=(Campo("nome", "Compito", "testo", predefinito=""),) + _GEOMETRIA,
    min_compiti=2,
    calcola=calcola_composto,
)
