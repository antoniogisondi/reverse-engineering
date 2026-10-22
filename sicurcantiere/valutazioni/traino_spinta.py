"""Traino e spinta manuale con tutto il corpo: UNI ISO 11228-2, metodo 1.

Per ogni azione le forze misurate con il dinamometro (iniziale, per mettere in movimento
l'oggetto, e di mantenimento, per tenerlo in movimento) si confrontano con le forze
raccomandate dalle tavole di Snook e Ciriello per il 90% della popolazione, scelte in base a
genere, altezza delle mani, distanza percorsa e frequenza:
    indice = forza misurata / forza raccomandata
Si considera l'indice più alto tra forza iniziale e di mantenimento e tra le azioni.
Fasce: fino a 0,85 accettabile, fino a 1 attenzione, oltre 1 rischio presente.
"""

from __future__ import annotations

from typing import Any

from sicurcantiere.valutazioni import snook
from sicurcantiere.valutazioni.base import GIALLO, ROSSO, VERDE, VIOLA, Campo, Esito, Metodo, numero_it
from sicurcantiere.valutazioni.niosh import classe

SCELTE_GENERE = (
    ("M", "Solo maschile"),
    ("F", "Femminile o mista (limiti per le donne)"),
)
SCELTE_AZIONE = (("spinta", "Spinta"), ("traino", "Traino"))
SCELTE_CONDIZIONI = (
    ("buone", "Nessun fattore aggravante rilevante"),
    ("sfavorevoli", "Prevalgono fattori aggravanti (pavimento, ruote, spazi, postura)"),
)

MISURE = {
    "iniziale": "Ridurre la forza iniziale: ruote di diametro maggiore e ben mantenute, freni facili da "
                "sbloccare, carichi più leggeri o suddivisi, pavimenti lisci e senza soglie.",
    "mantenimento": "Ridurre la forza di mantenimento: diminuire gli attriti (ruote e cuscinetti, superfici "
                    "compatte), eliminare pendenze e superfici cedevoli come terra o ghiaia.",
    "altezza": "Portare le maniglie tra l'altezza delle anche e quella delle spalle (circa 90-110 cm).",
    "distanza": "Accorciare i percorsi o usare mezzi a motore (transpallet elettrici, motocarriole, "
                "argani) per i tragitti lunghi.",
    "frequenza": "Ridurre la frequenza delle azioni o alternare il compito con attività senza sforzo.",
}
MISURE_COMUNI = {
    VERDE: ["Rischio accettabile: mantenere in efficienza carrelli e percorsi e ripetere la valutazione "
            "se cambiano carichi o mezzi."],
    GIALLO: ["Informare e formare i lavoratori sulla corretta tecnica di traino e spinta (art. 169).",
             "Programmare la manutenzione di ruote e carrelli e la pulizia dei percorsi."],
    ROSSO: ["Riprogettare il compito o adottare ausili meccanici; in attesa, ridurre i carichi (art. 168).",
            "Sorveglianza sanitaria dei lavoratori addetti (art. 168, comma 2, lettera d).",
            "Informazione, formazione e addestramento specifici (art. 169)."],
}
MISURE_COMUNI[VIOLA] = ["Intervento immediato: il compito non può essere svolto manualmente nelle condizioni "
                        "attuali."] + MISURE_COMUNI[ROSSO]


def _valuta_azione(genere: str, a: dict[str, Any]) -> dict[str, Any]:
    risultato: dict[str, Any] = {"azione": a, "errore": ""}
    try:
        for forza in ("iniziale", "mantenimento"):
            racc, info = snook.forza_raccomandata(a["tipo"], genere, forza, a["altezza"], a["distanza"],
                                                  a["frequenza"])
            misurata = a["forza_" + forza]
            risultato[forza] = (misurata, racc, misurata / racc if racc else 0.0)
            risultato["info"] = info
    except snook.FuoriTabella as e:
        risultato["errore"] = str(e)
    return risultato


