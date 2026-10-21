import io
import json

import pytest

from sicurcantiere import __version__, aggiornamenti


class Risposta(io.BytesIO):
    def __init__(self, dati: bytes, lunghezza=None):
        super().__init__(dati)
        self.headers = {"Content-Length": str(len(dati) if lunghezza is None else lunghezza)}


def apri_con(dati, lunghezza=None):
    def apri(richiesta, timeout):
        apri.richieste.append(richiesta)
        if isinstance(dati, Exception):
            raise dati
        return Risposta(dati if isinstance(dati, bytes) else json.dumps(dati).encode(), lunghezza)
    apri.richieste = []
    return apri


def test_confronto_versioni():
    assert aggiornamenti.numero("v0.13.1") == (0, 13, 1)
    assert aggiornamenti.piu_recente("0.13.10", "0.13.9")
    assert not aggiornamenti.piu_recente("v0.13.1", "0.13.1")
    assert not aggiornamenti.piu_recente("0.12.9", "0.13.0")


def test_ultima_versione(monkeypatch):
    rilascio = {"tag_name": "v9.0.0", "html_url": "https://example.com/v9", "body": "Novità", "assets": [
        {"name": "SicurCantiere-9.0.0-setup.exe", "browser_download_url": "https://example.com/a.exe"},
        {"name": "SicurCantiere-setup.exe", "browser_download_url": "https://example.com/fisso.exe"}]}
    apri = apri_con(rilascio)
    v = aggiornamenti.ultima_versione(apri=apri)
    assert v == aggiornamenti.Versione("9.0.0", "https://example.com/fisso.exe", "https://example.com/v9", "Novità")
    assert apri.richieste[0].full_url == aggiornamenti.URL_ULTIMA_VERSIONE
    assert aggiornamenti.piu_recente(v.numero)
    monkeypatch.setenv("SICURCANTIERE_URL_AGGIORNAMENTI", "https://example.com/ultima")
    aggiornamenti.ultima_versione(apri=apri)
    assert apri.richieste[1].full_url == "https://example.com/ultima"
    with pytest.raises(aggiornamenti.ErroreAggiornamento, match="installatore"):
        aggiornamenti.ultima_versione(apri=apri_con({"tag_name": "v9", "assets": []}))
    with pytest.raises(aggiornamenti.ErroreAggiornamento, match="Impossibile"):
        aggiornamenti.ultima_versione(apri=apri_con(OSError("rete assente")))


def test_scarica(tmp_path):
    dati = b"x" * 600_000
    visti = []
    file = aggiornamenti.scarica("https://example.com/s.exe", tmp_path / "s.exe",
                                 lambda letti, totale: visti.append((letti, totale)), apri=apri_con(dati))
    assert file.read_bytes() == dati and visti[-1] == (600_000, 600_000)
    with pytest.raises(aggiornamenti.ErroreAggiornamento, match="annullato"):
        aggiornamenti.scarica("https://example.com/s.exe", tmp_path / "b.exe", lambda letti, totale: False, apri=apri_con(dati))
    with pytest.raises(aggiornamenti.ErroreAggiornamento, match="incompleto"):
        aggiornamenti.scarica("https://example.com/s.exe", tmp_path / "c.exe", apri=apri_con(dati, lunghezza=999_999))
    assert sorted(p.name for p in tmp_path.iterdir()) == ["s.exe"]  # niente file parziali


def test_comando_installatore(tmp_path):
    pytest.importorskip("PySide6.QtWidgets")
    from sicurcantiere.ui.aggiornamenti import comando_installatore

    comando = comando_installatore(tmp_path / "setup.exe", "PSC")
    assert "/SILENT" in comando and "/aggiornamento=si" in comando and "/programma=PSC" in comando
    assert __version__
