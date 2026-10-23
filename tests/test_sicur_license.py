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
from sicur_license.cliente import ErroreRete, Licenze
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
SALE = "licenza:prova-sale"


@pytest.fixture(autouse=True)
def cartella_licenza(tmp_path, monkeypatch):
    monkeypatch.setenv("SICUR_LICENSE_CARTELLA", str(tmp_path / "licenza"))


def _servizio(da=ORA - timedelta(days=30), a=ORA + timedelta(days=150)):
    return firma_servizio(RADICE, pubblica_da_privata(SERVIZIO), da, a, "servizio di prova")


def _certificato(componenti=PC_A, **modifiche) -> Certificato:
    sale = SALE
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
    sale = SALE
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
    assert impronta.calcola("licenza:altra", PC_A) != a


def test_sale_provvisorio_casuale():
    assert impronta.sale_provvisorio() != impronta.sale_provvisorio()
    assert impronta.normalizza_codice(" SC-7KQ4\n -M2XD ") == "SC-7KQ4-M2XD"


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
    return impronta.calcola(SALE, componenti)


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


# --- attivazione offline (l'attivazione online è provata con il server vero in test_server_licenze.py) ---

def _licenze(componenti=PC_A, programma="psc"):
    return Licenze(programma, _radice_pubblica(), None, versione="0.23.0", componenti=componenti)


def test_attivazione_offline():
    l = _licenze()
    richiesta = json.loads(l.richiesta_offline(CODICE))
    assert richiesta["codice"] == CODICE and len(richiesta["impronte"]) == 3
    assert richiesta["sale"].startswith("provvisorio:")  # il programma non ha ancora parlato con il server
    assert "guid-a" not in json.dumps(richiesta)
    # l'assistenza carica la richiesta nel gestionale e restituisce il file firmato
    risposta = _testo(_certificato(impronte=tuple(richiesta["impronte"]), sale=richiesta["sale"], offline=True,
                                   valido_fino=ORA + timedelta(days=90)))
    assert l.importa_offline(risposta).offline
    assert l.esito(ORA + timedelta(days=30)).puo_modificare
    with pytest.raises(ErroreCertificato):
        _licenze(PC_B).importa_offline(risposta)  # file di un altro PC
    with pytest.raises(ErroreCertificato):
        l.importa_offline("non è un file di attivazione")
    with pytest.raises(ErroreRete):
        l.convalida()  # senza server impostato: il programma resta com'è
