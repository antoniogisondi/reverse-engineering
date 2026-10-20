"""Trasporto manuale in piano: UNI ISO 11228-1 (massa cumulata) e tavole di Snook e Ciriello.

Due verifiche, come nelle linee di indirizzo nazionali sulla movimentazione manuale dei carichi:
1. massa cumulata trasportata in un minuto, in un'ora e nel turno, confrontata con i limiti
   della UNI ISO 11228-1 in funzione della distanza (ridotti di un terzo in condizioni
   sfavorevoli);
2. per ogni trasporto, peso confrontato con quello accettabile per il 90% della popolazione
   secondo le tavole di Snook e Ciriello (genere, altezza delle mani, distanza, frequenza).
L'indice di trasporto è il rapporto più alto tra valore reale e valore raccomandato.
"""

from __future__ import annotations

from typing import Any

from sicurcantiere.valutazioni import snook
from sicurcantiere.valutazioni.base import GIALLO, ROSSO, VERDE, VIOLA, Campo, Esito, Metodo, numero_it
from sicurcantiere.valutazioni.niosh import COSTANTI_PESO, SCELTE_LAVORATORI, classe

# Distanza massima (m) -> limiti di massa cumulata (kg/min, kg/h, kg/8h), UNI ISO 11228-1.
LIMITI_MASSA = (
    (1, (120, 7200, 10000)),
    (2, (75, 4500, 10000)),
    (4, (60, 3000, 10000)),
    (10, (30, 1500, 10000)),
    (20, (15, 750, 6000)),
)
SCELTE_ALTEZZA = (
    ("alta", "Mani all'altezza della vita (gomiti flessi)"),
    ("bassa", "Braccia distese lungo il corpo"),
)
SCELTE_CONDIZIONI = (
    ("buone", "Favorevoli"),
    ("sfavorevoli", "Sfavorevoli (ambiente, prese molto in basso o sopra le spalle)"),
)


def limiti_massa(distanza: float, sfavorevoli: bool) -> tuple[float, float, float]:
    limiti = next((l for d, l in LIMITI_MASSA if distanza <= d), LIMITI_MASSA[-1][1])
    fattore = 2 / 3 if sfavorevoli else 1.0
    return tuple(x * fattore for x in limiti)  # type: ignore[return-value]


def masse_cumulate(trasporti: list[dict[str, Any]]) -> tuple[float, float, float]:
    """Massa (kg) nel minuto, nell'ora e nel turno più gravosi.

    I trasporti si considerano in sequenza: nel minuto conta il compito con il ritmo più alto,
    nell'ora si sommano i compiti a ritmo più alto fino a coprire 60 minuti.
    """
    ritmi = sorted(((t["peso"] * t["frequenza"], t["durata"]) for t in trasporti), reverse=True)
    al_minuto = ritmi[0][0] if ritmi else 0.0
    ora, minuti = 0.0, 0.0
    for ritmo, durata in ritmi:
        quota = min(durata, 60 - minuti)
        ora += ritmo * quota
        minuti += quota
        if minuti >= 60:
            break
    turno = sum(r * d for r, d in ritmi)
    return al_minuto, ora, turno


MISURE = {
    "massa": "Ridurre la massa cumulata: carrelli, transpallet, montacarichi o nastri trasportatori per "
             "i materiali movimentati di frequente, rotazione tra più addetti.",
    "distanza": "Avvicinare i depositi dei materiali al punto di utilizzo per accorciare i percorsi.",
    "peso": "Ridurre il peso dei singoli colli (confezioni più piccole, sacchi da 25 kg o meno) o "
            "trasportarli in due.",
    "frequenza": "Ridurre la frequenza dei trasporti alternandoli con attività che non richiedono sforzo.",
}
MISURE_COMUNI = {
    VERDE: ["Rischio accettabile: mantenere percorsi sgombri e in piano e ripetere la valutazione se "
            "cambiano carichi o organizzazione."],
    GIALLO: ["Informare e formare i lavoratori sulla corretta movimentazione dei carichi (art. 169).",
             "Mantenere percorsi sgombri, in piano e illuminati."],
    ROSSO: ["Adottare ausili meccanici o riorganizzare il lavoro per ridurre il rischio (art. 168).",
            "Sorveglianza sanitaria dei lavoratori addetti (art. 168 c. 2 lett. d).",
            "Informazione, formazione e addestramento specifici (art. 169)."],
}
MISURE_COMUNI[VIOLA] = ["Intervento immediato: il trasporto non può essere svolto manualmente nelle "
                        "condizioni attuali."] + MISURE_COMUNI[ROSSO]


