"""Prova di fumo dell'interfaccia (senza display)."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from sicurcantiere.archivio import LAVORAZIONI  # noqa: E402
from sicurcantiere.db import Progetto  # noqa: E402
from sicurcantiere.ui.finestra import FinestraPrincipale  # noqa: E402
from sicurcantiere.documenti.pos import chiave_testo  # noqa: E402
from sicurcantiere.repository import Repository  # noqa: E402
from sicurcantiere.ui.pagine import (  # noqa: E402
    PaginaCosti,
    PaginaDocumenti,
    PaginaFasi,
    PaginaImprese,
    PaginaInterferenze,
)


@pytest.fixture(autouse=True)
def senza_dialoghi(monkeypatch):
    # I messaggi modali bloccherebbero il test.
    mb = QtWidgets.QMessageBox
    monkeypatch.setattr(mb, "warning", lambda *a, **k: mb.StandardButton.Ok)
    monkeypatch.setattr(mb, "critical", lambda *a, **k: mb.StandardButton.Ok)
    monkeypatch.setattr(mb, "question", lambda *a, **k: mb.StandardButton.Yes)


@pytest.fixture(scope="module")
def app():
    a = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    a.setOrganizationName("SicurCantiereTest")
    a.setApplicationName("SicurCantiereTest")
    return a


def _pagina(finestra, classe):
    return next(pg for pg in finestra.pagine if isinstance(pg, classe))


def _colonna(tabella, campo):
    return next(i for i, c in enumerate(tabella.colonne) if c.campo == campo)


def test_apre_e_mostra_tutte_le_pagine(app, tmp_path):
    p = Progetto(tmp_path / "c.scs", crea=True)
    p.chiudi()
    f = FinestraPrincipale()
    f.apri_file(tmp_path / "c.scs")
    assert f.progetto is not None
    repo = f.pagine[0].repo
    a = repo.inserisci("imprese", ragione_sociale="Alfa")
    b = repo.inserisci("imprese", ragione_sociale="Beta")
    repo.importa_lavorazione(LAVORAZIONI[0])
    for i in range(len(f.pagine)):
        f.navigazione.setCurrentRow(i)
        app.processEvents()

    fasi = _pagina(f, PaginaFasi)
    f.navigazione.setCurrentRow(f.pagine.index(fasi))
    t = fasi.fasi
    t.salva_cella(0, _colonna(t, "data_inizio"), "2025-10-06")
    t.salva_cella(0, _colonna(t, "data_fine"), "2025-10-01")  # fine prima dell'inizio: rifiutata
    assert repo.elenco("fasi")[0]["data_fine"] is None

    # Gantt analitico: 20.000 € x 50% / 250 = 40 ug, squadra 4 -> 10 giorni
    t.salva_cella(0, _colonna(t, "importo"), 20000.0)
    t.salva_cella(0, _colonna(t, "lavoratori"), 4)
    t.vista.selectRow(0)
    fasi._calcola_durata()
    assert repo.elenco("fasi")[0]["data_fine"] == "2025-10-17"
    assert fasi.dettaglio.isEnabled()
    n = len(fasi.rischi.righe())
    fasi.scelta_archivio.setCurrentText("Escavatore")
    fasi._aggiungi_attrezzatura()
    assert len(fasi.rischi.righe()) > n

    # Una seconda fase contemporanea di un'altra impresa crea un'interferenza.
    f2 = repo.inserisci("fasi", codice="X", impresa_id=b, data_inizio="2025-10-08", data_fine="2025-10-09")
    repo.aggiorna("fasi", repo.elenco("fasi")[0]["id"], impresa_id=a)
    pag = _pagina(f, PaginaInterferenze)
    f.navigazione.setCurrentRow(f.pagine.index(pag))
    assert pag.vista.rowCount() == 1
    pag.vista.item(0, 5).setText("Lavorare in zone separate")
    assert list(repo.prescrizioni().values()) == ["Lavorare in zone separate"]
    repo.elimina("fasi", f2)

    imprese = _pagina(f, PaginaImprese)
    f.navigazione.setCurrentRow(f.pagine.index(imprese))
    imprese.tabella.seleziona(a)
    imprese.figure.campi["datore_lavoro"].setText("Mario Bianchi")
    imprese.testi_pos.editor["rumore"].setPlainText("Sotto 80 dB(A)")

    costi = _pagina(f, PaginaCosti)
    f.navigazione.setCurrentRow(f.pagine.index(costi))
    costi.tabella.aggiungi()
    costi.tabella.salva_cella(0, 3, 10.0)
    costi.tabella.salva_cella(0, 4, 2.5)
    assert "25,00" in costi.totale.text()

    doc = _pagina(f, PaginaDocumenti)
    f.navigazione.setCurrentRow(f.pagine.index(doc))
    assert doc.controlli.count() > 0
    assert doc.impresa_pos.count() == 2

    f.navigazione.setCurrentRow(0)
    f.pagine[0].campi["nome"].setText("Scuola")
    f.close()
    assert f.progetto is None
    p = Progetto(tmp_path / "c.scs")
    r = Repository(p)
    assert r.cantiere()["nome"] == "Scuola"
    assert r.leggi("imprese", a)["datore_lavoro"] == "Mario Bianchi"
    assert r.testo(chiave_testo(a, "rumore")) == "Sotto 80 dB(A)"
    p.chiudi()
