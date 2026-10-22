"""Modelli di cantiere: un cantiere salvato come punto di partenza per i successivi (per esempio
«Ristrutturazione di appartamento», «Rifacimento copertura»), con lavorazioni, rischi, testi della
relazione e costi già pronti. Il modello non porta con sé i documenti composti né le revisioni.

I modelli stanno nella cartella dei dati del programma, divisi per tipo di file (PSC, POS, PiMUS).
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path


def cartella_modelli() -> Path:
    from sicurcantiere.db import cartella_copie

    if os.environ.get("SICURCANTIERE_MODELLI"):
        return Path(os.environ["SICURCANTIERE_MODELLI"])
    return cartella_copie().parent / "modelli di cantiere"


def _nome_file(nome: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "-", nome).strip() or "Modello"


def elenco(estensione: str) -> list[Path]:
    """Modelli disponibili per il tipo di file indicato (".scs", ".spo", ".spm"), in ordine di nome."""
    cartella = cartella_modelli()
    if not cartella.is_dir():
        return []
    return sorted(cartella.glob(f"*{estensione}"), key=lambda p: p.stem.lower())


def salva_come_modello(sorgente: sqlite3.Connection, nome: str, estensione: str) -> Path:
    """Copia il cantiere aperto come modello, senza documenti composti e revisioni."""
    cartella = cartella_modelli()
    cartella.mkdir(parents=True, exist_ok=True)
    destinazione = cartella / f"{_nome_file(nome)}{estensione}"
    if destinazione.exists():
        destinazione.unlink()
    copia = sqlite3.connect(destinazione)
    try:
        sorgente.backup(copia)
        for tabella in ("composizioni", "personalizzazioni", "revisioni"):
            try:
                copia.execute(f"DELETE FROM {tabella}")
            except sqlite3.OperationalError:
                pass  # tabella assente nei file più vecchi
        copia.commit()
        copia.execute("VACUUM")
    finally:
        copia.close()
    return destinazione


def elimina(modello: Path) -> None:
    modello.unlink(missing_ok=True)


def crea_da_modello(modello: Path, destinazione: Path) -> Path:
    """Nuovo cantiere a partire dal modello (copia del file)."""
    sorgente = sqlite3.connect(modello)
    copia = sqlite3.connect(destinazione)
    try:
        sorgente.backup(copia)
    finally:
        copia.close()
        sorgente.close()
    return destinazione
