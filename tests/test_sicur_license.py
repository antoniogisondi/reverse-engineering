"""Modulo comune delle licenze: impronta, certificato firmato, stato, custodia e collegamento al server."""

import json
from datetime import date, datetime, timedelta, timezone

import pytest

from sicur_license import custodia, impronta
from sicur_license.certificato import (
    ABBONAMENTO,
    PERPETUA,
    PROVA,
    REVOCATA,
    Certificato,
    ErroreCertificato,
    emetti,
    firma_servizio,
    leggi_certificato,
    pubblica_da_privata,
)
from sicur_license.cliente import POSTI_ESAURITI, ErroreRete, ErroreServer, Licenze
from sicur_license.stato import (
    AGGIORNAMENTI,
    ALTRO_PC,
    ATTIVA,
    DA_ATTIVARE,
    DA_CONVALIDARE,
    NON_INCLUSO,
    OROLOGIO,
    REVOCATA_,
    SCADUTA,
    valuta,
)

RADICE = bytes(range(32))
SERVIZIO = bytes(range(100, 132))
ORA = datetime(2026, 10, 23, 9, 0, tzinfo=timezone.utc)
PC_A = {"sistema": "guid-a", "hardware": "uuid-a|serie-a", "nome": "UFFICIO-1"}
PC_B = {"sistema": "guid-b", "hardware": "uuid-b|serie-b", "nome": "PORTATILE"}
CODICE = "SC-7KQ4-M2XD-9WPA-H3TR"


@pytest.fixture(autouse=True)
def cartella_licenza(tmp_path, monkeypatch):
    monkeypatch.setenv("SICUR_LICENSE_CARTELLA", str(tmp_path / "licenza"))


def _servizio(da=ORA - timedelta(days=30), a=ORA + timedelta(days=150)):
    return firma_servizio(RADICE, pubblica_da_privata(SERVIZIO), da, a, "servizio di prova")


def _certificato(componenti=PC_A, **modifiche) -> Certificato:
    sale = impronta.sale_della_licenza(CODICE)
    valori = dict(licenza="SC-2026-0001", cliente="Studio Rossi", prodotti=frozenset({"psc", "pos"}),
                  tipo=ABBONAMENTO, pc="pc-1", impronte=tuple(impronta.calcola(sale, componenti)), sale=sale,
                  emesso=ORA, valido_fino=ORA + timedelta(days=14), scadenza_licenza=date(2027, 10, 22),
                  aggiornamenti_fino=date(2027, 10, 22), posti=3)
    valori.update(modifiche)
    return Certificato(**valori)


def _testo(certificato=None, servizio=None) -> str:
    return emetti(certificato or _certificato(), SERVIZIO, servizio or _servizio())


def _radice_pubblica() -> bytes:
    return pubblica_da_privata(RADICE)


# --- impronta ---

def test_impronta_solo_hash_e_tolleranza_due_su_tre():
    sale = impronta.sale_della_licenza(CODICE)
    a = impronta.calcola(sale, PC_A)
    assert len(a) == 3 and all(len(h) == 64 for h in a)
    assert not any(v in "".join(a) for v in ("guid-a", "serie-a", "UFFICIO"))  # mai dati in chiaro
    # cambiato il nome del PC (o il disco): resta lo stesso PC
    assert impronta.stesso_pc(a, impronta.calcola(sale, {**PC_A, "nome": "NUOVO-NOME"}))
    # reinstallato Windows con lo stesso nome: MachineGuid nuovo, scheda madre e nome uguali
    assert impronta.stesso_pc(a, impronta.calcola(sale, {**PC_A, "sistema": "guid-nuovo"}))
    # un altro PC, o uno che ha in comune solo il nome
    assert not impronta.stesso_pc(a, impronta.calcola(sale, PC_B))
    assert not impronta.stesso_pc(a, impronta.calcola(sale, {**PC_B, "nome": "UFFICIO-1"}))
    # componenti mancanti o segnaposto del fabbricante non contano come uguali
    vuoto = impronta.calcola(sale, {"sistema": "", "hardware": "", "nome": "X"})
    assert vuoto[:2] == ["", ""] and not impronta.stesso_pc(vuoto, vuoto)
    assert impronta._pulito("To be filled by O.E.M.") == ""
    # licenze diverse: impronte diverse dello stesso PC (non collegabili)
    assert impronta.calcola(impronta.sale_della_licenza("SC-ALTRO-CODICE"), PC_A) != a


