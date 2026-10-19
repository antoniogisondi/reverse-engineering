"""Accesso al file di progetto (un database SQLite per cantiere).

Ogni modifica viene salvata subito in una transazione, così un crash
dell'applicazione non fa perdere dati.
"""

from __future__ import annotations

import shutil
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

ESTENSIONE = ".scs"

# Ogni elemento è una migrazione; l'indice + 1 è la versione dello schema
# (salvata in PRAGMA user_version). Non modificare le migrazioni già
# rilasciate: aggiungerne di nuove in coda.
MIGRAZIONI: list[str] = [
    """
    CREATE TABLE cantiere (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        nome TEXT NOT NULL DEFAULT '',
        natura_opera TEXT NOT NULL DEFAULT '',
        indirizzo TEXT NOT NULL DEFAULT '',
        comune TEXT NOT NULL DEFAULT '',
        provincia TEXT NOT NULL DEFAULT '',
        descrizione TEXT NOT NULL DEFAULT '',
        importo_lavori REAL NOT NULL DEFAULT 0
    );
    INSERT INTO cantiere (id) VALUES (1);

    CREATE TABLE soggetti (
        id INTEGER PRIMARY KEY,
        ruolo TEXT NOT NULL DEFAULT '',
        nome TEXT NOT NULL DEFAULT '',
        codice_fiscale TEXT NOT NULL DEFAULT '',
        indirizzo TEXT NOT NULL DEFAULT '',
        telefono TEXT NOT NULL DEFAULT '',
        email TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE imprese (
        id INTEGER PRIMARY KEY,
        ragione_sociale TEXT NOT NULL DEFAULT '',
        tipo TEXT NOT NULL DEFAULT 'Esecutrice',
        partita_iva TEXT NOT NULL DEFAULT '',
        indirizzo TEXT NOT NULL DEFAULT '',
        referente TEXT NOT NULL DEFAULT '',
        telefono TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE fasi (
        id INTEGER PRIMARY KEY,
        codice TEXT NOT NULL DEFAULT '',
        descrizione TEXT NOT NULL DEFAULT '',
        impresa_id INTEGER REFERENCES imprese(id) ON DELETE SET NULL,
        data_inizio TEXT,
        data_fine TEXT,
        lavoratori INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE rischi (
        id INTEGER PRIMARY KEY,
        fase_id INTEGER NOT NULL REFERENCES fasi(id) ON DELETE CASCADE,
        descrizione TEXT NOT NULL DEFAULT '',
        probabilita INTEGER NOT NULL DEFAULT 1 CHECK (probabilita BETWEEN 1 AND 4),
        danno INTEGER NOT NULL DEFAULT 1 CHECK (danno BETWEEN 1 AND 4),
        misure TEXT NOT NULL DEFAULT '',
        dpi TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE costi (
        id INTEGER PRIMARY KEY,
        codice TEXT NOT NULL DEFAULT '',
        descrizione TEXT NOT NULL DEFAULT '',
        unita TEXT NOT NULL DEFAULT 'cad',
        quantita REAL NOT NULL DEFAULT 0,
        prezzo_unitario REAL NOT NULL DEFAULT 0
    );

    CREATE TABLE relazione (
        sezione TEXT PRIMARY KEY,
        testo TEXT NOT NULL DEFAULT ''
    );
    """,
    # v0.2: Gantt analitico, interferenze per zona, POS, fascicolo, revisioni.
    """
    ALTER TABLE cantiere ADD COLUMN costo_uomo_giorno REAL NOT NULL DEFAULT 250;

    ALTER TABLE fasi ADD COLUMN zona TEXT NOT NULL DEFAULT '';
    ALTER TABLE fasi ADD COLUMN importo REAL NOT NULL DEFAULT 0;
    ALTER TABLE fasi ADD COLUMN incidenza_manodopera REAL NOT NULL DEFAULT 0;

    ALTER TABLE rischi ADD COLUMN fonte TEXT NOT NULL DEFAULT '';

    CREATE TABLE attrezzature (
        id INTEGER PRIMARY KEY,
        fase_id INTEGER NOT NULL REFERENCES fasi(id) ON DELETE CASCADE,
        tipo TEXT NOT NULL DEFAULT 'Attrezzo',
        nome TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE prescrizioni (
        fase_a INTEGER NOT NULL REFERENCES fasi(id) ON DELETE CASCADE,
        fase_b INTEGER NOT NULL REFERENCES fasi(id) ON DELETE CASCADE,
        testo TEXT NOT NULL DEFAULT '',
        PRIMARY KEY (fase_a, fase_b),
        CHECK (fase_a < fase_b)
    );

    CREATE TABLE revisioni (
        id INTEGER PRIMARY KEY,
        documento TEXT NOT NULL DEFAULT 'PSC',
        numero INTEGER NOT NULL DEFAULT 0,
        data TEXT,
        descrizione TEXT NOT NULL DEFAULT ''
    );

    ALTER TABLE imprese ADD COLUMN codice_fiscale TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN datore_lavoro TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN rspp TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN medico_competente TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN rls TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN preposto TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN addetti_emergenze TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN posizione_inail_inps TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN orario_lavoro TEXT NOT NULL DEFAULT '';

    CREATE TABLE lavoratori (
        id INTEGER PRIMARY KEY,
        impresa_id INTEGER NOT NULL REFERENCES imprese(id) ON DELETE CASCADE,
        nome TEXT NOT NULL DEFAULT '',
        mansione TEXT NOT NULL DEFAULT '',
        formazione TEXT NOT NULL DEFAULT '',
        idoneita_scadenza TEXT
    );

    CREATE TABLE interventi (
        id INTEGER PRIMARY KEY,
        parte_opera TEXT NOT NULL DEFAULT '',
        intervento TEXT NOT NULL DEFAULT '',
        periodicita TEXT NOT NULL DEFAULT '',
        rischi TEXT NOT NULL DEFAULT '',
        misure_in_dotazione TEXT NOT NULL DEFAULT '',
        misure_ausiliarie TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE elaborati (
        id INTEGER PRIMARY KEY,
        titolo TEXT NOT NULL DEFAULT '',
        autore TEXT NOT NULL DEFAULT '',
        data TEXT,
        collocazione TEXT NOT NULL DEFAULT ''
    );
    """,
]

