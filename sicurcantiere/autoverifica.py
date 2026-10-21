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
    finestra.show()
    processi: list[str] = []
    finestre_native: list[str] = []
    from sicurcantiere.ui import lavoro_ai

    # come sul computer di chi ha la licenza: con l'assistente acceso compaiono i suoi pulsanti
    ai_attiva, lavoro_ai.ai_attiva = lavoro_ai.ai_attiva, lambda: True
    try:
        with _registra_processi(processi), _registra_finestre_native(finestra, finestre_native):
            lampi = _finestre_comparse(finestra, lambda: _apri_e_sfoglia(finestra, file))
    finally:
        lavoro_ai.ai_attiva = ai_attiva
    righe.append(f"processi avviati all'apertura: {len(processi)}")
    righe.extend(f"  {p}" for p in processi)
    righe.append(f"finestre di sistema comparse all'apertura: {len(finestre_native)}")
    righe.extend(f"  {f}" for f in finestre_native)
    import os

    # falliscono la prova i processi avviati e le finestre di questo programma; le altre (di altri
    # programmi del computer) si riportano soltanto
    lampi += processi + [f for f in finestre_native if f.startswith(f"pid {os.getpid()} ")]
    assert finestra.pagine, "pagine non create"
    righe.append(f"finestra: {len(finestra.pagine)} pagine")
    # Elementi che compaiono per un istante come finestre a sé (icone che lampeggiano nella barra
    # delle applicazioni di Windows): non devono essercene.
    assert not lampi, "finestre lampo all'apertura del cantiere: " + "; ".join(lampi)
    righe.append("apertura del cantiere senza finestre lampo")
    finestra.salva()  # senza modifiche in sospeso la chiusura non chiede di salvare (niente finestre in attesa)
    assert not finestra.modifiche_non_salvate(), "modifiche non salvate dopo Salva"
    finestra.close()
    finestra.deleteLater()
    return righe


class _registra_processi:
    """Registra i processi avviati (con il punto del codice che li avvia): su Windows ognuno fa
    lampeggiare un'icona nella barra delle applicazioni."""

    def __init__(self, elenco: list[str]):
        self.elenco = elenco
        self.originali: list[tuple[object, str, object]] = []

    def __enter__(self):
        import os
        import subprocess

        def spia(oggetto, nome):
            originale = getattr(oggetto, nome, None)
            if originale is None:
                return

            def registrata(*a, **k):
                pila = "".join(traceback.format_stack(limit=12)[:-1])
                self.elenco.append(f"{nome}{a[:2]!r}\n{pila}")
                return originale(*a, **k)

            setattr(oggetto, nome, registrata)
            self.originali.append((oggetto, nome, originale))

        try:
            import _winapi

            spia(_winapi, "CreateProcess")
        except ImportError:
            spia(subprocess, "Popen")
        for nome in ("system", "startfile", "spawnv", "spawnl", "execv"):
            spia(os, nome)
        return self

    def __exit__(self, *_):
        for oggetto, nome, originale in self.originali:
            setattr(oggetto, nome, originale)
        return False


class _registra_finestre_native:
    """Su Windows: finestre visibili comparse durante l'apertura, anche per un istante e anche non di
    Qt. Un thread separato le cerca ogni pochi millesimi di secondo (Python passa da un thread
    all'altro anche mentre il programma è occupato), poi si risale all'elemento di Qt che le ha create."""

    def __init__(self, principale, elenco: list[str]):
        self.principale, self.elenco = principale, elenco
        self.trovate: dict[int, str] = {}
        self.attivo = False
        self.filo = None

    @staticmethod
    def _visibili() -> dict[int, str]:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        trovate: dict[int, str] = {}

        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def una(hwnd, _):
            if user32.IsWindowVisible(hwnd):
                titolo = ctypes.create_unicode_buffer(256)
                classe = ctypes.create_unicode_buffer(256)
                user32.GetWindowTextW(hwnd, titolo, 256)
                user32.GetClassNameW(hwnd, classe, 256)
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                r = wintypes.RECT()
                user32.GetWindowRect(hwnd, ctypes.byref(r))
                trovate[int(hwnd)] = (f"pid {pid.value} classe {classe.value!r} titolo {titolo.value!r} "
                                      f"posizione {r.left},{r.top} dimensioni {r.right - r.left}x{r.bottom - r.top}")
            return True

        user32.EnumWindows(una, 0)
        return trovate

    def _cerca(self) -> None:
        import time

        while self.attivo:
            for hwnd, descrizione in self._visibili().items():
                if hwnd not in self.iniziali and hwnd != self.principale_hwnd:
                    self.trovate.setdefault(hwnd, descrizione)
            time.sleep(0.002)

    def __enter__(self):
        import sys
        import threading

        if sys.platform != "win32":
            return self
        self.principale_hwnd = int(self.principale.winId())
        self.iniziali = set(self._visibili())
        self.attivo = True
        self.filo = threading.Thread(target=self._cerca, daemon=True)
        self.filo.start()
        return self

    def __exit__(self, *_):
        if self.filo is None:
            return False
        self.attivo = False
        self.filo.join(2)
        from PySide6.QtWidgets import QApplication

        # di quale elemento di Qt è la finestra (se esiste ancora)
        per_hwnd = {}
        for w in QApplication.allWidgets():
            try:
                if w.internalWinId():
                    per_hwnd[int(w.internalWinId())] = w
            except RuntimeError:
                continue
        for hwnd, descrizione in self.trovate.items():
            w = per_hwnd.get(hwnd)
            if w is not None:
                catena, x = [], w
                while x is not None and len(catena) < 6:
                    catena.append(f"{type(x).__name__}({x.objectName()!r})")
                    x = x.parentWidget()
                descrizione += " widget " + " < ".join(catena)
            self.elenco.append(descrizione)
        return False


def _apri_e_sfoglia(finestra, file: Path) -> None:
    """Apre il cantiere e passa per tutte le pagine, lasciando lavorare la finestra."""
    from PySide6.QtCore import QEventLoop, QTimer

    def attendi(ms: int) -> None:
        ciclo = QEventLoop()
        QTimer.singleShot(ms, ciclo.quit)
        ciclo.exec()

    finestra.apri_file(file)
    attendi(1500)
    for i in range(len(finestra.pagine)):
        finestra.navigazione.setCurrentRow(i)
        attendi(300)
    finestra.salva()
    finestra.apri_file(file)  # riapertura con un cantiere già aperto (cantieri recenti, Apri...)
    attendi(1500)


def _finestre_comparse(principale, azione) -> list[str]:
    """Finestre (di Qt) diverse da quella principale mostrate durante l'azione."""
    from PySide6.QtCore import QEvent, QObject
    from PySide6.QtWidgets import QApplication

    trovate: list[str] = []

    class Spia(QObject):
        def eventFilter(self, oggetto, evento):
            if evento.type() == QEvent.Type.Show:
                if oggetto.isWidgetType() and oggetto.isWindow() and oggetto is not principale:
                    trovate.append(f"{type(oggetto).__name__} {oggetto.objectName()!r} "
                                   f"{getattr(oggetto, 'text', lambda: '')()!r}"[:120])
                elif oggetto.isWindowType() and oggetto is not principale.windowHandle():
                    trovate.append(f"QWindow {oggetto.objectName()!r}")
            return False

    spia = Spia()
    app = QApplication.instance()
    app.installEventFilter(spia)
    try:
        azione()
    finally:
        app.removeEventFilter(spia)
    return trovate


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
