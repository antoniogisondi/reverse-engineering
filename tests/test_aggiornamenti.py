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


# --- aggiornamenti firmati ---

PRIVATA = bytes(range(40, 72))


def _pubblica():
    import base64

    from sicur_license.certificato import pubblica_da_privata

    return base64.b64encode(pubblica_da_privata(PRIVATA)).decode()


def _apri_file(contenuti: dict):
    """Server finto: risponde a ogni indirizzo con il contenuto indicato."""
    def apri(richiesta, timeout):
        return Risposta(contenuti[richiesta.full_url])
    return apri


def test_firma_e_verifica_dell_installatore(tmp_path, monkeypatch):
    monkeypatch.setenv("SICURCANTIERE_CHIAVE_AGGIORNAMENTI", _pubblica())
    setup = tmp_path / "setup.exe"
    setup.write_bytes(b"MZ" + bytes(5000))
    firma = aggiornamenti.firma_installatore(setup, "0.24.0", PRIVATA)
    aggiornamenti.verifica_installatore(setup, "0.24.0", firma)
    with pytest.raises(aggiornamenti.ErroreAggiornamento, match="altra versione"):
        aggiornamenti.verifica_installatore(setup, "0.25.0", firma)  # firma vecchia spacciata per nuova
    setup.write_bytes(b"MZ" + bytes(4999) + b"!")  # un byte cambiato
    with pytest.raises(aggiornamenti.ErroreAggiornamento, match="diverso"):
        aggiornamenti.verifica_installatore(setup, "0.24.0", firma)
    altra = aggiornamenti.firma_installatore(setup, "0.24.0", bytes(32))  # firmato da qualcun altro
    with pytest.raises(aggiornamenti.ErroreAggiornamento, match="non valida"):
        aggiornamenti.verifica_installatore(setup, "0.24.0", altra)
    with pytest.raises(aggiornamenti.ErroreAggiornamento, match="illeggibile"):
        aggiornamenti.verifica_installatore(setup, "0.24.0", "non è una firma")


def test_scaricamento_verificato(tmp_path, monkeypatch):
    monkeypatch.setenv("SICURCANTIERE_CHIAVE_AGGIORNAMENTI", _pubblica())
    contenuto = b"MZ" + bytes(range(256)) * 40
    originale = tmp_path / "originale.exe"
    originale.write_bytes(contenuto)
    firma = aggiornamenti.firma_installatore(originale, "9.0.0", PRIVATA).encode()
    v = aggiornamenti.Versione("9.0.0", "https://x/setup.exe", "", "", url_firma="https://x/setup.exe.firma")
    file = aggiornamenti.scarica_verificato(v, tmp_path / "a.exe",
                                            apri=_apri_file({v.url_installatore: contenuto, v.url_firma: firma}))
    assert file.read_bytes() == contenuto
    # installatore sostituito sul server: non viene lasciato sul disco
    with pytest.raises(aggiornamenti.ErroreAggiornamento):
        aggiornamenti.scarica_verificato(v, tmp_path / "b.exe", apri=_apri_file(
            {v.url_installatore: contenuto + b"virus", v.url_firma: firma}))
    assert not (tmp_path / "b.exe").exists()
    # versione senza firma: rifiutata
    senza = aggiornamenti.Versione("9.0.0", "https://x/setup.exe", "", "")
    with pytest.raises(aggiornamenti.ErroreAggiornamento, match="non è firmata"):
        aggiornamenti.scarica_verificato(senza, tmp_path / "c.exe", apri=_apri_file({}))


def test_senza_chiave_scaricamento_come_prima(tmp_path, monkeypatch):
    monkeypatch.delenv("SICURCANTIERE_CHIAVE_AGGIORNAMENTI", raising=False)
    monkeypatch.setattr(aggiornamenti, "CHIAVE_AGGIORNAMENTI", "")
    v = aggiornamenti.Versione("9.0.0", "https://x/setup.exe", "", "")
    assert aggiornamenti.scarica_verificato(v, tmp_path / "s.exe", apri=_apri_file(
        {v.url_installatore: b"MZ"})).read_bytes() == b"MZ"


def test_firma_nella_versione_pubblicata():
    v = aggiornamenti.ultima_versione(apri=apri_con({
        "tag_name": "v9.0.0", "assets": [
            {"name": "SicurCantiere-setup.exe", "browser_download_url": "https://x/setup.exe"},
            {"name": "SicurCantiere-setup.exe.firma", "browser_download_url": "https://x/setup.exe.firma"}]}))
    assert v.url_firma == "https://x/setup.exe.firma"


def test_script_di_firma_della_pubblicazione(tmp_path, monkeypatch):
    import base64
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location(
        "firma_aggiornamento", Path(__file__).resolve().parent.parent / "scripts" / "firma_aggiornamento.py")
    script = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(script)
    setup = tmp_path / f"SicurCantiere-{__version__}-setup.exe"
    setup.write_bytes(b"MZ installatore")
    # programma senza chiave e nessun segreto: si pubblica come prima
    monkeypatch.delenv("SICURCANTIERE_FIRMA_AGGIORNAMENTI", raising=False)
    monkeypatch.delenv("SICURCANTIERE_CHIAVE_AGGIORNAMENTI", raising=False)
    monkeypatch.setattr(aggiornamenti, "CHIAVE_AGGIORNAMENTI", "")
    assert script.main([str(setup)]) == 0 and not (tmp_path / "SicurCantiere-setup.exe.firma").exists()
    # programma con la chiave ma segreto mancante: pubblicazione bloccata
    monkeypatch.setattr(aggiornamenti, "CHIAVE_AGGIORNAMENTI", _pubblica())
    assert script.main([str(setup)]) == 1
    # segreto giusto: firma creata e verificata
    monkeypatch.setenv("SICURCANTIERE_FIRMA_AGGIORNAMENTI", base64.b64encode(PRIVATA).decode())
    assert script.main([str(setup)]) == 0
    firma = (tmp_path / "SicurCantiere-setup.exe.firma").read_text()
    aggiornamenti.verifica_installatore(setup, __version__, firma)
    # segreto sbagliato: la verifica con la chiave del programma blocca la pubblicazione
    monkeypatch.setenv("SICURCANTIERE_FIRMA_AGGIORNAMENTI", base64.b64encode(bytes(32)).decode())
    with pytest.raises(aggiornamenti.ErroreAggiornamento):
        script.main([str(setup)])


def test_comando_chiave_aggiornamenti(tmp_path, monkeypatch, capsys):
    pytest.importorskip("flask")
    monkeypatch.setenv("SICURCANTIERE_LICENZE_DATI", str(tmp_path / "dati"))
    from licenze.__main__ import main

    assert main(["chiave-aggiornamenti"]) == 0
    prima = capsys.readouterr().out
    assert "SICURCANTIERE_FIRMA_AGGIORNAMENTI" in prima and "creata" in prima
    assert main(["chiave-aggiornamenti"]) == 0  # seconda volta: stessa chiave, non rigenerata
    seconda = capsys.readouterr().out
    assert "esiste già" in seconda

    def chiavi(testo):  # le due righe con le chiavi (segreta e pubblica)
        return [r.strip() for r in testo.splitlines() if r.startswith("   ") and len(r.strip()) == 44]

    assert len(chiavi(prima)) == 2 and chiavi(prima) == chiavi(seconda)
