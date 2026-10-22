"""Movimenti ripetitivi degli arti superiori: indice OCRA (UNI ISO 11228-3).

ATA = azioni tecniche effettivamente svolte nel turno
    = somma sui compiti di (frequenza azioni/min x durata min)
RTA = azioni tecniche raccomandate
    = somma sui compiti di (CF x FoM x PoM x ReM x AdM x durata) x RcM x DuM
Indice OCRA = ATA / RTA, con CF = 30 azioni/min.

Le tabelle dei fattori sono riportate qui sotto in un unico punto, per poterle
confrontare facilmente con la norma.
"""

from __future__ import annotations

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

CF = 30.0  # costante di frequenza (azioni tecniche/min)

# Forza percepita (scala di Borg CR-10) -> fattore forza FoM.
TABELLA_FORZA = [(0.5, 1.00), (1, 0.85), (1.5, 0.75), (2, 0.65), (2.5, 0.55), (3, 0.45),
                 (3.5, 0.35), (4, 0.20), (4.5, 0.10), (5, 0.01)]

# Punteggio di postura (articolazione più sollecitata) -> fattore postura PoM.
TABELLA_POSTURA = [(3, 1.00), (7, 0.70), (11, 0.60), (15, 0.50)]
POSTURA_OLTRE = 0.33

SCELTE_STEREOTIPIA = (
    ("assente", "Assente (1,00)"),
    ("presente", "Gesti uguali per oltre metà ciclo o ciclo < 15 s (0,70)"),
)
FATTORE_STEREOTIPIA = {"assente": 1.0, "presente": 0.7}

SCELTE_COMPLEMENTARI = (
    ("assenti", "Assenti (1,00)"),
    ("terzo", "Presenti per circa 1/3 del tempo (0,95)"),
    ("due_terzi", "Presenti per circa 2/3 del tempo (0,90)"),
    ("sempre", "Presenti per tutto il tempo (0,80)"),
)
FATTORE_COMPLEMENTARI = {"assenti": 1.0, "terzo": 0.95, "due_terzi": 0.90, "sempre": 0.80}

# Ore del turno senza adeguato recupero -> fattore recupero RcM.
TABELLA_RECUPERO = [(0, 1.00), (1, 0.90), (2, 0.80), (3, 0.70), (4, 0.60), (5, 0.45),
                    (6, 0.25), (7, 0.10), (8, 0.00)]

# Minuti di lavoro ripetitivo nel turno -> fattore durata DuM (limite superiore dell'intervallo).
TABELLA_DURATA = [(60, 2.00), (120, 1.70), (180, 1.50), (240, 1.30), (300, 1.20), (360, 1.10),
                  (420, 1.05), (480, 1.00), (539, 0.95), (599, 0.90), (659, 0.85), (719, 0.80)]
DURATA_OLTRE = 0.75

SCELTE_ARTO = (("destro", "Destro"), ("sinistro", "Sinistro"), ("entrambi", "Entrambi"))


def fattore_forza(borg: float) -> float:
    return interpola(TABELLA_FORZA, borg)


def fattore_postura(punteggio: float) -> float:
    for limite, valore in TABELLA_POSTURA:
        if punteggio <= limite:
            return valore
    return POSTURA_OLTRE


def fattore_recupero(ore: float) -> float:
    return interpola(TABELLA_RECUPERO, ore)


def fattore_durata(minuti: float) -> float:
    for limite, valore in TABELLA_DURATA:
        if minuti <= limite:
            return valore
    return DURATA_OLTRE


def classe(indice: float) -> tuple[str, str]:
    if indice <= 2.2:
        return "Rischio accettabile (fascia verde)", VERDE
    if indice <= 3.5:
        return "Rischio molto lieve o incerto (fascia gialla)", GIALLO
    if indice <= 4.5:
        return "Rischio lieve (fascia rossa)", ROSSO
    if indice <= 9.0:
        return "Rischio medio (fascia rossa)", ROSSO
    return "Rischio elevato (fascia viola)", VIOLA


MISURE_PER_FATTORE = {
    "frequenza": "Ridurre la frequenza delle azioni tecniche: eliminare azioni inutili, meccanizzare fasi del ciclo.",
    "FoM": "Ridurre la forza richiesta: utensili più leggeri o bilanciati, attrezzi a motore, manutenzione degli utensili.",
    "PoM": "Migliorare le posture di spalla, gomito, polso e mano: regolare altezze e distanze, utensili ergonomici.",
    "ReM": "Ridurre la stereotipia alternando compiti con movimenti diversi.",
    "AdM": "Eliminare i fattori complementari: vibrazioni, colpi con la mano, guanti inadeguati, freddo.",
    "RcM": "Introdurre pause di recupero adeguate (almeno 8-10 minuti ogni ora) o compiti di controllo visivo.",
}
MISURE_GENERALI = {
    VERDE: ["Nessun intervento specifico; mantenere informazione e formazione."],
    GIALLO: ["Informare e formare i lavoratori; ripetere la valutazione se cambiano ritmi o compiti.",
             "Valutare la sorveglianza sanitaria."],
    ROSSO: ["Riprogettare compiti e postazioni con interventi tecnici e organizzativi.",
            "Sorveglianza sanitaria dei lavoratori esposti; formazione specifica."],
    VIOLA: ["Interventi di riprogettazione prioritari e immediati su ritmi, forza e posture.",
            "Sorveglianza sanitaria dei lavoratori esposti; formazione specifica."],
}


