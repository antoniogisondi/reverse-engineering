"""Ricerca in tutto il cantiere: fasi, rischi, attrezzature, imprese, lavoratori, soggetti, sostanze,
costi e testi. Ogni risultato dice in quale pagina si trova (la sezione dei controlli della pagina)."""

from __future__ import annotations

from dataclasses import dataclass

from sicurcantiere.repository import Repository


@dataclass(frozen=True)
class Risultato:
    tipo: str  # «Fase», «Rischio», «Impresa»...
    titolo: str
    dettaglio: str
    sezione: str  # sezione dei controlli della pagina in cui si trova
    tabella: str = ""
    id_: int | None = None


# (tabella, tipo, campi in cui cercare, campo del titolo, sezione)
_TABELLE = [
    ("fasi", "Fase", ("codice", "descrizione", "lavorazione", "dettaglio", "zona", "addetto", "procedure_psc"),
     "descrizione", "Fasi"),
    ("rischi", "Rischio", ("descrizione", "fonte", "misure", "dpi", "motivazione"), "descrizione", "Rischi"),
    ("attrezzature", "Attrezzatura", ("nome", "descrizione", "misure", "dpi"), "nome", "Fasi"),
    ("imprese", "Impresa", ("ragione_sociale", "datore_lavoro", "partita_iva", "codice_fiscale", "tipologia_lavori",
                            "referente", "email", "pec"), "ragione_sociale", "Imprese"),
    ("lavoratori", "Lavoratore", ("nome", "cognome", "mansione", "codice_fiscale"), "nome", "Lavoratori"),
    ("figure", "Figura della sicurezza", ("ruolo", "nome", "qualifica"), "nome", "Figure della sicurezza"),
    ("soggetti", "Soggetto", ("ruolo", "nome", "rappresentante", "qualifica", "email"), "nome", "Soggetti"),
    ("sostanze", "Sostanza", ("nome", "produttore", "codici_h", "uso"), "nome", "Sostanze"),
    ("costi", "Costo della sicurezza", ("codice", "descrizione"), "descrizione", "Costi"),
    ("valutazioni", "Valutazione", ("titolo", "mansione"), "titolo", "Valutazioni"),
    ("ponteggi", "Ponteggio", ("nome", "tipo", "fabbricante", "modello"), "nome", "Ponteggi"),
]


def _estratto(testo: str, cercato: str, larghezza: int = 90) -> str:
    posizione = testo.lower().find(cercato)
    if posizione < 0:
        return testo[:larghezza]
    inizio = max(0, posizione - larghezza // 3)
    estratto = testo[inizio:inizio + larghezza].replace("\n", " ")
    return ("..." if inizio else "") + estratto + ("..." if inizio + larghezza < len(testo) else "")


def cerca(repo: Repository, testo: str, massimo: int = 200) -> list[Risultato]:
    cercato = testo.strip().lower()
    if len(cercato) < 2:
        return []
    risultati: list[Risultato] = []
    for tabella, tipo, campi, campo_titolo, sezione in _TABELLE:
        try:
            righe = repo.elenco(tabella)
        except ValueError:  # tabella non presente in questa versione del file
            continue
        for riga in righe:
            for campo in campi:
                valore = str(riga.get(campo) or "")
                if cercato in valore.lower():
                    titolo = str(riga.get(campo_titolo) or "").strip() or f"{tipo} n. {riga['id']}"
                    if tabella == "lavoratori":
                        titolo = " ".join(v for v in (riga.get("cognome"), riga.get("nome")) if v) or titolo
                    risultati.append(Risultato(tipo, titolo, _estratto(valore, cercato), sezione, tabella, riga["id"]))
                    break
            if len(risultati) >= massimo:
                return risultati
    c = repo.cantiere()
    for campo, etichetta in (("nome", "Opera"), ("descrizione", "Descrizione dell'opera"),
                             ("natura_opera", "Natura dell'opera"), ("indirizzo", "Indirizzo")):
        if cercato in str(c.get(campo) or "").lower():
            risultati.append(Risultato("Dati del cantiere", etichetta, _estratto(str(c[campo]), cercato),
                                       "Dati generali"))
    for riga in repo.progetto.query("SELECT sezione, testo FROM relazione WHERE lower(testo) LIKE ?",
                                    (f"%{cercato}%",)):
        sezione = riga["sezione"]
        if sezione.startswith(("pos:", "pimus:")) or sezione in ("allegato_xi", "ordigni_bellici", "foto_cantiere",
                                                                 "logo_studio"):
            pagina = "Testi del POS" if sezione.startswith("pos:") else "Ponteggi" if sezione.startswith("pimus:") \
                else "Relazione"
        else:
            pagina = "Relazione"
        risultati.append(Risultato("Testo", _titolo_sezione(sezione), _estratto(riga["testo"], cercato), pagina))
    return risultati[:massimo]


def _titolo_sezione(chiave: str) -> str:
    from sicurcantiere.relazione import SEZIONI_DETTAGLIO

    if chiave in SEZIONI_DETTAGLIO:
        return SEZIONI_DETTAGLIO[chiave].titolo
    if chiave.startswith("pos:"):
        from sicurcantiere.documenti.pos import SEZIONI_POS

        return dict(SEZIONI_POS).get(chiave.rsplit(":", 1)[-1], "Testo del POS")
    return "Testo"
