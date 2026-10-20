"""Controllo automatico di un modulo dell'archivio: ``python -m sicurcantiere.archivio_dati.verifica modulo``.

Un modulo può definire LAVORAZIONI (lista di fase()), ATTREZZATURE (dizionario di
attrezzatura()) e MANCANTI (dizionario nome -> (tipo, motivo)).
"""

from __future__ import annotations

import importlib
import sys
from typing import Any

from sicurcantiere.anagrafiche import CATALOGO_DPI
from sicurcantiere.archivio_dati.base import CATALOGO, CATEGORIE, TIPOLOGIE

DPI_NOTI = {v for voci in CATALOGO_DPI.values() for v in voci}


def _testo(valore: Any, minimo: int = 3) -> bool:
    return isinstance(valore, str) and len(valore.strip()) >= minimo


def _rischio(r: dict[str, Any], dove: str) -> list[str]:
    errori = []
    if not _testo(r.get("descrizione")):
        errori.append(f"{dove}: rischio senza descrizione")
    for k in ("probabilita", "danno"):
        if r.get(k) not in (1, 2, 3, 4):
            errori.append(f"{dove}: {k} deve essere 1-4")
    if not _testo(r.get("misure"), 20):
        errori.append(f"{dove}: misure troppo brevi")
    if not _testo(r.get("dpi")):
        errori.append(f"{dove}: DPI mancanti")
    return errori


def verifica(modulo: Any) -> list[str]:
    errori: list[str] = []
    codici: set[str] = set()
    for f in getattr(modulo, "LAVORAZIONI", []):
        dove = f.get("codice", "?")
        if dove in codici:
            errori.append(f"{dove}: codice duplicato")
        codici.add(dove)
        if f.get("categoria") not in CATEGORIE:
            errori.append(f"{dove}: categoria sconosciuta {f.get('categoria')!r}")
        if not f.get("tipologie") or set(f["tipologie"]) - set(TIPOLOGIE):
            errori.append(f"{dove}: tipologie non valide")
        for campo, minimo in (("gruppo", 3), ("descrizione", 5), ("dettaglio", 40), ("addetto", 8)):
            if not _testo(f.get(campo), minimo):
                errori.append(f"{dove}: {campo} mancante o troppo breve")
        if not 0 <= float(f.get("incidenza_manodopera", -1)) <= 100:
            errori.append(f"{dove}: incidenza fuori da 0-100")
        nuove = getattr(modulo, "ATTREZZATURE", {})
        mancanti = getattr(modulo, "MANCANTI", {})
        for a in f.get("attrezzature", []):
            if a not in CATALOGO and a not in nuove and a not in mancanti:
                errori.append(f"{dove}: attrezzatura non in catalogo: {a!r}")
        if not f.get("rischi"):
            errori.append(f"{dove}: nessun rischio")
        for r in f.get("rischi", []):
            errori += _rischio(r, dove)
    for nome, a in getattr(modulo, "ATTREZZATURE", {}).items():
        if nome not in CATALOGO:
            errori.append(f"{nome}: non presente in CATALOGO (base.py)")
        elif a.get("tipo") != CATALOGO[nome]:
            errori.append(f"{nome}: tipo diverso da CATALOGO")
        if not a.get("rischi"):
            errori.append(f"{nome}: nessun rischio")
        for r in a.get("rischi", []):
            errori += _rischio(r, nome)
        s = a.get("scheda", {})
        if not _testo(s.get("descrizione"), 20):
            errori.append(f"{nome}: descrizione della scheda mancante")
        for k in ("prima", "durante", "dopo", "dpi"):
            if not s.get(k) or not all(_testo(x) for x in s[k]):
                errori.append(f"{nome}: scheda senza voci «{k}»")
    return errori


def main(argv: list[str]) -> int:
    totale = 0
    for nome in argv:
        modulo = importlib.import_module(f"sicurcantiere.archivio_dati.{nome}")
        errori = verifica(modulo)
        fasi = len(getattr(modulo, "LAVORAZIONI", []))
        attrezzi = len(getattr(modulo, "ATTREZZATURE", {}))
        print(f"{nome}: {fasi} fasi, {attrezzi} attrezzature, {len(errori)} errori")
        for e in errori:
            print("  -", e)
        totale += len(errori)
    return 1 if totale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
