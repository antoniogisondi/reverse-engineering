import shutil

import pytest

from sicurcantiere import modelli, ricerca
from sicurcantiere.archivio import LAVORAZIONI
from sicurcantiere.cronologia import Cronologia
from sicurcantiere.db import Progetto
from sicurcantiere.repository import Repository


@pytest.fixture
def repo(tmp_path):
    progetto = Progetto(tmp_path / "prova.scs", crea=True)
    yield Repository(progetto)
    progetto.chiudi()


def test_annulla_e_ripeti_su_tutto_il_cantiere(repo, tmp_path):
    cronologia = Cronologia(repo.progetto)
    assert not cronologia.puo_annullare()
    repo.aggiorna_cantiere(nome="Scuola")
    assert cronologia.registra()
    impresa = repo.inserisci("imprese", ragione_sociale="Alfa")
    repo.importa_lavorazione(next(l for l in LAVORAZIONI if l["codice"] == "AL.21"))
    assert cronologia.registra()
    assert not cronologia.registra()  # niente di nuovo

    assert cronologia.annulla()  # via impresa e lavorazione insieme
    assert repo.elenco("imprese") == [] and repo.elenco("fasi") == [] and repo.cantiere()["nome"] == "Scuola"
    assert cronologia.ripeti()
    assert repo.leggi("imprese", impresa)["ragione_sociale"] == "Alfa" and repo.elenco("fasi")
    assert cronologia.annulla() and cronologia.annulla()
    assert repo.cantiere()["nome"] == ""
    assert not cronologia.annulla()

    # una nuova modifica cancella i passi da ripetere; il file resta quello del cantiere
    repo.aggiorna_cantiere(nome="Ospedale")
    cronologia.registra()
    assert not cronologia.puo_ripetere()
    repo.progetto.chiudi()
    assert Repository(Progetto(tmp_path / "prova.scs")).cantiere()["nome"] == "Ospedale"


def test_ricerca_in_tutto_il_cantiere(repo):
    repo.aggiorna_cantiere(nome="Scuola media", descrizione="Rifacimento della copertura")
    repo.inserisci("imprese", ragione_sociale="Edil Copertura srl")
    repo.importa_lavorazione(next(l for l in LAVORAZIONI if l["codice"] == "AL.21"))
    repo.salva_testo("org_viabilita", "Viabilità separata per mezzi e pedoni lungo la copertura")
    risultati = ricerca.cerca(repo, "copertura")
    tipi = {r.tipo for r in risultati}
    assert {"Impresa", "Dati del cantiere", "Testo"} <= tipi
    testo = next(r for r in risultati if r.tipo == "Testo")
    assert testo.titolo == "Viabilità principale di cantiere" and testo.sezione == "Relazione"
    assert ricerca.cerca(repo, "c") == []
    assert any(r.tipo == "Rischio" for r in ricerca.cerca(repo, "investimento"))


def test_modelli_di_cantiere(repo, tmp_path, monkeypatch):
    from sicurcantiere import composizioni

    monkeypatch.setenv("SICURCANTIERE_MODELLI", str(tmp_path / "modelli"))
    repo.aggiorna_cantiere(nome="Appartamento tipo")
    repo.importa_lavorazione(next(l for l in LAVORAZIONI if l["codice"] == "AL.21"))
    repo.salva_testo("org_servizi", "Servizi dell'appartamento")
    composizioni.componi(repo, "PSC")
    modello = modelli.salva_come_modello(repo.progetto.conn, "Ristrutturazione: appartamento", ".scs")
    assert modello.name == "Ristrutturazione- appartamento.scs"
    assert modelli.elenco(".scs") == [modello] and modelli.elenco(".spo") == []

    nuovo = modelli.crea_da_modello(modello, tmp_path / "nuovo.scs")
    r = Repository(Progetto(nuovo))
    assert r.cantiere()["nome"] == "Appartamento tipo" and r.elenco("fasi")
    assert r.testo("org_servizi") == "Servizi dell'appartamento"
    assert composizioni.elenco(r, "PSC") == [] and r.elenco("revisioni") == []
    r.progetto.chiudi()
    modelli.elimina(modello)
    assert modelli.elenco(".scs") == []


@pytest.mark.skipif(not shutil.which("soffice") and not shutil.which("libreoffice"),
                    reason="serve LibreOffice (o Word su Windows)")
def test_conversione_in_pdf(repo, tmp_path):
    from sicurcantiere.documenti import pdf
    from sicurcantiere.documenti.notifica import genera_notifica

    docx = genera_notifica(repo, tmp_path / "notifica.docx")
    risultato = pdf.converti(docx)
    assert risultato.suffix == ".pdf" and risultato.read_bytes().startswith(b"%PDF")
