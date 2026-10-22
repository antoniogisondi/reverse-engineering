"""Relazione di valutazione dei rischi specifici (NIOSH, OCRA, ...)."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from sicurcantiere.documenti import stile
from sicurcantiere.documenti.comune import data_it, indirizzo_cantiere, nome_fase, salva
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


def aggiungi_valutazione(doc, repo: Repository, valutazione: dict[str, Any], livello: int = 1,
                         titolo: bool = True) -> None:
    """Relazione di una valutazione: dati, metodo, calcolo, esito e misure (nel POS e come documento a sé)."""
    metodo = METODI.get(valutazione["metodo"])
    if metodo is None:
        return
    dati = metodo.normalizza(repo.dati_valutazione(valutazione["id"]))
    esito = metodo.calcola(dati)
    impresa = repo.leggi("imprese", valutazione["impresa_id"]) if valutazione["impresa_id"] else None

    if titolo:
        stile.riquadro(doc, valutazione["titolo"] or metodo.nome, metodo.nome)
    stile.scheda(doc, [
        ("Metodo", f"{metodo.nome} · {metodo.norma}"),
        ("Mansione / gruppo omogeneo", valutazione["mansione"]),
        ("Lavorazioni", lavorazioni_valutazione(repo, valutazione)),
        ("Impresa", impresa["ragione_sociale"] if impresa else ""),
    ])

    grezzi = repo.dati_valutazione(valutazione["id"])
    if not grezzi:
        stile.nota(doc, "Valutazione da eseguire: la lavorazione presenta questo rischio, ma i parametri del "
                        "metodo non sono ancora stati indicati.", avviso=True)
        return
    if str(grezzi.get("descrizione", "")).strip():
        stile.banda(doc, "Descrizione dell'attività")
        stile.testo(doc, str(grezzi["descrizione"]), "")

    stile.banda(doc, "Metodo di valutazione")
    doc.add_paragraph(metodo.descrizione)

    stile.banda(doc, "Dati rilevati")
    voci = []
    for campo in metodo.campi:
        valore = dati[campo.chiave]
        if campo.tipo == "scelta":
            valore = dict(campo.scelte).get(valore, valore)
        elif campo.tipo == "numero":
            valore = f"{valore:g}".replace(".", ",") + campo.suffisso
        voci.append((campo.etichetta, str(valore)))
    if voci:
        stile.scheda(doc, voci, 7.0)
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
        stile.tabella_colorata(doc, intestazioni, righe, 8)

    ipotesi = [str(i) for i in grezzi.get("ipotesi_ai") or []]
    if ipotesi:
        stile.nota(doc, "Ipotesi formulate in fase di compilazione, verificate dal valutatore: " + "; ".join(ipotesi)
                   + ".")

    stile.banda(doc, "Calcolo e risultato")
    stile.scheda(doc, esito.dettagli, 7.0)
    if esito.righe_compiti:
        stile.tabella_colorata(doc, esito.intestazioni_compiti, esito.righe_compiti, 8)
    t = stile.tabella_colorata(doc, ["Indice", "Classe di rischio"], [[esito.indice_testo, esito.classe]], 9.5,
                               larghezze=[5.2, 12.2])
    for cella in t.rows[1].cells:
        stile.ombreggia_cella(cella, COLORI[esito.colore].lstrip("#"))
        for run in cella.paragraphs[0].runs:
            run.bold = True
    for testo_nota in esito.note:
        stile.nota(doc, testo_nota)

    stile.banda(doc, "Misure di prevenzione e protezione")
    stile.elenco(doc, list(esito.misure))
    if valutazione["note"].strip():
        stile.banda(doc, "Note del valutatore")
        stile.testo(doc, valutazione["note"], "")


def genera_valutazione(repo: Repository, valutazione_id: int, destinazione: str | Path) -> Path:
    valutazione = repo.leggi("valutazioni", valutazione_id)
    if valutazione is None:
        raise ValueError("Valutazione inesistente")
    c = repo.cantiere()
    metodo = METODI.get(valutazione["metodo"])
    comune = f"{c['comune']} ({c['provincia']})" if c["provincia"] else c["comune"]
    oggi = data_it(date.today())
    doc = stile.documento_semplice(" · ".join(v for v in (c["nome"], comune) if v),
                                   ("Valutazione dei rischi specifici", oggi))
    stile.intestazione_modulo(doc, f"D.Lgs. 9 aprile 2008, n. 81 · {metodo.norma}" if metodo else
                              "D.Lgs. 9 aprile 2008, n. 81", "Valutazione dei rischi specifici",
                              valutazione["titolo"] or (metodo.nome if metodo else ""))
    stile.scheda(doc, [("Cantiere", " · ".join(v for v in (c["nome"], indirizzo_cantiere(c)) if v))])
    aggiungi_valutazione(doc, repo, valutazione, titolo=False)
    p = doc.add_paragraph(f"{c['comune'] or ''}, {oggi}".strip(", "))
    stile._spaziatura(p, 14, 8)
    stile.firme(doc, [("Il datore di lavoro", ""), ("In collaborazione con il RSPP", ""),
                      ("Il medico competente, ove nominato", "")])
    return salva(doc, destinazione)
