"""Accesso al file di progetto (un database SQLite per cantiere).

Ogni modifica viene salvata subito in una transazione, così un crash
dell'applicazione non fa perdere dati.
"""

from __future__ import annotations

import glob
import hashlib
import os
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime
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
    # v0.3: valutazioni dei rischi specifici con metodi normati, PiMUS.
    """
    CREATE TABLE valutazioni (
        id INTEGER PRIMARY KEY,
        metodo TEXT NOT NULL DEFAULT 'niosh',
        titolo TEXT NOT NULL DEFAULT '',
        mansione TEXT NOT NULL DEFAULT '',
        fase_id INTEGER REFERENCES fasi(id) ON DELETE SET NULL,
        impresa_id INTEGER REFERENCES imprese(id) ON DELETE SET NULL,
        dati TEXT NOT NULL DEFAULT '{}',
        note TEXT NOT NULL DEFAULT '',
        data TEXT
    );

    CREATE TABLE ponteggi (
        id INTEGER PRIMARY KEY,
        nome TEXT NOT NULL DEFAULT '',
        impresa_id INTEGER REFERENCES imprese(id) ON DELETE SET NULL,
        tipo TEXT NOT NULL DEFAULT 'Telai prefabbricati',
        altezza REAL NOT NULL DEFAULT 0,
        lunghezza REAL NOT NULL DEFAULT 0,
        conforme_schemi INTEGER NOT NULL DEFAULT 1,
        fabbricante TEXT NOT NULL DEFAULT '',
        modello TEXT NOT NULL DEFAULT '',
        autorizzazione TEXT NOT NULL DEFAULT '',
        classe_carico TEXT NOT NULL DEFAULT '',
        ancoraggi TEXT NOT NULL DEFAULT '',
        piano_appoggio TEXT NOT NULL DEFAULT '',
        progettista TEXT NOT NULL DEFAULT '',
        preposto TEXT NOT NULL DEFAULT '',
        squadra TEXT NOT NULL DEFAULT '',
        sollevamento TEXT NOT NULL DEFAULT '',
        dpi TEXT NOT NULL DEFAULT ''
    );

    CREATE TABLE verifiche_ponteggio (
        id INTEGER PRIMARY KEY,
        ponteggio_id INTEGER NOT NULL REFERENCES ponteggi(id) ON DELETE CASCADE,
        momento TEXT NOT NULL DEFAULT 'Prima del montaggio',
        voce TEXT NOT NULL DEFAULT '',
        esito TEXT NOT NULL DEFAULT '',
        note TEXT NOT NULL DEFAULT ''
    );
    """,
    # v0.5: sostanze e miscele pericolose (POS, Allegato XV punto 3.2.1 lett. e).
    """
    CREATE TABLE sostanze (
        id INTEGER PRIMARY KEY,
        impresa_id INTEGER REFERENCES imprese(id) ON DELETE SET NULL,
        fase_id INTEGER REFERENCES fasi(id) ON DELETE SET NULL,
        nome TEXT NOT NULL DEFAULT '',
        produttore TEXT NOT NULL DEFAULT '',
        codici_h TEXT NOT NULL DEFAULT '',
        avvertenza TEXT NOT NULL DEFAULT '',
        stato_fisico TEXT NOT NULL DEFAULT '',
        quantita TEXT NOT NULL DEFAULT '',
        data_sds TEXT,
        file_sds TEXT NOT NULL DEFAULT '',
        uso TEXT NOT NULL DEFAULT '',
        dpi TEXT NOT NULL DEFAULT '',
        misure TEXT NOT NULL DEFAULT '',
        conservazione TEXT NOT NULL DEFAULT ''
    );
    """,
    # v0.7: anagrafica dettagliata dell'impresa, figure della sicurezza come elenco,
    # committente che svolge anche il ruolo di responsabile dei lavori.
    """
    ALTER TABLE cantiere ADD COLUMN committente_rl INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE cantiere ADD COLUMN titolo_abilitativo TEXT NOT NULL DEFAULT '';
    ALTER TABLE cantiere ADD COLUMN cap TEXT NOT NULL DEFAULT '';

    ALTER TABLE soggetti ADD COLUMN qualifica TEXT NOT NULL DEFAULT '';
    ALTER TABLE soggetti ADD COLUMN rappresentante TEXT NOT NULL DEFAULT '';
    ALTER TABLE soggetti ADD COLUMN partita_iva TEXT NOT NULL DEFAULT '';
    ALTER TABLE soggetti ADD COLUMN pec TEXT NOT NULL DEFAULT '';

    ALTER TABLE imprese ADD COLUMN forma_giuridica TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN cap TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN comune TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN provincia TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN email TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN pec TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN recapito_cantiere TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN cciaa TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN ateco TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN inail TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN inps TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN cassa_edile TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN ccnl TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN organico TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN durc_scadenza TEXT;
    ALTER TABLE imprese ADD COLUMN dvr_data TEXT;
    ALTER TABLE imprese ADD COLUMN soa TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN certificazioni TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN tipologia_lavori TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN importo_lavori REAL NOT NULL DEFAULT 0;
    ALTER TABLE imprese ADD COLUMN affidataria_id INTEGER REFERENCES imprese(id) ON DELETE SET NULL;
    ALTER TABLE imprese ADD COLUMN rspp_datore INTEGER NOT NULL DEFAULT 0;
    UPDATE imprese SET inail = posizione_inail_inps;

    CREATE TABLE figure (
        id INTEGER PRIMARY KEY,
        impresa_id INTEGER NOT NULL REFERENCES imprese(id) ON DELETE CASCADE,
        ruolo TEXT NOT NULL DEFAULT '',
        nome TEXT NOT NULL DEFAULT '',
        qualifica TEXT NOT NULL DEFAULT '',
        codice_fiscale TEXT NOT NULL DEFAULT '',
        telefono TEXT NOT NULL DEFAULT '',
        email TEXT NOT NULL DEFAULT '',
        formazione TEXT NOT NULL DEFAULT '',
        formazione_scadenza TEXT
    );
    INSERT INTO figure (impresa_id, ruolo, nome)
        SELECT id, 'RSPP', rspp FROM imprese WHERE trim(rspp) <> '';
    INSERT INTO figure (impresa_id, ruolo, nome)
        SELECT id, 'Medico competente', medico_competente FROM imprese WHERE trim(medico_competente) <> '';
    INSERT INTO figure (impresa_id, ruolo, nome)
        SELECT id, 'RLS', rls FROM imprese WHERE trim(rls) <> '';
    INSERT INTO figure (impresa_id, ruolo, nome)
        SELECT id, 'Preposto', preposto FROM imprese WHERE trim(preposto) <> '';
    INSERT INTO figure (impresa_id, ruolo, nome)
        SELECT id, 'Addetto al primo soccorso', addetti_emergenze FROM imprese WHERE trim(addetti_emergenze) <> '';
    INSERT INTO figure (impresa_id, ruolo, nome)
        SELECT id, 'Addetto antincendio ed evacuazione', addetti_emergenze FROM imprese
        WHERE trim(addetti_emergenze) <> '';
    """,
    # v0.8: dati dei lavori dell'impresa, soggetto incaricato (art. 97), anagrafica delle
    # maestranze con DPI assegnati e formazione ricevuta.
    """
    ALTER TABLE imprese ADD COLUMN fax TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN aut_subappalto TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN data_inizio TEXT;
    ALTER TABLE imprese ADD COLUMN data_fine TEXT;
    ALTER TABLE imprese ADD COLUMN incaricato_97 TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN incaricato_97_mansione TEXT NOT NULL DEFAULT '';
    ALTER TABLE imprese ADD COLUMN logo TEXT NOT NULL DEFAULT '';

    ALTER TABLE lavoratori ADD COLUMN cognome TEXT NOT NULL DEFAULT '';
    ALTER TABLE lavoratori ADD COLUMN data_nascita TEXT;
    ALTER TABLE lavoratori ADD COLUMN luogo_nascita TEXT NOT NULL DEFAULT '';
    ALTER TABLE lavoratori ADD COLUMN matricola TEXT NOT NULL DEFAULT '';
    ALTER TABLE lavoratori ADD COLUMN data_assunzione TEXT;
    ALTER TABLE lavoratori ADD COLUMN foto TEXT NOT NULL DEFAULT '';
    ALTER TABLE lavoratori ADD COLUMN dpi TEXT NOT NULL DEFAULT '';
    ALTER TABLE lavoratori ADD COLUMN form_base INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE lavoratori ADD COLUMN form_specifica INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE lavoratori ADD COLUMN form_cantiere INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE lavoratori ADD COLUMN form_dpi3 INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE lavoratori ADD COLUMN autonomo INTEGER NOT NULL DEFAULT 0;
    ALTER TABLE lavoratori ADD COLUMN data_inizio TEXT;
    ALTER TABLE lavoratori ADD COLUMN data_fine TEXT;
    ALTER TABLE lavoratori ADD COLUMN indirizzo TEXT NOT NULL DEFAULT '';
    ALTER TABLE lavoratori ADD COLUMN codice_fiscale TEXT NOT NULL DEFAULT '';
    ALTER TABLE lavoratori ADD COLUMN partita_iva TEXT NOT NULL DEFAULT '';

    -- Mansioni: lavorazioni svolte da ogni lavoratore e macchine o attrezzature che utilizza.
    CREATE TABLE mansioni_lavoratori (
        id INTEGER PRIMARY KEY,
        lavoratore_id INTEGER NOT NULL REFERENCES lavoratori(id) ON DELETE CASCADE,
        fase_id INTEGER NOT NULL REFERENCES fasi(id) ON DELETE CASCADE,
        attrezzatura_id INTEGER REFERENCES attrezzature(id) ON DELETE CASCADE
    );
    """,
    # v0.9: lavorazioni suddivise in fasi, addetto e descrizione della fase, schede d'uso di
    # macchine e attrezzi (misure prima, durante e dopo l'uso e DPI dell'operatore).
    """
    ALTER TABLE fasi ADD COLUMN lavorazione TEXT NOT NULL DEFAULT '';
    ALTER TABLE fasi ADD COLUMN dettaglio TEXT NOT NULL DEFAULT '';
    ALTER TABLE fasi ADD COLUMN addetto TEXT NOT NULL DEFAULT '';
    ALTER TABLE fasi ADD COLUMN modalita TEXT NOT NULL DEFAULT '';
    ALTER TABLE fasi ADD COLUMN turni TEXT NOT NULL DEFAULT '';
    ALTER TABLE fasi ADD COLUMN procedure_psc TEXT NOT NULL DEFAULT '';
    ALTER TABLE rischi ADD COLUMN valutazione_id INTEGER REFERENCES valutazioni(id) ON DELETE SET NULL;
    ALTER TABLE attrezzature ADD COLUMN descrizione TEXT NOT NULL DEFAULT '';
    ALTER TABLE attrezzature ADD COLUMN misure TEXT NOT NULL DEFAULT '';
    ALTER TABLE attrezzature ADD COLUMN dpi TEXT NOT NULL DEFAULT '';
    """,
    # v0.11: una sostanza può essere usata in più lavorazioni (la vecchia colonna sostanze.fase_id
    # resta nel file ma non è più usata).
    """
    CREATE TABLE sostanze_fasi (
        id INTEGER PRIMARY KEY,
        sostanza_id INTEGER NOT NULL REFERENCES sostanze(id) ON DELETE CASCADE,
        fase_id INTEGER NOT NULL REFERENCES fasi(id) ON DELETE CASCADE,
        UNIQUE (sostanza_id, fase_id)
    );
    INSERT INTO sostanze_fasi (sostanza_id, fase_id)
        SELECT id, fase_id FROM sostanze WHERE fase_id IS NOT NULL AND fase_id IN (SELECT id FROM fasi);
    """,
    # v0.12: una valutazione dei rischi specifici può riguardare più lavorazioni (la vecchia
    # colonna valutazioni.fase_id resta nel file ma non è più usata).
    """
    CREATE TABLE valutazioni_fasi (
        id INTEGER PRIMARY KEY,
        valutazione_id INTEGER NOT NULL REFERENCES valutazioni(id) ON DELETE CASCADE,
        fase_id INTEGER NOT NULL REFERENCES fasi(id) ON DELETE CASCADE,
        UNIQUE (valutazione_id, fase_id)
    );
    INSERT INTO valutazioni_fasi (valutazione_id, fase_id)
        SELECT id, fase_id FROM valutazioni WHERE fase_id IS NOT NULL AND fase_id IN (SELECT id FROM fasi);
    """,
]

VERSIONE_SCHEMA = len(MIGRAZIONI)


COPIE_TENUTE = 5


def cartella_copie() -> Path:
    """Cartella delle copie di sicurezza dei cantieri (variabile SICURCANTIERE_COPIE per i test)."""
    if os.environ.get("SICURCANTIERE_COPIE"):
        return Path(os.environ["SICURCANTIERE_COPIE"])
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "SicurCantiere" / "copie di sicurezza"


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
        # Copia di sicurezza fatta all'apertura, prima di qualsiasi modifica, nella cartella delle
        # copie (non accanto al file): per ogni cantiere si tengono le ultime COPIE_TENUTE.
        cartella = cartella_copie()
        cartella.mkdir(parents=True, exist_ok=True)
        impronta = hashlib.sha1(str(self.percorso.resolve()).lower().encode()).hexdigest()[:8]
        prefisso = f"{self.percorso.stem}-{impronta}-"
        istante = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        shutil.copy2(self.percorso, cartella / f"{prefisso}{istante}{self.percorso.suffix}")
        copie = sorted(cartella.glob(f"{glob.escape(prefisso)}*{self.percorso.suffix}"))
        for vecchia in copie[:-COPIE_TENUTE]:
            vecchia.unlink(missing_ok=True)

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
