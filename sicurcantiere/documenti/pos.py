"""Generazione del Piano Operativo di Sicurezza (Allegato XV, punto 3.2.1)."""

from __future__ import annotations

import re
from pathlib import Path

from sicurcantiere import analisi
from sicurcantiere.documenti.comune import (
    data_it,
    firma,
    frontespizio,
    nome_fase,
    nuovo_documento,
    tabella,
    tabella_voci,
    testo_o_segnaposto,
)
from sicurcantiere.documenti.valutazione import aggiungi_valutazione, valutazioni_impresa
from sicurcantiere.repository import Repository
from sicurcantiere.valutazioni import METODI

# Sezioni a testo libero del POS, salvate per impresa.
SEZIONI_POS: list[tuple[str, str]] = [
    ("attivita", "Attività svolte in cantiere, modalità organizzative e turni di lavoro"),
    ("sostanze", "Sostanze e miscele pericolose utilizzate"),
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
                 f"POS:{impresa_id}", [("Impresa", impresa["ragione_sociale"])])

    doc.add_heading("1. Dati identificativi dell'impresa", 1)
    tabella_voci(doc, [
        ("Ragione sociale", impresa["ragione_sociale"]),
        ("Ruolo nel cantiere", impresa["tipo"]),
        ("Partita IVA", impresa["partita_iva"]),
        ("Codice fiscale", impresa["codice_fiscale"]),
        ("Sede", impresa["indirizzo"]),
        ("Telefono", impresa["telefono"]),
        ("Posizioni INAIL / INPS / Cassa edile", impresa["posizione_inail_inps"]),
    ])

    doc.add_heading("2. Figure della sicurezza e relative mansioni", 1)
    tabella(doc, ["Figura", "Nominativo", "Compiti in cantiere"], [
        ["Datore di lavoro", impresa["datore_lavoro"],
         "Organizza il lavoro, redige il POS, fornisce DPI, formazione e attrezzature conformi."],
        ["Responsabile del servizio di prevenzione e protezione", impresa["rspp"],
         "Collabora alla valutazione dei rischi e alla redazione del POS."],
        ["Medico competente", impresa["medico_competente"],
         "Sorveglianza sanitaria ed espressione dei giudizi di idoneità."],
        ["Rappresentante dei lavoratori per la sicurezza", impresa["rls"],
         "Consultato sul PSC e sul POS; segnala i rischi individuati."],
        ["Direttore tecnico / capocantiere / preposto", impresa["preposto"] or impresa["referente"],
         "Sovrintende alle lavorazioni e verifica l'applicazione delle misure di sicurezza."],
        ["Addetti alle emergenze (primo soccorso, antincendio, evacuazione)", impresa["addetti_emergenze"],
         "Attuano le procedure di emergenza del cantiere."],
    ])

    doc.add_heading("3. Lavoratori impiegati in cantiere", 1)
    if lavoratori:
        tabella(doc, ["Nominativo", "Mansione", "Formazione e addestramento", "Idoneità sanitaria fino al"], [
            [l["nome"], l["mansione"], l["formazione"], data_it(l["idoneita_scadenza"])] for l in lavoratori
        ])
    else:
        testo_o_segnaposto(doc, "")

    numero = 4
    sezioni = {chiave: repo.testo(chiave_testo(impresa_id, chiave)) for chiave, _ in SEZIONI_POS}
    doc.add_heading(f"{numero}. {SEZIONI_POS[0][1]}", 1)
    testo_o_segnaposto(doc, sezioni["attivita"])
    if impresa["orario_lavoro"]:
        doc.add_paragraph(f"Orario di lavoro: {impresa['orario_lavoro']}")
    numero += 1

    doc.add_heading(f"{numero}. Lavorazioni svolte dall'impresa", 1)
    numero += 1
    tabella(doc, ["Lavorazione", "Zona", "Inizio", "Fine", "Lavoratori"], [
        [nome_fase(f), f["zona"], data_it(f["data_inizio"]), data_it(f["data_fine"]), str(f["lavoratori"])]
        for f in fasi
    ])

    doc.add_heading(f"{numero}. Opere provvisionali, macchine e attrezzature", 1)
    numero += 1
    per_tipo: dict[str, set[str]] = {}
    for a in attrezzature:
        per_tipo.setdefault(a["tipo"], set()).add(a["nome"])
    if per_tipo:
        tabella(doc, ["Tipo", "Elenco"], [
            [tipo, ", ".join(sorted(nomi))] for tipo, nomi in sorted(per_tipo.items())
        ])
    else:
        testo_o_segnaposto(doc, "")

    for chiave in ("sostanze", "rumore"):
        doc.add_heading(f"{numero}. {dict(SEZIONI_POS)[chiave]}", 1)
        testo_o_segnaposto(doc, sezioni[chiave])
        numero += 1

    doc.add_heading(f"{numero}. Valutazione dei rischi e misure di prevenzione", 1)
    numero += 1
    for f in fasi:
        doc.add_heading(nome_fase(f), 2)
        righe = []
        for r in (r for r in rischi if r["fase_id"] == f["id"]):
            livello = analisi.livello_rischio(r["probabilita"], r["danno"])
            descrizione = f"{r['descrizione']} ({r['fonte']})" if r["fonte"] else r["descrizione"]
            righe.append([descrizione, f"{livello} {analisi.classe_rischio(livello)}", r["misure"]])
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
    dpi = elenco_dpi([r["dpi"] for r in rischi])
    if dpi:
        for voce in dpi:
            doc.add_paragraph(voce, style="List Bullet")
    else:
        testo_o_segnaposto(doc, "")

    doc.add_heading(f"{numero}. Informazione e formazione dei lavoratori", 1)
    doc.add_paragraph(
        "I lavoratori elencati al capitolo 3 hanno ricevuto informazione, formazione e addestramento "
        "ai sensi degli artt. 36 e 37 del D.Lgs. 81/2008; la documentazione è conservata in cantiere."
    )

    firma(doc, "Il Datore di lavoro")
    doc.add_paragraph("Per presa visione, il Rappresentante dei lavoratori per la sicurezza")
    doc.add_paragraph("_______________________________")

    destinazione = Path(destinazione)
    doc.save(destinazione)
    return destinazione
