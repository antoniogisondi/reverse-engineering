import pytest


@pytest.fixture(autouse=True)
def archivio_temporaneo(tmp_path, monkeypatch):
    # L'archivio delle anagrafiche dei test non deve finire nella cartella dell'utente.
    monkeypatch.setenv("SICURCANTIERE_ARCHIVIO", str(tmp_path / "archivio.db"))


@pytest.fixture(autouse=True)
def copie_temporanee(tmp_path, monkeypatch):
    # Le copie di sicurezza dei test non devono finire nella cartella dell'utente.
    monkeypatch.setenv("SICURCANTIERE_COPIE", str(tmp_path / "copie"))


@pytest.fixture(autouse=True)
def licenze_non_attive(monkeypatch):
    # I test del programma non dipendono dalla chiave delle licenze; quelli delle licenze usano
    # una chiave di prova con SICURCANTIERE_CHIAVE_LICENZE.
    from sicurcantiere import licenza

    monkeypatch.setattr(licenza, "CHIAVE_PUBBLICA", "")
    monkeypatch.setattr(licenza, "_attivo", None)
