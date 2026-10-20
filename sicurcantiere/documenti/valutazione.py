"""Relazione di valutazione dei rischi specifici (NIOSH, OCRA, ...)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sicurcantiere.documenti.comune import (
    firma,
    nome_fase,
    nuovo_documento,
    ombreggia,
    tabella,
    tabella_voci,
)
from sicurcantiere.repository import Repository
from sicurcantiere.valutazioni import COLORI, METODI


def valutazioni_impresa(repo: Repository, impresa_id: int) -> list[dict[str, Any]]:
    """Valutazioni riferite all'impresa direttamente o tramite una sua lavorazione."""
    fasi = {f["id"] for f in repo.elenco("fasi", impresa_id=impresa_id)}
    return [v for v in repo.elenco("valutazioni")
            if v["impresa_id"] == impresa_id or fasi & set(repo.fasi_valutazione(v["id"]))]


def lavorazioni_valutazione(repo: Repository, valutazione: dict[str, Any]) -> str:
    """Nomi delle lavorazioni a cui si riferisce la valutazione, separati da punto e virgola."""
    fasi = {f["id"]: f for f in repo.elenco("fasi")}
    return "; ".join(nome_fase(fasi[f]) for f in repo.fasi_valutazione(valutazione["id"]) if f in fasi)


def aggiungi_valutazione(doc, repo: Repository, valutazione: dict[str, Any], livello: int = 1) -> None:
    metodo = METODI.get(valutazione["metodo"])
    if metodo is None:
        return
    dati = metodo.normalizza(repo.dati_valutazione(valutazione["id"]))
    esito = metodo.calcola(dati)
    impresa = repo.leggi("imprese", valutazione["impresa_id"]) if valutazione["impresa_id"] else None

    doc.add_heading(valutazione["titolo"] or metodo.nome, livello)
    tabella_voci(doc, [
        ("Metodo", f"{metodo.nome} - {metodo.norma}"),
        ("Mansione / gruppo omogeneo", valutazione["mansione"]),
        ("Lavorazioni", lavorazioni_valutazione(repo, valutazione)),
        ("Impresa", impresa["ragione_sociale"] if impresa else ""),
    ])

    grezzi = repo.dati_valutazione(valutazione["id"])
    if not grezzi:
        p = doc.add_paragraph()
        r = p.add_run("Valutazione da eseguire: la lavorazione presenta questo rischio, ma i parametri "
                      "del metodo non sono ancora stati inseriti.")
        r.bold = True
        return
    if str(grezzi.get("descrizione", "")).strip():
        doc.add_heading("Descrizione dell'attività", livello + 1)
        for paragrafo in str(grezzi["descrizione"]).strip().split("\n"):
            doc.add_paragraph(paragrafo)

    doc.add_heading("Metodo di valutazione", livello + 1)
    doc.add_paragraph(metodo.descrizione)

    doc.add_heading("Dati rilevati", livello + 1)
    voci = []
    for campo in metodo.campi:
        valore = dati[campo.chiave]
        if campo.tipo == "scelta":
            valore = dict(campo.scelte).get(valore, valore)
        elif campo.tipo == "numero":
            valore = f"{valore:g}".replace(".", ",") + campo.suffisso
        voci.append((campo.etichetta, str(valore)))
    if voci:
        tabella_voci(doc, voci)
    if metodo.colonne_compiti and dati.get("compiti"):
        righe = []
        for compito in dati["compiti"]:
            riga = []
            for campo in metodo.colonne_compiti:
                valore = compito[campo.chiave]
                if campo.tipo == "scelta":
                    valore = dict(campo.scelte).get(valore, valore).split(" (")[0]
                elif campo.tipo == "numero":
                    valore = f"{valore:g}".replace(".", ",")
                riga.append(str(valore))
            righe.append(riga)
        intestazioni = [c.etichetta + (f" ({c.suffisso.strip()})" if c.suffisso.strip() else "")
                        for c in metodo.colonne_compiti]
        doc.add_paragraph()
        tabella(doc, intestazioni, righe, dimensione=8)

    ipotesi = [str(i) for i in grezzi.get("ipotesi_ai") or []]
    if ipotesi:
        doc.add_paragraph().add_run("Ipotesi formulate in fase di compilazione, verificate dal valutatore:").italic = True
        for voce in ipotesi:
            doc.add_paragraph(voce, style="List Bullet")

    doc.add_heading("Calcolo e risultato", livello + 1)
    tabella_voci(doc, esito.dettagli)
    if esito.righe_compiti:
        doc.add_paragraph()
        tabella(doc, esito.intestazioni_compiti, esito.righe_compiti, dimensione=8)
    doc.add_paragraph()
    t = tabella(doc, ["Indice", "Classe di rischio"], [[esito.indice_testo, esito.classe]])
    for cella in t.rows[1].cells:
        ombreggia(cella, COLORI[esito.colore].lstrip("#"))
        for run in cella.paragraphs[0].runs:
            run.bold = True
    for nota in esito.note:
        doc.add_paragraph(nota).runs[0].italic = True

    doc.add_heading("Misure di prevenzione e protezione", livello + 1)
    for misura in esito.misure:
        doc.add_paragraph(misura, style="List Bullet")
    if valutazione["note"].strip():
        doc.add_heading("Note del valutatore", livello + 1)
        doc.add_paragraph(valutazione["note"].strip())


def genera_valutazione(repo: Repository, valutazione_id: int, destinazione: str | Path) -> Path:
    valutazione = repo.leggi("valutazioni", valutazione_id)
    if valutazione is None:
        raise ValueError("Valutazione inesistente")
    c = repo.cantiere()
    doc = nuovo_documento()
    doc.add_heading("VALUTAZIONE DEI RISCHI SPECIFICI", 0)
    doc.add_paragraph(f"Cantiere: {c['nome'] or '-'} - {c['comune'] or ''}".strip(" -"))
    aggiungi_valutazione(doc, repo, valutazione)
    firma(doc, "Il Datore di lavoro, in collaborazione con RSPP e medico competente")
    destinazione = Path(destinazione)
    doc.save(destinazione)
    return destinazione
