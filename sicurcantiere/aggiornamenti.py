"""Aggiornamenti del programma: controllo dell'ultima versione pubblicata e scaricamento.

Le versioni sono pubblicate dal workflow «Installatore Windows» come release del repository,
con l'installatore anche sotto il nome fisso SicurCantiere-setup.exe. L'indirizzo si può
cambiare con la variabile SICURCANTIERE_URL_AGGIORNAMENTI (per esempio per un repository
pubblico che contiene solo gli installatori).
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable

from sicurcantiere import __version__

URL_ULTIMA_VERSIONE = "https://api.github.com/repos/antoniogisondi/sicurcantiere/releases/latest"
NOME_INSTALLATORE = "SicurCantiere-setup.exe"


class ErroreAggiornamento(Exception):
    """Controllo o scaricamento non riuscito (rete assente, indirizzo non raggiungibile...)."""


@dataclass(frozen=True)
class Versione:
    numero: str
    url_installatore: str
    pagina: str
    note: str
    pubblicata: date | None = None


def numero(testo: str) -> tuple[int, ...]:
    """«v0.13.1» -> (0, 13, 1); le parti non numeriche sono ignorate."""
    return tuple(int(n) for n in re.findall(r"\d+", testo)[:4])


def piu_recente(pubblicata: str, installata: str = __version__) -> bool:
    return numero(pubblicata) > numero(installata)


def url_controllo() -> str:
    return os.environ.get("SICURCANTIERE_URL_AGGIORNAMENTI") or URL_ULTIMA_VERSIONE


def ultima_versione(timeout: float = 8, apri: Callable = urllib.request.urlopen) -> Versione:
    """Ultima versione pubblicata, con l'indirizzo del suo installatore."""
    richiesta = urllib.request.Request(url_controllo(), headers={
        "Accept": "application/vnd.github+json", "User-Agent": f"SicurCantiere/{__version__}"})
    try:
        with apri(richiesta, timeout=timeout) as risposta:
            dati = json.loads(risposta.read().decode("utf-8"))
    except (OSError, ValueError) as e:
        raise ErroreAggiornamento(f"Impossibile controllare gli aggiornamenti: {e}") from e
    allegati = {a.get("name", ""): a.get("browser_download_url", "") for a in dati.get("assets") or []}
    url = allegati.get(NOME_INSTALLATORE) or next(
        (u for n, u in allegati.items() if n.lower().endswith("-setup.exe")), "")
    if not dati.get("tag_name") or not url:
        raise ErroreAggiornamento("La versione pubblicata non contiene l'installatore.")
    try:
        pubblicata = date.fromisoformat(str(dati.get("published_at") or "")[:10])
    except ValueError:
        pubblicata = None
    return Versione(dati["tag_name"].lstrip("v"), url, dati.get("html_url", ""), dati.get("body") or "", pubblicata)


def inclusa_nella_licenza(versione: Versione, scadenza: date | None) -> bool:
    """Con la licenza scaduta si ricevono solo le versioni pubblicate prima della scadenza."""
    return scadenza is None or versione.pubblicata is None or versione.pubblicata <= scadenza


def scarica(url: str, destinazione: str | Path, avanzamento: Callable[[int, int], bool] | None = None,
            timeout: float = 30, apri: Callable = urllib.request.urlopen) -> Path:
    """Scarica l'installatore; `avanzamento(letti, totale)` restituisce False per annullare."""
    destinazione = Path(destinazione)
    parziale = destinazione.with_name(destinazione.name + ".part")
    richiesta = urllib.request.Request(url, headers={"User-Agent": f"SicurCantiere/{__version__}"})
    try:
        with apri(richiesta, timeout=timeout) as risposta, open(parziale, "wb") as file:
            totale = int(risposta.headers.get("Content-Length") or 0)
            letti = 0
            while blocco := risposta.read(256 * 1024):
                file.write(blocco)
                letti += len(blocco)
                if avanzamento and avanzamento(letti, totale) is False:
                    raise ErroreAggiornamento("Scaricamento annullato.")
        if totale and letti != totale:
            raise ErroreAggiornamento("Scaricamento incompleto: riprovare.")
        parziale.replace(destinazione)
    except OSError as e:
        raise ErroreAggiornamento(f"Scaricamento non riuscito: {e}") from e
    finally:
        parziale.unlink(missing_ok=True)
    return destinazione
