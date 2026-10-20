"""Cartelli di sicurezza e icone dei DPI usati nei documenti.

Le immagini sono disegnate per SicurCantiere (scripts/genera_segnali.py) con forme e colori
della segnaletica di sicurezza (D.Lgs. 81/2008 Titolo V e Allegati XXIV-XXXII): cerchio blu per
gli obblighi, cerchio rosso barrato per i divieti, triangolo giallo per gli avvertimenti,
quadrato verde per il soccorso, quadrato rosso per l'antincendio. Sono rappresentazioni
semplificate per i documenti: i cartelli posati in cantiere devono essere conformi alla
UNI EN ISO 7010.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

CARTELLA = Path(__file__).parent / "risorse" / "segnali"

OBBLIGO, DIVIETO, AVVERTIMENTO, SOCCORSO, ANTINCENDIO = "obbligo", "divieto", "avvertimento", "soccorso", "antincendio"


@dataclass(frozen=True)
class Segnale:
    chiave: str
    tipo: str
    testo: str

    @property
    def file(self) -> Path:
        return CARTELLA / f"{self.chiave}.png"


SEGNALI: dict[str, Segnale] = {s.chiave: s for s in (
    Segnale("casco", OBBLIGO, "Casco di protezione obbligatorio"),
    Segnale("guanti", OBBLIGO, "Guanti di protezione obbligatori"),
    Segnale("calzature", OBBLIGO, "Calzature di sicurezza obbligatorie"),
    Segnale("udito", OBBLIGO, "Protezione dell'udito obbligatoria"),
    Segnale("occhiali", OBBLIGO, "Protezione degli occhi obbligatoria"),
    Segnale("visiera", OBBLIGO, "Protezione del viso obbligatoria"),
    Segnale("maschera", OBBLIGO, "Protezione delle vie respiratorie obbligatoria"),
    Segnale("imbracatura", OBBLIGO, "Imbracatura di sicurezza obbligatoria"),
    Segnale("altavisibilita", OBBLIGO, "Indumenti ad alta visibilità obbligatori"),
    Segnale("indumenti", OBBLIGO, "Indumenti di protezione obbligatori"),
    Segnale("accesso", DIVIETO, "Vietato l'accesso ai non addetti ai lavori"),
    Segnale("sotto_carichi", DIVIETO, "Vietato passare o sostare sotto i carichi sospesi"),
    Segnale("fiamme", DIVIETO, "Vietato fumare e usare fiamme libere"),
    Segnale("pericolo", AVVERTIMENTO, "Pericolo generico"),
    Segnale("tensione", AVVERTIMENTO, "Pericolo tensione elettrica"),
    Segnale("carichi", AVVERTIMENTO, "Attenzione ai carichi sospesi"),
    Segnale("caduta", AVVERTIMENTO, "Pericolo di caduta dall'alto"),
    Segnale("mezzi", AVVERTIMENTO, "Attenzione ai mezzi in movimento"),
    Segnale("scavo", AVVERTIMENTO, "Pericolo di caduta negli scavi"),
    Segnale("soccorso", SOCCORSO, "Pronto soccorso"),
    Segnale("estintore", ANTINCENDIO, "Estintore"),
)}

# DPI: parole chiave (minuscole) -> icona di obbligo.
DPI_ICONE: list[tuple[tuple[str, ...], str]] = [
    (("casco", "elmetto", "copricapo"), "casco"),
    (("guant",), "guanti"),
    (("calzatur", "scarpe", "stival"), "calzature"),
    (("otoprot", "cuffie", "inserti auricolari", "udito"), "udito"),
    (("occhial",), "occhiali"),
    (("visiera", "schermo"), "visiera"),
    (("mascher", "facciale", "ffp", "respirator", "autorespir", "filtr"), "maschera"),
    (("imbracatura", "anticaduta", "cordino", "linea vita", "retrattile"), "imbracatura"),
    (("alta visibilit",), "altavisibilita"),
    (("indumenti", "tuta", "grembiule", "pantaloni"), "indumenti"),
]

# Rischi: parole chiave (minuscole) -> cartelli da prevedere.
RISCHI_SEGNALI: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
    (("caduta dall'alto", "lavori in quota", "caduta dal"), ("caduta", "imbracatura")),
    (("elettr",), ("tensione",)),
    (("carico sospeso", "carichi sospesi", "caduta di materiale", "sollevamento"), ("carichi", "sotto_carichi")),
    (("investimento", "mezzi", "ribaltamento"), ("mezzi",)),
    (("seppelliment", "scav", "sprofond"), ("scavo",)),
    (("incendio", "esplosion", "fiamm"), ("fiamme", "estintore")),
    (("rumore",), ("udito",)),
    (("polver", "fibre", "silice", "chimic"), ("maschera",)),
    (("schegge", "proiezione", "getti", "schizzi"), ("occhiali",)),
]

SEGNALI_BASE = ("accesso", "casco", "calzature", "guanti", "altavisibilita", "pericolo", "soccorso", "estintore")


def icone_dpi(testi: list[str] | str) -> list[str]:
    """Icone di obbligo corrispondenti ai DPI citati nei testi, senza ripetizioni e in ordine fisso."""
    testo = " ".join(testi if isinstance(testi, list) else [testi]).lower()
    return [icona for parole, icona in DPI_ICONE if any(p in testo for p in parole)]


def icona_dpi(voce: str) -> str | None:
    icone = icone_dpi(voce)
    return icone[0] if icone else None


def segnali_cantiere(rischi: list[str], dpi: list[str]) -> list[Segnale]:
    """Cartelli da posare in cantiere: quelli di base più quelli richiesti da rischi e DPI."""
    chiavi = list(SEGNALI_BASE)
    testo = " ".join(rischi).lower()
    for parole, segnali in RISCHI_SEGNALI:
        if any(p in testo for p in parole):
            chiavi += segnali
    chiavi += icone_dpi(dpi)
    ordine = {k: i for i, k in enumerate(SEGNALI)}
    return [SEGNALI[k] for k in sorted(dict.fromkeys(chiavi), key=lambda k: (
        [DIVIETO, AVVERTIMENTO, OBBLIGO, SOCCORSO, ANTINCENDIO].index(SEGNALI[k].tipo), ordine[k]))]
