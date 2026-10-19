"""Lettura delle schede di dati di sicurezza (SDS) in PDF.

Senza assistente AI si ricavano dal testo i dati più affidabili da
riconoscere: frasi H, avvertenza, data di revisione e nome commerciale.
L'assistente AI, se configurato, completa gli altri campi.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from sicurcantiere import sostanze


class ErroreSDS(Exception):
    pass


@dataclass
class DatiSDS:
    nome: str = ""
    produttore: str = ""
    codici_h: list[str] = field(default_factory=list)
    avvertenza: str = ""
    data_revisione: str = ""  # ISO yyyy-mm-dd
    stato_fisico: str = ""
    dpi: str = ""
    misure: str = ""
    conservazione: str = ""


def estrai_testo(percorso: str | Path) -> str:
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    try:
        lettore = PdfReader(str(percorso))
        testo = "\n".join(pagina.extract_text() or "" for pagina in lettore.pages)
    except (OSError, PdfReadError) as e:
        raise ErroreSDS(f"Impossibile leggere il PDF: {e}") from e
    testo = re.sub(r"[ \t\xa0]+", " ", testo)  # alcuni PDF separano le parole con tabulazioni
    if len(testo.strip()) < 50:
        raise ErroreSDS("Il PDF non contiene testo leggibile (probabilmente è una scansione).")
    return testo


_RE_DATA = re.compile(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4})")
_RE_REVISIONE = re.compile(r"(?:data\s+(?:di\s+)?revisione|revisione\s+del|revisionato\s+il|data\s+rev\.?)"
                           r"[^\d]{0,30}(\d{1,2}[./-]\d{1,2}[./-]\d{4})", re.IGNORECASE)
_RE_NOME = re.compile(r"(?:nome\s+(?:commerciale|del\s+prodotto)|denominazione\s+commerciale)\s*[:.]?\s*(.+)",
                      re.IGNORECASE)


def _data_iso(testo: str) -> str:
    m = _RE_DATA.search(testo)
    if not m:
        return ""
    giorno, mese, anno = (int(x) for x in m.groups())
    if not (1 <= giorno <= 31 and 1 <= mese <= 12):
        return ""
    return f"{anno:04d}-{mese:02d}-{giorno:02d}"


def analizza_testo(testo: str) -> DatiSDS:
    dati = DatiSDS(codici_h=sostanze.codici_h(testo))
    m = re.search(r"avvertenz[ae][^\n:]*[:\s]+(pericolo|attenzione)", testo, re.IGNORECASE)
    if m:
        dati.avvertenza = m.group(1).capitalize()
    m = _RE_REVISIONE.search(testo)
    if m:
        dati.data_revisione = _data_iso(m.group(1))
    m = _RE_NOME.search(testo)
    if m:
        dati.nome = m.group(1).strip().strip(":").strip()[:120]
    return dati


def leggi_pdf(percorso: str | Path) -> tuple[DatiSDS, str]:
    testo = estrai_testo(percorso)
    return analizza_testo(testo), testo
