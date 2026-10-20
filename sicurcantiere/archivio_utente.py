"""Archivio delle anagrafiche dell'utente, comune a tutti i cantieri e ai tre programmi.

Contiene le persone (committenti, coordinatori, RSPP, medici competenti, preposti...) e le
imprese con le loro figure e maestranze, così da non doverle riscrivere in ogni cantiere.
Si trova in un file SQLite nella cartella dei dati dell'utente.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from sicurcantiere.repository import Repository

PERSONA = "persona"
IMPRESA = "impresa"

# Campi che non hanno senso fuori dal cantiere di origine.
_ESCLUSI = {"id", "impresa_id", "affidataria_id", "fase_id"}


def percorso_predefinito() -> Path:
    if os.environ.get("SICURCANTIERE_ARCHIVIO"):
        return Path(os.environ["SICURCANTIERE_ARCHIVIO"])
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "SicurCantiere" / "archivio.db"


def _pulisci(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in _ESCLUSI and k != "nota"}


class ArchivioAnagrafiche:
    def __init__(self, percorso: str | Path | None = None):
        self.percorso = Path(percorso) if percorso else percorso_predefinito()
        self.percorso.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.percorso)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS voci (
                id INTEGER PRIMARY KEY,
                tipo TEXT NOT NULL,
                ruolo TEXT NOT NULL DEFAULT '',
                nome TEXT NOT NULL,
                dati TEXT NOT NULL,
                modificato TEXT NOT NULL
            )""")
        self.conn.commit()

    def chiudi(self) -> None:
        self.conn.close()

    # --- operazioni di base ---

    def salva(self, tipo: str, nome: str, dati: dict[str, Any], ruolo: str = "") -> int:
        """Inserisce la voce o aggiorna quella con lo stesso tipo, ruolo e nome."""
        nome = nome.strip()
        if not nome:
            raise ValueError("Indicare il nominativo prima di salvarlo in archivio.")
        testo = json.dumps(dati, ensure_ascii=False)
        adesso = datetime.now().isoformat(timespec="seconds")
        riga = self.conn.execute(
            "SELECT id FROM voci WHERE tipo = ? AND ruolo = ? AND lower(nome) = lower(?)", (tipo, ruolo, nome)
        ).fetchone()
        with self.conn:
            if riga:
                self.conn.execute("UPDATE voci SET nome = ?, dati = ?, modificato = ? WHERE id = ?",
                                  (nome, testo, adesso, riga["id"]))
                return int(riga["id"])
            cur = self.conn.execute("INSERT INTO voci (tipo, ruolo, nome, dati, modificato) VALUES (?, ?, ?, ?, ?)",
                                    (tipo, ruolo, nome, testo, adesso))
            return int(cur.lastrowid)

    def elenco(self, tipo: str | None = None, testo: str = "") -> list[dict[str, Any]]:
        sql, parametri = "SELECT * FROM voci WHERE 1 = 1", []
        if tipo:
            sql += " AND tipo = ?"
            parametri.append(tipo)
        if testo.strip():
            sql += " AND (lower(nome) LIKE ? OR lower(ruolo) LIKE ?)"
            parametri += [f"%{testo.strip().lower()}%"] * 2
        sql += " ORDER BY ruolo, lower(nome)"
        return [self._voce(r) for r in self.conn.execute(sql, parametri)]

    def leggi(self, id_: int) -> dict[str, Any] | None:
        r = self.conn.execute("SELECT * FROM voci WHERE id = ?", (id_,)).fetchone()
        return self._voce(r) if r else None

    def elimina(self, id_: int) -> None:
        with self.conn:
            self.conn.execute("DELETE FROM voci WHERE id = ?", (id_,))

    @staticmethod
    def _voce(r: sqlite3.Row) -> dict[str, Any]:
        return {"id": r["id"], "tipo": r["tipo"], "ruolo": r["ruolo"], "nome": r["nome"],
                "dati": json.loads(r["dati"]), "modificato": r["modificato"]}

    # --- dal cantiere all'archivio ---

    def salva_persona(self, record: dict[str, Any]) -> int:
        return self.salva(PERSONA, record.get("nome", ""), _pulisci(record), record.get("ruolo", ""))

    def salva_impresa(self, repo: Repository, impresa_id: int) -> int:
        impresa = repo.leggi("imprese", impresa_id)
        if impresa is None:
            raise ValueError("Impresa inesistente")
        dati = _pulisci(impresa)
        dati["figure"] = [_pulisci(f) for f in repo.elenco("figure", impresa_id=impresa_id)]
        dati["lavoratori"] = [_pulisci(l) for l in repo.elenco("lavoratori", impresa_id=impresa_id)]
        return self.salva(IMPRESA, impresa["ragione_sociale"], dati)

    # --- dall'archivio al cantiere ---

    @staticmethod
    def _campi(repo: Repository, tabella: str, dati: dict[str, Any]) -> dict[str, Any]:
        colonne = repo._colonne[tabella] - _ESCLUSI
        return {k: v for k, v in dati.items() if k in colonne}

    def inserisci_persona(self, repo: Repository, voce: dict[str, Any], tabella: str, **extra: Any) -> int:
        """Inserisce la persona in «soggetti» o «figure», con i soli campi che la tabella prevede."""
        return repo.inserisci(tabella, **{**self._campi(repo, tabella, voce["dati"]), **extra})

    def inserisci_impresa(self, repo: Repository, voce: dict[str, Any]) -> int:
        dati = voce["dati"]
        impresa_id = repo.inserisci("imprese", **self._campi(repo, "imprese", dati))
        for f in dati.get("figure", []):
            repo.inserisci("figure", impresa_id=impresa_id, **self._campi(repo, "figure", f))
        for l in dati.get("lavoratori", []):
            repo.inserisci("lavoratori", impresa_id=impresa_id, **self._campi(repo, "lavoratori", l))
        return impresa_id