def test_sale_dei_codici_sc1_stabile_al_rinnovo():
    from sicurcantiere import licenza

    l = licenza.Licenza(id="SC-2026-0007", cliente="Rossi", piano="pos", emessa=date(2026, 1, 1))
    primo = licenza.firma(l, RADICE)
    rinnovato = licenza.firma(licenza.Licenza(**{**l.__dict__, "scadenza": date(2027, 1, 1)}), RADICE)
    assert primo != rinnovato
    assert impronta.sale_della_licenza(primo) == impronta.sale_della_licenza(rinnovato) == "id:SC-2026-0007"
    assert impronta.sale_della_licenza(" sc-7kq4-m2xd \n") == impronta.sale_della_licenza("SC-7KQ4-M2XD")


def test_componenti_locali_senza_errori():
    valori = impronta.componenti_locali()
    assert set(valori) == set(impronta.COMPONENTI) and valori["nome"]


# --- certificato ---

def test_certificato_firmato_e_verificato():
    c = _certificato()
    letto = leggi_certificato(_testo(c), _radice_pubblica())
    assert letto == c and letto.prodotti == {"psc", "pos"}


def test_certificato_alterato_o_firmato_da_altri():
    testo = json.loads(_testo())
    import base64

    dati = json.loads(base64.b64decode(testo["certificato"]["dati"]))
    dati["prodotti"] = ["psc", "pos", "pimus"]  # aggiunge un programma
    testo["certificato"]["dati"] = base64.b64encode(json.dumps(dati).encode()).decode()
    with pytest.raises(ErroreCertificato):
        leggi_certificato(json.dumps(testo), _radice_pubblica())
    # chiave di servizio non autorizzata dalla radice
    falso_servizio = firma_servizio(bytes(32), pubblica_da_privata(SERVIZIO), ORA - timedelta(days=1),
                                    ORA + timedelta(days=1))
    with pytest.raises(ErroreCertificato):
        leggi_certificato(_testo(servizio=falso_servizio), _radice_pubblica())
    # certificato emesso fuori dal periodo della chiave di servizio
    scaduta = _servizio(ORA - timedelta(days=200), ORA - timedelta(days=20))
    with pytest.raises(ErroreCertificato):
        leggi_certificato(_testo(servizio=scaduta), _radice_pubblica())
    for rovinato in ("", "non json", "[]", '{"servizio": 1}'):
        with pytest.raises(ErroreCertificato):
            leggi_certificato(rovinato, _radice_pubblica())


def test_verifica_senza_libreria_compilata(monkeypatch):
    import builtins

    originale = builtins.__import__

    def senza_cryptography(nome, *args, **kwargs):
        if nome.startswith("cryptography"):
            raise ImportError(nome)
        return originale(nome, *args, **kwargs)

    testo = _testo()
    monkeypatch.setattr(builtins, "__import__", senza_cryptography)
    assert leggi_certificato(testo, _radice_pubblica()).cliente == "Studio Rossi"


# --- stato ---

def _impronte(componenti=PC_A):
    return impronta.calcola(impronta.sale_della_licenza(CODICE), componenti)


def test_stato_attiva_e_avvisi():
    esito = valuta(_certificato(), "psc", _impronte(), ORA + timedelta(days=2))
    assert esito.tipo == ATTIVA and esito.puo_modificare and not esito.avvisi
    vicino = valuta(_certificato(), "psc", _impronte(), ORA + timedelta(days=12))
    assert vicino.puo_modificare and "Collegati a internet entro 2 giorni" in vicino.avvisi[0]
    in_scadenza = valuta(_certificato(scadenza_licenza=date(2026, 11, 10)), "psc", _impronte(), ORA)
    assert in_scadenza.puo_modificare and "La licenza scade il 10/11/2026." in in_scadenza.avvisi


def test_stato_sola_lettura_con_motivo():
    impronte = _impronte()
    casi = [
        (valuta(None, "psc", impronte, ORA), DA_ATTIVARE),
        (valuta(_certificato(), "psc", _impronte(PC_B), ORA), ALTRO_PC),  # certificato copiato da un altro PC
        (valuta(_certificato(stato=REVOCATA), "psc", impronte, ORA), REVOCATA_),
        (valuta(_certificato(), "pimus", impronte, ORA), NON_INCLUSO),
        (valuta(_certificato(scadenza_licenza=date(2026, 10, 1)), "psc", impronte, ORA), SCADUTA),
        (valuta(_certificato(tipo=PROVA, scadenza_licenza=date(2026, 10, 1)), "psc", impronte, ORA), SCADUTA),
        (valuta(_certificato(), "psc", impronte, ORA + timedelta(days=15)), DA_CONVALIDARE),
    ]
    for esito, tipo in casi:
        assert esito.tipo == tipo and esito.sola_lettura and esito.motivo and esito.cosa_fare, tipo
    assert valuta(None, "psc", impronte, ORA).serve_attivazione
    assert "consultabili" in casi[4][0].cosa_fare  # i documenti già fatti restano accessibili


