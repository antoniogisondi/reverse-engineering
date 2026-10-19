"""Avvio dell'applicazione e gestione degli errori imprevisti."""

from __future__ import annotations

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

from PySide6.QtCore import QLocale, QStandardPaths
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
            f"I dati inseriti sono già salvati. Dettagli nel file:\n{file_log}",
        )
    return gestisci


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv if argv is None else argv
    app = QApplication(argv)
    app.setOrganizationName("SicurCantiere")
    app.setApplicationName("SicurCantiere")
    app.setApplicationVersion(__version__)
    QLocale.setDefault(QLocale(QLocale.Language.Italian, QLocale.Country.Italy))
    app.setStyle("Fusion")

    file_log = _configura_log()
    sys.excepthook = _gestore_eccezioni(file_log)
    log.info("Avvio SicurCantiere %s", __version__)

    from sicurcantiere.ui.finestra import FinestraPrincipale

    finestra = FinestraPrincipale()
    finestra.show()
    if len(argv) > 1:
        finestra.apri_file(argv[1])
    return app.exec()
