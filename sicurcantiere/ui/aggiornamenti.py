"""Controllo degli aggiornamenti all'avvio e installazione della nuova versione con un clic."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, QUrl, Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QProgressDialog, QPushButton, QWidget

from sicurcantiere import __version__, aggiornamenti
from sicurcantiere.ui import licenza as licenza_ui
from sicurcantiere.ui.lavoro_ai import impostazioni_comuni

CHIAVE_ULTIMO_CONTROLLO = "aggiornamenti/ultimo_controllo"
INTERVALLO = 24 * 3600  # controllo automatico al massimo una volta al giorno


class _Segnali(QObject):
    completato = Signal(object)
    fallito = Signal(str)
    avanzamento = Signal(int, int)


class _Lavoro(QRunnable):
    def __init__(self, funzione: Callable[[_Segnali], Any]):
        super().__init__()
        self.funzione = funzione
        self.segnali = _Segnali()
        self.annullato = False

    def run(self) -> None:
        try:
            risultato = self.funzione(self.segnali)
        except aggiornamenti.ErroreAggiornamento as e:
            self.segnali.fallito.emit(str(e))
        except Exception as e:  # noqa: BLE001 - l'errore va mostrato, non deve chiudere il programma
            self.segnali.fallito.emit(f"Errore imprevisto: {e}")
        else:
            self.segnali.completato.emit(risultato)


_in_corso: set[_Lavoro] = set()


def _avvia(lavoro: _Lavoro, completato: Callable[[Any], None], fallito: Callable[[str], None]) -> None:
    _in_corso.add(lavoro)
    lavoro.segnali.completato.connect(lambda r: (_in_corso.discard(lavoro), completato(r)))
    lavoro.segnali.fallito.connect(lambda e: (_in_corso.discard(lavoro), fallito(e)))
    QThreadPool.globalInstance().start(lavoro)


def automatico_attivo() -> bool:
    return os.environ.get("SICURCANTIERE_AGGIORNAMENTI", "1") != "0"


def controlla(finestra, manuale: bool = False) -> None:
    """Controlla se c'è una versione più recente: in automatico in silenzio, a mano con un messaggio."""
    impostazioni = impostazioni_comuni()
    if not manuale:
        ultimo = impostazioni.value(CHIAVE_ULTIMO_CONTROLLO, 0, type=float)
        if not automatico_attivo() or time.time() - ultimo < INTERVALLO:
            return

    def trovata(versione: aggiornamenti.Versione) -> None:
        impostazioni.setValue(CHIAVE_ULTIMO_CONTROLLO, time.time())
        if aggiornamenti.piu_recente(versione.numero):
            stato = licenza_ui.stato_corrente(finestra.edizione.chiave)
            scadenza = stato.licenza.scadenza if stato.scaduta else None
            if not aggiornamenti.inclusa_nella_licenza(versione, scadenza):
                mostra_avviso(finestra, versione, rinnovo=True)
                if manuale:
                    QMessageBox.information(finestra, "Aggiornamenti",
                                            f"È disponibile la versione {versione.numero}, che richiede il rinnovo "
                                            "della licenza (aggiornamenti e assistenza).")
                return
            mostra_avviso(finestra, versione)
            if manuale:
                proponi(finestra, versione)
        elif manuale:
            QMessageBox.information(finestra, "Aggiornamenti",
                                    f"Stai usando l'ultima versione ({__version__}).")

    def errore(testo: str) -> None:
        if manuale:
            QMessageBox.warning(finestra, "Aggiornamenti", testo)

    _avvia(_Lavoro(lambda segnali: aggiornamenti.ultima_versione()), trovata, errore)


