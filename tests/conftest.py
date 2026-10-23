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


@pytest.fixture(autouse=True)
def senza_server_ai(monkeypatch):
    # I test non contattano il server ponte reale: chi lo prova lo imposta da sé.
    from sicurcantiere import ai

    monkeypatch.setattr(ai, "SERVER_AI", "")
    monkeypatch.delenv("SICURCANTIERE_SERVER_AI", raising=False)


@pytest.fixture(autouse=True)
def licenza_pc_temporanea(tmp_path, monkeypatch):
    # Certificato e impronte del PC dei test in una cartella temporanea; nessun server delle licenze.
    monkeypatch.setenv("SICUR_LICENSE_CARTELLA", str(tmp_path / "licenza-pc"))
    monkeypatch.delenv("SICUR_LICENSE_SERVER", raising=False)
    from sicurcantiere import licenza_pc
    from sicurcantiere.ui import sola_lettura

    monkeypatch.setattr(licenza_pc, "trasporto", None)
    sola_lettura.imposta(False)
