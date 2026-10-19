from datetime import date

import pytest
from docx import Document

from sicurcantiere import analisi
from sicurcantiere.archivio import ATTREZZATURE, CATEGORIE, LAVORAZIONI
from sicurcantiere.db import MIGRAZIONI, ErroreProgetto, Progetto, VERSIONE_SCHEMA
from sicurcantiere.documenti.psc import genera_psc
from sicurcantiere.repository import Repository


def lav(codice):
    return next(l for l in LAVORAZIONI if l["codice"] == codice)


@pytest.fixture
def repo(tmp_path):
    progetto = Progetto(tmp_path / "prova.scs", crea=True)
    yield Repository(progetto)
    progetto.chiudi()


def test_nuovo_progetto_ha_schema_aggiornato(tmp_path):
    p = Progetto(tmp_path / "a.scs", crea=True)
    assert p.query("PRAGMA user_version")[0][0] == VERSIONE_SCHEMA
    p.chiudi()
    # Riapertura: crea il backup e non riapplica le migrazioni.
    p = Progetto(tmp_path / "a.scs")
    assert (tmp_path / "a.scs.bak").exists()
    p.chiudi()


def test_file_non_valido(tmp_path):
    f = tmp_path / "rotto.scs"
    f.write_bytes(b"non sono un database" * 100)
    with pytest.raises(ErroreProgetto):
        Progetto(f)


def test_versione_futura_rifiutata(tmp_path):
    p = Progetto(tmp_path / "f.scs", crea=True)
    p.conn.execute(f"PRAGMA user_version = {VERSIONE_SCHEMA + 1}")
    p.chiudi()
    with pytest.raises(ErroreProgetto):
        Progetto(tmp_path / "f.scs")


def test_campi_non_validi_rifiutati(repo):
    with pytest.raises(ValueError):
        repo.inserisci("imprese", **{"ragione_sociale; DROP TABLE imprese": "x"})
    with pytest.raises(ValueError):
        repo.elenco("sqlite_master")


def test_crud_e_cascata(repo):
    impresa = repo.inserisci("imprese", ragione_sociale="Edil Srl")
    lavorazione = lav("AL.01")
    fase = repo.importa_lavorazione(lavorazione)
    repo.aggiorna("fasi", fase, impresa_id=impresa)
    assert repo.leggi("fasi", fase)["impresa_id"] == impresa
    attese = len(lavorazione["rischi"]) + sum(len(ATTREZZATURE[a]["rischi"]) for a in lavorazione["attrezzature"])
    assert len(repo.elenco("rischi", fase_id=fase)) == attese
    assert {a["nome"] for a in repo.elenco("attrezzature", fase_id=fase)} == set(lavorazione["attrezzature"])
    repo.elimina("imprese", impresa)
    assert repo.leggi("fasi", fase)["impresa_id"] is None
    repo.elimina("fasi", fase)
    assert repo.elenco("rischi") == []
    assert repo.elenco("attrezzature") == []


def test_salva_con_nome(repo, tmp_path):
    repo.aggiorna_cantiere(nome="Scuola")
    repo.progetto.salva_con_nome(tmp_path / "copia.scs")
    copia = Progetto(tmp_path / "copia.scs")
    assert Repository(copia).cantiere()["nome"] == "Scuola"
    copia.chiudi()


def test_classi_rischio():
    assert analisi.classe_rischio(analisi.livello_rischio(1, 2)) == "Basso"
    assert analisi.classe_rischio(analisi.livello_rischio(2, 2)) == "Medio"
    assert analisi.classe_rischio(analisi.livello_rischio(2, 3)) == "Alto"
    assert analisi.classe_rischio(analisi.livello_rischio(3, 4)) == "Molto alto"


def test_giorni_lavorativi():
    # 6-19 ottobre 2025: due settimane complete, lunedì -> domenica.
    assert analisi.giorni_lavorativi(date(2025, 10, 6), date(2025, 10, 19)) == 10
    assert analisi.giorni_lavorativi(date(2025, 10, 10), date(2025, 10, 13)) == 2  # ven -> lun
    assert analisi.giorni_lavorativi(date(2025, 10, 11), date(2025, 10, 12)) == 0
    assert analisi.giorni_lavorativi(date(2025, 10, 13), date(2025, 10, 10)) == 0


