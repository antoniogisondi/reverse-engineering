"""Prova di funzionamento del programma installato.

`SicurCantiere POS.exe --autoverifica CARTELLA` crea in CARTELLA un cantiere di prova con una
lavorazione dell'archivio, genera i documenti principali, costruisce la finestra senza
mostrarla e scrive l'esito in CARTELLA/autoverifica.txt (codice di uscita 0 se tutto è andato
bene). Serve a controllare gli eseguibili prodotti da PyInstaller, in cui moduli caricati a
richiesta, immagini e modelli dei documenti potrebbero mancare.
"""

from __future__ import annotations

import traceback
from pathlib import Path


def esegui(cartella: str | Path, edizione: str) -> int:
    cartella = Path(cartella)
    cartella.mkdir(parents=True, exist_ok=True)
    righe: list[str] = []
    try:
        righe += _prove(cartella, edizione)
        righe.append("ESITO: OK")
        codice = 0
    except Exception:  # noqa: BLE001 - l'esito va scritto comunque
        righe.append(traceback.format_exc())
        righe.append("ESITO: ERRORE")
        codice = 1
    (cartella / "autoverifica.txt").write_text("\n".join(righe), encoding="utf-8")
    return codice


def _prove(cartella: Path, edizione: str) -> list[str]:
    from sicurcantiere import __version__, archivio, segnaletica
    from sicurcantiere.db import Progetto
    from sicurcantiere.documenti.pos import genera_pos
    from sicurcantiere.documenti.psc import genera_psc
    from sicurcantiere.repository import Repository
    from sicurcantiere.ui.edizioni import EDIZIONI
    from sicurcantiere.ui.finestra import FinestraPrincipale
    from sicurcantiere.valutazioni import automatiche

    righe = [f"SicurCantiere {__version__} - {EDIZIONI[edizione].nome}"]
    assert len(archivio.LAVORAZIONI) > 200 and len(archivio.ATTREZZATURE) > 100, "archivio incompleto"
    righe.append(f"archivio: {len(archivio.LAVORAZIONI)} fasi, {len(archivio.ATTREZZATURE)} attrezzature")
    mancanti = [s.chiave for s in segnaletica.SEGNALI.values() if not s.file.is_file()]
    assert not mancanti, f"cartelli mancanti: {mancanti}"
    righe.append(f"cartelli: {len(segnaletica.SEGNALI)}")
    from sicurcantiere.ui import tema

    foglio = tema.foglio_di_stile(False, edizione)
    assert len(foglio) > 5000 and "@" not in foglio, "foglio di stile mancante o incompleto"
    tema.carica_caratteri()
    righe.append(f"tema: {len(foglio)} caratteri, carattere {tema._corrente['sans']}")
    righe.append(_prova_licenza())
    from PySide6.QtWidgets import QApplication

    from sicurcantiere.app import traduci_in_italiano

    assert traduci_in_italiano(QApplication.instance()), "traduzioni italiane di Qt mancanti"
    righe.append("pulsanti e menu di Qt in italiano")
    from sicurcantiere import licenza

    # La prova non deve far partire la prova gratuita né fermarsi sui suoi messaggi.
    licenza.CHIAVE_PUBBLICA = ""

    file = cartella / f"prova{EDIZIONI[edizione].estensione}"
    progetto = Progetto(file, crea=True)
    try:
        repo = Repository(progetto)
        repo.aggiorna_cantiere(nome="Cantiere di prova", indirizzo="Via Roma 1", comune="Bari", provincia="BA")
        impresa = repo.inserisci("imprese", ragione_sociale="Impresa di prova", datore_lavoro="Mario Rossi")
        repo.inserisci("lavoratori", impresa_id=impresa, nome="Luigi", cognome="Bianchi", mansione="Muratore")
        fase = repo.importa_lavorazione(archivio.LAVORAZIONI[0])
        repo.aggiorna("fasi", fase, impresa_id=impresa)
        automatiche.sincronizza(repo)
        righe.append(f"valutazioni create: {len(repo.elenco('valutazioni'))}")
        for nome, genera in (("POS", lambda p: genera_pos(repo, impresa, p)), ("PSC", lambda p: genera_psc(repo, p))):
            documento = genera(cartella / f"prova {nome}.docx")
            assert documento.stat().st_size > 10_000, f"{nome} vuoto"
            righe.append(f"{nome}: {documento.stat().st_size} byte")
    finally:
        progetto.chiudi()

    finestra = FinestraPrincipale(EDIZIONI[edizione])
    finestra.apri_file(file)
    assert finestra.pagine, "pagine non create"
    righe.append(f"finestra: {len(finestra.pagine)} pagine")
    finestra.salva()  # senza modifiche in sospeso la chiusura non chiede di salvare (niente finestre in attesa)
    assert not finestra.modifiche_non_salvate(), "modifiche non salvate dopo Salva"
    finestra.close()
    finestra.deleteLater()
    return righe


def _prova_licenza() -> str:
    """Firma e verifica una licenza con una chiave di prova appena creata."""
    import base64
    import os
    from datetime import date

    from sicurcantiere import ed25519, licenza

    segreto = os.urandom(32)
    pubblica = base64.b64encode(ed25519.chiave_pubblica(segreto)).decode()
    prova = licenza.Licenza("PROVA", "Autoverifica", "completo", date.today())
    assert licenza.leggi(licenza.firma(prova, segreto), pubblica) == prova, "verifica della licenza non riuscita"
    return f"licenze: verifica della firma riuscita (controllo {'attivo' if licenza.controllo_attivo() else 'non attivo'})"
