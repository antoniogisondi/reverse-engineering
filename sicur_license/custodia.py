"""Dove il programma conserva il certificato e l'ultima ora vista.

Su Windows i file sono cifrati con DPAPI (CryptProtectData), cioè legati all'utente di Windows di
quel PC: copiati su un altro PC non si leggono. Sugli altri sistemi (sviluppo e test) restano in
chiaro, leggibili solo dall'utente. La cartella è %APPDATA%\\SicurCantiere\\licenza, oppure quella
indicata da SICUR_LICENSE_CARTELLA.

L'«ultima ora vista» serve contro l'orologio spostato indietro: si conserva la più recente, e se
la data del PC torna indietro di molto il programma chiede di collegarsi a internet.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ENTROPIA = b"SicurCantiere/licenza/v1"


def cartella() -> Path:
    scelta = os.environ.get("SICUR_LICENSE_CARTELLA")
    if scelta:
        base = Path(scelta)
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home()) / "SicurCantiere" / "licenza"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config") / "sicurcantiere" / "licenza"
    base.mkdir(parents=True, exist_ok=True)
    return base


# --- DPAPI ---

def _blob(dati: bytes):
    import ctypes
    from ctypes import wintypes

    class DATA_BLOB(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    buffer = ctypes.create_string_buffer(dati, len(dati))
    return DATA_BLOB(len(dati), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char))), buffer, DATA_BLOB


def _dpapi(dati: bytes, cifra: bool) -> bytes:
    import ctypes

    ingresso, _buffer, DATA_BLOB = _blob(dati)
    entropia, _buffer_e, _ = _blob(ENTROPIA)
    uscita = DATA_BLOB()
    funzione = ctypes.windll.crypt32.CryptProtectData if cifra else ctypes.windll.crypt32.CryptUnprotectData
    ok = funzione(ctypes.byref(ingresso), None, ctypes.byref(entropia), None, None, 0x1,  # senza finestre
                  ctypes.byref(uscita))
    if not ok:
        raise OSError("Impossibile leggere i dati della licenza su questo PC.")
    try:
        return ctypes.string_at(uscita.pbData, uscita.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(uscita.pbData)


def proteggi(dati: bytes) -> bytes:
    return _dpapi(dati, True) if sys.platform == "win32" else dati


def apri(dati: bytes) -> bytes:
    return _dpapi(dati, False) if sys.platform == "win32" else dati


def _scrivi(nome: str, dati: bytes) -> None:
    percorso = cartella() / nome
    temporaneo = percorso.with_suffix(".tmp")
    temporaneo.write_bytes(proteggi(dati))
    if sys.platform != "win32":
        os.chmod(temporaneo, 0o600)
    os.replace(temporaneo, percorso)


def _leggi(nome: str) -> bytes | None:
    percorso = cartella() / nome
    try:
        return apri(percorso.read_bytes())
    except OSError:  # assente, o copiato da un altro PC o utente
        return None


# --- certificato ---

def salva_certificato(testo: str) -> None:
    _scrivi("certificato.dat", testo.encode("utf-8"))


def leggi_certificato() -> str:
    dati = _leggi("certificato.dat")
    return dati.decode("utf-8", errors="replace") if dati else ""


def elimina_certificato() -> None:
    (cartella() / "certificato.dat").unlink(missing_ok=True)


# --- ultima ora vista ---

def ultima_ora_vista() -> datetime | None:
    dati = _leggi("orologio.dat")
    try:
        return datetime.fromisoformat(json.loads(dati)["ora"]) if dati else None
    except (ValueError, KeyError, TypeError):
        return None


def registra_ora(ora: datetime) -> None:
    """Conserva l'ora più recente vista (mai una precedente)."""
    precedente = ultima_ora_vista()
    if precedente is None or ora > precedente:
        _scrivi("orologio.dat", json.dumps({"ora": ora.astimezone(timezone.utc).isoformat()}).encode())


# --- dati di servizio (impronte calcolate, ultimo controllo online) ---

def leggi_memoria() -> dict:
    dati = _leggi("memoria.dat")
    try:
        valore = json.loads(dati) if dati else {}
    except ValueError:
        return {}
    return valore if isinstance(valore, dict) else {}


def salva_memoria(valori: dict) -> None:
    _scrivi("memoria.dat", json.dumps(valori, ensure_ascii=False).encode("utf-8"))
