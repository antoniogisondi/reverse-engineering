"""Calcoli sul progetto: livelli di rischio, interferenze, uomini-giorno, obblighi."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

# Matrice P x D (probabilità 1-4, danno 1-4).
CLASSI_RISCHIO = [
    (9, "Molto alto"),
    (6, "Alto"),
    (3, "Medio"),
    (1, "Basso"),
]

# Art. 99 c. 1 lett. c: notifica obbligatoria con impresa unica oltre questa soglia.
SOGLIA_UOMINI_GIORNO = 200


def livello_rischio(probabilita: int, danno: int) -> int:
    return int(probabilita) * int(danno)


def classe_rischio(livello: int) -> str:
    for soglia, nome in CLASSI_RISCHIO:
        if livello >= soglia:
            return nome
    return "Basso"


def data(valore: str | None) -> date | None:
    if not valore:
        return None
    try:
        return date.fromisoformat(valore)
    except ValueError:
        return None


def giorni_lavorativi(inizio: date, fine: date) -> int:
    """Giorni dal lunedì al venerdì compresi tra inizio e fine (estremi inclusi)."""
    if fine < inizio:
        return 0
    totale = (fine - inizio).days + 1
    settimane, resto = divmod(totale, 7)
    giorni = settimane * 5
    giorno = inizio + timedelta(days=settimane * 7)
    for _ in range(resto):
        if giorno.weekday() < 5:
            giorni += 1
        giorno += timedelta(days=1)
    return giorni


def uomini_giorno(fasi: list[dict[str, Any]]) -> int:
    totale = 0
    for f in fasi:
        inizio, fine = data(f.get("data_inizio")), data(f.get("data_fine"))
        if inizio and fine:
            totale += giorni_lavorativi(inizio, fine) * max(int(f.get("lavoratori") or 0), 0)
    return totale


def periodo_lavori(fasi: list[dict[str, Any]]) -> tuple[date, date] | None:
    inizi = [d for f in fasi if (d := data(f.get("data_inizio")))]
    fini = [d for f in fasi if (d := data(f.get("data_fine")))]
    if not inizi or not fini:
        return None
    return min(inizi), max(fini)


@dataclass(frozen=True)
class Interferenza:
    fase_a: dict[str, Any]
    fase_b: dict[str, Any]
    inizio: date
    fine: date


def interferenze(fasi: list[dict[str, Any]]) -> list[Interferenza]:
    """Coppie di fasi sovrapposte nel tempo eseguite da imprese diverse.

    Le fasi senza impresa assegnata sono considerate potenzialmente
    interferenti con tutte le altre, finché l'impresa non viene indicata.
    """
    risultato = []
    datate = [
        (f, i, e)
        for f in fasi
        if (i := data(f.get("data_inizio"))) and (e := data(f.get("data_fine"))) and i <= e
    ]
    for n, (a, ia, fa) in enumerate(datate):
        for b, ib, fb in datate[n + 1:]:
            inizio, fine = max(ia, ib), min(fa, fb)
            if inizio > fine:
                continue
            stessa_impresa = a.get("impresa_id") and a.get("impresa_id") == b.get("impresa_id")
            if not stessa_impresa:
                risultato.append(Interferenza(a, b, inizio, fine))
    return risultato


def totale_costi(costi: list[dict[str, Any]]) -> float:
    return round(sum(float(c["quantita"] or 0) * float(c["prezzo_unitario"] or 0) for c in costi), 2)


def imprese_esecutrici(imprese: list[dict[str, Any]], fasi: list[dict[str, Any]]) -> int:
    """Numero di imprese (escl. lavoratori autonomi) che eseguono almeno una fase.

    Se nessuna fase ha un'impresa assegnata si contano le imprese in elenco.
    """
    assegnate = {f["impresa_id"] for f in fasi if f.get("impresa_id")}
    candidati = [i for i in imprese if i["tipo"] != "Lavoratore autonomo"]
    if assegnate:
        candidati = [i for i in candidati if i["id"] in assegnate]
    return len(candidati)


@dataclass(frozen=True)
class Obblighi:
    imprese: int
    uomini_giorno: int
    psc: bool
    notifica: bool

    def descrizione(self) -> list[str]:
        righe = [
            f"Imprese esecutrici: {self.imprese}",
            f"Entità presunta del cantiere: {self.uomini_giorno} uomini-giorno",
        ]
        if self.psc:
            righe.append("Nomina CSP/CSE e redazione del PSC obbligatorie (art. 90 c. 3-4).")
        else:
            righe.append("PSC non obbligatorio con un'unica impresa esecutrice (resta il POS dell'impresa).")
        if self.notifica:
            righe.append("Notifica preliminare obbligatoria (art. 99).")
        else:
            righe.append("Notifica preliminare non obbligatoria.")
        return righe


def obblighi(imprese: list[dict[str, Any]], fasi: list[dict[str, Any]]) -> Obblighi:
    n = imprese_esecutrici(imprese, fasi)
    ug = uomini_giorno(fasi)
    piu_imprese = n > 1
    return Obblighi(
        imprese=n,
        uomini_giorno=ug,
        psc=piu_imprese,
        notifica=piu_imprese or ug >= SOGLIA_UOMINI_GIORNO,
    )
