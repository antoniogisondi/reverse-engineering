"""Prova di fumo dell'interfaccia (senza display)."""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
if os.name == "nt":
    # In modalità offscreen Qt su Windows non trova da solo i caratteri di sistema.
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"))

QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtCore = pytest.importorskip("PySide6.QtCore")

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
    PaginaSoggetti,
)

QDate = QtCore.QDate


@pytest.fixture(autouse=True)
def senza_dialoghi(monkeypatch):
    # I messaggi modali bloccherebbero il test.
    mb = QtWidgets.QMessageBox
    monkeypatch.setattr(mb, "warning", lambda *a, **k: mb.StandardButton.Ok)
    monkeypatch.setattr(mb, "critical", lambda *a, **k: mb.StandardButton.Ok)
    monkeypatch.setattr(mb, "question", lambda *a, **k: mb.StandardButton.Yes)
    monkeypatch.setattr(mb, "information", lambda *a, **k: mb.StandardButton.Ok)


@pytest.fixture(scope="module")
def app():
    a = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    a.setOrganizationName("SicurCantiereTest")
    a.setApplicationName("SicurCantiereTest")
    yield a
    # Distrugge i widget prima dell'uscita dell'interprete: lasciati al
    # garbage collector verrebbero liberati in ordine casuale (crash di Qt).
    for w in a.topLevelWidgets():
        w.close()
        w.deleteLater()
    a.sendPostedEvents(None, QtCore.QEvent.Type.DeferredDelete)
    a.processEvents()


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
    repo.importa_lavorazione(next(l for l in LAVORAZIONI if l["codice"] == "AL.21"))  # manodopera 50%
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
    assert not imprese.schede.isVisibleTo(imprese)  # nel PSC niente dati del POS

    costi = _pagina(f, PaginaCosti)
    f.navigazione.setCurrentRow(f.pagine.index(costi))
    costi.tabella.aggiungi()
    costi.tabella.salva_cella(0, 3, 10.0)
    costi.tabella.salva_cella(0, 4, 2.5)
    assert "25,00" in costi.totale.text()

    doc = _pagina(f, PaginaDocumenti)
    f.navigazione.setCurrentRow(f.pagine.index(doc))
    assert doc.controlli.count() > 0
    assert doc.documenti == ("psc", "fascicolo", "notifica")
    assert not any(type(pg).__name__ in ("PaginaValutazioni", "PaginaPonteggi") for pg in f.pagine)

    f.navigazione.setCurrentRow(0)
    f.pagine[0].campi["nome"].setText("Scuola")
    f.close()
    assert f.progetto is None
    p = Progetto(tmp_path / "c.scs")
    r = Repository(p)
    assert r.cantiere()["nome"] == "Scuola"
    p.chiudi()


def test_icone_e_tema(app):
    from sicurcantiere.ui import tema
    from sicurcantiere.ui.icone import NOMI, icona
    from sicurcantiere.ui.edizioni import EDIZIONI

    for nome in NOMI:
        assert not icona(nome, "#000000").pixmap(24, 24).toImage().isNull()
    assert {p.icona for e in EDIZIONI.values() for p in e.pagine} <= set(NOMI)
    for scuro in (True, False):
        c = tema.applica(app, scuro)
        assert app.palette().window().color().name().lower() == c.sfondo.lower()
        assert "QListWidget#navigazione" in app.styleSheet()


def test_campi_numerici_visibili(app):
    # Regressione: con il foglio di stile, il testo dei campi numerici non deve sparire.
    from sicurcantiere.ui import tema

    tema.applica(app)
    s = QtWidgets.QDoubleSpinBox()
    s.setRange(0, 1e10)
    s.setValue(480000)
    s.resize(300, 30)
    s.show()
    app.processEvents()
    assert s.lineEdit().width() > 200
    s.close()


