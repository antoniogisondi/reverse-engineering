"""Elenco delle sostanze e miscele pericolose con le schede di sicurezza (Allegato XV punto 3.2.1, lettera e)."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from sicurcantiere import sostanze
from sicurcantiere.documenti import stile
from sicurcantiere.documenti.comune import data_it, indirizzo_cantiere, nome_fase, salva
from sicurcantiere.repository import Repository


def sostanze_impresa(repo: Repository, impresa_id: int) -> list[dict[str, Any]]:
    """Sostanze dell'impresa, indicate direttamente o tramite una sua lavorazione."""
    fasi = {f["id"] for f in repo.elenco("fasi", impresa_id=impresa_id)}
    return [s for s in repo.elenco("sostanze")
            if s["impresa_id"] == impresa_id or fasi & set(repo.fasi_sostanza(s["id"]))]


def lavorazioni_sostanza(repo: Repository, sostanza: dict[str, Any]) -> str:
    """Nomi delle lavorazioni in cui si usa la sostanza, separati da punto e virgola."""
    fasi = {f["id"]: f for f in repo.elenco("fasi")}
    return "; ".join(nome_fase(fasi[f]) for f in repo.fasi_sostanza(sostanza["id"]) if f in fasi)


def aggiungi_sostanze(doc, repo: Repository, elenco: list[dict[str, Any]], livello: int = 2) -> None:
    """Tabella riepilogativa e una scheda per prodotto (nel POS e nell'elenco a sé)."""
    if not elenco:
        doc.add_paragraph("Non è previsto l'uso di sostanze o miscele pericolose.")
        return
    righe = []
    for s in elenco:
        codici = sostanze.codici_h(s["codici_h"])
        uso = "; ".join(v for v in (lavorazioni_sostanza(repo, s), s["uso"]) if v)
        righe.append([
            s["nome"], uso,
            ", ".join(f"{p} {sostanze.PITTOGRAMMI[p]}" for p in sostanze.pittogrammi(codici)) or "-",
            ", ".join(codici) or "-",
            data_it(s["data_sds"]),
        ])
    stile.tabella_colorata(doc, ["Prodotto", "Uso / lavorazione", "Pittogrammi", "Frasi H", "Data della SDS"], righe,
                           8, larghezze=[3.6, 4.6, 4.0, 2.8, 2.4])
    stile.nota(doc, "Le schede di dati di sicurezza aggiornate sono conservate in cantiere e consultabili dai "
                    "lavoratori.")

    for s in elenco:
        codici = sostanze.codici_h(s["codici_h"])
        stile.riquadro(doc, s["nome"] or "Prodotto", s["produttore"], livello=livello)
        stile.scheda(doc, [
            ("Avvertenza", s["avvertenza"]),
            ("Stato fisico", s["stato_fisico"]),
            ("Quantità presente in cantiere", s["quantita"]),
            ("Conservazione", s["conservazione"]),
        ])
        if codici:
            stile.tabella_colorata(doc, ["Codice", "Indicazione di pericolo"],
                                   [[c, sostanze.descrizione(c)] for c in codici], 8, larghezze=[2.0, 15.4])
        categorie = sostanze.categorie(codici)
        misure = [m for c in categorie for m in c.misure]
        if s["misure"].strip():
            misure.insert(0, s["misure"].strip())
        if categorie:
            stile.scheda(doc, [("Categorie di pericolo", ", ".join(c.nome for c in categorie))])
        if misure:
            stile.banda(doc, "Misure di prevenzione e protezione")
            stile.elenco(doc, list(dict.fromkeys(misure)))
        if s["dpi"].strip():
            stile.scheda(doc, [("Dispositivi di protezione individuale", s["dpi"].strip())])


def genera_elenco_sostanze(repo: Repository, impresa_id: int, destinazione: str | Path) -> Path:
    impresa = repo.leggi("imprese", impresa_id)
    if impresa is None:
        raise ValueError("Impresa inesistente")
    c = repo.cantiere()
    comune = f"{c['comune']} ({c['provincia']})" if c["provincia"] else c["comune"]
    oggi = data_it(date.today())
    doc = stile.documento_semplice(" · ".join(v for v in (c["nome"], comune) if v),
                                   ("Sostanze e miscele pericolose", oggi))
    stile.intestazione_modulo(doc, "D.Lgs. 9 aprile 2008, n. 81 · Allegato XV punto 3.2.1, lettera e), e Titolo IX",
                              "Sostanze e miscele pericolose utilizzate in cantiere", impresa["ragione_sociale"])
    stile.scheda(doc, [("Impresa", impresa["ragione_sociale"]),
                       ("Cantiere", " · ".join(v for v in (c["nome"], indirizzo_cantiere(c)) if v))])
    aggiungi_sostanze(doc, repo, sostanze_impresa(repo, impresa_id), livello=3)
    p = doc.add_paragraph(f"{c['comune'] or ''}, {oggi}".strip(", "))
    stile._spaziatura(p, 14, 8)
    stile.firme(doc, [("Il datore di lavoro", impresa["datore_lavoro"])])
    return salva(doc, destinazione)