def calcola(dati: dict[str, Any]) -> Esito:
    compiti = [c for c in dati["compiti"] if c["durata"] > 0]
    if not compiti:
        return Esito(None, "-", "Dati insufficienti", GIALLO, note=["Inserire almeno un compito con la durata."])
    durata_totale = sum(c["durata"] for c in compiti)
    rcm = fattore_recupero(dati["ore_senza_recupero"])
    dum = fattore_durata(durata_totale)
    ata = 0.0
    rta_base = 0.0
    righe = []
    peggiori: dict[str, float] = {}
    for c in compiti:
        fo = fattore_forza(c["forza"])
        po = fattore_postura(c["postura"])
        re = FATTORE_STEREOTIPIA[c["stereotipia"]]
        ad = FATTORE_COMPLEMENTARI[c["complementari"]]
        ata_c = c["azioni_min"] * c["durata"]
        rta_c = CF * fo * po * re * ad * c["durata"]
        ata += ata_c
        rta_base += rta_c
        for chiave, valore in (("FoM", fo), ("PoM", po), ("ReM", re), ("AdM", ad)):
            peggiori[chiave] = min(peggiori.get(chiave, 1.0), valore)
        if c["azioni_min"] > 40:
            peggiori["frequenza"] = min(peggiori.get("frequenza", 1.0), 40 / c["azioni_min"])
        righe.append([c["nome"] or "Compito", numero_it(c["durata"], 0), numero_it(c["azioni_min"], 1),
                      numero_it(fo), numero_it(po), numero_it(re), numero_it(ad),
                      numero_it(ata_c, 0), numero_it(rta_c, 0)])
    peggiori["RcM"] = rcm
    rta = rta_base * rcm * dum
    if rta <= 0:
        indice = float("inf")
        testo = "> 9 (recupero nullo)"
    else:
        indice = ata / rta
        testo = numero_it(indice, 1)
    nome, colore = classe(indice)
    dettagli = [
        ("Arto valutato", dict(SCELTE_ARTO)[dati["arto"]]),
        ("Durata complessiva del lavoro ripetitivo", f"{numero_it(durata_totale, 0)} min"),
        ("Fattore recupero (RcM)", numero_it(rcm)),
        ("Fattore durata (DuM)", numero_it(dum)),
        ("Azioni tecniche svolte (ATA)", numero_it(ata, 0)),
        ("Azioni tecniche raccomandate (RTA)", numero_it(rta, 0)),
        ("Indice OCRA (ATA/RTA)", testo),
    ]
    misure = list(MISURE_GENERALI[colore])
    if colore != VERDE:
        misure += [MISURE_PER_FATTORE[k] for v, k in sorted((v, k) for k, v in peggiori.items()) if v < 0.9]
    return Esito(indice, testo, nome, colore, dettagli,
                 ["Compito", "Durata min", "Azioni/min", "FoM", "PoM", "ReM", "AdM", "ATA", "RTA parziale"],
                 righe, misure)


OCRA = Metodo(
    chiave="ocra",
    nome="Movimenti ripetitivi degli arti superiori (indice OCRA)",
    norma="UNI ISO 11228-3",
    descrizione=(
        "Il metodo OCRA, indicato come metodo preferenziale dalla norma UNI ISO 11228-3, confronta "
        "il numero di azioni tecniche effettivamente svolte nel turno (ATA) con il numero di azioni "
        "raccomandate (RTA). Le azioni raccomandate partono da 30 azioni al minuto e si riducono in "
        "funzione di forza, postura, stereotipia, fattori complementari, carenza di recupero e "
        "durata del lavoro ripetitivo. Fino a 2,2 il rischio è accettabile, tra 2,3 e 3,5 è molto "
        "lieve o incerto, oltre 3,5 il rischio è presente (lieve fino a 4,5, medio fino a 9, "
        "elevato oltre). La valutazione si esegue per ciascun arto."
    ),
    campi=(
        Campo("arto", "Arto valutato", "scelta", scelte=SCELTE_ARTO, predefinito="destro"),
        Campo("ore_senza_recupero", "Ore del turno senza adeguato recupero", minimo=0, massimo=8,
              decimali=1, suffisso=" ore", predefinito=2),
    ),
    colonne_compiti=(
        Campo("nome", "Compito", "testo", predefinito=""),
        Campo("durata", "Durata netta", minimo=0, massimo=720, suffisso=" min", predefinito=240),
        Campo("azioni_min", "Azioni tecniche", minimo=0, massimo=200, decimali=1, suffisso="/min",
              predefinito=30),
        Campo("forza", "Forza (Borg CR-10)", minimo=0, massimo=10, decimali=1, predefinito=1),
        Campo("postura", "Punteggio postura", minimo=0, massimo=30, predefinito=4,
              aiuto="Punteggio dell'articolazione più sollecitata (spalla, gomito, polso, mano)."),
        Campo("stereotipia", "Stereotipia", "scelta", scelte=SCELTE_STEREOTIPIA, predefinito="assente"),
        Campo("complementari", "Fattori complementari", "scelta", scelte=SCELTE_COMPLEMENTARI,
              predefinito="assenti"),
    ),
    min_compiti=1,
    calcola=calcola,
)