def test_riepilogo(app, tmp_path):
    from sicurcantiere.ui.riepilogo import ATTENZIONE, ERRORE, OK, calcola

    p = Progetto(tmp_path / "r.scs", crea=True)
    r = Repository(p)
    voci = {v.chiave: v for v in calcola(r)}
    assert voci["psc"].stato == OK and voci["interferenze"].stato == OK
    r.aggiorna_cantiere(importo_lavori=100000)
    a = r.inserisci("imprese", ragione_sociale="A")
    b = r.inserisci("imprese", ragione_sociale="B")
    f1 = r.importa_lavorazione(next(l for l in LAVORAZIONI if l["codice"] == "AL.29"))  # ponteggio
    f2 = r.inserisci("fasi", codice="X")
    r.aggiorna("fasi", f1, impresa_id=a, data_inizio="2025-10-06", data_fine="2025-10-10", lavoratori=3)
    r.aggiorna("fasi", f2, impresa_id=b, data_inizio="2025-10-08", data_fine="2025-10-09", lavoratori=2)
    r.inserisci("costi", quantita=1, prezzo_unitario=3000)
    voci = {v.chiave: v for v in calcola(r)}
    assert voci["psc"].stato == ATTENZIONE
    assert voci["interferenze"].valore == "1" and voci["interferenze"].stato == ERRORE
    assert voci["picco"].valore == "5"
    assert "3,0%" in voci["importo"].nota
    assert voci["controlli"].stato == ERRORE
    p.chiudi()


def test_gantt_trascinamento_e_zoom(app):
    from datetime import date

    from PySide6.QtCore import QPoint
    from PySide6.QtTest import QTest

    from sicurcantiere.ui.gantt import ALTEZZA_INTESTAZIONE, ALTEZZA_RIGA, ZOOM, Gantt

    g = Gantt()
    fasi = [
        {"id": 1, "codice": "A", "descrizione": "", "impresa_id": 1, "zona": "", "lavoratori": 2,
         "data_inizio": "2025-10-06", "data_fine": "2025-10-10"},
        {"id": 2, "codice": "B", "descrizione": "", "impresa_id": 2, "zona": "", "lavoratori": 2,
         "data_inizio": "2025-10-08", "data_fine": "2025-10-09"},
    ]
    g.imposta_fasi(fasi, {}, {1: "Alfa", 2: "Beta"})
    assert g.colore_impresa(1) != g.colore_impresa(2)
    g.imposta_zoom("Giorni")
    g.show()
    app.processEvents()
    assert g.width() > 30 * ZOOM["Giorni"]
    g.grab()  # il disegno non deve sollevare eccezioni

    ricevuti = []
    g.fase_modificata.connect(lambda *a: ricevuti.append(a))
    y = ALTEZZA_INTESTAZIONE + ALTEZZA_RIGA // 2
    barra = g._rett_barra(0, date(2025, 10, 6), date(2025, 10, 10))
    # Sposta di 3 giorni trascinando dal centro.
    centro = QPoint(int(barra.center().x()), y)
    QTest.mousePress(g, QtCore.Qt.MouseButton.LeftButton, pos=centro)
    QTest.mouseMove(g, centro + QPoint(3 * ZOOM["Giorni"], 0))
    QTest.mouseRelease(g, QtCore.Qt.MouseButton.LeftButton, pos=centro + QPoint(3 * ZOOM["Giorni"], 0))
    assert ricevuti[-1] == (1, "2025-10-09", "2025-10-13")
    # Allunga di 2 giorni dal bordo destro.
    bordo = QPoint(int(barra.right()) - 2, y)
    QTest.mousePress(g, QtCore.Qt.MouseButton.LeftButton, pos=bordo)
    QTest.mouseMove(g, bordo + QPoint(2 * ZOOM["Giorni"], 0))
    QTest.mouseRelease(g, QtCore.Qt.MouseButton.LeftButton, pos=bordo + QPoint(2 * ZOOM["Giorni"], 0))
    assert ricevuti[-1] == (1, "2025-10-06", "2025-10-12")
    g.close()


