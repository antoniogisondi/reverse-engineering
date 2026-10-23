"""Gestionale: PC attivati delle licenze, interventi dell'assistenza e segnalazioni.

I PC dei clienti passano dal server vero delle attivazioni (licenze.api) con il modulo dei programmi;
il gestionale li mostra e li gestisce.
"""

import io
import os
import re
from datetime import date

import pytest

pytest.importorskip("flask")

from sicur_license.cliente import PC_LIBERATO, POSTI_ESAURITI, TROPPI_TRASFERIMENTI, ErroreServer, Licenze  # noqa
from sicur_license.stato import ATTIVA, REVOCATA_  # noqa: E402


@pytest.fixture
def ufficio(tmp_path, monkeypatch):
    monkeypatch.setenv("SICURCANTIERE_LICENZE_DATI", str(tmp_path / "dati"))
    from licenze import api, archivio
    from licenze.app import crea_app, crea_utente, emetti

    archivio.genera_chiave()
    monkeypatch.setenv("SICURCANTIERE_CHIAVE_LICENZE", archivio.chiave_pubblica())
    crea_utente("antonio", "una password lunga")
    gestionale = crea_app()
    gestionale.config["TESTING"] = True
    browser = gestionale.test_client()
    browser.environ_base["wsgi.url_scheme"] = "https"
    browser.get("/accesso")
    with browser.session_transaction() as s:
        token = s["token"]
    browser.post("/accesso", data={"nome": "antonio", "password": "una password lunga", "codice": "",
                                   "token": token})
    with browser.session_transaction() as s:
        token = s["token"]
    pubblico = api.crea_api().test_client()
    conn = archivio.connessione()
    cliente = conn.execute("INSERT INTO clienti (nome, email) VALUES ('Studio Rossi', 'r@example.com')").lastrowid
    conn.commit()

    class Ufficio:
        def __init__(self):
            self.browser, self.token, self.cliente, self.conn = browser, token, cliente, conn

        def licenza(self, postazioni=2, piano="completo"):
            id_ = emetti(self.conn, cliente, piano, date(2030, 1, 1), postazioni, 0)
            return self.conn.execute("SELECT codice FROM licenze WHERE id = ?", (id_,)).fetchone()[0], id_

        def pc(self, nome, ip="203.0.113.10", cartella=None, **componenti):
            valori = {"sistema": f"guid-{nome}", "hardware": f"scheda-{nome}", "nome": nome, **componenti}

            def invia(percorso, dati):
                r = pubblico.post("/api/licenze/" + percorso, json=dati, environ_base={"REMOTE_ADDR": ip})
                return r.status_code, r.get_json()

            cartella = tmp_path / "pc" / (cartella or f"{nome}-{ip}")
            licenze = Licenze("psc", archivio.radice_pubblica(), invia, versione="0.23.0", componenti=valori, nome=nome)

            class PC:
                percorso = cartella

                def __getattr__(self, attributo):
                    os.environ["SICUR_LICENSE_CARTELLA"] = str(cartella)
                    return getattr(licenze, attributo)

            return PC()

        def pagina(self, percorso):
            r = self.browser.get(percorso)
            assert r.status_code == 200, percorso
            return r.get_data(as_text=True)

        def invia(self, percorso, **dati):
            return self.browser.post(percorso, data={"token": self.token, **dati})

    return Ufficio()


def _codici_pc(pagina):
    return re.findall(r"PC-[0-9A-F]{12}", pagina)


def test_pagina_della_licenza_con_i_pc(ufficio):
    codice, id_ = ufficio.licenza(postazioni=2)
    pagina = ufficio.pagina(f"/licenze/{id_}")
    assert "0 su 2" in pagina and "Nessun PC attivato" in pagina
    ufficio.pc("UFFICIO-1").attiva(codice)
    ufficio.pc("PORTATILE").attiva(codice)
    pagina = ufficio.pagina(f"/licenze/{id_}")
    assert "2 su 2" in pagina and "UFFICIO-1" in pagina and "PORTATILE" in pagina
    assert "PC attivato" in pagina  # registro
    assert "2 su 2" in ufficio.pagina(f"/clienti/{ufficio.cliente}")
    assert "PC attivati" in ufficio.pagina("/")


def test_pc_in_piu_segnalato_nel_cruscotto(ufficio):
    codice, id_ = ufficio.licenza(postazioni=1)
    ufficio.pc("A").attiva(codice)
    for _ in range(3):
        with pytest.raises(ErroreServer) as rifiuto:
            ufficio.pc("B").attiva(codice)
        assert rifiuto.value.codice == POSTI_ESAURITI
    cruscotto = ufficio.pagina("/")
    assert "Da guardare" in cruscotto and "servono posti in più" in cruscotto
    assert "3 tentativi rifiutati" in ufficio.pagina(f"/licenze/{id_}")
    attivazioni = ufficio.pagina("/attivazioni")
    assert "Rifiutato: posti esauriti" in attivazioni and "Studio Rossi" in attivazioni


def test_disattiva_un_pc_dal_gestionale(ufficio):
    codice, id_ = ufficio.licenza(postazioni=1)
    a = ufficio.pc("A")
    a.attiva(codice)
    codice_pc = _codici_pc(ufficio.pagina(f"/licenze/{id_}"))[0]
    r = ufficio.invia(f"/licenze/{id_}/pc/{codice_pc}/disattiva", motivo="PC rubato")
    assert r.status_code == 302
    pagina = ufficio.pagina(f"/licenze/{id_}")
    assert "0 su 1" in pagina and "PC rubato" in pagina and "PC disattivato dal gestionale" in pagina
    with pytest.raises(ErroreServer) as liberato:
        a.convalida()
    assert liberato.value.codice == PC_LIBERATO
    ufficio.pc("B").attiva(codice)  # il posto è libero