def test_perpetua_aggiornamenti():
    c = _certificato(tipo=PERPETUA, scadenza_licenza=None, aggiornamenti_fino=date(2026, 6, 30))
    assert valuta(c, "psc", _impronte(), ORA, data_versione=date(2026, 5, 1)).puo_modificare
    esito = valuta(c, "psc", _impronte(), ORA, data_versione=date(2026, 9, 1))
    assert esito.tipo == AGGIORNAMENTI and "30/06/2026" in esito.motivo
    # l'abbonamento scaduto non diventa perpetuo: sola lettura anche con una versione vecchia
    abbonamento = _certificato(scadenza_licenza=date(2026, 6, 30))
    assert valuta(abbonamento, "psc", _impronte(), ORA, data_versione=date(2026, 5, 1)).tipo == SCADUTA


def test_orologio_spostato_indietro():
    c = _certificato()
    assert valuta(c, "psc", _impronte(), ORA - timedelta(days=3)).tipo == OROLOGIO  # prima dell'emissione
    dopo = ORA + timedelta(days=5)
    assert valuta(c, "psc", _impronte(), ORA + timedelta(days=1), ultima_ora_vista=dopo).tipo == OROLOGIO
    # piccoli scarti (fuso orario, ora legale) sono tollerati
    assert valuta(c, "psc", _impronte(), dopo - timedelta(hours=5), ultima_ora_vista=dopo).puo_modificare


def test_attivazione_offline_avviso_lungo():
    c = _certificato(offline=True, valido_fino=ORA + timedelta(days=90))
    assert not valuta(c, "psc", _impronte(), ORA + timedelta(days=60)).avvisi
    assert valuta(c, "psc", _impronte(), ORA + timedelta(days=80)).avvisi
    finita = valuta(c, "psc", _impronte(), ORA + timedelta(days=91))
    assert finita.tipo == DA_CONVALIDARE and "offline" in finita.motivo


# --- custodia ---

def test_custodia_certificato_e_orologio():
    assert custodia.leggi_certificato() == "" and custodia.ultima_ora_vista() is None
    custodia.salva_certificato("contenuto")
    assert custodia.leggi_certificato() == "contenuto"
    custodia.registra_ora(ORA)
    custodia.registra_ora(ORA - timedelta(days=10))  # mai indietro
    assert custodia.ultima_ora_vista() == ORA
    custodia.elimina_certificato()
    assert custodia.leggi_certificato() == ""


# --- collegamento al server (server finto: quello vero è in licenze/) ---

class ServerFinto:
    def __init__(self, posti=3):
        self.posti = posti
        self.pc: dict[str, list[str]] = {}
        self.revocata = False
        self.raggiungibile = True
        self.contatore = 0

    def _emetti(self, impronte, pc, ora=ORA):
        c = _certificato(impronte=tuple(impronte), pc=pc, emesso=ora, valido_fino=ora + timedelta(days=14),
                         stato=REVOCATA if self.revocata else "attiva")
        return _testo(c)

    def __call__(self, percorso, dati):
        if not self.raggiungibile:
            raise ErroreRete("offline")
        if percorso == "attiva":
            if dati["codice"] != CODICE:
                return 404, {"errore": "codice_errato", "messaggio": "Codice di licenza non valido."}
            for id_, impronte in self.pc.items():
                if impronta.stesso_pc(impronte, dati["impronte"]):
                    return 200, {"certificato": self._emetti(dati["impronte"], id_)}  # stesso PC: nessun posto
            if len(self.pc) >= self.posti:
                return 409, {"errore": POSTI_ESAURITI,
                             "messaggio": f"La licenza è già attiva su {self.posti} PC su {self.posti}.",
                             "pc": [{"id": k, "nome": k} for k in self.pc]}
            self.contatore += 1
            id_ = f"pc-{self.contatore}"
            self.pc[id_] = dati["impronte"]
            return 200, {"certificato": self._emetti(dati["impronte"], id_)}
        if percorso == "convalida":
            c = leggi_certificato(dati["certificato"], _radice_pubblica())
            if self.revocata:
                return 403, {"errore": "revocata", "messaggio": "Licenza revocata.",
                             "certificato": self._emetti(dati["impronte"], c.pc, ORA + timedelta(days=1))}
            return 200, {"certificato": self._emetti(dati["impronte"], c.pc, ORA + timedelta(days=1))}
        if percorso == "disattiva":
            self.pc.pop(leggi_certificato(dati["certificato"], _radice_pubblica()).pc, None)
            return 200, {"ok": True}
        if percorso == "libera":
            self.pc.pop(dati["pc"], None)
            return 200, {"ok": True, "trasferimenti_rimasti": 1}
        return 404, {"errore": "sconosciuto"}