def test_benvenuto_con_recenti(app, tmp_path):
    p = Progetto(tmp_path / "recente.scs", crea=True)
    Repository(p).aggiorna_cantiere(nome="Cantiere Rossi", comune="Lecce")
    p.chiudi()
    f = FinestraPrincipale()
    f.impostazioni.setValue("recenti", [str(tmp_path / "recente.scs"), str(tmp_path / "sparito.scs")])
    f._mostra_benvenuto()
    from sicurcantiere.ui.finestra import SchedaRecente

    schede = f.contenitore.widget(0).findChildren(SchedaRecente)
    assert len(schede) == 1
    testi = " ".join(l.text() for l in schede[0].findChildren(QtWidgets.QLabel))
    assert "Cantiere Rossi" in testi and "Lecce" in testi
    schede[0].click()
    assert f.progetto is not None and f.progetto.percorso.name == "recente.scs"
    f.close()


def test_programma_pos(app, tmp_path):
    from sicurcantiere.ai import Compilazione
    from sicurcantiere.ui.edizioni import POS
    from sicurcantiere.ui.valutazioni import PaginaValutazioni
    from sicurcantiere.valutazioni import METODI

    p = Progetto(tmp_path / "v.spo", crea=True)
    p.chiudi()
    f = FinestraPrincipale(POS)
    f.apri_file(tmp_path / "v.spo")
    assert f.windowTitle() == "v.spo - SicurCantiere POS"
    assert [type(pg).__name__ for pg in f.pagine] == [
        "PaginaCantierePOS", "PaginaSoggettiPOS", "PaginaImpresePOS", "PaginaFasiPOS",
        "PaginaValutazioni", "PaginaSostanze", "PaginaDocumentiPOS"]
    repo = f.pagine[0].repo
    assert f.pagine[0].riepilogo is not None and "lavoratori" in f.pagine[0].riepilogo.tessere

    a = repo.inserisci("imprese", ragione_sociale="Alfa")
    imprese = _pagina(f, PaginaImprese)
    f.navigazione.setCurrentRow(f.pagine.index(imprese))
    imprese.tabella.seleziona(a)
    assert imprese.schede.count() == 5
    imprese.figure.campi["datore_lavoro"].setText("Mario Bianchi")
    f.salva()  # pulsante Salva: anche il campo ancora in modifica finisce nel file
    assert repo.leggi("imprese", a)["datore_lavoro"] == "Mario Bianchi"
    assert f.azione_salva.isEnabled() and "Salvato alle" in f.stato_salvataggio.text()
    imprese.figure.campi["rspp_datore"].setChecked(True)
    imprese.dati.campi["ccnl"].setCurrentText("Edilizia - artigianato")
    imprese.dati.campi["durc_scadenza"].setDate(QDate(2030, 5, 31))
    assert imprese.dati.valore("durc_scadenza") == "2030-05-31"
    imprese.elenco_figure.aggiungi()
    assert repo.elenco("figure", impresa_id=a)[0]["ruolo"] == "Preposto"
    b = repo.inserisci("imprese", ragione_sociale="Beta", tipo="Subappaltatrice")
    imprese.tabella.ricarica()
    imprese.tabella.seleziona(b)
    affidataria = imprese.dati.campi["affidataria_id"]
    affidataria.setCurrentIndex(affidataria.findData(a))
    assert repo.leggi("imprese", b)["affidataria_id"] == a
    imprese.tabella.seleziona(a)
    assert imprese.dati.valore("ccnl") == "Edilizia - artigianato"

    from sicurcantiere.ui.edizioni import PaginaFasiPOS

    lavorazioni = _pagina(f, PaginaFasiPOS)
    campi = [c.campo for c in lavorazioni.fasi.colonne]
    assert "data_inizio" not in campi and "importo" not in campi and "lavorazione" in campi
    assert lavorazioni.gantt.isHidden() or not lavorazioni.gantt.isVisible()

    # Maestranze: dettaglio, DPI, mansioni.
    from sicurcantiere.ui.maestranze import DialogoMansioni
    from sicurcantiere.ui.modulo import DialogoDPI

    fase = repo.importa_lavorazione(LAVORAZIONI[0])
    repo.aggiorna("fasi", fase, impresa_id=a)
    imprese.lavoratori.tabella.aggiungi()
    lav = repo.elenco("lavoratori", impresa_id=a)[0]
    assert lav["autonomo"] == 0
    imprese.lavoratori.tabella.seleziona(lav["id"])
    det = imprese.lavoratori.dettaglio
    det.campi["form_base"].setChecked(True)
    det.campi["data_nascita"].setDate(QDate(1966, 5, 20))
    assert repo.leggi("lavoratori", lav["id"])["data_nascita"] == "1966-05-20"
    dialogo_dpi = DialogoDPI(["casco"], ["guanti", "Imbracatura speciale"])
    dialogo_dpi._suggeriti()
    assert dialogo_dpi.scelti()[:1] == ["casco"] and "guanti" in dialogo_dpi.scelti()
    assert "Imbracatura speciale" in dialogo_dpi.scelti()
    mansioni = DialogoMansioni(repo, repo.leggi("lavoratori", lav["id"]))
    radice = mansioni.albero.topLevelItem(0)
    assert radice.foreground(0).color().name() == "#c0392b"  # nessun lavoratore ancora assegnato
    radice.child(0).setCheckState(0, QtCore.Qt.CheckState.Checked)  # spunta anche la lavorazione
    mansioni._conferma()
    assert {f for f, _ in repo.mansioni(lav["id"])} == {fase}
    assert len(repo.mansioni(lav["id"])) == 2
    imprese.autonomi.tabella.aggiungi()
    assert repo.elenco("lavoratori", impresa_id=a, autonomo=1)
    assert imprese.lavoratori.tabella.vista.rowCount() == 1

    soggetti = _pagina(f, PaginaSoggetti)
    f.navigazione.setCurrentRow(f.pagine.index(soggetti))
    soggetti.committente_rl.setChecked(True)
    assert repo.cantiere()["committente_rl"] == 1
    imprese.testi_pos.editor["rumore"].setPlainText("Sotto 80 dB(A)")

    pv = _pagina(f, PaginaValutazioni)
    f.navigazione.setCurrentRow(f.pagine.index(pv))
    pv.tabella.aggiungi()
    v = repo.elenco("valutazioni")[0]["id"]
    pv.tabella.seleziona(v)
    assert pv.editor.metodo.chiave == "niosh"
    pv.editor.campi["peso"].setValue(30)
    assert "Indice" in pv.esito.indice.text()
    pv.salva_in_sospeso()
    assert repo.dati_valutazione(v)["peso"] == 30
    # Risultato dell'assistente applicato all'editor e salvato.
    dati = {**METODI["niosh"].dati_predefiniti(), "peso": 12}
    pv._applica_ai(v, METODI["niosh"], Compilazione("Casseforme", "Carpentiere", dati, ["Ipotesi 1"]))
    riga = repo.leggi("valutazioni", v)
    assert riga["titolo"] == "Casseforme" and repo.dati_valutazione(v)["ipotesi_ai"] == ["Ipotesi 1"]
    # Cambio di metodo: l'editor mostra la tabella dei compiti.
    pv.tabella.salva_cella(0, 1, "ocra")
    assert pv.editor.metodo.chiave == "ocra" and pv.editor.tabella.rowCount() >= 1
    pv.editor._aggiungi_compito()
    pv.salva_in_sospeso()
    assert len(repo.dati_valutazione(v)["compiti"]) == 2

    doc = _pagina(f, PaginaDocumenti)
    f.navigazione.setCurrentRow(f.pagine.index(doc))
    assert doc.documenti == ("pos", "sostanze", "dpi", "tesserini", "schede") and doc.impresa.count() == 2
    messaggi = [doc.controlli.item(i).text() for i in range(doc.controlli.count())]
    assert any("medico competente" in m for m in messaggi)
    assert "error" in f.stato_controlli.text()
    f.close()
    p = Progetto(tmp_path / "v.spo")
    r = Repository(p)
    impresa = r.leggi("imprese", a)
    assert r.leggi("lavoratori", lav["id"])["form_base"] == 1
    assert impresa["datore_lavoro"] == "Mario Bianchi" and impresa["rspp_datore"] == 1
    assert impresa["ccnl"] == "Edilizia - artigianato" and impresa["durc_scadenza"] == "2030-05-31"
    assert r.testo(chiave_testo(a, "rumore")) == "Sotto 80 dB(A)"
    p.chiudi()