VERSIONE_SCHEMA = len(MIGRAZIONI)


def anteprima(percorso: str | Path) -> dict[str, str] | None:
    """Nome e comune del cantiere letti in sola lettura, senza backup né migrazioni.

    Restituisce None se il file non esiste o non è un progetto leggibile.
    """
    try:
        uri = Path(percorso).resolve().as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        try:
            riga = conn.execute("SELECT nome, comune, provincia FROM cantiere WHERE id = 1").fetchone()
        finally:
            conn.close()
    except (sqlite3.Error, OSError, ValueError):
        return None
    if riga is None:
        return None
    return {"nome": riga[0], "comune": riga[1], "provincia": riga[2]}


class ErroreProgetto(Exception):
    """Il file non è un progetto valido o è di una versione più recente."""


class Progetto:
    """Un file di progetto aperto."""

    def __init__(self, percorso: str | Path, crea: bool = False):
        self.percorso = Path(percorso)
        if crea and self.percorso.exists():
            self.percorso.unlink()
        if not crea and not self.percorso.exists():
            raise ErroreProgetto(f"File non trovato: {self.percorso}")
        if not crea:
            self._backup()
        self.conn = sqlite3.connect(self.percorso, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        try:
            self._migra()
        except Exception:
            self.conn.close()
            raise

    def _backup(self) -> None:
        # Copia di sicurezza fatta all'apertura, prima di qualsiasi modifica.
        shutil.copy2(self.percorso, self.percorso.with_name(self.percorso.name + ".bak"))

    def _migra(self) -> None:
        try:
            versione = self.conn.execute("PRAGMA user_version").fetchone()[0]
        except sqlite3.DatabaseError as e:
            raise ErroreProgetto(f"Il file non è un progetto valido: {e}") from e
        if versione > VERSIONE_SCHEMA:
            raise ErroreProgetto(
                "Il progetto è stato creato con una versione più recente del programma."
            )
        for i in range(versione, VERSIONE_SCHEMA):
            try:
                self.conn.executescript(
                    f"BEGIN;{MIGRAZIONI[i]};PRAGMA user_version = {i + 1};COMMIT;"
                )
            except sqlite3.Error:
                if self.conn.in_transaction:
                    self.conn.execute("ROLLBACK")
                raise

    @contextmanager
    def transazione(self) -> Iterator[sqlite3.Connection]:
        self.conn.execute("BEGIN")
        try:
            yield self.conn
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise
        else:
            self.conn.execute("COMMIT")

    def query(self, sql: str, parametri: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        return self.conn.execute(sql, parametri).fetchall()

    def salva_con_nome(self, destinazione: str | Path) -> None:
        destinazione = Path(destinazione)
        if destinazione.resolve() == self.percorso.resolve():
            return
        dest = sqlite3.connect(destinazione)
        try:
            self.conn.backup(dest)
        finally:
            dest.close()

    def chiudi(self) -> None:
        self.conn.close()
