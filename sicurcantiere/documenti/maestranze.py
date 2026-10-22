"""Tesserini di riconoscimento e schede dei lavoratori con mansioni, rischi, DPI e formazione."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.shared import Cm

from sicurcantiere import analisi, anagrafiche
from sicurcantiere.documenti import stile
from sicurcantiere.documenti.comune import data_it, indirizzo_cantiere, nome_fase, salva
from sicurcantiere.documenti.pos import elenco_dpi
from sicurcantiere.repository import Repository
from sicurcantiere.valutazioni import METODI


def lavoratori_impresa(repo: Repository, impresa_id: int) -> list[dict[str, Any]]:
    """Dipendenti prima, poi lavoratori autonomi."""
    return sorted(repo.elenco("lavoratori", impresa_id=impresa_id), key=lambda l: (l["autonomo"], l["id"]))


def _immagine(run, percorso: str, larghezza: Cm) -> bool:
    if not percorso or not Path(percorso).is_file():
        return False
    try:
        run.add_picture(percorso, width=larghezza)
        return True
    except Exception:  # noqa: BLE001 - immagine non leggibile: il tesserino resta senza foto
        return False


def genera_tesserini(repo: Repository, impresa_id: int, destinazione: str | Path) -> Path:
    """Tessere di riconoscimento (art. 18, comma 1, lettera u), art. 21, comma 1, lettera c), e art. 26, comma 8,
    del D.Lgs. 81/2008; art. 5 della L. 136/2010)."""
    impresa = repo.leggi("imprese", impresa_id)
    if impresa is None:
        raise ValueError("Impresa inesistente")
    c = repo.cantiere()
    lavoratori = lavoratori_impresa(repo, impresa_id) or [{"nome": "", "cognome": "", "autonomo": 0}]
    doc = stile.documento_semplice(c["nome"] or "", ("Tessere di riconoscimento", impresa["ragione_sociale"]))
    stile.intestazione_modulo(doc, "D.Lgs. 9 aprile 2008, n. 81 · artt. 18, 21 e 26 · L. 136/2010, art. 5",
                              "Tessere di riconoscimento", impresa["ragione_sociale"])
    stile.nota(doc, "Ritagliare lungo il bordo e inserire nell'apposita custodia. Il lavoratore espone la tessera in "
                    "modo visibile per tutta la permanenza in cantiere.")

    griglia = doc.add_table(rows=0, cols=3)  # due tessere con uno spazio in mezzo per il taglio
    griglia.alignment = WD_TABLE_ALIGNMENT.CENTER
    for n, l in enumerate(lavoratori):
        if n % 2 == 0:
            riga = griglia.add_row()
            stile._non_spezzare(riga)
            celle = riga.cells
        cella = celle[0 if n % 2 == 0 else 2]
        stile.bordi_cella(cella, stile.LINEA_FORTE, 6)
        intestazione = cella.paragraphs[0]
        stile.ombreggia_paragrafo(intestazione, stile.ACCENTO)
        stile._spaziatura(intestazione, 0, 4)
        stile._run(intestazione, f" {impresa['ragione_sociale'] or 'Impresa'}", 8.5, "FFFFFF", grassetto=True,
                   carattere=stile.CARATTERE_TITOLI)
        interna = cella.add_table(rows=1, cols=2)
        foto, dati = interna.rows[0].cells
        foto.width, dati.width = Cm(2.4), Cm(5.6)
        p_foto = foto.paragraphs[0]
        if not _immagine(p_foto.add_run(), l.get("foto", ""), Cm(2.2)):
            stile.bordi_cella(foto, stile.LINEA, 4)
            stile._run(p_foto, "\nFOTO\n\n", 7, stile.TESTO3)
        righe = [("", anagrafiche.nominativo(l) or "________________")]
        if l.get("data_nascita"):
            righe.append(("Nato/a il", f"{data_it(l['data_nascita'])} {l.get('luogo_nascita', '')}".strip()))
        if l.get("autonomo"):
            righe.append(("", "Lavoratore autonomo"))
            if l.get("partita_iva") or l.get("codice_fiscale"):
                righe.append(("P. IVA / C.F.", l.get("partita_iva") or l.get("codice_fiscale")))
        else:
            righe.append(("Qualifica", l.get("mansione", "")))
            if l.get("matricola"):
                righe.append(("Matricola", l["matricola"]))
            righe.append(("Assunto il", data_it(l.get("data_assunzione")) if l.get("data_assunzione") else "______"))
            righe.append(("Datore di lavoro", impresa["datore_lavoro"]))
        if impresa["aut_subappalto"]:
            righe.append(("Aut. subappalto", impresa["aut_subappalto"]))
        for i, (etichetta, valore) in enumerate(righe):
            p = dati.paragraphs[0] if i == 0 else dati.add_paragraph()
            stile._spaziatura(p, 0, 1)
            if etichetta:
                stile._run(p, f"{etichetta}: ", 6.5, stile.TESTO3)
            stile._run(p, valore or "—", 10 if i == 0 else 7.5, stile.INCHIOSTRO, grassetto=i == 0,
                       carattere=stile.CARATTERE_TITOLI if i == 0 else None)
        nota = cella.add_paragraph()
        stile._spaziatura(nota, 3, 2)
        stile._run(nota, f" {c['nome'] or 'Cantiere'} · tessera ai sensi degli artt. 18, 21 e 26 del D.Lgs. 81/2008",
                   6, stile.TESTO3)
    stile.larghezze_colonne(griglia, [8.4, 0.6, 8.4])
    return salva(doc, destinazione)


def mansioni_lavoratore(repo: Repository, lavoratore: dict[str, Any]) -> list[dict[str, Any]]:
    """Per ogni lavorazione assegnata: fase, attrezzature usate e rischi a cui il lavoratore è esposto.

    Se per una lavorazione sono indicate le attrezzature usate, i rischi delle altre attrezzature
    della fase non si attribuiscono al lavoratore.
    """
    coppie = repo.mansioni(lavoratore["id"])
    risultato = []
    for fase_id in dict.fromkeys(f for f, _ in sorted(coppie, key=lambda x: (x[0], x[1] or 0))):
        fase = repo.leggi("fasi", fase_id)
        if fase is None:
            continue
        attrezzature = {a["id"]: a for a in repo.elenco("attrezzature", fase_id=fase_id)}
        usate = [attrezzature[a] for f, a in coppie if f == fase_id and a in attrezzature]
        nomi_fase = {a["nome"] for a in attrezzature.values()}
        nomi_usate = {a["nome"] for a in usate}
        rischi = [r for r in repo.rischi(fase_id=fase_id)
                  if not usate or r["fonte"] not in nomi_fase or r["fonte"] in nomi_usate]
        risultato.append({"fase": fase, "attrezzature": usate or list(attrezzature.values()), "rischi": rischi})
    return risultato


def genera_schede_lavoratori(repo: Repository, impresa_id: int, destinazione: str | Path) -> Path:
    """Una scheda per lavoratore: dati, mansioni, macchine e attrezzature, rischi, DPI, formazione."""
    impresa = repo.leggi("imprese", impresa_id)
    if impresa is None:
        raise ValueError("Impresa inesistente")
    c = repo.cantiere()
    valutazioni = [v for v in repo.elenco("valutazioni") if v["fase_id"] is not None and v["metodo"] in METODI]
    comune = f"{c['comune']} ({c['provincia']})" if c["provincia"] else c["comune"]
    doc = stile.documento_semplice(" · ".join(v for v in (c["nome"], comune) if v),
                                   ("Schede dei lavoratori", impresa["ragione_sociale"]))
    lavoratori = lavoratori_impresa(repo, impresa_id)
    if not lavoratori:
        stile.intestazione_modulo(doc, "D.Lgs. 9 aprile 2008, n. 81 · artt. 36 e 37", "Scheda del lavoratore",
                                  impresa["ragione_sociale"])
        stile.nota(doc, "Nessun lavoratore indicato per l'impresa.", avviso=True)
    for n, l in enumerate(lavoratori):
        stile.intestazione_modulo(doc, "D.Lgs. 9 aprile 2008, n. 81 · artt. 36 e 37", "Scheda del lavoratore",
                                  anagrafiche.nominativo(l) or "Nominativo da indicare", nuova_pagina=n > 0)
        voci = [
            ("Impresa", impresa["ragione_sociale"]),
            ("Cantiere", " · ".join(v for v in (c["nome"], indirizzo_cantiere(c)) if v)),
            ("Posizione", "Lavoratore autonomo" if l["autonomo"] else "Lavoratore dipendente"),
            ("Qualifica / mansione", l["mansione"]),
            ("Data e luogo di nascita",
             f"{data_it(l['data_nascita']) if l['data_nascita'] else ''} {l['luogo_nascita']}".strip()),
        ]
        if l["autonomo"]:
            voci += [("Codice fiscale / P. IVA", " · ".join(v for v in (l["codice_fiscale"], l["partita_iva"]) if v)),
                     ("Periodo in cantiere", " - ".join(v for v in (data_it(l["data_inizio"]),
                                                                    data_it(l["data_fine"])) if v != "-"))]
        else:
            voci += [("Matricola", l["matricola"]),
                     ("Data di assunzione", data_it(l["data_assunzione"]) if l["data_assunzione"] else "")]
        voci.append(("Idoneità sanitaria fino al", data_it(l["idoneita_scadenza"]) if l["idoneita_scadenza"] else ""))
        stile.scheda(doc, voci)

        mansioni = mansioni_lavoratore(repo, l)
        stile.banda(doc, "Lavorazioni svolte e macchine o attrezzature utilizzate")
        if mansioni:
            stile.tabella_colorata(doc, ["Lavorazione", "Periodo", "Macchine e attrezzature"], [
                [nome_fase(m["fase"]), " - ".join(v for v in (data_it(m["fase"]["data_inizio"]),
                                                              data_it(m["fase"]["data_fine"])) if v != "-"),
                 ", ".join(a["nome"] for a in m["attrezzature"]) or "-"] for m in mansioni
            ], 8.5, larghezze=[6.4, 3.6, 7.4])
        else:
            stile.nota(doc, "Mansioni non ancora assegnate.")

        rischi = [r for m in mansioni for r in m["rischi"]]
        stile.banda(doc, "Rischi cui è esposto il lavoratore e misure di prevenzione")
        if rischi:
            visti: dict[str, dict] = {}
            for r in rischi:
                chiave = r["descrizione"].lower()
                livello = analisi.livello_rischio(r["probabilita"], r["danno"])
                if chiave not in visti or livello > visti[chiave]["livello"]:
                    visti[chiave] = {**r, "livello": livello}
            ordinati = sorted(visti.values(), key=lambda x: -x["livello"])
            t = stile.tabella_colorata(doc, ["Rischio", "Livello", "Misure"], [
                [r["descrizione"], f"{r['livello']} {analisi.classe_rischio(r['livello'])}", r["misure"]]
                for r in ordinati], 8, larghezze=[4.6, 2.4, 10.4])
            for riga, r in zip(t.rows[1:], ordinati):
                livello = r["livello"]
                stile.colora_livello(riga.cells[1], 3 if livello >= 9 else 2 if livello >= 6 else 1 if livello >= 3
                                     else 0)
        else:
            doc.add_paragraph("Nessun rischio associato alle lavorazioni assegnate.")

        fasi_lavoratore = {m["fase"]["id"] for m in mansioni}
        sue = [v for v in valutazioni if v["fase_id"] in fasi_lavoratore]
        if sue:
            stile.banda(doc, "Valutazioni dei rischi specifici")
            stile.tabella_colorata(doc, ["Valutazione", "Metodo", "Esito"], [
                [v["titolo"] or METODI[v["metodo"]].nome, METODI[v["metodo"]].norma,
                 f"{(e := METODI[v['metodo']].esegui(repo.dati_valutazione(v['id']))).indice_testo} · {e.classe}"]
                for v in sue
            ], 8.5, larghezze=[6.0, 5.0, 6.4])

        stile.banda(doc, "Dispositivi di protezione individuale")
        dpi = anagrafiche.dpi_lavoratore(l) or elenco_dpi([r["dpi"] for r in rischi])
        if dpi:
            stile.elenco_colonne(doc, dpi, 2)
        else:
            doc.add_paragraph("—")
        stile.banda(doc, "Informazione, formazione e addestramento")
        stile.elenco(doc, anagrafiche.formazione_lavoratore(l) or ["Da indicare."])

        p = doc.add_paragraph("Il lavoratore dichiara di aver ricevuto copia della presente scheda e le informazioni "
                              "sui rischi e sulle misure relative alle proprie mansioni (art. 36).")
        stile._spaziatura(p, 10, 6)
        stile.firme(doc, [("Il datore di lavoro", impresa["datore_lavoro"]),
                          ("Il lavoratore", anagrafiche.nominativo(l))])
    return salva(doc, destinazione)