def mostra_avviso(finestra, versione: aggiornamenti.Versione, rinnovo: bool = False) -> None:
    """Pulsante nella barra di stato: resta visibile finché il programma è aperto."""
    pulsante = getattr(finestra, "avviso_aggiornamento", None)
    if pulsante is None:
        pulsante = finestra.avviso_aggiornamento = QPushButton()
        pulsante.setFlat(True)
        pulsante.setCursor(Qt.CursorShape.PointingHandCursor)
        pulsante.setStyleSheet("QPushButton { color: #1E7B34; font-weight: 600; border: none; padding: 2px 8px; }")
        finestra.statusBar().addPermanentWidget(pulsante)
    pulsante.versione, pulsante.rinnovo = versione, rinnovo  # l'ultima trovata: il clic propone quella
    if not getattr(pulsante, "collegato", False):
        pulsante.clicked.connect(lambda: finestra.mostra_licenza() if pulsante.rinnovo
                                 else proponi(finestra, pulsante.versione))
        pulsante.collegato = True
    pulsante.setText(f"Versione {versione.numero} disponibile con il rinnovo" if rinnovo
                     else f"Aggiornamento disponibile: versione {versione.numero}")
    pulsante.show()


def proponi(finestra, versione: aggiornamenti.Versione) -> None:
    risposta = QMessageBox.question(
        finestra, "Aggiornamento disponibile",
        f"È disponibile SicurCantiere {versione.numero} (in uso: {__version__}).\n\n"
        "Il programma scarica la nuova versione, si chiude, la installa e si riapre. "
        "I cantieri e l'archivio non vengono modificati; i dati sono già salvati.\n\nVuoi aggiornare ora?")
    if risposta == QMessageBox.StandardButton.Yes:
        scarica_e_installa(finestra, versione)


def scarica_e_installa(finestra, versione: aggiornamenti.Versione) -> None:
    if sys.platform != "win32":
        QDesktopServices.openUrl(QUrl(versione.pagina or versione.url_installatore))
        return
    destinazione = Path(tempfile.gettempdir()) / f"SicurCantiere-{versione.numero}-setup.exe"
    attesa = QProgressDialog("Scaricamento della nuova versione...", "Annulla", 0, 100, finestra)
    attesa.setWindowTitle("Aggiornamento")
    attesa.setWindowModality(Qt.WindowModality.WindowModal)
    attesa.setMinimumDuration(0)
    attesa.setValue(0)

    def lavoro(segnali: _Segnali) -> Path:
        def avanzamento(letti: int, totale: int) -> bool:
            segnali.avanzamento.emit(letti, totale)
            return not lavoro_corrente.annullato
        return aggiornamenti.scarica(versione.url_installatore, destinazione, avanzamento)

    lavoro_corrente = _Lavoro(lavoro)
    lavoro_corrente.segnali.avanzamento.connect(
        lambda letti, totale: attesa.setValue(int(letti * 100 / totale)) if totale else None)
    attesa.canceled.connect(lambda: setattr(lavoro_corrente, "annullato", True))

    def scaricato(file: Path) -> None:
        attesa.close()
        avvia_installatore(file, finestra)

    def errore(testo: str) -> None:
        attesa.close()
        if not lavoro_corrente.annullato:
            QMessageBox.warning(finestra, "Aggiornamento", f"{testo}\n\nPuoi scaricare la nuova versione "
                                f"anche dal browser:\n{versione.url_installatore}")

    _avvia(lavoro_corrente, scaricato, errore)


def comando_installatore(file: Path, edizione: str) -> list[str]:
    """Installazione senza domande, con riavvio del programma che era aperto (vedi installer/*.iss)."""
    return [str(file), "/SILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/CLOSEAPPLICATIONS",
            "/aggiornamento=si", f"/programma={edizione}"]


def avvia_installatore(file: Path, finestra: QWidget) -> None:
    edizione = {"psc": "PSC", "pos": "POS", "pimus": "PiMUS"}.get(finestra.edizione.chiave, "POS")
    comando = comando_installatore(file, edizione)
    try:
        # ShellExecute (os.startfile) gestisce la richiesta dei permessi di amministratore di Windows.
        avvia = getattr(os, "startfile", None)
        if avvia is not None:
            avvia(comando[0], "open", subprocess.list2cmdline(comando[1:]))
        else:
            subprocess.Popen(comando, close_fds=True)
    except OSError as e:
        QMessageBox.warning(finestra, "Aggiornamento", f"Impossibile avviare l'installazione: {e}")
        return
    finestra.close()  # salva e chiude: l'installatore sostituisce i file e riapre il programma
