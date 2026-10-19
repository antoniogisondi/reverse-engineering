"""Prova di fumo dell'interfaccia (senza display)."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from sicurcantiere.archivio import LAVORAZIONI  # noqa: E402
from sicurcantiere.db import Progetto  # noqa: E402
from sicurcantiere.ui.finestra import FinestraPrincipale  # noqa: E402
from sicurcantiere.ui.pagine import PaginaCosti, PaginaFasi  # noqa: E402


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


def test_apre_e_mostra_tutte_le_pagine(app, tmp_path):
    p = Progetto(tmp_path / "c.scs", crea=True)
    p.chiudi()
    f = FinestraPrincipale()
    f.apri_file(tmp_path / "c.scs")
    assert f.progetto is not None
    repo = f.pagine[0].repo
    repo.inserisci("imprese", ragione_sociale="Alfa")
    repo.importa_lavorazione(LAVORAZIONI[0])
    for i in range(len(f.pagine)):
        f.navigazione.setCurrentRow(i)
        app.processEvents()

    fasi = next(pg for pg in f.pagine if isinstance(pg, PaginaFasi))
    fasi.fasi.salva_cella(0, 3, "2025-10-06")
    fasi.fasi.salva_cella(0, 4, "2025-10-01")  # fine prima dell'inizio: rifiutata
    assert repo.elenco("fasi")[0]["data_fine"] is None
    fasi.fasi.vista.selectRow(0)
    assert fasi.rischi.isEnabled()
    assert len(fasi.rischi.righe()) == len(LAVORAZIONI[0]["rischi"])

    costi = next(pg for pg in f.pagine if isinstance(pg, PaginaCosti))
    costi.tabella.aggiungi()
    costi.tabella.salva_cella(0, 3, 10.0)
    costi.tabella.salva_cella(0, 4, 2.5)
    assert "25,00" in costi.totale.text()

    f.pagine[0].campi["nome"].setText("Scuola")
    f.close()
    assert f.progetto is None
    p = Progetto(tmp_path / "c.scs")
    assert p.query("SELECT nome FROM cantiere")[0]["nome"] == "Scuola"
    p.chiudi()
