"""Struttura di una fase di lavoro: lavoratori con attrezzi e rischi, macchine con i loro rischi."""

from __future__ import annotations

from typing import Any

from sicurcantiere import anagrafiche
from sicurcantiere.repository import Repository

MACCHINA = "Macchina"


def struttura_fase(repo: Repository, fase_id: int) -> dict[str, Any]:
    """Raggruppa i rischi della fase per origine.

    I rischi senza origine (o con un'origine che non è un'attrezzatura della fase) sono quelli
    della lavorazione, a cui è esposto l'addetto; gli altri appartengono alla macchina o
    all'attrezzo da cui derivano. Le macchine hanno un operatore, gli attrezzi e le opere
    provvisionali sono usati dall'addetto.
    """
    fase = repo.leggi("fasi", fase_id) or {}
    rischi = repo.rischi(fase_id=fase_id)
    attrezzature = repo.elenco("attrezzature", fase_id=fase_id)
    nomi = {a["nome"] for a in attrezzature}

    def con_rischi(a: dict[str, Any]) -> dict[str, Any]:
        return {**a, "rischi": [r for r in rischi if r["fonte"] == a["nome"]]}

    lavoratori = repo.lavoratori_fase(fase_id)
    return {
        "fase": fase,
        "addetto": fase.get("addetto") or "Addetto alla fase",
        "lavoratori": [anagrafiche.nominativo(l) for l in lavoratori],
        "rischi_lavorazione": [r for r in rischi if not r["fonte"] or r["fonte"] not in nomi],
        "attrezzi": [con_rischi(a) for a in attrezzature if a["tipo"] != MACCHINA],
        "macchine": [con_rischi(a) for a in attrezzature if a["tipo"] == MACCHINA],
    }
