"""Database del gestionale delle licenze (SQLite) e chiave di firma.

I dati stanno nella cartella indicata da SICURCANTIERE_LICENZE_DATI (sul server:
/var/lib/sicurcantiere-licenze): licenze.db, chiave_privata.pem e segreto della sessione.
La chiave privata firma le licenze: se va persa non si possono più emettere licenze valide
per i programmi già distribuiti, quindi va copiata in un posto sicuro (vedi README).
"""

from __future__ import annotations

import base64
import os
import secrets
import sqlite3
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

SCHEMA = """
CREATE TABLE IF NOT EXISTS utenti (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    totp TEXT NOT NULL DEFAULT '',
    totp_ultimo INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS accessi_falliti (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    ip TEXT NOT NULL,
    quando REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS clienti (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL DEFAULT '',
    partita_iva TEXT NOT NULL DEFAULT '',
    codice_fiscale TEXT NOT NULL DEFAULT '',
    email TEXT NOT NULL DEFAULT '',
    pec TEXT NOT NULL DEFAULT '',
    telefono TEXT NOT NULL DEFAULT '',
    indirizzo TEXT NOT NULL DEFAULT '',
    codice_sdi TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    creato TEXT NOT NULL DEFAULT (date('now'))
);
CREATE TABLE IF NOT EXISTS licenze (
    id INTEGER PRIMARY KEY,
    codice_licenza TEXT NOT NULL UNIQUE,
    cliente_id INTEGER NOT NULL REFERENCES clienti(id),
    piano TEXT NOT NULL,
    emessa TEXT NOT NULL,
    scadenza TEXT,
    postazioni INTEGER NOT NULL DEFAULT 1,
    prezzo REAL NOT NULL DEFAULT 0,
    codice TEXT NOT NULL,
    rinnovo_di INTEGER REFERENCES licenze(id),
    stato TEXT NOT NULL DEFAULT 'attiva',
    note TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS invii (
    id INTEGER PRIMARY KEY,
    licenza_id INTEGER NOT NULL REFERENCES licenze(id),
    data TEXT NOT NULL,
    tipo TEXT NOT NULL,
    destinatario TEXT NOT NULL DEFAULT '',
    utente TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS consumi_ai (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clienti(id),
    licenza_id INTEGER REFERENCES licenze(id),
    data TEXT NOT NULL,
    istante REAL NOT NULL,
    motore TEXT NOT NULL,
    token_ingresso INTEGER NOT NULL DEFAULT 0,
    token_uscita INTEGER NOT NULL DEFAULT 0,
    crediti INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS consumi_ai_cliente ON consumi_ai (cliente_id, data);
CREATE TABLE IF NOT EXISTS ricariche_ai (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clienti(id),
    data TEXT NOT NULL,
    crediti INTEGER NOT NULL,
    prezzo REAL NOT NULL DEFAULT 0,
    note TEXT NOT NULL DEFAULT ''
);
-- Licenze per PC (server delle attivazioni). Una «catena» è una licenza con i suoi rinnovi:
-- radice_id è la prima licenza della catena, così i PC attivati restano validi anche dopo il rinnovo.
CREATE TABLE IF NOT EXISTS catene_licenza (
    radice_id INTEGER PRIMARY KEY REFERENCES licenze(id),
    sale TEXT NOT NULL,
    posti_extra INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS pc_licenza (
    id INTEGER PRIMARY KEY,
    codice_pc TEXT NOT NULL UNIQUE,
    radice_id INTEGER NOT NULL REFERENCES licenze(id),
    sale TEXT NOT NULL,
    impronta_sistema TEXT NOT NULL DEFAULT '',
    impronta_hardware TEXT NOT NULL DEFAULT '',
    impronta_nome TEXT NOT NULL DEFAULT '',
    nome TEXT NOT NULL DEFAULT '',
    programma TEXT NOT NULL DEFAULT '',
    versione TEXT NOT NULL DEFAULT '',
    attivato TEXT NOT NULL,
    ultimo_uso TEXT NOT NULL,
    ultimo_ip TEXT NOT NULL DEFAULT '',
    stato TEXT NOT NULL DEFAULT 'attivo',
    disattivato TEXT,
    motivo TEXT NOT NULL DEFAULT '',
    offline INTEGER NOT NULL DEFAULT 0,
    sospetto TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS pc_licenza_radice ON pc_licenza (radice_id, stato);
CREATE TABLE IF NOT EXISTS eventi_licenza (
    id INTEGER PRIMARY KEY,
    quando TEXT NOT NULL,
    radice_id INTEGER,
    codice_pc TEXT NOT NULL DEFAULT '',
    evento TEXT NOT NULL,
    esito TEXT NOT NULL DEFAULT '',
    ip TEXT NOT NULL DEFAULT '',
    dettagli TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS eventi_licenza_radice ON eventi_licenza (radice_id, evento, quando);
CREATE TABLE IF NOT EXISTS limiti_richieste (
    chiave TEXT NOT NULL,
    quando REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS limiti_richieste_chiave ON limiti_richieste (chiave, quando);
CREATE TABLE IF NOT EXISTS pagamenti (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER NOT NULL REFERENCES clienti(id),
    licenza_id INTEGER REFERENCES licenze(id),
    data TEXT NOT NULL,
    importo REAL NOT NULL,
    metodo TEXT NOT NULL DEFAULT '',
    fattura TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT ''
);
"""