def _fase(id_, impresa, inizio, fine, lavoratori=1):
    return {"id": id_, "codice": f"F{id_}", "descrizione": "", "impresa_id": impresa,
            "data_inizio": inizio, "data_fine": fine, "lavoratori": lavoratori}


def test_interferenze():
    fasi = [
        _fase(1, 1, "2025-10-06", "2025-10-17"),
        _fase(2, 2, "2025-10-15", "2025-10-24"),  # si sovrappone a 1, altra impresa
        _fase(3, 1, "2025-10-16", "2025-10-16"),  # stessa impresa di 1, sovrapposta a 2
        _fase(4, 2, "2025-11-01", "2025-11-05"),  # isolata
        _fase(5, None, None, None),
    ]
    coppie = {(i.fase_a["id"], i.fase_b["id"]) for i in analisi.interferenze(fasi)}
    assert coppie == {(1, 2), (2, 3)}
    prima = analisi.interferenze(fasi)[0]
    assert (prima.inizio, prima.fine) == (date(2025, 10, 15), date(2025, 10, 17))


def test_obblighi():
    imprese = [{"id": 1, "tipo": "Affidataria"}, {"id": 2, "tipo": "Esecutrice"},
               {"id": 3, "tipo": "Lavoratore autonomo"}]
    una = [_fase(1, 1, "2025-10-06", "2025-10-10", 3)]
    o = analisi.obblighi(imprese, una)
    assert (o.imprese, o.uomini_giorno, o.psc, o.notifica) == (1, 15, False, False)

    grande = [_fase(1, 1, "2025-01-06", "2025-03-28", 4)]  # 60 gg lavorativi x 4
    o = analisi.obblighi(imprese, grande)
    assert o.uomini_giorno == 240 and not o.psc and o.notifica

    due = una + [_fase(2, 2, "2025-12-01", "2025-12-02")]
    o = analisi.obblighi(imprese, due)
    assert o.psc and o.notifica


def test_genera_psc(repo, tmp_path):
    repo.aggiorna_cantiere(nome="Ristrutturazione scuola", comune="Bari", provincia="BA",
                           importo_lavori=250000)
    repo.inserisci("soggetti", ruolo="Committente", nome="Comune di Bari")
    a = repo.inserisci("imprese", ragione_sociale="Alfa Costruzioni", tipo="Affidataria")
    b = repo.inserisci("imprese", ragione_sociale="Beta Impianti")
    f1 = repo.importa_lavorazione(lav("NC.01"))
    f2 = repo.importa_lavorazione(lav("AL.04"))
    repo.aggiorna("fasi", f1, impresa_id=a, data_inizio="2025-10-06", data_fine="2025-10-31")
    repo.aggiorna("fasi", f2, impresa_id=b, data_inizio="2025-10-20", data_fine="2025-11-14")
    repo.inserisci("costi", descrizione="Recinzione", unita="m", quantita=120, prezzo_unitario=12.5)
    repo.salva_testo("emergenze", "Presidio di primo soccorso nel box.")

    file = genera_psc(repo, tmp_path / "psc.docx")
    doc = Document(file)
    testo = "\n".join(p.text for p in doc.paragraphs)
    celle = "\n".join(c.text for t in doc.tables for r in t.rows for c in r.cells)
    assert "PIANO DI SICUREZZA E COORDINAMENTO" in testo
    assert "Presidio di primo soccorso" in testo
    assert "Alfa Costruzioni" in celle
    assert "€ 1.500,00" in celle
    assert "Scavo di sbancamento" in celle  # interferenza e cronoprogramma
    assert "Sfasamento spaziale" in celle  # prescrizione generica


def test_genera_psc_progetto_vuoto(repo, tmp_path):
    assert genera_psc(repo, tmp_path / "vuoto.docx").exists()