def calcola(dati: dict[str, Any]) -> Esito:
    genere = dati["genere"]
    azioni = [a for a in dati["compiti"] if a["forza_iniziale"] > 0 or a["forza_mantenimento"] > 0]
    if not azioni:
        return Esito(None, "-", "Dati insufficienti", GIALLO,
                     note=["Inserire almeno un'azione con le forze misurate."])
    valutate = [_valuta_azione(genere, a) for a in azioni]
    note: list[str] = []
    righe = []
    indice = 0.0
    peggiore = None
    for v in valutate:
        a = v["azione"]
        nome = a["nome"] or dict(SCELTE_AZIONE)[a["tipo"]]
        if v["errore"]:
            note.append(f"«{nome}»: {v['errore']}. L'azione supera le condizioni delle tavole psicofisiche "
                        "ed è da considerare a rischio elevato.")
            righe.append([nome, dict(SCELTE_AZIONE)[a["tipo"]], "-", "-", "-", "-", "fuori tabella"])
            indice = float("inf")
            peggiore = v
            continue
        fi, fm = v["iniziale"], v["mantenimento"]
        massimo = max(fi[2], fm[2])
        if massimo > indice:
            indice, peggiore = massimo, v
        info = v["info"]
        if info["oltre"]:
            note.append(f"«{nome}»: distanza oltre i {numero_it(info['distanza'], 1)} m delle tavole, "
                        "si usano i valori della distanza massima.")
        righe.append([nome, dict(SCELTE_AZIONE)[a["tipo"]],
                      f"{numero_it(fi[0], 0)} / {numero_it(fi[1], 0)}", numero_it(fi[2]),
                      f"{numero_it(fm[0], 0)} / {numero_it(fm[1], 0)}", numero_it(fm[2]),
                      f"h {info['altezza']} cm, {numero_it(info['distanza'], 1)} m, "
                      f"{snook.intervallo_testo(info['intervallo'])}"])

    finito = indice != float("inf")
    nome_classe, colore = classe(indice)
    if dati["condizioni"] == "sfavorevoli" and colore in (VERDE, GIALLO):
        nome_classe, colore = "Rischio presente per i fattori aggravanti", ROSSO
        note.append("Le forze rientrano nei valori raccomandati, ma la prevalenza di fattori aggravanti "
                    "porta il rischio in fascia rossa (UNI ISO 11228-2, metodo 1).")
    testo = numero_it(indice) if finito else "> 3 (fuori tabella)"

    misure: list[str] = []
    if peggiore is not None and colore != VERDE:
        a = peggiore["azione"]
        if peggiore["errore"]:
            misure += [MISURE["frequenza"], MISURE["distanza"]]
        else:
            fi, fm = peggiore["iniziale"], peggiore["mantenimento"]
            misure.append(MISURE["iniziale"] if fi[2] >= fm[2] else MISURE["mantenimento"])
            if a["altezza"] < 80 or a["altezza"] > 125:
                misure.append(MISURE["altezza"])
            if a["distanza"] > 15:
                misure.append(MISURE["distanza"])
            if a["frequenza"] > 60:
                misure.append(MISURE["frequenza"])
    misure += MISURE_COMUNI[colore]

    dettagli = [
        ("Popolazione", dict(SCELTE_GENERE)[genere]),
        ("Azioni valutate", str(len(valutate))),
        ("Azione con indice più alto", (peggiore["azione"]["nome"] or "Azione") if peggiore else "-"),
        ("Indice di rischio", testo),
    ]
    note.append("Forze raccomandate dalle tavole di Snook e Ciriello (1991) per il 90% della popolazione; "
                "1 kg di forza = 9,81 N.")
    return Esito(indice if finito else float("inf"), testo, nome_classe, colore, dettagli,
                 ["Azione", "Tipo", "F. iniziale kg (mis./racc.)", "Indice iniz.",
                  "F. mantenimento kg (mis./racc.)", "Indice mant.", "Riferimento in tabella"],
                 righe, misure, note)


TRAINO_SPINTA = Metodo(
    chiave="traino_spinta",
    nome="Traino e spinta (Snook e Ciriello)",
    norma="UNI ISO 11228-2, metodo 1",
    descrizione=(
        "Il metodo 1 della norma UNI ISO 11228-2, richiamata dall'Allegato XXXIII del D.Lgs. 81/2008, "
        "confronta le forze di spinta e di traino misurate con un dinamometro con quelle accettabili "
        "per il 90% della popolazione secondo le tavole psicofisiche di Snook e Ciriello. Le forze "
        "raccomandate dipendono dal genere, dall'altezza delle mani da terra, dalla distanza percorsa e "
        "dalla frequenza delle azioni; si valutano sia la forza iniziale, per mettere in movimento "
        "l'oggetto, sia quella di mantenimento. L'indice è il rapporto tra forza misurata e "
        "raccomandata: fino a 0,85 il rischio è accettabile, tra 0,85 e 1 serve attenzione, oltre 1 "
        "il rischio è presente. Per popolazioni miste si usano i limiti femminili."
    ),
    campi=(
        Campo("genere", "Lavoratori esposti", "scelta", scelte=SCELTE_GENERE, predefinito="M"),
        Campo("condizioni", "Fattori aggravanti", "scelta", scelte=SCELTE_CONDIZIONI, predefinito="buone"),
    ),
    colonne_compiti=(
        Campo("nome", "Azione / mezzo", "testo", predefinito=""),
        Campo("tipo", "Tipo", "scelta", scelte=SCELTE_AZIONE, predefinito="spinta"),
        Campo("forza_iniziale", "Forza iniziale", minimo=0, massimo=200, decimali=1, suffisso=" kg",
              predefinito=20, aiuto="Picco di forza misurato per mettere in movimento l'oggetto."),
        Campo("forza_mantenimento", "Forza di mantenimento", minimo=0, massimo=200, decimali=1,
              suffisso=" kg", predefinito=10, aiuto="Forza media misurata durante il movimento."),
        Campo("altezza", "Altezza delle mani", minimo=30, massimo=200, suffisso=" cm", predefinito=95),
        Campo("distanza", "Distanza", minimo=0, massimo=200, decimali=1, suffisso=" m", predefinito=7.6),
        Campo("frequenza", "Frequenza", minimo=0, massimo=3600, decimali=2, suffisso=" azioni/ora",
              predefinito=12, aiuto="1 al minuto = 60; 1 ogni 5 minuti = 12; 1 per turno = 0,13."),
    ),
    min_compiti=1,
    calcola=calcola,
)