def test_programma_pimus(app, tmp_path):
    from sicurcantiere import pimus
    from sicurcantiere.ui.edizioni import PIMUS
    from sicurcantiere.ui.ponteggi import PaginaPonteggi

    p = Progetto(tmp_path / "p.spm", crea=True)
    p.chiudi()
    f = FinestraPrincipale(PIMUS)
    f.apri_file(tmp_path / "p.spm")
    repo = f.pagine[0].repo
    assert f.pagine[0].riepilogo is None
    pp = _pagina(f, PaginaPonteggi)
    f.navigazione.setCurrentRow(f.pagine.index(pp))
    pp.tabella.aggiungi()
    pid = repo.elenco("ponteggi")[0]["id"]
    pp.tabella.seleziona(pid)
    assert pp.avvisi.text()
    pp._testi_base()
    pp._carica_verifiche()
    assert len(repo.elenco("verifiche_ponteggio", ponteggio_id=pid)) > 10
    assert repo.testo(pimus.chiave_testo(pid, "uso")).startswith("È vietato")
    assert f._pagina_principale() is pp
    f.close()


def test_nuovo_file_con_estensione_del_programma(app, tmp_path, monkeypatch):
    from sicurcantiere.ui.edizioni import POS

    f = FinestraPrincipale(POS)
    monkeypatch.setattr(QtWidgets.QFileDialog, "getSaveFileName",
                        lambda *a, **k: (str(tmp_path / "Cliente X"), ""))
    f.nuovo()
    assert f.progetto.percorso.name == "Cliente X.spo"
    f.close()


