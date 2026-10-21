"""Licenze offline: verifica della firma, piani, scadenza e prova gratuita.

Una licenza è un codice «SC1-<dati>.<firma>»: i dati (JSON in base64url) dicono cliente, piano,
scadenza e postazioni; la firma Ed25519 è fatta dal gestionale delle licenze sul server
dell'ufficio con la chiave privata, che non lascia mai il server. Il programma contiene solo la
chiave pubblica e verifica la firma senza collegarsi a internet: un codice modificato, anche di
una lettera, non è più valido.

Alla scadenza il programma continua a funzionare (opzione scelta per il prodotto), ma non
propone gli aggiornamenti pubblicati dopo la scadenza. Senza licenza c'è la prova gratuita:
30 giorni con un solo cantiere.

Nessuna dipendenza da Qt: il modulo è usato anche dal gestionale sul server.
"""

from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass, field
from datetime import date, timedelta

PREFISSO = "SC1-"
GIORNI_PROVA = 30

# Chiave pubblica Ed25519 (32 byte in base64) del gestionale delle licenze. Vuota = controllo
# delle licenze non ancora attivo: tutto funziona come prima. La variabile d'ambiente serve ai test.
CHIAVE_PUBBLICA = ""

# Contatti mostrati a chi non ha la licenza per un programma («Come acquistarlo»).
CONTATTO_ACQUISTO = ""

PIANI: dict[str, tuple[str, frozenset[str]]] = {
    "pos": ("POS", frozenset({"pos"})),
    "psc": ("PSC", frozenset({"psc"})),
    "pimus": ("PiMUS", frozenset({"pimus"})),
    "completo": ("Completo", frozenset({"pos", "psc", "pimus"})),
    "studio": ("Studio", frozenset({"pos", "psc", "pimus"})),
}


class ErroreLicenza(Exception):
    """Codice di licenza non valido."""


@dataclass(frozen=True)
class Licenza:
    id: str
    cliente: str
    piano: str
    emessa: date
    scadenza: date | None = None  # None = senza scadenza
    postazioni: int = 1
    note: str = ""

    @property
    def nome_piano(self) -> str:
        return PIANI.get(self.piano, (self.piano, frozenset()))[0]

    @property
    def programmi(self) -> frozenset[str]:
        return PIANI.get(self.piano, ("", frozenset()))[1]

    def scaduta(self, oggi: date | None = None) -> bool:
        return self.scadenza is not None and (oggi or date.today()) > self.scadenza

    def dati(self) -> dict:
        return {"i": self.id, "c": self.cliente, "p": self.piano, "d": self.emessa.isoformat(),
                "s": self.scadenza.isoformat() if self.scadenza else None, "n": self.postazioni,
                "x": self.note}

    @classmethod
    def da_dati(cls, d: dict) -> Licenza:
        try:
            return cls(id=str(d["i"]), cliente=str(d["c"]), piano=str(d["p"]),
                       emessa=date.fromisoformat(d["d"]),
                       scadenza=date.fromisoformat(d["s"]) if d.get("s") else None,
                       postazioni=int(d.get("n") or 1), note=str(d.get("x") or ""))
        except (KeyError, TypeError, ValueError) as e:
            raise ErroreLicenza("Il codice di licenza non è completo.") from e


def _b64(dati: bytes) -> str:
    return base64.urlsafe_b64encode(dati).decode().rstrip("=")


def _da_b64(testo: str) -> bytes:
    return base64.urlsafe_b64decode(testo + "=" * (-len(testo) % 4))


def chiave_pubblica() -> str:
    return os.environ.get("SICURCANTIERE_CHIAVE_LICENZE") or CHIAVE_PUBBLICA


def controllo_attivo() -> bool:
    return bool(chiave_pubblica())


def firma(licenza: Licenza, chiave_privata: bytes) -> str:
    """Codice di licenza firmato (usato dal gestionale sul server)."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    dati = json.dumps(licenza.dati(), ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    firma_ = Ed25519PrivateKey.from_private_bytes(chiave_privata).sign(dati)
    return f"{PREFISSO}{_b64(dati)}.{_b64(firma_)}"


def leggi(codice: str, chiave: str | None = None) -> Licenza:
    """Verifica il codice e restituisce la licenza; ErroreLicenza se non è valido."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    codice = "".join(codice.split())  # tollera spazi e a capo copiati dall'email
    if not codice.startswith(PREFISSO) or "." not in codice:
        raise ErroreLicenza("Il codice di licenza non è nel formato giusto (deve iniziare con SC1-).")
    dati_b64, firma_b64 = codice[len(PREFISSO):].split(".", 1)
    try:
        dati, firma_ = _da_b64(dati_b64), _da_b64(firma_b64)
        pubblica = Ed25519PublicKey.from_public_bytes(base64.b64decode(chiave or chiave_pubblica()))
        pubblica.verify(firma_, dati)
        contenuto = json.loads(dati.decode("utf-8"))
    except (InvalidSignature, ValueError, UnicodeDecodeError) as e:
        raise ErroreLicenza("Il codice di licenza non è valido: controllare di averlo copiato per intero.") from e
    return Licenza.da_dati(contenuto)


# --- stato per un programma ---

LICENZA, PROVA, PROVA_FINITA, NON_INCLUSO, LIBERO = "licenza", "prova", "prova_finita", "non_incluso", "libero"


@dataclass
class Stato:
    tipo: str
    licenza: Licenza | None = None
    giorni_prova: int = 0
    messaggi: list[str] = field(default_factory=list)
    scaduta: bool = False  # licenza scaduta: il programma funziona, ma senza nuovi aggiornamenti

    @property
    def utilizzabile(self) -> bool:
        return self.tipo in (LICENZA, PROVA, LIBERO)


def stato(programma: str, codice: str, inizio_prova: date | None, oggi: date | None = None) -> Stato:
    """Cosa può fare il programma: licenza valida, prova in corso o finita, programma non incluso."""
    oggi = oggi or date.today()
    if not controllo_attivo():
        return Stato(LIBERO)
    messaggi = []
    if codice:
        try:
            licenza = leggi(codice)
        except ErroreLicenza as e:
            messaggi.append(str(e))  # codice rovinato: si torna alla prova
        else:
            return Stato(LICENZA if programma in licenza.programmi else NON_INCLUSO, licenza,
                         scaduta=licenza.scaduta(oggi))
    risultato = _stato_prova(inizio_prova or oggi, oggi)
    risultato.messaggi = messaggi
    return risultato


def _stato_prova(inizio: date, oggi: date) -> Stato:
    rimasti = GIORNI_PROVA - (oggi - inizio).days
    return Stato(PROVA, giorni_prova=rimasti) if rimasti > 0 else Stato(PROVA_FINITA)


def fine_prova(inizio: date) -> date:
    return inizio + timedelta(days=GIORNI_PROVA)
