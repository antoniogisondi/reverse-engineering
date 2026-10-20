import pytest


@pytest.fixture(autouse=True)
def archivio_temporaneo(tmp_path, monkeypatch):
    # L'archivio delle anagrafiche dei test non deve finire nella cartella dell'utente.
    monkeypatch.setenv("SICURCANTIERE_ARCHIVIO", str(tmp_path / "archivio.db"))
