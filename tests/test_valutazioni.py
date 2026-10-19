import math

import pytest

from sicurcantiere.valutazioni import METODI
from sicurcantiere.valutazioni import niosh, ocra
from sicurcantiere.valutazioni.base import GIALLO, ROSSO, VERDE, VIOLA


def test_fattori_niosh():
    assert niosh.hm(20) == 1 and niosh.hm(50) == pytest.approx(0.5) and niosh.hm(70) == 0
    assert niosh.vm(75) == 1 and niosh.vm(0) == pytest.approx(0.775) and niosh.vm(180) == 0
    assert niosh.dm(20) == 1 and niosh.dm(50) == pytest.approx(0.91) and niosh.dm(180) == 0
    assert niosh.am(0) == 1 and niosh.am(90) == pytest.approx(0.712) and niosh.am(140) == 0
    assert niosh.fm(0.1, "breve", 40) == 1
    assert niosh.fm(1, "lunga", 40) == pytest.approx(0.75)
    assert niosh.fm(1.5, "lunga", 40) == pytest.approx(0.70)  # interpolato tra 0,75 e 0,65
    assert niosh.fm(9, "lunga", 40) == 0 and niosh.fm(9, "lunga", 80) == pytest.approx(0.15)
    assert niosh.fm(16, "breve", 80) == 0
    assert niosh.cm("discreta", 40) == 0.95 and niosh.cm("discreta", 80) == 1


def test_niosh_semplice_esempio():
    # 15 kg, H 30, V 40, D 60, A 0, 1 atto/min, durata breve, presa discreta, maschi 18-45
    dati = {"lavoratori": "M18-45", "durata": "breve", "peso": 15, "h": 30, "v": 40, "d": 60,
            "a": 0, "frequenza": 1, "presa": "discreta"}
    esito = METODI["niosh"].esegui(dati)
    rwl = 25 * (25 / 30) * (1 - 0.003 * 35) * (0.82 + 4.5 / 60) * 1 * 0.94 * 0.95
    assert esito.indice == pytest.approx(15 / rwl)
    assert esito.colore == ROSSO  # LI appena sopra 1
    assert any("RWL" in d[0] for d in esito.dettagli)
    assert any("Avvicinare il carico" in m for m in esito.misure)


def test_niosh_classi_e_limiti():
    base = {"lavoratori": "M18-45", "durata": "breve", "h": 25, "v": 75, "d": 25, "a": 0,
            "frequenza": 0.2, "presa": "buona"}
    assert METODI["niosh"].esegui({**base, "peso": 20}).colore == VERDE  # 20/25 = 0,8
    assert METODI["niosh"].esegui({**base, "peso": 24}).colore == GIALLO
    assert METODI["niosh"].esegui({**base, "peso": 80}).colore == VIOLA
    fuori = METODI["niosh"].esegui({**base, "peso": 5, "h": 70})
    assert math.isinf(fuori.indice) and fuori.colore == VIOLA and fuori.note


def test_niosh_composto():
    compito = {"peso": 10, "h": 25, "v": 75, "d": 25, "a": 0, "presa": "buona"}
    dati = {"lavoratori": "M18-45", "durata": "media", "compiti": [
        {**compito, "nome": "A", "frequenza": 1},
        {**compito, "nome": "B", "peso": 5, "frequenza": 2},
    ]}
    esito = METODI["niosh_composto"].esegui(dati)
    # STLI_A = 10/(25*0,88), FILI_B = 5/25; CLI = STLI_A + FILI_B*(1/FM(3) - 1/FM(1))
    atteso = 10 / (25 * 0.88) + 5 / 25 * (1 / 0.79 - 1 / 0.88)
    assert esito.indice == pytest.approx(atteso)
    assert len(esito.righe_compiti) == 2
    # Un solo compito: il CLI coincide con l'indice semplice.
    solo = METODI["niosh_composto"].esegui({**dati, "compiti": [dati["compiti"][0]]})
    assert solo.indice == pytest.approx(10 / (25 * 0.88))
    vuoto = METODI["niosh_composto"].esegui({**dati, "compiti": []})
    assert vuoto.indice is None


def test_ocra():
    assert ocra.fattore_forza(0.5) == 1 and ocra.fattore_forza(3) == pytest.approx(0.45)
    assert ocra.fattore_postura(3) == 1 and ocra.fattore_postura(8) == 0.6 and ocra.fattore_postura(20) == 0.33
    assert ocra.fattore_recupero(2) == pytest.approx(0.8)
    assert ocra.fattore_durata(480) == 1 and ocra.fattore_durata(100) == 1.7 and ocra.fattore_durata(800) == 0.75
    dati = {"arto": "destro", "ore_senza_recupero": 2, "compiti": [
        {"nome": "Legature ferri", "durata": 400, "azioni_min": 40, "forza": 2, "postura": 6,
         "stereotipia": "presente", "complementari": "terzo"},
    ]}
    esito = METODI["ocra"].esegui(dati)
    ata = 40 * 400
    rta = 30 * 0.65 * 0.70 * 0.70 * 0.95 * 400 * 0.80 * 1.05
    assert esito.indice == pytest.approx(ata / rta)
    assert esito.colore in (ROSSO, VIOLA)
    assert any("forza" in m.lower() for m in esito.misure)
    leggero = METODI["ocra"].esegui({**dati, "compiti": [{**dati["compiti"][0], "azioni_min": 10,
                                                          "forza": 0.5, "postura": 0,
                                                          "stereotipia": "assente",
                                                          "complementari": "assenti"}],
                                    "ore_senza_recupero": 0})
    assert leggero.colore == VERDE


def test_normalizza_dati_sporchi():
    m = METODI["niosh"]
    dati = m.normalizza({"peso": "abc", "h": -5, "presa": "inventata"})
    assert dati["peso"] == 10 and dati["h"] == 0 and dati["presa"] == "discreta"
    for metodo in METODI.values():
        assert metodo.esegui(metodo.dati_predefiniti()).classe