def cartella_dati() -> Path:
    cartella = Path(os.environ.get("SICURCANTIERE_LICENZE_DATI", "/var/lib/sicurcantiere-licenze"))
    cartella.mkdir(parents=True, exist_ok=True)
    return cartella


def connessione() -> sqlite3.Connection:
    conn = sqlite3.connect(cartella_dati() / "licenze.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    colonne = {r[1] for r in conn.execute("PRAGMA table_info(utenti)")}
    for nome, tipo in (("totp", "TEXT NOT NULL DEFAULT ''"), ("totp_ultimo", "INTEGER NOT NULL DEFAULT 0")):
        if nome not in colonne:  # database creato da una versione precedente
            conn.execute(f"ALTER TABLE utenti ADD COLUMN {nome} {tipo}")
    return conn


def _file_chiave() -> Path:
    return cartella_dati() / "chiave_privata.pem"


def genera_chiave() -> str:
    """Crea la chiave di firma (una sola volta) e restituisce la chiave pubblica in base64."""
    file = _file_chiave()
    if file.exists():
        raise FileExistsError(f"La chiave di firma esiste già: {file}. Non deve essere rigenerata.")
    privata = Ed25519PrivateKey.generate()
    file.write_bytes(privata.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                           serialization.NoEncryption()))
    file.chmod(0o600)
    return chiave_pubblica()


def chiave_privata() -> bytes:
    file = _file_chiave()
    if not file.exists():
        raise FileNotFoundError("Chiave di firma assente: esegui «python -m licenze genera-chiave».")
    privata = serialization.load_pem_private_key(file.read_bytes(), password=None)
    return privata.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                 serialization.NoEncryption())


def chiave_pubblica() -> str:
    privata = Ed25519PrivateKey.from_private_bytes(chiave_privata())
    grezza = privata.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return base64.b64encode(grezza).decode()


# --- chiave di servizio del server delle attivazioni ---
#
# Il server firma i certificati dei PC con una chiave di servizio, autorizzata dalla chiave radice
# (quella delle licenze) per un periodo limitato. Finché il server delle attivazioni gira sulla
# stessa macchina del gestionale, la chiave di servizio si rinnova da sola; su un server separato
# (per esempio il futuro Proxmox o un VPS) si copia solo il file servizio.json, mai la chiave radice.

DURATA_SERVIZIO_GIORNI = 180
RINNOVO_SERVIZIO_GIORNI = 30  # si rinnova quando ne mancano meno di tanti alla fine


def _file_servizio() -> Path:
    return cartella_dati() / "servizio.json"


def nuova_chiave_servizio(da=None) -> dict:
    """Crea una chiave di servizio autorizzata dalla chiave radice e la salva in servizio.json."""
    import json
    from datetime import datetime, timedelta, timezone

    from sicur_license.certificato import firma_servizio, pubblica_da_privata

    da = da or datetime.now(timezone.utc)
    privata = secrets.token_bytes(32)
    autorizzazione = firma_servizio(chiave_privata(), pubblica_da_privata(privata), da - timedelta(minutes=5),
                                    da + timedelta(days=DURATA_SERVIZIO_GIORNI), f"servizio {da:%Y-%m-%d}")
    dati = {"privata": base64.b64encode(privata).decode(), "autorizzazione": autorizzazione,
            "fino_al": (da + timedelta(days=DURATA_SERVIZIO_GIORNI)).isoformat()}
    file = _file_servizio()
    temporaneo = file.with_suffix(".tmp")
    temporaneo.write_text(json.dumps(dati))
    temporaneo.chmod(0o600)
    temporaneo.replace(file)
    return dati


def chiave_servizio(ora=None) -> tuple[bytes, dict]:
    """(chiave privata di servizio, autorizzazione firmata dalla radice), rinnovata quando serve."""
    import json
    from datetime import datetime, timedelta, timezone

    ora = ora or datetime.now(timezone.utc)
    file = _file_servizio()
    dati = json.loads(file.read_text()) if file.exists() else None
    if dati is None or datetime.fromisoformat(dati["fino_al"]) - ora < timedelta(days=RINNOVO_SERVIZIO_GIORNI):
        if _file_chiave().exists():
            dati = nuova_chiave_servizio(ora)
        elif dati is None or datetime.fromisoformat(dati["fino_al"]) <= ora:
            raise FileNotFoundError("Chiave di servizio assente o scaduta: copia un nuovo servizio.json dal "
                                    "gestionale («python -m licenze chiave-servizio»).")
    return base64.b64decode(dati["privata"]), dati["autorizzazione"]


def radice_pubblica() -> bytes:
    """Chiave pubblica radice (quella che i programmi conoscono)."""
    valore = os.environ.get("SICURCANTIERE_CHIAVE_LICENZE")
    if valore:
        return base64.b64decode(valore)
    if _file_chiave().exists():
        return base64.b64decode(chiave_pubblica())
    from sicurcantiere import licenza

    return base64.b64decode(licenza.CHIAVE_PUBBLICA)


def segreto_sessione() -> str:
    file = cartella_dati() / "segreto_sessione"
    if not file.exists():
        file.write_text(secrets.token_hex(32))
        file.chmod(0o600)
    return file.read_text().strip()
