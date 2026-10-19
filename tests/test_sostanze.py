import os

import pytest

from sicurcantiere import sds, sostanze

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_codici_h():
    testo = "Indicazioni: H315 Provoca irritazione. H317, H318Danni H360FD EUH 208 H350i h999 H2O"
    assert sostanze.codici_h(testo) == ["H315", "H317", "H318", "H360FD", "EUH208", "H350i"]
    assert sostanze.elenco_codici("H315,H315 H319") == "H315, H319"
    assert sostanze.descrizione("H360FD") == sostanze.FRASI_H["H360"]
    assert "cancro se inalato" in sostanze.descrizione("H350i")


def test_pittogrammi_e_precedenze():
    assert sostanze.pittogrammi(["H225", "H319"]) == ["GHS02", "GHS07"]
    # GHS06 esclude GHS07
    assert sostanze.pittogrammi(["H301", "H302"]) == ["GHS06"]
    # GHS05 esclude GHS07 per irritazione cutanea/oculare, non per altri motivi
    assert sostanze.pittogrammi(["H318", "H315"]) == ["GHS05"]
    assert sostanze.pittogrammi(["H318", "H335"]) == ["GHS05", "GHS07"]
    # sensibilizzante respiratorio: GHS08, niente GHS07 per sensibilizzazione cutanea
    assert sostanze.pittogrammi(["H334", "H317"]) == ["GHS08"]
    assert sostanze.pittogrammi(["H350i"]) == ["GHS08"]
    assert sostanze.pittogrammi([]) == []


def test_categorie():
    cemento = sostanze.categorie(["H315", "H317", "H318", "H335"])
    nomi = [c.nome for c in cemento]
    assert nomi == ["Sensibilizzante", "Corrosivo", "Nocivo o irritante"]
    cancerogeno = sostanze.categorie(["H350", "H225"])
    assert cancerogeno[0].nome == "Cancerogeno o mutageno" and cancerogeno[0].grave
    assert any("Titolo IX, Capo II" in m for m in cancerogeno[0].misure)
    assert sostanze.categorie([]) == []


def _pdf(percorso, righe):
    from PySide6.QtGui import QPageSize, QPainter, QPdfWriter
    from PySide6.QtWidgets import QApplication

    QApplication.instance() or QApplication([])
    writer = QPdfWriter(str(percorso))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    p = QPainter(writer)
    for n, riga in enumerate(righe):
        p.drawText(200, 300 + n * 300, riga)
    p.end()


def test_lettura_sds_pdf(tmp_path):
    f = tmp_path / "scheda.pdf"
    _pdf(f, [
        "SCHEDA DI DATI DI SICUREZZA",
        "SEZIONE 1: Identificazione",
        "Nome commerciale: Cemento Portland CEM II 42,5",
        "Data di revisione: 15/03/2024",
        "SEZIONE 2: Identificazione dei pericoli",
        "Avvertenza: Pericolo",
        "H315 Provoca irritazione cutanea. H317 Puo provocare una reazione allergica cutanea.",
        "H318 Provoca gravi lesioni oculari. H335 Puo irritare le vie respiratorie.",
    ])
    dati, testo = sds.leggi_pdf(f)
    assert dati.codici_h == ["H315", "H317", "H318", "H335"]
    assert dati.avvertenza == "Pericolo"
    assert dati.data_revisione == "2024-03-15"
    assert dati.nome.startswith("Cemento Portland")
    assert "SEZIONE 2" in testo


def test_pdf_senza_testo(tmp_path):
    f = tmp_path / "vuoto.pdf"
    _pdf(f, [])
    with pytest.raises(sds.ErroreSDS, match="testo leggibile"):
        sds.leggi_pdf(f)
    with pytest.raises(sds.ErroreSDS):
        sds.leggi_pdf(tmp_path / "manca.pdf")
