"""Lettura e scrittura dei dati di progetto."""

from __future__ import annotations

from typing import Any

from sicurcantiere.db import Progetto

TABELLE_ELENCO = ("soggetti", "imprese", "fasi", "rischi", "costi")


class Repository:
    def __init__(self, progetto: Progetto):
        self.progetto = progetto
        self._colonne: dict[str, set[str]] = {}
        for tabella in TABELLE_ELENCO + ("cantiere",):
            righe = progetto.query(f"PRAGMA table_info({tabella})")
            self._colonne[tabella] = {r["name"] for r in righe}

    def _verifica(self, tabella: str, campi: list[str] | set[str]) -> None:
        # I nomi di tabella e colonna non possono essere parametri SQL:
        # li accettiamo solo se esistono nello schema.
        colonne = self._colonne.get(tabella)
        if colonne is None:
            raise ValueError(f"Tabella sconosciuta: {tabella}")
        sconosciuti = set(campi) - colonne
        if sconosciuti:
            raise ValueError(f"Campi sconosciuti in {tabella}: {sorted(sconosciuti)}")

    # --- dati del cantiere (riga unica) ---

    def cantiere(self) -> dict[str, Any]:
        return dict(self.progetto.query("SELECT * FROM cantiere WHERE id = 1")[0])

    def aggiorna_cantiere(self, **valori: Any) -> None:
        self._verifica("cantiere", valori.keys())
        valori.pop("id", None)
        if not valori:
            return
        assegnazioni = ", ".join(f"{c} = ?" for c in valori)
        with self.progetto.transazione() as c:
            c.execute(f"UPDATE cantiere SET {assegnazioni} WHERE id = 1", tuple(valori.values()))

    # --- tabelle elenco ---

    def elenco(self, tabella: str, **filtri: Any) -> list[dict[str, Any]]:
        self._verifica(tabella, filtri.keys())
        sql = f"SELECT * FROM {tabella}"
        if filtri:
            sql += " WHERE " + " AND ".join(f"{c} = ?" for c in filtri)
        ordine = "data_inizio IS NULL, data_inizio, id" if tabella == "fasi" else "id"
        sql += f" ORDER BY {ordine}"
        return [dict(r) for r in self.progetto.query(sql, tuple(filtri.values()))]

    def leggi(self, tabella: str, id_: int) -> dict[str, Any] | None:
        self._verifica(tabella, [])
        righe = self.progetto.query(f"SELECT * FROM {tabella} WHERE id = ?", (id_,))
        return dict(righe[0]) if righe else None

    def inserisci(self, tabella: str, **valori: Any) -> int:
        self._verifica(tabella, valori.keys())
        with self.progetto.transazione() as c:
            if valori:
                campi = ", ".join(valori)
                segnaposto = ", ".join("?" for _ in valori)
                cur = c.execute(
                    f"INSERT INTO {tabella} ({campi}) VALUES ({segnaposto})", tuple(valori.values())
                )
            else:
                cur = c.execute(f"INSERT INTO {tabella} DEFAULT VALUES")
            return int(cur.lastrowid)

    def aggiorna(self, tabella: str, id_: int, **valori: Any) -> None:
        self._verifica(tabella, valori.keys())
        if not valori:
            return
        assegnazioni = ", ".join(f"{c} = ?" for c in valori)
        with self.progetto.transazione() as c:
            c.execute(
                f"UPDATE {tabella} SET {assegnazioni} WHERE id = ?", (*valori.values(), id_)
            )

    def elimina(self, tabella: str, id_: int) -> None:
        self._verifica(tabella, [])
        with self.progetto.transazione() as c:
            c.execute(f"DELETE FROM {tabella} WHERE id = ?", (id_,))

    # --- relazione (testi liberi per sezione) ---

    def testo(self, sezione: str) -> str:
        righe = self.progetto.query("SELECT testo FROM relazione WHERE sezione = ?", (sezione,))
        return righe[0]["testo"] if righe else ""

    def salva_testo(self, sezione: str, testo: str) -> None:
        with self.progetto.transazione() as c:
            c.execute(
                "INSERT INTO relazione (sezione, testo) VALUES (?, ?) "
                "ON CONFLICT(sezione) DO UPDATE SET testo = excluded.testo",
                (sezione, testo),
            )

    # --- archivio ---

    def importa_lavorazione(self, lavorazione: dict[str, Any]) -> int:
        """Copia una lavorazione dell'archivio nel progetto come nuova fase."""
        with self.progetto.transazione() as c:
            fase_id = int(
                c.execute(
                    "INSERT INTO fasi (codice, descrizione) VALUES (?, ?)",
                    (lavorazione["codice"], lavorazione["descrizione"]),
                ).lastrowid
            )
            for r in lavorazione["rischi"]:
                c.execute(
                    "INSERT INTO rischi (fase_id, descrizione, probabilita, danno, misure, dpi) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (fase_id, r["descrizione"], r["probabilita"], r["danno"], r["misure"], r["dpi"]),
                )
        return fase_id
