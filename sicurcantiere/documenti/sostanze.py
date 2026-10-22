"""Elenco delle sostanze e miscele pericolose con le schede di sicurezza (Allegato XV punto 3.2.1, lettera e)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sicurcantiere import sostanze
from sicurcantiere.documenti.comune import (
    data_it,
    firma,
    indirizzo_cantiere,
    nome_fase,
    nuovo_documento,
    salva,
    tabella,
    tabella_voci,
)
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
    tabella(doc, ["Prodotto", "Uso / lavorazione", "Pittogrammi", "Frasi H", "SDS del"], righe, dimensione=8)
    doc.add_paragraph("Le schede di dati di sicurezza aggiornate sono conservate in cantiere e consultabili "
                      "dai lavoratori.").runs[0].italic = True

    for s in elenco:
        codici = sostanze.codici_h(s["codici_h"])
        doc.add_heading(s["nome"] or "Prodotto", livello)
        tabella_voci(doc, [
            ("Produttore / fornitore", s["produttore"]),
            ("Avvertenza", s["avvertenza"]),
            ("Stato fisico", s["stato_fisico"]),
            ("Quantità presente in cantiere", s["quantita"]),
            ("Conservazione", s["conservazione"]),
        ])
        if codici:
            doc.add_paragraph()
            tabella(doc, ["Codice", "Indicazione di pericolo"],
                    [[c, sostanze.descrizione(c)] for c in codici], dimensione=8)
        categorie = sostanze.categorie(codici)
        misure = [m for c in categorie for m in c.misure]
        if s["misure"].strip():
            misure.insert(0, s["misure"].strip())
        if categorie:
            p = doc.add_paragraph()
            p.add_run("Categorie di pericolo: ").bold = True
            p.add_run(", ".join(c.nome for c in categorie))
        if misure:
            p = doc.add_paragraph()
            p.add_run("Misure di prevenzione e protezione:").bold = True
            for m in dict.fromkeys(misure):
                doc.add_paragraph(m, style="List Bullet")
        if s["dpi"].strip():
            p = doc.add_paragraph()
            p.add_run("DPI: ").bold = True
            p.add_run(s["dpi"].strip())


def genera_elenco_sostanze(repo: Repository, impresa_id: int, destinazione: str | Path) -> Path:
    impresa = repo.leggi("imprese", impresa_id)
    if impresa is None:
        raise ValueError("Impresa inesistente")
    c = repo.cantiere()
    doc = nuovo_documento()
    doc.add_heading("SOSTANZE E MISCELE PERICOLOSE UTILIZZATE IN CANTIERE", 0)
    doc.add_paragraph("Allegato XV punto 3.2.1, lettera e), e Titolo IX del D.Lgs. 81/2008")
    tabella_voci(doc, [("Impresa", impresa["ragione_sociale"]),
                       ("Cantiere", f"{c['nome']} - {indirizzo_cantiere(c)}".strip(" -"))])
    doc.add_paragraph()
    aggiungi_sostanze(doc, repo, sostanze_impresa(repo, impresa_id), livello=1)
    firma(doc, "Il datore di lavoro")
    return salva(doc, destinazione)
