"""Annulla e ripeti per tutto il cantiere.

Dopo ogni gruppo di modifiche (per esempio una cella salvata, una fase eliminata, un'importazione
dall'archivio) si conserva in memoria una copia del file del cantiere; «Annulla» la ripristina. Così si
annulla qualsiasi operazione, non solo la scrittura in un campo di testo. Le copie restano in memoria e
spariscono alla chiusura del cantiere.
"""

from __future__ import annotations

from sicurcantiere.db import Progetto

MASSIMO_PASSI = 40
MASSIMA_MEMORIA = 400 * 1024 * 1024  # con molte foto e tavole si tengono meno passi


def _stesso_contenuto(a: bytes, b: bytes) -> bool:
    """Confronto che ignora l'intestazione del file (byte 24-99): SQLite vi aggiorna un contatore a ogni
    scrittura, anche quando un campo viene salvato con lo stesso valore."""
    return len(a) == len(b) and a[:24] == b[:24] and a[100:] == b[100:]


class Cronologia:
    def __init__(self, progetto: Progetto):
        self.progetto = progetto
        self._indietro: list[bytes] = []
        self._avanti: list[bytes] = []
        self._attuale = self._istantanea()
        self._modifiche = progetto.conn.total_changes

    def _istantanea(self) -> bytes:
        return self.progetto.conn.serialize()

    def registra(self) -> bool:
        """Da chiamare dopo le modifiche: se il file è cambiato, lo stato precedente diventa un passo da
        annullare. Restituisce True se è stato registrato un passo."""
        conn = self.progetto.conn
        if conn.in_transaction or conn.total_changes == self._modifiche:
            return False
        self._modifiche = conn.total_changes
        nuova = self._istantanea()
        if _stesso_contenuto(nuova, self._attuale):
            self._attuale = nuova
            return False
        self._indietro.append(self._attuale)
        del self._indietro[:-MASSIMO_PASSI]
        while len(self._indietro) > 1 and sum(map(len, self._indietro)) + len(nuova) > MASSIMA_MEMORIA:
            del self._indietro[0]
        self._avanti.clear()
        self._attuale = nuova
        return True

    def puo_annullare(self) -> bool:
        return bool(self._indietro)

    def puo_ripetere(self) -> bool:
        return bool(self._avanti)

    def _ripristina(self, dati: bytes) -> None:
        """Riporta il file del cantiere allo stato salvato (copia dentro la connessione aperta, così si
        continua a lavorare sul file)."""
        import sqlite3

        sorgente = sqlite3.connect(":memory:")
        try:
            sorgente.deserialize(dati)
            sorgente.backup(self.progetto.conn)
        finally:
            sorgente.close()
        self._attuale = dati
        self._modifiche = self.progetto.conn.total_changes

    def annulla(self) -> bool:
        self.registra()
        if not self._indietro:
            return False
        self._avanti.append(self._attuale)
        self._ripristina(self._indietro.pop())
        return True

    def ripeti(self) -> bool:
        if not self._avanti:
            return False
        self._indietro.append(self._attuale)
        self._ripristina(self._avanti.pop())
        return True
