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


def test_rumore():
    from sicurcantiere.valutazioni import rumore

    # 4 ore a 90 dB(A) -> LEX = 90 + 10 log(0,5) = 86,99
    assert rumore.lex([{"laeq": 90, "durata": 240}]) == pytest.approx(86.99, abs=0.01)
    # due attività da 85 dB(A) per 4 ore ciascuna -> 85 dB(A)
    assert rumore.lex([{"laeq": 85, "durata": 240}, {"laeq": 85, "durata": 240}]) == pytest.approx(85.0)
    assert rumore.classe(79.9, 130)[1] == VERDE
    assert rumore.classe(80.5, 130)[1] == GIALLO
    assert rumore.classe(79, 136)[1] == GIALLO  # conta anche il picco
    assert rumore.classe(86, 130)[1] == ROSSO
    assert rumore.classe(88, 130)[1] == VIOLA

    dati = {"snr": 0, "compiti": [
        {"nome": "Taglio con smerigliatrice", "laeq": 100, "durata": 60, "picco": 125},
        {"nome": "Lavori manuali", "laeq": 78, "durata": 360, "picco": 110},
    ]}
    esito = METODI["rumore"].esegui(dati)
    atteso = 10 * math.log10(60 / 480 * 10 ** 10 + 360 / 480 * 10 ** 7.8)
    assert esito.indice == pytest.approx(atteso)
    assert esito.colore == VIOLA  # oltre 87 dB(A) senza DPI
    assert "smerigliatrice" in esito.misure[0]
    # Con DPI SNR 25 (attenuazione 18 dB) il valore limite è rispettato: resta il rosso per gli obblighi.
    protetto = METODI["rumore"].esegui({**dati, "snr": 25})
    assert protetto.colore == ROSSO and "limite rispettato" in protetto.classe
    assert any("65 e 80" in n for n in protetto.note)


def test_vibrazioni():
    from sicurcantiere.valutazioni import vibrazioni

    # 8 m/s^2 per 2 ore -> A(8) = 8 * radice(0,25) = 4
    esito = METODI["vibrazioni"].esegui({"sistema": "hav", "compiti": [
        {"nome": "Martello demolitore", "accelerazione": 8, "durata": 120}]})
    assert esito.indice == pytest.approx(4.0) and esito.colore == ROSSO
    assert esito.righe_compiti[0][-1] == "47"  # 480 x (2,5/8)^2 = 46,9 minuti al valore d'azione
    assert any("impugnature antivibranti" in m for m in esito.misure)
    oltre = METODI["vibrazioni"].esegui({"sistema": "hav", "compiti": [
        {"nome": "Demolitore", "accelerazione": 22, "durata": 60}]})
    assert oltre.colore == VIOLA and oltre.note  # anche oltre il limite su periodi brevi
    wbv = METODI["vibrazioni"].esegui({"sistema": "wbv", "compiti": [
        {"nome": "Escavatore", "accelerazione": 0.6, "durata": 360}]})
    assert wbv.indice == pytest.approx(0.6 * math.sqrt(0.75))
    assert wbv.colore == ROSSO and any("Sedili" in m for m in wbv.misure)
    assert vibrazioni.classe(0.3, "wbv")[1] == VERDE


def test_tavole_snook_complete():
    from sicurcantiere.valutazioni import snook

    colonne = sum(len(i) for _, i in snook.COLONNE_SPINTA_TRAINO)
    assert all(len(r) == colonne == 35 for righe in snook.SPINTA_TRAINO.values() for r in righe)
    assert all(len(r) == 21 for righe in snook.TRASPORTO.values() for r in righe)
    # Femmine, traino, mani a 89 cm, 7,6 m, una volta al minuto.
    assert snook.forza_raccomandata("traino", "F", "iniziale", 90, 7.6, 60)[0] == 16
    assert snook.forza_raccomandata("traino", "F", "mantenimento", 90, 7.6, 60)[0] == 9
    # Scelte prudenziali: 10 m -> 15,2 m; una ogni 3 minuti -> colonna dei 2 minuti.
    valore, info = snook.forza_raccomandata("spinta", "M", "iniziale", 100, 10, 20)
    assert valore == 22 and info["distanza"] == 15.2 and info["intervallo"] == 120
    # Una volta per turno resta nella colonna delle 8 ore.
    assert snook.forza_raccomandata("spinta", "M", "iniziale", 144, 2, 0.13)[0] == 31
    with pytest.raises(snook.FuoriTabella):
        snook.forza_raccomandata("spinta", "M", "iniziale", 95, 2.1, 1000)


def test_traino_spinta():
    azione = {"nome": "Carriola", "tipo": "spinta", "forza_iniziale": 22, "forza_mantenimento": 12,
              "altezza": 95, "distanza": 15, "frequenza": 20}
    dati = {"genere": "M", "condizioni": "buone", "compiti": [azione]}
    esito = METODI["traino_spinta"].esegui(dati)
    assert esito.indice == pytest.approx(1.0) and esito.colore == GIALLO
    leggera = {**azione, "forza_iniziale": 11, "forza_mantenimento": 6}
    assert METODI["traino_spinta"].esegui({**dati, "compiti": [leggera]}).colore == VERDE
    assert METODI["traino_spinta"].esegui({**dati, "condizioni": "sfavorevoli",
                                           "compiti": [leggera]}).colore == ROSSO
    # Popolazione mista: limiti femminili (mantenimento 7 kg), indice 12/7.
    mista = METODI["traino_spinta"].esegui({**dati, "genere": "F"})
    assert mista.indice == pytest.approx(12 / 7) and mista.colore == ROSSO
    fuori = METODI["traino_spinta"].esegui({**dati, "compiti": [{**azione, "distanza": 2, "frequenza": 1000}]})
    assert math.isinf(fuori.indice) and fuori.colore == VIOLA and fuori.note
    assert METODI["traino_spinta"].esegui({**dati, "compiti": []}).indice is None


def test_trasporto():
    from sicurcantiere.valutazioni import trasporto

    blocchi = {"nome": "Blocchi", "peso": 12, "frequenza": 3, "durata": 120, "distanza": 5, "altezza": "bassa"}
    dati = {"lavoratori": "M18-45", "condizioni": "buone", "compiti": [blocchi]}
    esito = METODI["trasporto"].esegui(dati)
    # 36 kg/min contro 30 kg/min (distanza fino a 10 m); Snook 12/13.
    assert esito.indice == pytest.approx(36 * 60 / 1500) and esito.colore == ROSSO
    assert trasporto.limiti_massa(5, True) == pytest.approx((20, 1000, 10000 * 2 / 3))
    assert trasporto.limiti_massa(30, False) == (15, 750, 6000)
    # Nell'ora più gravosa: 30 min a 36 kg/min e 30 min a 10 kg/min.
    m = trasporto.masse_cumulate([blocchi | {"durata": 30}, {**blocchi, "peso": 10, "frequenza": 1}])
    assert m == pytest.approx((36, 36 * 30 + 10 * 30, 36 * 30 + 10 * 120))
    leggero = METODI["trasporto"].esegui({**dati, "compiti": [{**blocchi, "peso": 5, "frequenza": 1}]})
    assert leggero.colore == VERDE
