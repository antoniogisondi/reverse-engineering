"""Generazione del Piano Operativo di Sicurezza (Allegato XV, punto 3.2.1)."""

from __future__ import annotations

import re
from pathlib import Path

from sicurcantiere import anagrafiche, analisi
from sicurcantiere.documenti.comune import (
    data_it,
    euro,
    firma,
    frontespizio,
    indirizzo_cantiere,
    nome_fase,
    nuovo_documento,
    tabella,
    tabella_voci,
    testo_o_segnaposto,
)
from sicurcantiere.documenti.sostanze import aggiungi_sostanze, sostanze_impresa
from sicurcantiere.documenti.valutazione import aggiungi_valutazione, valutazioni_impresa
from sicurcantiere.repository import Repository
from sicurcantiere.struttura import MACCHINA, struttura_fase
from sicurcantiere.valutazioni import METODI

# Sezioni a testo libero del POS, salvate per impresa.
SEZIONI_POS: list[tuple[str, str]] = [
    ("attivita", "Attività svolte in cantiere, modalità organizzative e turni di lavoro"),
    ("sostanze", "Sostanze pericolose: note integrative all'elenco"),
    ("rumore", "Esito della valutazione del rumore"),
    ("integrative", "Misure preventive e protettive integrative rispetto al PSC"),
    ("procedure", "Procedure complementari e di dettaglio richieste dal PSC"),
]


def chiave_testo(impresa_id: int, sezione: str) -> str:
    return f"pos:{impresa_id}:{sezione}"


def elenco_dpi(testi: list[str]) -> list[str]:
    """Unisce gli elenchi di DPI delle schede di rischio eliminando i doppioni."""
    visti: dict[str, str] = {}
    for testo in testi:
        for voce in re.split(r",|;|\n", testo):
            voce = voce.strip().rstrip(".")
            if voce:
                visti.setdefault(voce.lower(), voce[0].upper() + voce[1:])
    return sorted(visti.values(), key=str.lower)


def _periodo(impresa: dict, periodo_fasi: tuple | None) -> str:
    """Date dei lavori indicate per l'impresa o, in mancanza, ricavate dalle sue lavorazioni."""
    inizio = analisi.data(impresa["data_inizio"]) or (periodo_fasi[0] if periodo_fasi else None)
    fine = analisi.data(impresa["data_fine"]) or (periodo_fasi[1] if periodo_fasi else None)
    if not (inizio and fine):
        return ""
    return f"dal {data_it(inizio)} al {data_it(fine)} ({(fine - inizio).days + 1} giorni)"


