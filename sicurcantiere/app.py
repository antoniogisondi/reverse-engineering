"""Avvio dell'applicazione e gestione degli errori imprevisti."""

from __future__ import annotations

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QEvent, QLibraryInfo, QLocale, QSettings, QStandardPaths, QTranslator
from PySide6.QtWidgets import QApplication, QMessageBox

from sicurcantiere import __version__

log = logging.getLogger("sicurcantiere")


def _configura_log() -> Path:
    cartella = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation))
    cartella.mkdir(parents=True, exist_ok=True)
    file = cartella / "sicurcantiere.log"
    gestore = RotatingFileHandler(file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    gestore.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    log.addHandler(gestore)
    log.setLevel(logging.INFO)
    return file


def _gestore_eccezioni(file_log: Path):
    def gestisci(tipo, valore, tb):
        log.error("Errore non gestito:\n%s", "".join(traceback.format_exception(tipo, valore, tb)))
        # I dati sono già salvati a ogni modifica: l'utente può continuare.
        QMessageBox.critical(
            None, "Errore imprevisto",
            f"Si è verificato un errore:\n{valore}\n\n"
            f"I dati inseriti sono già stati salvati. I dettagli sono nel file:\n{file_log}",
        )
    return gestisci


def traduci_in_italiano(app: QApplication) -> bool:
    """Pulsanti e menu standard di Qt in italiano (Sì/No/Annulla/Salva, Copia/Incolla...)."""
    cartella = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    caricate = False
    for nome in ("qtbase_it", "qt_it"):
        traduttore = QTranslator(app)
        if traduttore.load(nome, cartella):
            app.installTranslator(traduttore)
            caricate = True
    return caricate


def main(argv: list[str] | None = None, edizione: str | None = None) -> int:
    """Avvia un programma della famiglia: psc (predefinito), pos o pimus.

    Da riga di comando: python -m sicurcantiere [psc|pos|pimus] [file]
    """
    argv = list(sys.argv if argv is None else argv)
    if edizione is None:
        if len(argv) > 1 and argv[1].lower() in ("psc", "pos", "pimus"):
            edizione = argv.pop(1).lower()
        else:
            edizione = "psc"
    app = QApplication(argv)
    app.setOrganizationName("SicurCantiere")
    app.setApplicationVersion(__version__)
    QLocale.setDefault(QLocale(QLocale.Language.Italian, QLocale.Country.Italy))
    traduci_in_italiano(app)

    from sicurcantiere.ui import tema

    from sicurcantiere.ui.edizioni import EDIZIONI

    scelta = EDIZIONI[edizione]
    # Nome distinto per programma: file recenti e finestre restano separati.
    app.setApplicationName(scelta.nome)
    app.setApplicationDisplayName(scelta.nome)
    tema.applica(app, QSettings().value("tema_scuro", False, type=bool), edizione)

    if "--autoverifica" in argv:
        # Prova del programma installato: niente finestra, esito su file e nel codice di uscita.
        from sicurcantiere import autoverifica

        i = argv.index("--autoverifica")
        return autoverifica.esegui(argv[i + 1] if i + 1 < len(argv) else ".", edizione)

    file_log = _configura_log()
    sys.excepthook = _gestore_eccezioni(file_log)
    log.info("Avvio %s %s", scelta.nome, __version__)

    from sicurcantiere.ui.finestra import FinestraPrincipale

    finestra = FinestraPrincipale(scelta)
    finestra.show()
    from PySide6.QtCore import QTimer

    from sicurcantiere.ui import aggiornamenti

    # Controllo delle nuove versioni poco dopo l'avvio, in background (al massimo una volta al giorno).
    QTimer.singleShot(4000, lambda: aggiornamenti.controlla(finestra))
    if len(argv) > 1:
        finestra.apri_file(argv[1])
    codice = app.exec()
    # Distruzione esplicita prima della chiusura dell'interprete, per evitare
    # che Python liberi i widget dopo l'applicazione Qt.
    finestra.deleteLater()
    app.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    return codice


def main_psc() -> int:
    return main(edizione="psc")


def main_pos() -> int:
    return main(edizione="pos")


def main_pimus() -> int:
    return main(edizione="pimus")
