"""Certificato di licenza firmato: cosa può fare un PC, fino a quando.

Il file del certificato è un JSON con due parti, ognuna «dati» (JSON in base64) e «firma»:
- «servizio»: la chiave di servizio del server e il periodo in cui può firmare, firmati con la
  chiave radice;
- «certificato»: i dati della licenza per questo PC, firmati con la chiave di servizio.

Il programma conosce solo la chiave pubblica radice: un certificato modificato, firmato con una
chiave diversa o emesso fuori dal periodo della chiave di servizio non è valido. Le funzioni
`firma_servizio` ed `emetti` servono al gestionale e al server, che hanno le chiavi private.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from sicur_license import ed25519

VERSIONE = 1
ABBONAMENTO, PERPETUA, PROVA = "abbonamento", "perpetua", "prova"
ATTIVA, REVOCATA = "attiva", "revocata"


class ErroreCertificato(Exception):
    """Certificato illeggibile, alterato o non firmato dalle chiavi di SicurCantiere."""


def _b64(dati: bytes) -> str:
    return base64.b64encode(dati).decode("ascii")


def _da_b64(testo: str) -> bytes:
    return base64.b64decode(testo.encode("ascii"), validate=True)


def _json(dati: dict) -> bytes:
    return json.dumps(dati, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def ora_utc() -> datetime:
    return datetime.now(timezone.utc)


def _istante(testo: str) -> datetime:
    valore = datetime.fromisoformat(testo)
    return valore if valore.tzinfo else valore.replace(tzinfo=timezone.utc)


def _giorno(testo: str | None) -> date | None:
    return date.fromisoformat(testo) if testo else None


def _firma(chiave_privata: bytes, dati: bytes) -> bytes:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    except ImportError:
        return ed25519.firma(chiave_privata, dati)
    return Ed25519PrivateKey.from_private_bytes(chiave_privata).sign(dati)


def _verifica(chiave_pubblica: bytes, dati: bytes, firma: bytes) -> bool:
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError:  # nell'eseguibile può mancare la libreria compilata
        return ed25519.verifica(chiave_pubblica, dati, firma)
    try:
        Ed25519PublicKey.from_public_bytes(chiave_pubblica).verify(firma, dati)
    except (InvalidSignature, ValueError):
        return False
    return True


def firma_dati(chiave_privata: bytes, dati: bytes) -> bytes:
    """Firma Ed25519 di dati qualsiasi (per esempio gli aggiornamenti del programma)."""
    return _firma(chiave_privata, dati)


def verifica_dati(chiave_pubblica: bytes, dati: bytes, firma: bytes) -> bool:
    return _verifica(chiave_pubblica, dati, firma)


def pubblica_da_privata(chiave_privata: bytes) -> bytes:
    return ed25519.chiave_pubblica(chiave_privata)


@dataclass(frozen=True)
class Certificato:
    licenza: str               # identificativo della licenza (es. SC-2026-0012)
    cliente: str
    prodotti: frozenset[str]   # programmi abilitati: «psc», «pos», «pimus»...
    tipo: str                  # abbonamento, perpetua o prova
    pc: str                    # identificativo del PC sul server
    impronte: tuple[str, ...]  # impronte del PC (vedi impronta.py)
    sale: str                  # sale con cui sono calcolate le impronte
    emesso: datetime           # ora del server all'emissione
    valido_fino: datetime      # dopo questa data serve una nuova convalida online
    scadenza_licenza: date | None = None
    aggiornamenti_fino: date | None = None  # versioni pubblicate fino a questa data
    posti: int = 1
    stato: str = ATTIVA
    offline: bool = False      # emesso da un file di attivazione offline
    extra: dict = field(default_factory=dict, compare=False)

    def dati(self) -> dict:
        return {
            "v": VERSIONE, "licenza": self.licenza, "cliente": self.cliente, "prodotti": sorted(self.prodotti),
            "tipo": self.tipo, "pc": self.pc, "impronte": list(self.impronte), "sale": self.sale,
            "emesso": self.emesso.isoformat(), "valido_fino": self.valido_fino.isoformat(),
            "scadenza_licenza": self.scadenza_licenza.isoformat() if self.scadenza_licenza else None,
            "aggiornamenti_fino": self.aggiornamenti_fino.isoformat() if self.aggiornamenti_fino else None,
            "posti": self.posti, "stato": self.stato, "offline": self.offline, **self.extra,
        }

    @classmethod
    def da_dati(cls, d: dict) -> Certificato:
        noti = {"v", "licenza", "cliente", "prodotti", "tipo", "pc", "impronte", "sale", "emesso", "valido_fino",
                "scadenza_licenza", "aggiornamenti_fino", "posti", "stato", "offline"}
        try:
            if int(d.get("v", 0)) != VERSIONE:
                raise ErroreCertificato("Il certificato è di una versione non riconosciuta: aggiorna il programma.")
            return cls(
                licenza=str(d["licenza"]), cliente=str(d["cliente"]), prodotti=frozenset(map(str, d["prodotti"])),
                tipo=str(d["tipo"]), pc=str(d["pc"]), impronte=tuple(map(str, d["impronte"])), sale=str(d["sale"]),
                emesso=_istante(d["emesso"]), valido_fino=_istante(d["valido_fino"]),
                scadenza_licenza=_giorno(d.get("scadenza_licenza")),
                aggiornamenti_fino=_giorno(d.get("aggiornamenti_fino")),
                posti=int(d.get("posti") or 1), stato=str(d.get("stato") or ATTIVA), offline=bool(d.get("offline")),
                extra={k: v for k, v in d.items() if k not in noti},
            )
        except (KeyError, TypeError, ValueError) as e:
            raise ErroreCertificato("Il certificato di licenza non è completo.") from e


# --- emissione (gestionale e server) ---

def firma_servizio(radice_privata: bytes, servizio_pubblica: bytes, da: datetime, a: datetime,
                   nome: str = "") -> dict:
    """Autorizzazione della chiave di servizio, firmata con la chiave radice."""
    dati = _json({"chiave": _b64(servizio_pubblica), "da": da.isoformat(), "a": a.isoformat(), "nome": nome})
    return {"dati": _b64(dati), "firma": _b64(_firma(radice_privata, dati))}


def emetti(certificato: Certificato, servizio_privata: bytes, servizio: dict) -> str:
    """Testo del file del certificato, firmato con la chiave di servizio."""
    dati = _json(certificato.dati())
    return json.dumps({"servizio": servizio,
                       "certificato": {"dati": _b64(dati), "firma": _b64(_firma(servizio_privata, dati))}},
                      ensure_ascii=False)


# --- verifica (programmi) ---

def _parte(contenitore: dict, nome: str) -> tuple[bytes, bytes]:
    parte = contenitore.get(nome)
    if not isinstance(parte, dict):
        raise ErroreCertificato("Il certificato di licenza non è completo.")
    try:
        return _da_b64(str(parte["dati"])), _da_b64(str(parte["firma"]))
    except (KeyError, ValueError) as e:
        raise ErroreCertificato("Il certificato di licenza è danneggiato.") from e


def leggi_certificato(testo: str, radice_pubblica: bytes) -> Certificato:
    """Verifica le due firme e restituisce il certificato; ErroreCertificato se non è valido."""
    alterato = ErroreCertificato("Il certificato di licenza è stato modificato o non è di SicurCantiere.")
    try:
        contenitore = json.loads(testo)
    except (ValueError, TypeError) as e:
        raise ErroreCertificato("Il certificato di licenza è danneggiato.") from e
    if not isinstance(contenitore, dict):
        raise ErroreCertificato("Il certificato di licenza è danneggiato.")
    dati_servizio, firma_servizio_ = _parte(contenitore, "servizio")
    if not _verifica(radice_pubblica, dati_servizio, firma_servizio_):
        raise alterato
    try:
        servizio = json.loads(dati_servizio)
        chiave_servizio = _da_b64(servizio["chiave"])
        da, a = _istante(servizio["da"]), _istante(servizio["a"])
    except (KeyError, TypeError, ValueError) as e:
        raise alterato from e
    dati, firma = _parte(contenitore, "certificato")
    if not _verifica(chiave_servizio, dati, firma):
        raise alterato
    try:
        certificato = Certificato.da_dati(json.loads(dati))
    except ValueError as e:
        raise alterato from e
    if not da <= certificato.emesso <= a:
        raise ErroreCertificato("Il certificato è stato emesso con una chiave di servizio scaduta.")
    return certificato
