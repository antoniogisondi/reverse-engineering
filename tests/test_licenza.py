import base64
from datetime import date, timedelta

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from sicurcantiere import aggiornamenti, licenza


@pytest.fixture
def chiavi(monkeypatch):
    privata = Ed25519PrivateKey.generate()
    grezza = privata.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                                   serialization.NoEncryption())
    pubblica = privata.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    monkeypatch.setenv("SICURCANTIERE_CHIAVE_LICENZE", base64.b64encode(pubblica).decode())
    return grezza


def _licenza(**k):
    dati = dict(id="L-1", cliente="Studio Rossi", piano="pos", emessa=date(2026, 10, 1),
                scadenza=date(2027, 10, 1), postazioni=1)
    dati.update(k)
    return licenza.Licenza(**dati)


def test_firma_e_verifica(chiavi):
    codice = licenza.firma(_licenza(), chiavi)
    assert codice.startswith("SC1-")
    letta = licenza.leggi(codice[:30] + "\n  " + codice[30:])  # spazi e a capo copiati dall'email
    assert letta == _licenza() and letta.nome_piano == "POS" and letta.programmi == {"pos"}
    # una lettera cambiata nei dati o nella firma rende il codice non valido
    dati, firma = codice[4:].split(".")
    for falso in (f"SC1-{dati[:-2]}AA.{firma}", f"SC1-{dati}.{firma[:-2]}AA", "SC1-abc", "XYZ"):
        with pytest.raises(licenza.ErroreLicenza):
            licenza.leggi(falso)
    # firmata con un'altra chiave
    altra = Ed25519PrivateKey.generate().private_bytes(
        serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
    with pytest.raises(licenza.ErroreLicenza):
        licenza.leggi(licenza.firma(_licenza(), altra))


def test_stati(chiavi):
    oggi = date(2026, 11, 1)
    pos = licenza.firma(_licenza(), chiavi)
    assert licenza.stato("pos", pos, None, oggi).tipo == licenza.LICENZA
    assert licenza.stato("psc", pos, None, oggi).tipo == licenza.NON_INCLUSO  # pagina «non incluso»
    completo = licenza.firma(_licenza(piano="completo", scadenza=None), chiavi)
    assert licenza.stato("pimus", completo, None, oggi).tipo == licenza.LICENZA
    # alla scadenza il programma continua a funzionare (opzione b)
    scaduta = licenza.stato("pos", pos, None, date(2028, 1, 1))
    assert scaduta.tipo == licenza.LICENZA and scaduta.utilizzabile and scaduta.scaduta
    # prova: 30 giorni dall'inizio, poi finita
    prova = licenza.stato("pos", "", date(2026, 10, 20), oggi)
    assert prova.tipo == licenza.PROVA and prova.giorni_prova == 18
    assert licenza.stato("pos", "", oggi - timedelta(days=31), oggi).tipo == licenza.PROVA_FINITA
    assert not licenza.stato("pos", "", oggi - timedelta(days=31), oggi).utilizzabile
    # codice rovinato: si resta in prova, con il messaggio
    rovinato = licenza.stato("pos", "SC1-xx.yy", oggi, oggi)
    assert rovinato.tipo == licenza.PROVA and rovinato.messaggi


def test_controllo_non_attivo_senza_chiave(monkeypatch):
    monkeypatch.delenv("SICURCANTIERE_CHIAVE_LICENZE", raising=False)
    monkeypatch.setattr(licenza, "CHIAVE_PUBBLICA", "")
    assert licenza.stato("psc", "", None).tipo == licenza.LIBERO


def test_aggiornamenti_con_licenza_scaduta():
    v = aggiornamenti.Versione("1.0", "u", "p", "", date(2027, 11, 1))
    assert aggiornamenti.inclusa_nella_licenza(v, None)
    assert not aggiornamenti.inclusa_nella_licenza(v, date(2027, 10, 1))
    assert aggiornamenti.inclusa_nella_licenza(v, date(2027, 12, 1))