def genera_pos(repo: Repository, impresa_id: int, destinazione: str | Path) -> Path:
    impresa = repo.leggi("imprese", impresa_id)
    if impresa is None:
        raise ValueError("Impresa inesistente")
    fasi = repo.elenco("fasi", impresa_id=impresa_id)
    lavoratori = repo.elenco("lavoratori", impresa_id=impresa_id)
    rischi = [r for f in fasi for r in repo.elenco("rischi", fase_id=f["id"])]
    attrezzature = [a for f in fasi for a in repo.elenco("attrezzature", fase_id=f["id"])]

    doc = nuovo_documento()
    frontespizio(doc, repo, "PIANO OPERATIVO DI SICUREZZA",
                 "art. 89 c. 1 lett. h) e Allegato XV punto 3.2 del D.Lgs. 81/2008",
                 f"POS:{impresa_id}", [("Impresa", impresa["ragione_sociale"])], logo=impresa["logo"])

    c = repo.cantiere()
    periodo = analisi.periodo_lavori(fasi)
    doc.add_heading("1. Dati generali del lavoro", 1)
    tabella_voci(doc, [
        ("Opera", c["nome"]),
        ("Natura dell'opera", c["natura_opera"]),
        ("Indirizzo del cantiere", indirizzo_cantiere(c)),
        ("Titolo abilitativo", c["titolo_abilitativo"]),
        ("Importo presunto dei lavori", euro(c["importo_lavori"]) if c["importo_lavori"] else ""),
    ])
    doc.add_heading("Committente, responsabile dei lavori, coordinatori e direzione lavori", 2)
    soggetti = anagrafiche.soggetti(repo)
    if soggetti:
        tabella(doc, ["Ruolo", "Nominativo", "Qualifica", "Codice fiscale / P. IVA", "Recapiti"], [
            [s["ruolo"],
             s["nome"] + (f", nella persona di {s['rappresentante']}" if s["rappresentante"] else ""),
             s["qualifica"], s["codice_fiscale"] or s["partita_iva"],
             " - ".join(v for v in (s["indirizzo"], s["telefono"], s["email"], s["pec"]) if v)]
            for s in soggetti
        ])
        for s in soggetti:
            if s.get("nota"):
                doc.add_paragraph(s["nota"]).runs[0].italic = True
                break
    else:
        testo_o_segnaposto(doc, "")

    doc.add_heading("2. Dati identificativi dell'impresa esecutrice", 1)
    affidataria = repo.leggi("imprese", impresa["affidataria_id"]) if impresa["affidataria_id"] else None
    tabella_voci(doc, [
        ("Ragione sociale", impresa["ragione_sociale"]),
        ("Forma giuridica", impresa["forma_giuridica"]),
        ("Tipologia nel cantiere", impresa["tipo"]),
        ("Impresa affidataria", affidataria["ragione_sociale"] if affidataria else ""),
        ("Datore di lavoro", impresa["datore_lavoro"]),
        ("Sede legale", anagrafiche.sede(impresa)),
        ("Telefono / fax", " - ".join(v for v in (impresa["telefono"], impresa["fax"]) if v)),
        ("Email / PEC", " - ".join(v for v in (impresa["email"], impresa["pec"]) if v)),
        ("Ufficio o recapito in cantiere", impresa["recapito_cantiere"]),
        ("Partita IVA", impresa["partita_iva"]),
        ("Codice fiscale", impresa["codice_fiscale"]),
        ("Iscrizione CCIAA", impresa["cciaa"]),
        ("Codice ATECO", impresa["ateco"]),
        ("Posizione INAIL", impresa["inail"]),
        ("Matricola INPS", impresa["inps"]),
        ("Cassa edile", impresa["cassa_edile"]),
        ("Contratto collettivo applicato", impresa["ccnl"]),
        ("Organico medio annuo", impresa["organico"]),
        ("DURC valido fino al", data_it(impresa["durc_scadenza"]) if impresa["durc_scadenza"] else ""),
        ("Documento di valutazione dei rischi del", data_it(impresa["dvr_data"]) if impresa["dvr_data"] else ""),
        ("Attestazione SOA", impresa["soa"]),
        ("Certificazioni", impresa["certificazioni"]),
        ("Tipologia dei lavori affidati", impresa["tipologia_lavori"]),
        ("Importo dei lavori da eseguire", euro(impresa["importo_lavori"]) if impresa["importo_lavori"] else ""),
        ("Inizio e fine dei lavori dell'impresa", _periodo(impresa, periodo)),
        ("Autorizzazione al subappalto", impresa["aut_subappalto"]),
        ("Soggetto incaricato (art. 97)", " - ".join(v for v in (impresa["incaricato_97"],
                                                                 impresa["incaricato_97_mansione"]) if v)),
    ])
    subaffidatari = [i for i in repo.elenco("imprese", affidataria_id=impresa_id)]
    if subaffidatari:
        doc.add_heading("Imprese subappaltatrici e lavoratori autonomi", 2)
        tabella(doc, ["Ragione sociale", "Tipologia", "P. IVA", "Lavori affidati"], [
            [i["ragione_sociale"], i["tipo"], i["partita_iva"], i["tipologia_lavori"]] for i in subaffidatari
        ])

    doc.add_heading("3. Figure della sicurezza e specifiche mansioni", 1)
    figure = [{"ruolo": anagrafiche.DATORE, "nome": impresa["datore_lavoro"], "qualifica": "",
               "telefono": impresa["telefono"], "formazione": ""}] + anagrafiche.figure(repo, impresa)
    tabella(doc, ["Figura", "Nominativo", "Recapiti", "Formazione"], [
        [f["ruolo"], " - ".join(v for v in (f["nome"], f["qualifica"]) if v), f["telefono"],
         f["formazione"]] for f in figure
    ])
    doc.add_heading("Specifiche mansioni inerenti la sicurezza", 2)
    for ruolo in dict.fromkeys(f["ruolo"] for f in figure):
        nomi = ", ".join(f["nome"] for f in figure if f["ruolo"] == ruolo and f["nome"])
        p = doc.add_paragraph()
        p.add_run(f"{ruolo}{f' ({nomi})' if nomi else ''}: ").bold = True
        p.add_run(anagrafiche.compiti(ruolo) or "compiti secondo l'incarico ricevuto.")
        nota = next((f.get("nota") for f in figure if f["ruolo"] == ruolo and f.get("nota")), None)
        if nota:
            p.add_run(" " + nota).italic = True

    doc.add_heading("4. Numero e qualifiche dei lavoratori dipendenti e autonomi", 1)
    dipendenti = [l for l in lavoratori if not l["autonomo"]]
    autonomi = [l for l in lavoratori if l["autonomo"]]
    if dipendenti:
        doc.add_heading(f"Lavoratori dipendenti: {len(dipendenti)}", 2)
        tabella(doc, ["N.", "Qualifica", "Cognome", "Nome", "Matricola", "Idoneità fino al"], [
            [str(n), l["mansione"], l["cognome"], l["nome"], l["matricola"],
             data_it(l["idoneita_scadenza"]) if l["idoneita_scadenza"] else ""]
            for n, l in enumerate(dipendenti, 1)
        ])
    if autonomi:
        doc.add_heading(f"Lavoratori autonomi: {len(autonomi)}", 2)
        tabella(doc, ["N.", "Qualifica", "Nominativo", "C.F. / P. IVA", "Periodo"], [
            [str(n), l["mansione"], anagrafiche.nominativo(l), l["partita_iva"] or l["codice_fiscale"],
             f"{data_it(l['data_inizio'])} - {data_it(l['data_fine'])}"]
            for n, l in enumerate(autonomi, 1)
        ])
    if not lavoratori:
        testo_o_segnaposto(doc, "")

    numero = 5
    sezioni = {chiave: repo.testo(chiave_testo(impresa_id, chiave)) for chiave, _ in SEZIONI_POS}
    doc.add_heading(f"{numero}. {SEZIONI_POS[0][1]}", 1)
    testo_o_segnaposto(doc, sezioni["attivita"])
    if impresa["orario_lavoro"]:
        doc.add_paragraph(f"Orario di lavoro: {impresa['orario_lavoro']}")
    numero += 1

    doc.add_heading(f"{numero}. Lavorazioni svolte dall'impresa", 1)
    numero += 1
    tabella(doc, ["Lavorazione", "Fase di lavoro"], [[f["lavorazione"], nome_fase(f)] for f in fasi])

    doc.add_heading(f"{numero}. Opere provvisionali, macchine e attrezzature", 1)
    numero += 1
    per_tipo: dict[str, set[str]] = {}
    for a in attrezzature:
        per_tipo.setdefault(a["tipo"], set()).add(a["nome"])
    if per_tipo:
        tabella(doc, ["Tipo", "Elenco"], [
            [tipo, ", ".join(sorted(nomi))] for tipo, nomi in sorted(per_tipo.items())
        ])
        for titolo, macchine in (("Attrezzature e opere provvisionali utilizzate nelle lavorazioni", False),
                                 ("Macchine utilizzate nelle lavorazioni", True)):
            elenco = {a["nome"]: a for a in attrezzature if (a["tipo"] == MACCHINA) == macchine}
            if not elenco:
                continue
            doc.add_heading(titolo, 2)
            for nome, a in sorted(elenco.items()):
                doc.add_heading(nome, 3)
                if a["descrizione"]:
                    doc.add_paragraph(a["descrizione"])
                propri = {r["descrizione"]: r for r in rischi if r["fonte"] == nome}
                if propri:
                    p = doc.add_paragraph()
                    p.add_run("Rischi generati dall'uso: ").bold = True
                    p.add_run("; ".join(propri) + ".")
                if a["misure"]:
                    doc.add_paragraph().add_run("Misure preventive e protettive:").bold = True
                    for riga in a["misure"].split("\n"):
                        doc.add_paragraph(riga)
                if a["dpi"]:
                    p = doc.add_paragraph()
                    chi = "dell'operatore" if macchine else "dell'utilizzatore"
                    p.add_run(f"DPI {chi}: ").bold = True
                    p.add_run(a["dpi"] + ".")
    else:
        testo_o_segnaposto(doc, "")

    doc.add_heading(f"{numero}. Sostanze e miscele pericolose e relative schede di sicurezza", 1)
    numero += 1
    aggiungi_sostanze(doc, repo, sostanze_impresa(repo, impresa_id))
    if sezioni["sostanze"].strip():
        testo_o_segnaposto(doc, sezioni["sostanze"])

    valutazioni = valutazioni_impresa(repo, impresa_id)
    for metodo, titolo in (("rumore", dict(SEZIONI_POS)["rumore"]),
                           ("vibrazioni", "Esito della valutazione delle vibrazioni")):
        elenco = [v for v in valutazioni if v["metodo"] == metodo]
        if metodo == "vibrazioni" and not elenco:
            continue
        doc.add_heading(f"{numero}. {titolo}", 1)
        numero += 1
        if elenco:
            tabella(doc, ["Mansione / gruppo omogeneo", "Esposizione", "Esito"], [
                [v["mansione"] or v["titolo"],
                 (e := METODI[metodo].esegui(repo.dati_valutazione(v["id"]))).indice_testo, e.classe]
                for v in elenco
            ])
            doc.add_paragraph("Il dettaglio dei calcoli e delle misure è riportato nel capitolo delle "
                              "valutazioni dei rischi specifici.").runs[0].italic = True
        if metodo == "rumore" and (sezioni["rumore"].strip() or not elenco):
            testo_o_segnaposto(doc, sezioni["rumore"])

    doc.add_heading(f"{numero}. Valutazione dei rischi e misure di prevenzione", 1)
    numero += 1
    lavorazione_corrente = None
    for f in fasi:
        if f["lavorazione"] != lavorazione_corrente:
            lavorazione_corrente = f["lavorazione"]
            if lavorazione_corrente:
                doc.add_heading(lavorazione_corrente, 2)
                gruppo = [g for g in fasi if g["lavorazione"] == lavorazione_corrente]
                doc.add_paragraph("La lavorazione è suddivisa nelle seguenti fasi: "
                                  + "; ".join(nome_fase(g) for g in gruppo) + ".")
        doc.add_heading(nome_fase(f) + (" (fase)" if f["lavorazione"] else ""), 3 if f["lavorazione"] else 2)
        if f["dettaglio"]:
            doc.add_paragraph(f["dettaglio"])
        struttura = struttura_fase(repo, f["id"])
        for etichetta, valore in (
            ("Macchine utilizzate", ", ".join(a["nome"] for a in struttura["macchine"])),
            ("Attrezzi e opere provvisionali", ", ".join(a["nome"] for a in struttura["attrezzi"])),
            ("Addetto", f["addetto"]),
            ("Modalità organizzative", f["modalita"]),
            ("Turni di lavoro", f["turni"]),
            ("Procedure complementari richieste dal PSC", f["procedure_psc"]),
        ):
            if valore:
                p = doc.add_paragraph()
                p.add_run(f"{etichetta}: ").bold = True
                p.add_run(valore)
        righe = []
        for r in (r for r in rischi if r["fase_id"] == f["id"]):
            livello = analisi.livello_rischio(r["probabilita"], r["danno"])
            descrizione = f"{r['descrizione']} ({r['fonte']})" if r["fonte"] else r["descrizione"]
            righe.append([descrizione, f"{livello} {analisi.classe_rischio(livello)}", r["misure"]])
        impegnati = repo.lavoratori_fase(f["id"])
        if impegnati:
            p = doc.add_paragraph()
            p.add_run("Lavoratori impegnati: ").bold = True
            p.add_run(", ".join(f"{anagrafiche.nominativo(l)} ({l['mansione']})" if l["mansione"]
                                else anagrafiche.nominativo(l) for l in impegnati))
        if righe:
            tabella(doc, ["Rischio", "Livello", "Misure"], righe)
        else:
            testo_o_segnaposto(doc, "")

    for chiave in ("integrative", "procedure"):
        doc.add_heading(f"{numero}. {dict(SEZIONI_POS)[chiave]}", 1)
        testo_o_segnaposto(doc, sezioni[chiave])
        numero += 1

    valutazioni = valutazioni_impresa(repo, impresa_id)
    if valutazioni:
        doc.add_heading(f"{numero}. Valutazioni dei rischi specifici", 1)
        numero += 1
        tabella(doc, ["Valutazione", "Metodo", "Indice", "Classe"], [
            [v["titolo"] or METODI[v["metodo"]].nome, METODI[v["metodo"]].norma,
             (e := METODI[v["metodo"]].esegui(repo.dati_valutazione(v["id"]))).indice_testo, e.classe]
            for v in valutazioni if v["metodo"] in METODI
        ])
        for v in valutazioni:
            aggiungi_valutazione(doc, repo, v, livello=2)

    doc.add_heading(f"{numero}. Dispositivi di protezione individuale forniti", 1)
    numero += 1
    con_dpi = [l for l in lavoratori if anagrafiche.dpi_lavoratore(l)]
    if con_dpi:
        tabella(doc, ["Qualifica", "Lavoratore", "DPI forniti"], [
            [l["mansione"], anagrafiche.nominativo(l), "; ".join(anagrafiche.dpi_lavoratore(l))] for l in con_dpi
        ])
    dpi = elenco_dpi([r["dpi"] for r in rischi])
    if dpi:
        doc.add_paragraph("DPI previsti dalle schede di rischio delle lavorazioni:")
        for voce in dpi:
            doc.add_paragraph(voce, style="List Bullet")
    elif not con_dpi:
        testo_o_segnaposto(doc, "")

    doc.add_heading(f"{numero}. Informazione e formazione dei lavoratori", 1)
    doc.add_paragraph(
        "I lavoratori ricevono informazione, formazione e addestramento ai sensi degli artt. 36, 37 e 77 "
        "del D.Lgs. 81/2008 e dell'Accordo Stato-Regioni vigente; la documentazione è conservata in cantiere."
    )
    if lavoratori:
        tabella(doc, ["N.", "Lavoratore", "Qualifica", "Informazione, formazione e addestramento"], [
            [str(n), anagrafiche.nominativo(l), l["mansione"], "; ".join(anagrafiche.formazione_lavoratore(l)) or "-"]
            for n, l in enumerate(lavoratori, 1)
        ])

    firma(doc, "Il Datore di lavoro")
    doc.add_paragraph("Per presa visione, il Rappresentante dei lavoratori per la sicurezza")
    doc.add_paragraph("_______________________________")

    destinazione = Path(destinazione)
    doc.save(destinazione)
    return destinazione
