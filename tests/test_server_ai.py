import json
import threading
from datetime import date, timedelta

import pytest

pytest.importorskip("flask")

from sicurcantiere import ai, licenza  # noqa: E402


@pytest.fixture
def server(tmp_path, monkeypatch):
    """Gestionale con chiave di firma, un cliente e il server ponte con un fornitore finto."""
    monkeypatch.setenv("SICURCANTIERE_LICENZE_DATI", str(tmp_path / "dati"))
    monkeypatch.setenv("SICURCANTIERE_AI_STANDARD_CHIAVE", "chiave-standard")
    monkeypatch.setenv("SICURCANTIERE_AI_AVANZATO_CHIAVE", "chiave-avanzata")
    from licenze import api, archivio
    from licenze.app import emetti

    archivio.genera_chiave()
    monkeypatch.setenv("SICURCANTIERE_CHIAVE_LICENZE", archivio.chiave_pubblica())
    conn = archivio.connessione()
    cliente = conn.execute("INSERT INTO clienti (nome) VALUES ('Studio Rossi')").lastrowid
    conn.commit()
    chiamate = []
    vera = ai.AssistenteAI.richiesta_grezza

    def finta(self, testo, schema):
        if self.fornitore == ai.INTEGRATO:  # il programma del cliente: va davvero al server
            return vera(self, testo, schema)
        chiamate.append((self.fornitore, self.api_key, self.modello))
        self.uso = (1000, 500)
        return json.dumps({"testo": "ok"})

    monkeypatch.setattr(ai.AssistenteAI, "richiesta_grezza", finta)

    def codice(piano="completo", scadenza=None, prezzo=0):
        id_ = emetti(conn, cliente, piano, scadenza, 1, prezzo)
        return conn.execute("SELECT codice FROM licenze WHERE id = ?", (id_,)).fetchone()[0], id_

    return api.crea_api().test_client(), codice, conn, cliente, chiamate


def _chiedi(client, codice, motore="standard"):
    return client.post("/api/ai/richiesta", json={"licenza": codice, "motore": motore, "testo": "Rischi?",
                                                  "schema": {"type": "object"}})


def test_richiesta_e_consumo(server):
    client, codice, conn, cliente, chiamate = server
    c, _ = codice("completo")
    r = _chiedi(client, c)
    assert r.status_code == 200 and json.loads(r.json["contenuto"]) == {"testo": "ok"}
    assert r.json["credito"]["usati_mese"] == 1500 and r.json["credito"]["quota"] == 3_000_000
    assert chiamate == [(ai.DEEPSEEK, "chiave-standard", "deepseek-v4-pro")]
    stato = client.post("/api/ai/stato", json={"licenza": c}).json
    assert stato["credito"]["residuo"] == 3_000_000 - 1500 and not stato["motori"]["avanzato"]["disponibile"]
    # Claude solo nel piano Studio, e conta 8 crediti per token
    assert _chiedi(client, c, "avanzato").status_code == 403
    studio, _ = codice("studio")
    r = _chiedi(client, studio, "avanzato")
    assert r.status_code == 200 and chiamate[-1][0] == ai.ANTHROPIC
    assert r.json["credito"]["usati_mese"] == 1500 + 1500 * 8  # stesso cliente: credito condiviso


def test_licenze_non_valide(server):
    client, codice, conn, cliente, _ = server
    assert _chiedi(client, "SC1-falso.falso").status_code == 403
    scaduta, _ = codice("pos", date.today() - timedelta(days=1))
    assert "scaduta" in _chiedi(client, scaduta).json["errore"]
    annullata, id_ = codice("pos")
    conn.execute("UPDATE licenze SET stato = 'annullata' WHERE id = ?", (id_,))
    conn.commit()
    assert _chiedi(client, annullata).status_code == 403
    assert client.post("/api/ai/richiesta", json={"licenza": "x"}).status_code == 400


