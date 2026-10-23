"""Licenza legata al PC nei programmi: attivazione, PC in più, attesa senza internet, sola lettura.

Il programma parla con il server vero delle attivazioni (licenze.api) attraverso il client di prova di
Flask; il gestionale emette le licenze nello stesso database.
"""

import os
from datetime import date, timedelta

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("flask")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtCore = pytest.importorskip("PySide6.QtCore")

from sicur_license import custodia, impronta  # noqa: E402
from sicur_license.cliente import ErroreRete, Licenze  # noqa: E402
from sicurcantiere import licenza, licenza_pc  # noqa: E402
from sicurcantiere.db import Progetto  # noqa: E402
from sicurcantiere.repository import Repository  # noqa: E402

QUESTO_PC = {"sistema": "guid-ufficio", "hardware": "scheda-ufficio", "nome": "UFFICIO"}


@pytest.fixture(scope="module")
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture(autouse=True)
def senza_dialoghi(monkeypatch):
    mb = QtWidgets.QMessageBox
    for nome in ("warning", "critical", "information"):
        monkeypatch.setattr(mb, nome, lambda *a, **k: mb.StandardButton.Ok)
    monkeypatch.setattr(mb, "question", lambda *a, **k: mb.StandardButton.Yes)
    monkeypatch.setattr(mb, "exec", lambda self: mb.StandardButton.Save)


@pytest.fixture
def ufficio(tmp_path, monkeypatch, app):
    """Server delle attivazioni con una licenza PSC per 1 PC, e il programma collegato a quel server."""
    monkeypatch.setenv("SICURCANTIERE_LICENZE_DATI", str(tmp_path / "dati"))
    from licenze import api, archivio
    from licenze.app import emetti
    from sicurcantiere.ui import licenza as licenza_ui

    archivio.genera_chiave()
    monkeypatch.setenv("SICURCANTIERE_CHIAVE_LICENZE", archivio.chiave_pubblica())
    impostazioni = QtCore.QSettings(str(tmp_path / "comune.ini"), QtCore.QSettings.Format.IniFormat)
    monkeypatch.setattr(licenza_ui, "impostazioni_comuni", lambda: impostazioni)
    monkeypatch.setattr(impronta, "componenti_locali", lambda: dict(QUESTO_PC))
    monkeypatch.setattr(impronta, "nome_pc", lambda: "UFFICIO")
    pubblico = api.crea_api().test_client()

    class Ufficio:
        rete = True
        conn = archivio.connessione()

        def trasporto(self, percorso, dati):
            if not self.rete:
                raise ErroreRete("senza internet")
            r = pubblico.post("/api/licenze/" + percorso, json=dati, environ_base={"REMOTE_ADDR": "203.0.113.5"})
            return r.status_code, r.get_json()

        def licenza(self, postazioni=1, piano="psc"):
            cliente = self.conn.execute("INSERT INTO clienti (nome) VALUES ('Studio Rossi')").lastrowid
            id_ = emetti(self.conn, cliente, piano, date(2030, 1, 1), postazioni, 0)
            self.conn.commit()
            return self.conn.execute("SELECT codice FROM licenze WHERE id = ?", (id_,)).fetchone()[0], id_

        def altro_pc(self, codice, nome="PORTATILE"):
            """Un altro PC del cliente che occupa un posto."""
            vecchia = os.environ["SICUR_LICENSE_CARTELLA"]
            os.environ["SICUR_LICENSE_CARTELLA"] = str(tmp_path / nome)
            try:
                Licenze("psc", archivio.radice_pubblica(), self.trasporto,
                        componenti={"sistema": f"g-{nome}", "hardware": f"h-{nome}", "nome": nome},
                        nome=nome).attiva(codice)
            finally:
                os.environ["SICUR_LICENSE_CARTELLA"] = vecchia

        def pc_attivi(self):
            return archivio.connessione().execute(
                "SELECT nome FROM pc_licenza WHERE stato = 'attivo' ORDER BY id").fetchall()

        def salva_codice(self, codice):
            impostazioni.setValue("licenza/codice", codice)

    u = Ufficio()
    monkeypatch.setattr(licenza_pc, "trasporto", u.trasporto)
    return u


def _stato():
    from sicurcantiere.ui import licenza as licenza_ui

    return licenza_ui.stato_corrente("psc")


def test_attivazione_dal_dialogo(ufficio):
    from sicurcantiere.ui.licenza import DialogoLicenza

    codice, _ = ufficio.licenza()
    dialogo = DialogoLicenza("psc", "SicurCantiere PSC")
    dialogo.codice.setText(codice)
    dialogo._attiva()
    assert _stato().tipo == licenza.LICENZA and _stato().utilizzabile
    assert [r["nome"] for r in ufficio.pc_attivi()] == ["UFFICIO"]  # il PC compare nel gestionale
    dialogo._mostra()
    assert "Attivata su questo PC" in dialogo.dettagli.text() and dialogo.p_disattiva.isVisibleTo(dialogo)