def _licenze(server, componenti=PC_A, programma="psc"):
    return Licenze(programma, _radice_pubblica(), server, versione="0.23.0", componenti=componenti)


def test_attivazione_quarto_pc_e_trasferimento(tmp_path, monkeypatch):
    server = ServerFinto(posti=3)
    l = _licenze(server)
    assert l.esito(ORA).tipo == DA_ATTIVARE
    l.attiva(CODICE)
    assert l.esito(ORA).puo_modificare and l.codice_salvato() == CODICE
    l.attiva(CODICE)  # riattivazione dello stesso PC: nessun posto in più
    assert len(server.pc) == 1
    for i, nome in enumerate(("PC-2", "PC-3"), 2):
        monkeypatch.setenv("SICUR_LICENSE_CARTELLA", str(tmp_path / nome))
        _licenze(server, {"sistema": f"g{i}", "hardware": f"h{i}", "nome": nome}).attiva(CODICE)
    monkeypatch.setenv("SICUR_LICENSE_CARTELLA", str(tmp_path / "PC-4"))
    quarto = _licenze(server, PC_B)
    with pytest.raises(ErroreServer) as rifiuto:
        quarto.attiva(CODICE)
    assert rifiuto.value.codice == POSTI_ESAURITI and "3 PC su 3" in str(rifiuto.value)
    assert len(rifiuto.value.pc) == 3
    quarto.libera(CODICE, "pc-1")  # trasferimento: libera il primo PC e attiva questo
    quarto.attiva(CODICE)
    assert quarto.esito(ORA).puo_modificare and len(server.pc) == 3
    with pytest.raises(ErroreServer):
        quarto.attiva("SC-CODICE-SBAGLIATO")


def test_convalida_revoca_rete_e_disattivazione():
    server = ServerFinto()
    l = _licenze(server)
    l.attiva(CODICE)
    assert l.convalida().emesso == ORA + timedelta(days=1)  # rinnovato
    server.raggiungibile = False
    with pytest.raises(ErroreRete):
        l.convalida()
    assert l.esito(ORA + timedelta(days=2)).puo_modificare  # senza rete continua con il certificato
    server.raggiungibile, server.revocata = True, True
    l.convalida()
    assert l.esito(ORA + timedelta(days=2)).tipo == REVOCATA_
    server.revocata = False
    l.disattiva()
    assert not server.pc and l.esito(ORA + timedelta(days=2)).tipo == DA_ATTIVARE


def test_certificato_copiato_su_altro_pc(tmp_path):
    l = _licenze(ServerFinto())
    l.attiva(CODICE)
    copia = _licenze(ServerFinto(), PC_B)  # stessa cartella, altro hardware
    assert copia.esito(ORA).tipo == ALTRO_PC


def test_orologio_con_custodia():
    l = _licenze(ServerFinto())
    l.attiva(CODICE)
    assert l.esito(ORA + timedelta(days=6)).puo_modificare
    assert l.esito(ORA + timedelta(days=2)).tipo == OROLOGIO  # torna indietro di 4 giorni


def test_attivazione_offline():
    l = _licenze(None)
    richiesta = json.loads(l.richiesta_offline(CODICE))
    assert richiesta["codice"] == CODICE and len(richiesta["impronte"]) == 3
    assert "guid-a" not in json.dumps(richiesta)
    # l'assistenza carica la richiesta nel gestionale e restituisce il file firmato
    risposta = _testo(_certificato(impronte=tuple(richiesta["impronte"]), offline=True,
                                   valido_fino=ORA + timedelta(days=90)))
    assert l.importa_offline(risposta).offline
    assert l.esito(ORA + timedelta(days=30)).puo_modificare
    with pytest.raises(ErroreCertificato):
        _licenze(None, PC_B).importa_offline(risposta)  # file di un altro PC
    with pytest.raises(ErroreCertificato):
        l.importa_offline("non è un file di attivazione")
    with pytest.raises(ErroreRete):
        l.convalida()  # senza server impostato: il programma resta com'è