def test_posti_in_piu(ufficio):
    codice, id_ = ufficio.licenza(postazioni=1)
    ufficio.pc("A").attiva(codice)
    with pytest.raises(ErroreServer):
        ufficio.pc("B").attiva(codice)
    ufficio.invia(f"/licenze/{id_}/posti", posti_extra="1")
    ufficio.pc("B").attiva(codice)
    pagina = ufficio.pagina(f"/licenze/{id_}")
    assert "2 su 2" in pagina and "più 1 posto aggiunto" in pagina
    with pytest.raises(ErroreServer):
        ufficio.pc("C").attiva(codice)  # il PC in più rispetto ai 2 posti


def test_sblocca_trasferimenti(ufficio):
    codice, id_ = ufficio.licenza(postazioni=1)
    a, b = ufficio.pc("A"), ufficio.pc("B")
    a.attiva(codice)
    a.disattiva()
    b.attiva(codice)
    b.disattiva()
    a.attiva(codice)
    a.disattiva()
    with pytest.raises(ErroreServer) as rifiuto:
        b.attiva(codice)
    assert rifiuto.value.codice == TROPPI_TRASFERIMENTI
    ufficio.invia(f"/licenze/{id_}/trasferimenti")
    b.attiva(codice)
    assert b.esito().tipo == ATTIVA
    assert "Trasferimenti sbloccati" in ufficio.pagina(f"/licenze/{id_}")


def test_attivazione_offline_dal_gestionale(ufficio):
    codice, id_ = ufficio.licenza(postazioni=1)
    cantiere = ufficio.pc("CANTIERE")
    richiesta = cantiere.richiesta_offline(codice)
    r = ufficio.browser.post(f"/licenze/{id_}/offline", content_type="multipart/form-data",
                             data={"token": ufficio.token, "richiesta": (io.BytesIO(richiesta.encode()), "rich.json")})
    assert r.status_code == 200 and "attivazione-CANTIERE.sclic" in r.headers["Content-Disposition"]
    assert cantiere.importa_offline(r.get_data(as_text=True)).offline
    assert "offline" in ufficio.pagina(f"/licenze/{id_}")
    # richiesta di un'altra licenza caricata nella pagina sbagliata
    altro_codice, altro_id = ufficio.licenza(postazioni=1)
    r = ufficio.invia(f"/licenze/{id_}/offline", testo=ufficio.pc("ALTRO").richiesta_offline(altro_codice))
    assert r.status_code == 302
    assert "altra licenza" in ufficio.pagina(f"/licenze/{id_}")
    # posti esauriti: messaggio, nessun file
    ufficio.invia(f"/licenze/{id_}/offline", testo=ufficio.pc("TERZO").richiesta_offline(codice))
    assert "Attivazione non creata" in ufficio.pagina(f"/licenze/{id_}")
    ufficio.invia(f"/licenze/{id_}/offline", testo="")
    assert "Scegli il file" in ufficio.pagina(f"/licenze/{id_}")


def test_annulla_e_riattiva(ufficio):
    codice, id_ = ufficio.licenza()
    a = ufficio.pc("A")
    a.attiva(codice)
    ufficio.invia(f"/licenze/{id_}/annulla")
    a.convalida()
    assert a.esito().tipo == REVOCATA_
    pagina = ufficio.pagina(f"/licenze/{id_}")
    assert "Riattiva la licenza" in pagina and "Licenza annullata" in pagina
    ufficio.invia(f"/licenze/{id_}/riattiva")
    a.convalida()
    assert a.esito().tipo == ATTIVA
    assert "Licenza riattivata" in ufficio.pagina(f"/licenze/{id_}")


def test_pc_sospetto_e_ignora(ufficio):
    codice, id_ = ufficio.licenza()
    a = ufficio.pc("A", ip="203.0.113.10")
    a.attiva(codice)
    import shutil

    clone = ufficio.pc("A", ip="192.0.2.99", cartella="clone")  # stessa macchina copiata, altra rete
    shutil.copytree(a.percorso, clone.percorso)
    clone.convalida()
    assert "possibile copia della macchina" in ufficio.pagina(f"/licenze/{id_}")
    assert "PC sospetto" in ufficio.pagina("/")
    codice_pc = _codici_pc(ufficio.pagina(f"/licenze/{id_}"))[0]
    ufficio.invia(f"/licenze/{id_}/pc/{codice_pc}/ignora")
    assert "possibile copia della macchina" not in ufficio.pagina(f"/licenze/{id_}")


def test_azioni_protette(ufficio):
    codice, id_ = ufficio.licenza()
    for percorso in (f"/licenze/{id_}/posti", f"/licenze/{id_}/trasferimenti", f"/licenze/{id_}/offline",
                     f"/licenze/{id_}/riattiva", f"/licenze/{id_}/pc/PC-000000000000/disattiva"):
        assert ufficio.browser.post(percorso, data={"posti_extra": "5"}).status_code == 400  # senza token
    for tipo in ("rifiuti", "attivazioni", "sicurezza", "gestionale"):
        ufficio.pagina(f"/attivazioni?tipo={tipo}&giorni=90")
    assert ufficio.invia("/licenze/9999/posti", posti_extra="1").status_code == 404
