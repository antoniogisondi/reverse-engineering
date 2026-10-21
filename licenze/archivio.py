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
        raise FileExistsError(f"La chiave esiste già: {file}. Non va rigenerata.")
    privata = Ed25519PrivateKey.generate()
    file.write_bytes(privata.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                           serialization.NoEncryption()))
    file.chmod(0o600)
    return chiave_pubblica()


def chiave_privata() -> bytes:
    file = _file_chiave()
    if not file.exists():
        raise FileNotFoundError("Chiave di firma assente: eseguire «python -m licenze genera-chiave».")
    privata = serialization.load_pem_private_key(file.read_bytes(), password=None)
    return privata.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                 serialization.NoEncryption())


def chiave_pubblica() -> str:
    privata = Ed25519PrivateKey.from_private_bytes(chiave_privata())
    grezza = privata.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return base64.b64encode(grezza).decode()


def segreto_sessione() -> str:
    file = cartella_dati() / "segreto_sessione"
    if not file.exists():
        file.write_text(secrets.token_hex(32))
        file.chmod(0o600)
    return file.read_text().strip()