def test_pc_in_piu_libera_un_posto_e_attiva(ufficio, monkeypatch):
    from sicurcantiere.ui import licenza as licenza_ui

    codice, _ = ufficio.licenza(postazioni=1)
    ufficio.altro_pc(codice, "PORTATILE")  # l'unico posto è occupato
    mostrati = []

    def scegli_di_liberare(dialogo):
        mostrati.append((dialogo.messaggio.text(), [p["nome"] for p in dialogo.dati["pc"]]))
        dialogo._disattiva(dialogo.dati["pc"][0])  # «Disattiva» sul vecchio portatile

    monkeypatch.setattr(licenza_ui.DialogoPC, "exec", scegli_di_liberare)
    dialogo = licenza_ui.DialogoLicenza("psc", "SicurCantiere PSC")
    dialogo.codice.setText(codice)
    dialogo._attiva()
    assert "già attiva su 1 PC su 1" in mostrati[0][0] and mostrati[0][1] == ["PORTATILE"]
    assert _stato().utilizzabile
    assert [r["nome"] for r in ufficio.pc_attivi()] == ["UFFICIO"]


def test_pc_in_piu_senza_liberare_resta_in_sola_lettura(ufficio, monkeypatch):
    from sicurcantiere.ui import licenza as licenza_ui

    codice, _ = ufficio.licenza(postazioni=1)
    ufficio.altro_pc(codice)
    monkeypatch.setattr(licenza_ui.DialogoPC, "exec", lambda self: None)
    dialogo = licenza_ui.DialogoLicenza("psc", "SicurCantiere PSC")
    dialogo.codice.setText(codice)
    dialogo._attiva()
    assert "1 PC su 1" in dialogo.errore.text()
    stato = _stato()
    assert stato.tipo == licenza.SOLA_LETTURA and "Aiuto > Licenza" in stato.cosa_fare


def test_chi_ha_gia_il_codice_si_attiva_da_solo(ufficio):
    codice, _ = ufficio.licenza()
    ufficio.salva_codice(codice)  # cliente della versione precedente: codice inserito, PC non attivato
    assert licenza_pc.verifica_in_sottofondo("psc", codice) == ""
    assert _stato().utilizzabile and [r["nome"] for r in ufficio.pc_attivi()] == ["UFFICIO"]
    assert licenza_pc.verifica_in_sottofondo("psc", codice) == ""  # avvii successivi: rinnovo del certificato


def test_senza_internet_attesa_poi_sola_lettura(ufficio):
    from sicurcantiere.ui import licenza as licenza_ui

    codice, _ = ufficio.licenza()
    ufficio.salva_codice(codice)
    ufficio.rete = False
    assert licenza_pc.verifica_in_sottofondo("psc", codice) == "rete"
    stato = _stato()
    assert stato.tipo == licenza.LICENZA and stato.utilizzabile and "entro 14 giorni" in stato.avvisi[0]
    assert licenza_ui.testo_barra(stato) == "Licenza: collegati a internet per la verifica"
    memoria = custodia.leggi_memoria()
    memoria["attesa"]["dal"] = (date.today() - timedelta(days=20)).isoformat()
    custodia.salva_memoria(memoria)
    stato = _stato()
    assert stato.tipo == licenza.SOLA_LETTURA and "non è ancora attivata" in stato.motivo
    ufficio.rete = True
    assert licenza_pc.verifica_in_sottofondo("psc", codice) == ""  # tornata la connessione: si attiva
    assert _stato().utilizzabile


def test_rifiuto_del_server_sola_lettura_subito(ufficio):
    codice, _ = ufficio.licenza(postazioni=1)
    ufficio.altro_pc(codice)
    ufficio.salva_codice(codice)
    assert "1 PC su 1" in licenza_pc.verifica_in_sottofondo("psc", codice)
    stato = _stato()
    assert stato.tipo == licenza.SOLA_LETTURA and "1 PC su 1" in stato.motivo
    # agli avvii successivi non si riprova da solo (ogni tentativo finirebbe nel registro dei rifiuti)
    assert licenza_pc.verifica_in_sottofondo("psc", codice) == ""


def test_disattiva_questo_pc(ufficio):
    from sicurcantiere.ui.licenza import DialogoLicenza

    codice, _ = ufficio.licenza()
    dialogo = DialogoLicenza("psc", "SicurCantiere PSC")
    dialogo.codice.setText(codice)
    dialogo._attiva()
    dialogo.disattiva_questo()
    assert ufficio.pc_attivi() == []  # posto libero sul server
    assert _stato().tipo == licenza.SOLA_LETTURA  # niente attesa: subito sola lettura
    assert licenza_pc.verifica_in_sottofondo("psc", codice) == ""  # e non si riattiva da solo
    assert ufficio.pc_attivi() == []
    dialogo._attiva()  # riattivazione a mano
    assert _stato().utilizzabile


