"""Dal PSC al POS: file del POS di un'impresa preparato dal cantiere del PSC.

Il coordinatore (o il consulente che redige il POS per un'impresa del cantiere) sceglie l'impresa
nel programma PSC e ottiene un file .spo con:
- dati del cantiere, committente, coordinatori e altri soggetti;
- l'impresa, con figure e maestranze, più l'eventuale affidataria e le sue subappaltatrici
  (solo come riferimento, senza lavorazioni);
- le lavorazioni assegnate all'impresa con rischi, misure, macchine e attrezzature, e le
  valutazioni e sostanze collegate;
- per ogni fase, le interferenze con le altre imprese e le prescrizioni del coordinatore,
  riportate tra le procedure richieste dal PSC.

Il POS non viene generato subito: il file si apre in SicurCantiere POS, dove si integra quello che
manca (testi del POS, DPI, formazione...) e poi si genera il documento.

Il file si ottiene copiando quello del PSC e togliendo quello che non riguarda l'impresa: così passano
tutti i dati, anche le colonne aggiunte in futuro.
"""

from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path

from sicurcantiere import analisi
from sicurcantiere.documenti.comune import data_it, nome_fase
from sicurcantiere.repository import Repository

CHIAVE_ORIGINE = "origine_psc"


def prescrizioni_impresa(repo: Repository, impresa_id: int) -> dict[int, list[str]]:
    """Per ogni fase dell'impresa, le interferenze con fasi di altre imprese e le prescrizioni del CSE."""
    fasi = repo.elenco("fasi")
    imprese = {i["id"]: i["ragione_sociale"] or f"Impresa n. {i['id']}" for i in repo.elenco("imprese")}
    prescrizioni = repo.prescrizioni()
    livelli = analisi.livelli_fasi(repo.rischi())
    risultato: dict[int, list[str]] = {}
    for i in analisi.interferenze(fasi, livelli):
        for propria, altra in ((i.fase_a, i.fase_b), (i.fase_b, i.fase_a)):
            if propria.get("impresa_id") != impresa_id:
                continue
            chi = imprese.get(altra.get("impresa_id"), "impresa da definire")
            testo = prescrizioni.get(i.chiave, "").strip()
            risultato.setdefault(propria["id"], []).append(
                f"Interferenza con «{nome_fase(altra)}» ({chi}) dal {data_it(i.inizio)} al {data_it(i.fine)}: "
                + (testo if testo else "coordinarsi con il coordinatore per l'esecuzione prima di iniziare."))
    return risultato


def prepara_pos(repo: Repository, impresa_id: int, destinazione: str | Path) -> Path:
    """Crea il file .spo del POS dell'impresa a partire dal cantiere del PSC aperto in `repo`."""
    impresa = repo.leggi("imprese", impresa_id)
    if impresa is None:
        raise ValueError("Impresa inesistente")
    destinazione = Path(destinazione)
    note = prescrizioni_impresa(repo, impresa_id)
    origine = repo.progetto.percorso.name
    if destinazione.exists():
        destinazione.unlink()
    repo.progetto.salva_con_nome(destinazione)

    conn = sqlite3.connect(destinazione, isolation_level=None)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("BEGIN")
        collegate = {impresa_id, impresa["affidataria_id"]} | {
            r[0] for r in conn.execute("SELECT id FROM imprese WHERE affidataria_id = ?", (impresa_id,))}
        collegate.discard(None)
        segnaposti = ", ".join("?" for _ in collegate)
        for sql, parametri in (
            ("DELETE FROM fasi WHERE impresa_id IS NULL OR impresa_id <> ?", (impresa_id,)),
            ("DELETE FROM valutazioni WHERE (impresa_id IS NULL OR impresa_id <> ?) AND id NOT IN "
             "(SELECT valutazione_id FROM valutazioni_fasi)", (impresa_id,)),
            ("DELETE FROM sostanze WHERE (impresa_id IS NULL OR impresa_id <> ?) AND id NOT IN "
             "(SELECT sostanza_id FROM sostanze_fasi)", (impresa_id,)),
            ("DELETE FROM ponteggi WHERE impresa_id IS NULL OR impresa_id <> ?", (impresa_id,)),
            ("DELETE FROM lavoratori WHERE impresa_id <> ?", (impresa_id,)),
            ("DELETE FROM figure WHERE impresa_id <> ?", (impresa_id,)),
            (f"DELETE FROM imprese WHERE id NOT IN ({segnaposti})", tuple(collegate)),
            # dati solo del PSC: prescrizioni (ora nelle fasi), costi, fascicolo
            ("DELETE FROM prescrizioni", ()),
            ("DELETE FROM costi", ()),
            ("DELETE FROM interventi", ()),
            ("DELETE FROM elaborati", ()),
            ("DELETE FROM relazione WHERE sezione <> 'foto_cantiere' AND sezione NOT LIKE ?",
             (f"pos:{impresa_id}:%",)),
            ("DELETE FROM revisioni WHERE documento <> ?", (f"POS:{impresa_id}",)),
        ):
            conn.execute(sql, parametri)
        for fase_id, righe in note.items():
            attuale = conn.execute("SELECT procedure_psc FROM fasi WHERE id = ?", (fase_id,)).fetchone()
            if attuale is None:
                continue
            testo = "\n".join(v for v in (attuale[0].strip(), *righe) if v)
            conn.execute("UPDATE fasi SET procedure_psc = ? WHERE id = ?", (testo, fase_id))
        conn.execute("INSERT INTO relazione (sezione, testo) VALUES (?, ?) ON CONFLICT(sezione) DO UPDATE SET "
                     "testo = excluded.testo",
                     (CHIAVE_ORIGINE, f"Preparato dal PSC «{origine}» il {data_it(date.today())}"))
        conn.execute("COMMIT")
        conn.execute("VACUUM")
    except BaseException:
        if conn.in_transaction:
            conn.execute("ROLLBACK")
        conn.close()
        destinazione.unlink(missing_ok=True)
        raise
    conn.close()
    return destinazione
