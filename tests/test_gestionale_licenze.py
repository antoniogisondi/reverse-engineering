import re
from datetime import date, timedelta

import pytest

pytest.importorskip("flask")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SICURCANTIERE_LICENZE_DATI", str(tmp_path / "dati"))
    from licenze import archivio
    from licenze.app import crea_app, crea_utente

    pubblica = archivio.genera_chiave()
    monkeypatch.setenv("SICURCANTIERE_CHIAVE_LICENZE", pubblica)
    crea_utente("antonio", "una password lunga")
    app = crea_app()
    app.config["TESTING"] = True
    return app.test_client()


def _token(client):
    with client.session_transaction() as s:
        return s.get("token") or ""


def _accedi(client, password="una password lunga"):
    client.get("/accesso")
    return client.post("/accesso", data={"nome": "antonio", "password": password, "token": _token(client)})


def test_accesso_obbligatorio_e_token(client):
    assert client.get("/").status_code == 302  # senza accesso si va alla pagina di login
    assert "non corretti" in _accedi(client, "sbagliata").get_data(as_text=True)
    assert _accedi(client).status_code == 302
    assert client.get("/").status_code == 200
    # un modulo senza token (richiesta da un altro sito) viene rifiutato
    assert client.post("/clienti/nuovo", data={"nome": "X"}).status_code == 400


def test_cliente_licenza_rinnovo_pagamento(client):
    from licenze import archivio
    from sicurcantiere import licenza

    _accedi(client)
    t = _token(client)
    r = client.post("/clienti/nuovo", data={"nome": "Studio Rossi", "email": "rossi@example.com", "token": t})
    cliente = int(r.headers["Location"].rsplit("/", 1)[1])
    scadenza = (date.today() + timedelta(days=365)).isoformat()
    r = client.post(f"/clienti/{cliente}/licenza", data={"piano": "completo", "scadenza": scadenza,
                                                         "postazioni": "2", "prezzo": "249", "token": t})
    pagina = client.get(r.headers["Location"]).get_data(as_text=True)
    codice = re.search(r"(SC1-[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)", pagina).group(1)
    l = licenza.leggi(codice)  # il programma riconosce la licenza firmata dal gestionale
    assert l.cliente == "Studio Rossi" and l.piano == "completo" and l.postazioni == 2
    assert l.scadenza.isoformat() == scadenza and l.id.startswith(f"SC-{date.today().year}-")
    assert "Aiuto > Licenza" in pagina  # testo pronto per l'email

    id_licenza = int(r.headers["Location"].rsplit("/", 1)[1])
    r = client.post(f"/licenze/{id_licenza}/rinnova", data={"prezzo": "249", "token": t})
    rinnovo = client.get(r.headers["Location"]).get_data(as_text=True)
    nuovo = licenza.leggi(re.search(r"(SC1-[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+)", rinnovo).group(1))
    assert nuovo.scadenza == l.scadenza + timedelta(days=365)
    conn = archivio.connessione()
    assert conn.execute("SELECT stato FROM licenze WHERE id = ?", (id_licenza,)).fetchone()[0] == "rinnovata"

    client.post(f"/clienti/{cliente}/pagamento", data={"importo": "249,00", "metodo": "Bonifico",
                                                       "fattura": "12/2026", "licenza_id": str(id_licenza), "token": t})
    scheda = client.get(f"/clienti/{cliente}").get_data(as_text=True)
    assert "249,00 €" in scheda and "12/2026" in scheda
    assert "Studio Rossi" in client.get("/clienti?cerca=rossi").get_data(as_text=True)
    csv = client.get("/esporta.csv").get_data(as_text=True)
    assert "Studio Rossi" in csv and csv.count("\n") == 3
    assert archivio.chiave_pubblica() in client.get("/impostazioni").get_data(as_text=True)