def test_pc_liberato_da_un_altro(ufficio):
    codice, _ = ufficio.licenza(postazioni=1)
    ufficio.salva_codice(codice)
    licenza_pc.attiva("psc", codice)
    from licenze import archivio, attivazioni

    conn = archivio.connessione()
    radice = conn.execute("SELECT radice_id FROM pc_licenza").fetchone()[0]
    codice_pc = conn.execute("SELECT codice_pc FROM pc_licenza").fetchone()[0]
    attivazioni.disattiva_da_gestionale(conn, radice, codice_pc, "antonio")
    conn.commit()
    assert licenza_pc.verifica_in_sottofondo("psc", codice) != ""
    assert _stato().tipo == licenza.SOLA_LETTURA


def test_attivazione_senza_internet(ufficio, tmp_path):
    from licenze import archivio, attivazioni
    from sicurcantiere.ui.licenza import DialogoLicenza

    codice, _ = ufficio.licenza()
    ufficio.rete = False
    dialogo = DialogoLicenza("psc", "SicurCantiere PSC")
    dialogo.codice.setText(codice)
    richiesta = dialogo.salva_richiesta(str(tmp_path / "richiesta.screq"))
    assert "guid-ufficio" not in richiesta.read_text()  # solo impronte
    conn = archivio.connessione()
    (tmp_path / "attivazione.sclic").write_text(attivazioni.attiva_offline(conn, richiesta.read_text()))
    conn.commit()
    assert dialogo.carica_attivazione(str(tmp_path / "attivazione.sclic"))
    assert _stato().utilizzabile
    assert not dialogo.carica_attivazione(str(richiesta))  # file sbagliato: messaggio, nessun cambio


def test_sola_lettura_nella_finestra(ufficio, tmp_path):
    from sicurcantiere.ui.edizioni import PSC
    from sicurcantiere.ui.finestra import FinestraPrincipale

    codice, id_ = ufficio.licenza()
    ufficio.salva_codice(codice)
    licenza_pc.attiva("psc", codice)
    file = tmp_path / "scuola.scs"
    p = Progetto(file, crea=True)
    Repository(p).aggiorna_cantiere(nome="Scuola media")
    p.chiudi()
    originale = file.read_bytes()

    ufficio.conn.execute("UPDATE licenze SET stato = 'annullata' WHERE id = ?", (id_,))
    ufficio.conn.commit()
    licenza_pc.verifica_in_sottofondo("psc", codice)  # licenza annullata dal gestionale: certificato «revocato»
    assert _stato().tipo == licenza.SOLA_LETTURA
    f = FinestraPrincipale(PSC)
    f.apri_file(file)
    assert f.progetto is not None and f.sola_lettura and "(sola lettura)" in f.windowTitle()
    assert f.avviso_lettura.isVisibleTo(f) and "Sola lettura" in f.testo_lettura.text()
    assert "disattivata" in f.testo_lettura.text()
    assert not f.azione_salva.isEnabled() and not f.azione_psc.isEnabled()
    campo = f.pagine[0].campi["nome"]
    assert campo.isReadOnly() and campo.text() == "Scuola media"  # si legge, non si modifica
    # anche se qualcosa scrivesse nel cantiere, il file del cliente non cambia
    f.pagine[0].repo.aggiorna_cantiere(nome="Modificato")
    for i in range(len(f.pagine)):  # tutte le pagine si aprono senza errori
        f.navigazione.setCurrentRow(i)
    assert not f.modifiche_non_salvate()
    f.close()
    assert file.read_bytes() == originale

    # licenza riattivata: alla verifica il cantiere torna modificabile
    ufficio.conn.execute("UPDATE licenze SET stato = 'attiva' WHERE id = ?", (id_,))
    ufficio.conn.commit()
    f = FinestraPrincipale(PSC)
    f.apri_file(file)
    assert f.sola_lettura
    licenza_pc.verifica_in_sottofondo("psc", codice)
    f._licenza_cambiata()
    assert f.progetto is not None and not f.sola_lettura and not f.pagine[0].campi["nome"].isReadOnly()
    f.close()


def test_documenti_composti_consultabili_in_sola_lettura(ufficio, tmp_path):
    from sicurcantiere.ui import sola_lettura
    from sicurcantiere.ui.composizioni import PannelloComposizioni

    p = Progetto(tmp_path / "c.scs", crea=True)
    pannello = PannelloComposizioni(Repository(p), lambda: "PSC", "PSC")
    sola_lettura.imposta(True)
    try:
        sola_lettura.applica(pannello)
        pannello._aggiorna_pulsanti()
        assert pannello.p_apri.property("solaLettura") and pannello.p_anteprima.property("solaLettura")
        assert not pannello.p_componi.isEnabled() and not pannello.p_emetti.isEnabled()
    finally:
        sola_lettura.imposta(False)
        p.chiudi()


def test_messaggi_senza_server(ufficio):
    # senza indirizzo del server le attivazioni non si usano: il codice vale come prima
    from sicurcantiere import ai

    codice, _ = ufficio.licenza()
    ufficio.salva_codice(codice)
    licenza_pc.trasporto = None
    os.environ.pop("SICUR_LICENSE_SERVER", None)
    vecchio = ai.SERVER_AI
    ai.SERVER_AI = ""
    try:
        assert not licenza_pc.attive() and _stato().utilizzabile
    finally:
        ai.SERVER_AI = vecchio