def test_migrazione_da_v1(tmp_path):
    import sqlite3

    f = tmp_path / "vecchio.scs"
    conn = sqlite3.connect(f)
    conn.executescript(MIGRAZIONI[0] + ";PRAGMA user_version = 1;")
    conn.execute("INSERT INTO fasi (codice, descrizione) VALUES ('X', 'Vecchia fase')")
    conn.commit()
    conn.close()
    p = Progetto(f)
    r = Repository(p)
    assert p.query("PRAGMA user_version")[0][0] == VERSIONE_SCHEMA
    fase = r.elenco("fasi")[0]
    assert fase["descrizione"] == "Vecchia fase" and fase["zona"] == ""
    assert r.cantiere()["costo_uomo_giorno"] == 250
    p.chiudi()


def test_archivio_coerente():
    codici = [l["codice"] for l in LAVORAZIONI]
    assert len(codici) == len(set(codici))
    for l in LAVORAZIONI:
        assert l["categoria"] in CATEGORIE
        assert 0 < l["incidenza_manodopera"] <= 100
        for r in l["rischi"]:
            assert 1 <= r["probabilita"] <= 4 and 1 <= r["danno"] <= 4
            assert r["misure"].strip(), (l["codice"], r["descrizione"])
    for nome, a in ATTREZZATURE.items():
        for r in a["rischi"]:
            assert r["misure"].strip(), (nome, r["descrizione"])


def test_durata_stimata():
    # 100.000 € x 40% / 250 €/ug = 160 ug; squadra di 4 -> 40 giorni lavorativi
    assert analisi.durata_stimata(100_000, 40, 250, 4) == 40
    assert analisi.durata_stimata(1_000, 40, 250, 4) == 1
    assert analisi.durata_stimata(0, 40, 250, 4) is None
    assert analisi.durata_stimata(1_000, 40, 250, 0) is None


def test_fine_dopo_giorni_lavorativi():
    assert analisi.fine_dopo_giorni_lavorativi(date(2025, 10, 6), 1) == date(2025, 10, 6)
    assert analisi.fine_dopo_giorni_lavorativi(date(2025, 10, 6), 5) == date(2025, 10, 10)
    assert analisi.fine_dopo_giorni_lavorativi(date(2025, 10, 6), 6) == date(2025, 10, 13)
    # inizio di sabato: si parte dal lunedì
    assert analisi.fine_dopo_giorni_lavorativi(date(2025, 10, 11), 1) == date(2025, 10, 13)
    d = analisi.fine_dopo_giorni_lavorativi(date(2025, 10, 6), 40)
    assert analisi.giorni_lavorativi(date(2025, 10, 6), d) == 40


def test_interferenze_zona_e_gravita():
    fasi = [
        {**_fase(1, 1, "2025-10-06", "2025-10-17"), "zona": "Edificio A"},
        {**_fase(2, 2, "2025-10-06", "2025-10-17"), "zona": "edificio a "},  # stessa zona
        {**_fase(3, 3, "2025-10-06", "2025-10-17"), "zona": "Edificio B"},
        {**_fase(4, 4, "2025-10-06", "2025-10-17"), "zona": ""},  # zona non indicata
    ]
    livelli = {1: 4, 2: 12, 4: 2}
    elenco = analisi.interferenze(fasi, livelli)
    assert {i.chiave for i in elenco} == {(1, 2), (1, 4), (2, 4), (3, 4)}
    assert elenco[0].chiave == (1, 2) and elenco[0].gravita == 12


def test_sovrapposizione_solo_nel_fine_settimana():
    fasi = [_fase(1, 1, "2025-10-06", "2025-10-11"), _fase(2, 2, "2025-10-11", "2025-10-12")]
    assert analisi.interferenze(fasi) == []


def test_andamento():
    fasi = [_fase(1, 1, "2025-10-06", "2025-10-10", 3), _fase(2, 2, "2025-10-09", "2025-10-14", 2)]
    giornate = analisi.andamento(fasi, {1: 4, 2: 9})
    assert [g.giorno.day for g in giornate] == [6, 7, 8, 9, 10, 13, 14]
    assert [g.lavoratori for g in giornate] == [3, 3, 3, 5, 5, 2, 2]
    assert [g.pericolosita for g in giornate] == [4, 4, 4, 9, 9, 9, 9]
    assert analisi.picco_lavoratori(fasi) == 5