def test_pagina_sostanze(app, tmp_path, monkeypatch):
    from sicurcantiere.ui import sostanze as ui_sostanze
    from sicurcantiere.ui.edizioni import POS
    from sicurcantiere.ui.sostanze import PaginaSostanze
    from tests.test_sostanze import _pdf

    scheda = tmp_path / "Cemento.pdf"
    _pdf(scheda, ["Nome commerciale: Cemento CEM II", "Avvertenza: Pericolo",
                  "H315 H317 H318 H335", "Data di revisione: 01/02/2024"])
    p = Progetto(tmp_path / "s.spo", crea=True)
    p.chiudi()
    f = FinestraPrincipale(POS)
    f.apri_file(tmp_path / "s.spo")
    repo = f.pagine[0].repo
    a = repo.inserisci("imprese", ragione_sociale="Alfa")
    pagina = _pagina(f, PaginaSostanze)
    f.navigazione.setCurrentRow(f.pagine.index(pagina))
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileName", lambda *a, **k: (str(scheda), ""))
    chiamate = []
    monkeypatch.setattr(ui_sostanze, "esegui_ai", lambda *a: chiamate.append(a))
    pagina._importa_pdf()
    s = repo.elenco("sostanze")[0]
    assert s["nome"] == "Cemento CEM II" and s["impresa_id"] == a
    assert s["codici_h"] == "H315, H317, H318, H335" and s["data_sds"] == "2024-02-01"
    assert "Corrosivo" in pagina.classificazione.testo.text()
    assert len(chiamate) == 1  # l'utente ha accettato il completamento con l'AI
    pagina._applica_ai(s["id"], {"produttore": "Beta spa", "codici_h": "H315, H319", "dpi": "Guanti",
                                 "nome": "Altro nome", "data_revisione": "2020-01-01"})
    s = repo.leggi("sostanze", s["id"])
    assert s["produttore"] == "Beta spa" and s["dpi"] == "Guanti"
    assert s["nome"] == "Cemento CEM II" and s["data_sds"] == "2024-02-01"  # dati del PDF mantenuti
    assert s["codici_h"] == "H315, H317, H318, H335, H319"
    # Più lavorazioni per la stessa sostanza.
    from sicurcantiere.ui.sostanze import DialogoLavorazioni

    f1 = repo.inserisci("fasi", codice="A", descrizione="Getti")
    f2 = repo.inserisci("fasi", codice="B", descrizione="Massetti")
    dialogo = DialogoLavorazioni(repo, s["id"])
    for i in range(dialogo.elenco.count()):
        dialogo.elenco.item(i).setCheckState(QtCore.Qt.CheckState.Checked)
    assert dialogo.scelte() == [f1, f2]
    repo.salva_fasi_sostanza(s["id"], dialogo.scelte())
    pagina.tabella.ricarica()
    assert "A Getti; B Massetti" in pagina.tabella.vista.item(0, 2).text()
    f.close()