def test_quota_tetto_giornaliero_e_ricariche(server, monkeypatch):
    from licenze import api

    client, codice, conn, cliente, _ = server
    c, id_ = codice("pos")
    oggi = date.today().isoformat()
    # oltre il 30% della quota oggi: si ferma fino a domani
    conn.execute("INSERT INTO consumi_ai (cliente_id, licenza_id, data, istante, motore, crediti) VALUES "
                 "(?, ?, ?, 0, 'standard', ?)", (cliente, id_, oggi, int(1_500_000 * 0.3)))
    conn.commit()
    assert "giornaliero" in _chiedi(client, c).json["errore"]
    # quota del mese esaurita (consumi dei giorni scorsi)
    conn.execute("UPDATE consumi_ai SET data = ?, crediti = 1500000", ((date.today().replace(day=1)).isoformat(),))
    conn.commit()
    if date.today().day == 1:
        pytest.skip("il primo del mese i consumi di ieri sono del mese prima")
    r = _chiedi(client, c)
    assert r.status_code == 402 and "esaurito" in r.json["errore"]
    # una ricarica rimette in moto l'assistente, e non scade
    conn.execute("INSERT INTO ricariche_ai (cliente_id, data, crediti) VALUES (?, ?, 2000000)", (cliente, oggi))
    conn.commit()
    r = _chiedi(client, c)
    assert r.status_code == 200 and r.json["credito"]["extra"] == 2_000_000 - 1500
    s = api.situazione(conn, cliente, "pos", date.today() + timedelta(days=40))  # mese nuovo: quota piena
    assert s["residuo"] == 1_500_000 + 2_000_000 - 1500
    # troppe richieste in un minuto
    monkeypatch.setattr(api, "RICHIESTE_AL_MINUTO", 1)
    assert _chiedi(client, c).status_code == 429


def test_programma_usa_il_server(server, monkeypatch):
    from werkzeug.serving import make_server

    from licenze.api import crea_api

    _, codice, _, _, _ = server
    c, _ = codice("completo")
    http = make_server("127.0.0.1", 0, crea_api())
    filo = threading.Thread(target=http.serve_forever, daemon=True)
    filo.start()
    try:
        monkeypatch.setenv("SICURCANTIERE_SERVER_AI", f"http://127.0.0.1:{http.server_port}")
        assistente = ai.AssistenteAI(fornitore=ai.INTEGRATO, api_key=c)
        assert assistente.scrivi_sezione("Area", "Cantiere") == "ok"
        assert assistente.credito["usati_mese"] == 1500 and assistente.uso == (1000, 500)
        with pytest.raises(ai.ErroreAI, match="piano Studio"):
            ai.AssistenteAI(fornitore=ai.INTEGRATO, api_key=c, modello=ai.AVANZATO).scrivi_sezione("Area", "x")
        with pytest.raises(ai.ErroreAI, match="non valido"):
            ai.AssistenteAI(fornitore=ai.INTEGRATO, api_key="SC1-a.b").scrivi_sezione("Area", "x")
    finally:
        http.shutdown()


def test_server_non_configurato(monkeypatch):
    monkeypatch.delenv("SICURCANTIERE_SERVER_AI", raising=False)
    monkeypatch.setattr(ai, "SERVER_AI", "")
    with pytest.raises(ai.ErroreAI, match="non è ancora disponibile"):
        ai.AssistenteAI(fornitore=ai.INTEGRATO, api_key="x").scrivi_sezione("Area", "x")
    assert licenza  # modulo usato dal gestionale


def test_assistente_con_il_certificato_del_pc(server, tmp_path, monkeypatch):
    """Con un PC attivato il solo codice non basta più: serve il certificato del PC (non copiato)."""
    from licenze import archivio
    from sicur_license.cliente import Licenze

    client, codice, conn, cliente, _ = server
    c, id_ = codice("completo")
    assert _chiedi(client, c).status_code == 200  # nessun PC attivato: il codice vale ancora (versioni vecchie)

    def trasporto(percorso, dati):
        r = client.post("/api/licenze/" + percorso, json=dati, environ_base={"REMOTE_ADDR": "203.0.113.9"})
        return r.status_code, r.get_json()

    monkeypatch.setenv("SICUR_LICENSE_CARTELLA", str(tmp_path / "pc"))
    pc = Licenze("psc", archivio.radice_pubblica(), trasporto,
                 componenti={"sistema": "g", "hardware": "h", "nome": "UFFICIO"}, nome="UFFICIO")
    certificato = pc.attiva(c)
    from sicur_license import custodia

    credenziali = {"certificato": custodia.leggi_certificato(), "impronte": pc.impronte(certificato.sale)}

    def chiedi(**extra):
        return client.post("/api/ai/richiesta", json={"licenza": c, "motore": "standard", "testo": "Rischi?",
                                                      "schema": {"type": "object"}, **extra})

    r = chiedi()
    assert r.status_code == 403 and "aggiorna SicurCantiere" in r.json["errore"]  # codice copiato: non basta
    assert chiedi(**credenziali).status_code == 200
    assert client.post("/api/ai/stato", json={"licenza": c, **credenziali}).status_code == 200
    copiato = {**credenziali, "impronte": ["a" * 64, "b" * 64, "c" * 64]}  # certificato su un altro PC
    assert chiedi(**copiato).status_code == 403
    assert chiedi(certificato="{}", impronte=credenziali["impronte"]).status_code == 403
    pc.disattiva()  # PC non più attivo: il certificato vecchio non vale
    assert "non è attivo" in chiedi(**credenziali).json["errore"]