def test_prescrizioni(repo):
    a = repo.inserisci("fasi")
    b = repo.inserisci("fasi")
    repo.salva_prescrizione(b, a, "Lavorare in orari diversi")
    assert repo.prescrizioni() == {(a, b): "Lavorare in orari diversi"}
    repo.salva_prescrizione(a, b, "  ")
    assert repo.prescrizioni() == {}


def test_controlli(repo):
    from sicurcantiere import controlli

    messaggi = {s.messaggio for s in controlli.controlla(repo)}
    assert "Manca il committente." in messaggi
    assert "Nessuna fase di lavoro inserita." in messaggi
    repo.inserisci("imprese", ragione_sociale="A")
    repo.inserisci("imprese", ragione_sociale="B")
    errori = [s for s in controlli.controlla(repo) if s.livello == controlli.ERRORE]
    assert any("CSE" in s.messaggio for s in errori)


def _cantiere_completo(repo):
    repo.aggiorna_cantiere(nome="Scuola", indirizzo="Via Roma 1", comune="Bari", provincia="BA",
                           natura_opera="Ristrutturazione", importo_lavori=250000)
    repo.inserisci("soggetti", ruolo="Committente", nome="Comune di Bari")
    repo.inserisci("soggetti", ruolo="Coordinatore per l'esecuzione (CSE)", nome="Ing. Rossi")
    a = repo.inserisci("imprese", ragione_sociale="Alfa Costruzioni", tipo="Affidataria",
                       datore_lavoro="Mario Bianchi", rspp="Luca Verdi")
    repo.inserisci("lavoratori", impresa_id=a, nome="Giuseppe Neri", mansione="Muratore",
                   formazione="Formazione generale e specifica 16 ore")
    f = repo.importa_lavorazione(lav("NC.03"))
    repo.aggiorna("fasi", f, impresa_id=a, data_inizio="2025-10-06", data_fine="2025-10-31", lavoratori=4)
    repo.inserisci("interventi", parte_opera="Copertura", intervento="Pulizia dei canali di gronda",
                   periodicita="Annuale", misure_in_dotazione="Linea vita")
    repo.inserisci("elaborati", titolo="Progetto strutturale", autore="Ing. Blu")
    repo.inserisci("revisioni", documento="PSC", numero=1, data="2025-09-01", descrizione="Prima emissione")
    return a


def _testo_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs] +
                     [c.text for t in doc.tables for r in t.rows for c in r.cells])


def test_genera_pos(repo, tmp_path):
    from sicurcantiere.documenti.pos import chiave_testo, genera_pos

    a = _cantiere_completo(repo)
    repo.salva_testo(chiave_testo(a, "rumore"), "Esposizione inferiore a 80 dB(A).")
    testo = _testo_docx(genera_pos(repo, a, tmp_path / "pos.docx"))
    assert "PIANO OPERATIVO DI SICUREZZA" in testo
    assert "Mario Bianchi" in testo and "Giuseppe Neri" in testo
    assert "Gru a torre" in testo
    assert "80 dB(A)" in testo
    assert "Otoprotettori" in testo  # DPI raccolti dalle schede


def test_genera_fascicolo_e_notifica(repo, tmp_path):
    from sicurcantiere.documenti.fascicolo import genera_fascicolo
    from sicurcantiere.documenti.notifica import genera_notifica

    _cantiere_completo(repo)
    testo = _testo_docx(genera_fascicolo(repo, tmp_path / "f.docx"))
    assert "Pulizia dei canali di gronda" in testo and "Linea vita" in testo
    assert "Progetto strutturale" in testo
    testo = _testo_docx(genera_notifica(repo, tmp_path / "n.docx"))
    assert "Comune di Bari" in testo and "Ing. Rossi" in testo
    assert "06/10/2025" in testo and "20 giorni lavorativi" in testo


def test_revisioni_nel_frontespizio(repo, tmp_path):
    _cantiere_completo(repo)
    assert "Prima emissione" in _testo_docx(genera_psc(repo, tmp_path / "p.docx"))


def test_elenco_dpi():
    from sicurcantiere.documenti.pos import elenco_dpi

    assert elenco_dpi(["Casco, guanti", "casco; otoprotettori.", ""]) == ["Casco", "Guanti", "Otoprotettori"]
