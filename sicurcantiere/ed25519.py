"""Firma Ed25519 in Python puro, secondo l'implementazione di riferimento della RFC 8032 (sezione 6).

Serve al programma per verificare le licenze senza librerie compilate (che negli eseguibili per
Windows possono mancare). Non è a tempo costante: va bene per verificare una firma pubblica, non
per firmare con una chiave segreta su un sistema condiviso. Il gestionale delle licenze firma con
la libreria `cryptography`.
"""

from __future__ import annotations

import hashlib

P = 2 ** 255 - 19
Q = 2 ** 252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, -1, P) % P
_RADICE_MENO_UNO = pow(2, (P - 1) // 4, P)


def _hash_mod_q(dati: bytes) -> int:
    return int.from_bytes(hashlib.sha512(dati).digest(), "little") % Q


# Punti in coordinate estese (X, Y, Z, T), con x = X/Z, y = Y/Z, x*y = T/Z.

def _somma(a: tuple, b: tuple) -> tuple:
    p1 = (a[1] - a[0]) * (b[1] - b[0]) % P
    p2 = (a[1] + a[0]) * (b[1] + b[0]) % P
    c = 2 * a[3] * b[3] * D % P
    d = 2 * a[2] * b[2] % P
    e, f, g, h = p2 - p1, d - c, d + c, p2 + p1
    return (e * f, g * h, f * g, e * h)


def _moltiplica(s: int, punto: tuple) -> tuple:
    risultato = (0, 1, 1, 0)  # elemento neutro
    while s > 0:
        if s & 1:
            risultato = _somma(risultato, punto)
        punto = _somma(punto, punto)
        s >>= 1
    return risultato


def _uguali(a: tuple, b: tuple) -> bool:
    return (a[0] * b[2] - b[0] * a[2]) % P == 0 and (a[1] * b[2] - b[1] * a[2]) % P == 0


def _recupera_x(y: int, segno: int) -> int | None:
    if y >= P:
        return None
    x2 = (y * y - 1) * pow(D * y * y + 1, -1, P) % P
    if x2 == 0:
        return None if segno else 0
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P != 0:
        x = x * _RADICE_MENO_UNO % P
    if (x * x - x2) % P != 0:
        return None
    if (x & 1) != segno:
        x = P - x
    return x


_GY = 4 * pow(5, -1, P) % P
_GX = _recupera_x(_GY, 0)
G = (_GX, _GY, 1, _GX * _GY % P)


def _comprimi(punto: tuple) -> bytes:
    z_inv = pow(punto[2], -1, P)
    x, y = punto[0] * z_inv % P, punto[1] * z_inv % P
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")


def _decomprimi(dati: bytes) -> tuple | None:
    if len(dati) != 32:
        return None
    y = int.from_bytes(dati, "little")
    segno = y >> 255
    y &= (1 << 255) - 1
    x = _recupera_x(y, segno)
    return None if x is None else (x, y, 1, x * y % P)


def _espandi(segreto: bytes) -> tuple[int, bytes]:
    h = hashlib.sha512(segreto).digest()
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def chiave_pubblica(segreto: bytes) -> bytes:
    a, _ = _espandi(segreto)
    return _comprimi(_moltiplica(a, G))


def firma(segreto: bytes, messaggio: bytes) -> bytes:
    a, prefisso = _espandi(segreto)
    pubblica = _comprimi(_moltiplica(a, G))
    r = _hash_mod_q(prefisso + messaggio)
    r_compresso = _comprimi(_moltiplica(r, G))
    h = _hash_mod_q(r_compresso + pubblica + messaggio)
    return r_compresso + int.to_bytes((r + h * a) % Q, 32, "little")


def verifica(pubblica: bytes, messaggio: bytes, firma_: bytes) -> bool:
    if len(pubblica) != 32 or len(firma_) != 64:
        return False
    punto_a = _decomprimi(pubblica)
    punto_r = _decomprimi(firma_[:32])
    if punto_a is None or punto_r is None:
        return False
    s = int.from_bytes(firma_[32:], "little")
    if s >= Q:
        return False
    h = _hash_mod_q(firma_[:32] + pubblica + messaggio)
    return _uguali(_moltiplica(s, G), _somma(punto_r, _moltiplica(h, punto_a)))