def calcola(dati: dict[str, Any]) -> Esito:
    trasporti = [t for t in dati["compiti"] if t["peso"] > 0 and t["frequenza"] > 0 and t["durata"] > 0]
    if not trasporti:
        return Esito(None, "-", "Dati insufficienti", GIALLO,
                     note=["Inserire almeno un trasporto con peso, frequenza e durata."])
    genere = "F" if dati["lavoratori"].startswith("F") else "M"
    massa_riferimento = COSTANTI_PESO[dati["lavoratori"]]
    sfavorevoli = dati["condizioni"] == "sfavorevoli"
    distanza = max(t["distanza"] for t in trasporti)
    lim_min, lim_ora, lim_turno = limiti_massa(distanza, sfavorevoli)
    m_min, m_ora, m_turno = masse_cumulate(trasporti)
    indici_massa = {"minuto": m_min / lim_min, "ora": m_ora / lim_ora, "turno": m_turno / lim_turno}

    note: list[str] = []
    righe = []
    indici_snook: list[tuple[float, dict]] = []
    for t in trasporti:
        nome = t["nome"] or "Trasporto"
        try:
            racc, info = snook.peso_trasporto(genere, t["altezza"], t["distanza"], t["frequenza"] * 60)
        except snook.FuoriTabella as e:
            note.append(f"«{nome}»: {e}; trasporto a rischio elevato.")
            indici_snook.append((float("inf"), t))
            righe.append([nome, numero_it(t["peso"], 1), numero_it(t["frequenza"], 1),
                          numero_it(t["distanza"], 1), "-", "fuori tabella", numero_it(t["peso"] * t["frequenza"], 1)])
            continue
        if info["oltre"]:
            note.append(f"«{nome}»: distanza oltre gli {numero_it(info['distanza'], 1)} m delle tavole, "
                        "usati i valori della distanza massima.")
        indice_t = t["peso"] / racc
        indici_snook.append((indice_t, t))
        righe.append([nome, numero_it(t["peso"], 1), numero_it(t["frequenza"], 1), numero_it(t["distanza"], 1),
                      numero_it(racc, 0), numero_it(indice_t), numero_it(t["peso"] * t["frequenza"], 1)])
        if t["peso"] > massa_riferimento:
            note.append(f"«{nome}»: peso superiore alla massa di riferimento di "
                        f"{numero_it(massa_riferimento, 0)} kg per i lavoratori indicati.")
    indici_snook.sort(key=lambda x: x[0], reverse=True)

    indice_massa = max(indici_massa.values())
    indice = max(indice_massa, indici_snook[0][0])
    finito = indice != float("inf")
    nome_classe, colore = classe(indice)
    testo = numero_it(indice) if finito else "> 3 (fuori tabella)"

    misure: list[str] = []
    if colore != VERDE:
        if indice_massa >= indici_snook[0][0]:
            misure.append(MISURE["massa"])
            if distanza > 10:
                misure.append(MISURE["distanza"])
        else:
            misure.append(MISURE["peso"])
            t = indici_snook[0][1]
            if t["frequenza"] > 1:
                misure.append(MISURE["frequenza"])
            if t["distanza"] > 4.3:
                misure.append(MISURE["distanza"])
    misure += MISURE_COMUNI[colore]
    if m_turno > 10000:
        note.append("Massa cumulata oltre 10.000 kg nel turno, limite da non superare in ogni caso.")

    rid = " (ridotti di un terzo)" if sfavorevoli else ""
    dettagli = [
        ("Distanza di trasporto più lunga", f"{numero_it(distanza, 1)} m"),
        (f"Massa cumulata al minuto / limite{rid}", f"{numero_it(m_min, 1)} / {numero_it(lim_min, 0)} kg"),
        (f"Massa cumulata all'ora / limite{rid}", f"{numero_it(m_ora, 0)} / {numero_it(lim_ora, 0)} kg"),
        (f"Massa cumulata nel turno / limite{rid}", f"{numero_it(m_turno, 0)} / {numero_it(lim_turno, 0)} kg"),
        ("Indice di massa cumulata", numero_it(indice_massa)),
        ("Indice più alto dalle tavole di Snook e Ciriello",
         numero_it(indici_snook[0][0]) if indici_snook[0][0] != float("inf") else "fuori tabella"),
        ("Indice di trasporto", testo),
    ]
    note.append("Pesi raccomandati dalle tavole di Snook e Ciriello (1991) per il 90% della popolazione; "
                "limiti di massa cumulata della UNI ISO 11228-1.")
    return Esito(indice, testo, nome_classe, colore, dettagli,
                 ["Trasporto", "Peso kg", "Freq. /min", "Distanza m", "Peso racc. kg", "Indice", "kg/min"],
                 righe, misure, note)


TRASPORTO = Metodo(
    chiave="trasporto",
    nome="Trasporto manuale di carichi",
    norma="UNI ISO 11228-1 - tavole di Snook e Ciriello",
    descrizione=(
        "Il trasporto manuale di un carico per almeno un metro si valuta, secondo la UNI ISO 11228-1 "
        "richiamata dall'Allegato XXXIII del D.Lgs. 81/2008, con la massa cumulata trasportata in un "
        "minuto, in un'ora e nell'intero turno, confrontata con i limiti raccomandati in funzione della "
        "distanza (10.000 kg nel turno fino a 10 m, 6.000 kg per 20 m e oltre), ridotti di almeno un "
        "terzo in condizioni sfavorevoli. Ogni trasporto è inoltre confrontato con il peso accettabile "
        "per il 90% della popolazione secondo le tavole di Snook e Ciriello. L'indice di trasporto è "
        "il rapporto più alto tra valore reale e raccomandato: fino a 0,85 il rischio è accettabile, "
        "tra 0,85 e 1 serve attenzione, oltre 1 il rischio è presente."
    ),
    campi=(
        Campo("lavoratori", "Lavoratori esposti", "scelta", scelte=SCELTE_LAVORATORI, predefinito="M18-45"),
        Campo("condizioni", "Condizioni di trasporto", "scelta", scelte=SCELTE_CONDIZIONI, predefinito="buone"),
    ),
    colonne_compiti=(
        Campo("nome", "Trasporto", "testo", predefinito=""),
        Campo("peso", "Peso", minimo=0, massimo=100, decimali=1, suffisso=" kg", predefinito=15),
        Campo("frequenza", "Frequenza", minimo=0, massimo=30, decimali=2, suffisso=" trasporti/min",
              predefinito=1),
        Campo("durata", "Durata nel turno", minimo=0, massimo=720, suffisso=" min", predefinito=60),
        Campo("distanza", "Distanza", minimo=0, massimo=100, decimali=1, suffisso=" m", predefinito=4),
        Campo("altezza", "Posizione delle mani", "scelta", scelte=SCELTE_ALTEZZA, predefinito="bassa"),
    ),
    min_compiti=1,
    calcola=calcola,
)
