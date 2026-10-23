"""Avvio del programma compilato: l'edizione dipende dal nome dell'eseguibile."""

import pytest

pytest.importorskip("PySide6")

from sicurcantiere.app import edizione_da_eseguibile  # noqa: E402


@pytest.mark.parametrize("percorso, edizione", [
    (r"C:\Program Files\SicurCantiere\SicurCantiere PSC.exe", "psc"),
    (r"C:\Program Files\SicurCantiere\SicurCantiere POS.exe", "pos"),
    (r"C:\Program Files\SicurCantiere\SicurCantiere PiMUS.exe", "pimus"),
    ("/opt/sicurcantiere/SicurCantiere POS", "pos"),
    ("scripts/sicurcantiere.py", None),  # da sorgente: decide l'argomento (psc, pos, pimus)
    (r"C:\Python\python.exe", None),
])
def test_edizione_dal_nome_dell_eseguibile(percorso, edizione):
    assert edizione_da_eseguibile(percorso.replace("\\", "/")) == edizione