def test_dialogo_archivio_lavorazioni(app, tmp_path):
    from sicurcantiere.archivio_utente import ArchivioAnagrafiche
    from sicurcantiere.ui.pagine import DialogoArchivio

    p = Progetto(tmp_path / "a.spo", crea=True)
    r = Repository(p)
    fase = r.importa_lavorazione(LAVORAZIONI[0])
    archivio = ArchivioAnagrafiche()
    archivio.salva_lavorazione(r, fase)
    archivio.chiudi()
    d = DialogoArchivio()
    nodi = [d.albero.topLevelItem(i).text(0) for i in range(d.albero.topLevelItemCount())]
    assert nodi[0] == "Allestimento e smobilizzo del cantiere" and nodi[-1].startswith("UTENTE")
    utente = d.albero.topLevelItem(d.albero.topLevelItemCount() - 1)
    utente.child(0).setCheckState(0, QtCore.Qt.CheckState.Checked)
    d.tipologia.setCurrentText("Restauri")  # la spunta resta dopo il cambio di tipologia
    nodi = [d.albero.topLevelItem(i).text(0) for i in range(d.albero.topLevelItemCount())]
    assert "Lavori stradali" not in nodi
    scelte = d.selezionate()
    assert len(scelte) == 1 and "dati" in scelte[0]
    d.filtro.setText("ponteggio")
    assert not d.albero.topLevelItem(0).isHidden()
    d.deleteLater()
    p.chiudi()


def test_foto_cantiere_pos(app, tmp_path, monkeypatch):
    from sicurcantiere import segnaletica
    from sicurcantiere.ui.edizioni import POS, PaginaCantierePOS

    Progetto(tmp_path / "f.spo", crea=True).chiudi()
    f = FinestraPrincipale(POS)
    f.apri_file(tmp_path / "f.spo")
    pagina = _pagina(f, PaginaCantierePOS)
    foto = [str(segnaletica.SEGNALI[k].file) for k in ("casco", "guanti")]
    monkeypatch.setattr(QtWidgets.QFileDialog, "getOpenFileNames", lambda *a, **k: (foto, ""))
    pagina.foto._aggiungi()
    pagina.foto._aggiungi()  # nessun doppione
    assert pagina.foto.elenco.count() == 2 and pagina.foto.percorsi() == foto
    pagina.foto.elenco.setCurrentRow(0)
    pagina.foto._rimuovi()
    assert pagina.foto.percorsi() == foto[1:]
    f.close()
