"""Impronta del PC: tre componenti, ciascuno trasformato in hash con un sale legato alla licenza.

Componenti (su Windows):
- «sistema»: MachineGuid di Windows (cambia se si reinstalla Windows);
- «hardware»: UUID e numero di serie della scheda madre (restano anche reinstallando Windows);
- «nome»: nome del PC.

Al server arrivano solo gli hash: nessun dato dell'hardware in chiaro. Il sale lo assegna il
server, uno per licenza (resta lo stesso nei rinnovi), così le impronte di due licenze diverse sullo
stesso PC non sono collegabili tra loro; il certificato lo riporta, e a ogni avvio il programma
ricalcola l'impronta con quello. Due impronte sono dello stesso PC se coincidono almeno 2 componenti su 3:
cambiare il disco, la scheda di rete o il nome del PC non consuma un nuovo posto.
"""

from __future__ import annotations

import hashlib
import os
import platform
import subprocess
import sys

COMPONENTI = ("sistema", "hardware", "nome")
SALE = "SicurCantiere/impronta/v1"
MINIMO_UGUALI = 2

# valori che i fabbricanti lasciano al posto del numero di serie: non distinguono un PC da un altro
_SEGNAPOSTO = {"", "none", "default string", "to be filled by o.e.m.", "to be filled by oem", "not specified",
               "system serial number", "base board serial number", "0", "00000000-0000-0000-0000-000000000000",
               "ffffffff-ffff-ffff-ffff-ffffffffffff", "03000200-0400-0500-0006-000700080009"}


def _pulito(valore: str) -> str:
    valore = " ".join((valore or "").split())
    return "" if valore.lower() in _SEGNAPOSTO else valore


def _machine_guid() -> str:
    import winreg

    try:
        chiave = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0,
                                winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
        with chiave:
            return str(winreg.QueryValueEx(chiave, "MachineGuid")[0])
    except OSError:
        return ""


def _scheda_madre_windows() -> str:
    comando = ("$p=Get-CimInstance Win32_ComputerSystemProduct;$b=Get-CimInstance Win32_BaseBoard;"
               "Write-Output ($p.UUID + '|' + $b.SerialNumber)")
    try:
        uscita = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", comando],
                                capture_output=True, text=True, timeout=15,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
    except (OSError, subprocess.SubprocessError):
        return ""
    parti = [_pulito(p) for p in uscita.strip().split("|")]
    return "|".join(p for p in parti if p)


def _leggi_file(percorso: str) -> str:
    try:
        with open(percorso, encoding="ascii", errors="ignore") as f:
            return f.read().strip()
    except OSError:
        return ""


def componenti_locali() -> dict[str, str]:
    """Valori in chiaro dei componenti di questo PC: restano sul PC, al server va solo l'hash."""
    if sys.platform == "win32":
        sistema, hardware = _machine_guid(), _scheda_madre_windows()
    else:  # sviluppo e test su Linux o macOS
        sistema = _leggi_file("/etc/machine-id") or _leggi_file("/var/lib/dbus/machine-id")
        hardware = _leggi_file("/sys/class/dmi/id/product_uuid") or _leggi_file("/sys/class/dmi/id/board_serial")
    nome = os.environ.get("COMPUTERNAME") or platform.node()
    return {"sistema": _pulito(sistema), "hardware": _pulito(hardware), "nome": _pulito(nome).upper()}


def normalizza_codice(codice: str) -> str:
    return "".join(codice.split())


def sale_provvisorio() -> str:
    """Sale per un'attivazione offline quando il programma non ha ancora parlato con il server."""
    import secrets

    return "provvisorio:" + secrets.token_hex(12)


def calcola(sale: str, componenti: dict[str, str] | None = None) -> list[str]:
    """Le tre impronte (hash SHA-256 esadecimali) nell'ordine di COMPONENTI; "" se il componente manca."""
    componenti = componenti_locali() if componenti is None else componenti
    impronte = []
    for nome in COMPONENTI:
        valore = componenti.get(nome, "")
        if not valore:
            impronte.append("")
            continue
        dati = "\x1f".join((SALE, sale, nome, valore)).encode("utf-8")
        impronte.append(hashlib.sha256(dati).hexdigest())
    return impronte


def uguali(a: list[str], b: list[str]) -> int:
    """Quanti componenti coincidono (quelli mancanti non contano)."""
    return sum(1 for x, y in zip(a, b) if x and x == y)


def stesso_pc(a: list[str], b: list[str]) -> bool:
    return uguali(a, b) >= MINIMO_UGUALI


def nome_pc() -> str:
    """Nome del PC mostrato nell'elenco dei PC attivi della licenza."""
    return (os.environ.get("COMPUTERNAME") or platform.node() or "PC").strip()[:64]
