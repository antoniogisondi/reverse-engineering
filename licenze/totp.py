"""Codici a 6 cifre delle app di autenticazione (TOTP, RFC 6238), per la verifica in due passaggi.

Funziona con Google Authenticator, Microsoft Authenticator, Aegis, 1Password e simili.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

PERIODO = 30
TOLLERANZA = 1  # accetta anche il codice di 30 secondi prima o dopo (orologio del telefono non preciso)


def nuovo_segreto() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode()


def codice(segreto: str, contatore: int) -> str:
    chiave = base64.b32decode(segreto)
    h = hmac.new(chiave, struct.pack(">Q", contatore), hashlib.sha1).digest()
    pos = h[-1] & 0x0F
    return f"{(struct.unpack('>I', h[pos:pos + 4])[0] & 0x7FFFFFFF) % 1_000_000:06d}"


def verifica(segreto: str, inserito: str, ultimo: int = 0, adesso: float | None = None) -> int | None:
    """Contatore del codice se è giusto e non già usato (> ultimo), altrimenti None."""
    inserito = "".join(inserito.split())
    if not segreto or len(inserito) != 6 or not inserito.isdigit():
        return None
    attuale = int((time.time() if adesso is None else adesso) // PERIODO)
    for contatore in range(attuale - TOLLERANZA, attuale + TOLLERANZA + 1):
        if contatore > ultimo and hmac.compare_digest(codice(segreto, contatore), inserito):
            return contatore
    return None


def indirizzo(segreto: str, utente: str, emittente: str = "SicurCantiere Licenze") -> str:
    """Indirizzo otpauth:// da mostrare come QR code."""
    return (f"otpauth://totp/{quote(emittente)}:{quote(utente)}?secret={segreto}"
            f"&issuer={quote(emittente)}&period={PERIODO}&digits=6")
