"""Anteprima dei documenti nel programma: il documento Word viene convertito in PDF (con Word o
LibreOffice) e mostrato pagina per pagina, con il salvataggio del PDF."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from sicurcantiere.documenti import pdf


class DialogoAnteprima(QDialog):
    def __init__(self, contenuto_pdf: bytes, titolo: str, nome_file: str, apri_word: Callable[[], None] | None = None,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(f"Anteprima · {titolo}")
        self.resize(980, 860)
        self.nome_file = nome_file
        self._cartella = tempfile.TemporaryDirectory()
        self.percorso = Path(self._cartella.name) / f"{nome_file}.pdf"
        self.percorso.write_bytes(contenuto_pdf)
        self.documento = QPdfDocument(self)
        self.documento.load(str(self.percorso))
        self.vista = QPdfView(self)
        self.vista.setDocument(self.documento)
        self.vista.setPageMode(QPdfView.PageMode.MultiPage)
        self.vista.setZoomMode(QPdfView.ZoomMode.FitToWidth)

        pagine = QLabel(f"{self.documento.pageCount()} pagine", self)
        pagine.setObjectName("hint")
        piu = QPushButton("Ingrandisci", self)
        meno = QPushButton("Riduci", self)
        adatta = QPushButton("Adatta alla larghezza", self)
        piu.clicked.connect(lambda: self._zoom(1.2))
        meno.clicked.connect(lambda: self._zoom(1 / 1.2))
        adatta.clicked.connect(lambda: self.vista.setZoomMode(QPdfView.ZoomMode.FitToWidth))
        salva = QPushButton("Salva il PDF...", self)
        salva.clicked.connect(self._salva)
        barra = QHBoxLayout()
        barra.addWidget(pagine)
        barra.addStretch()
        for pulsante in (meno, piu, adatta):
            barra.addWidget(pulsante)
        barra.addSpacing(16)
        if apri_word is not None:
            word = QPushButton("Apri in Word", self)
            word.clicked.connect(apri_word)
            barra.addWidget(word)
        barra.addWidget(salva)
        layout = QVBoxLayout(self)
        layout.addLayout(barra)
        layout.addWidget(self.vista, 1)

    def _zoom(self, fattore: float) -> None:
        self.vista.setZoomMode(QPdfView.ZoomMode.Custom)
        self.vista.setZoomFactor(max(0.2, min(5.0, self.vista.zoomFactor() * fattore)))

    def _salva(self) -> None:
        percorso, _ = QFileDialog.getSaveFileName(self, "Salva il PDF", f"{self.nome_file}.pdf", "PDF (*.pdf)")
        if not percorso:
            return
        try:
            Path(percorso).write_bytes(self.percorso.read_bytes())
        except OSError as e:
            QMessageBox.warning(self, "Salva il PDF", f"Impossibile salvare il file:\n{e}")
            return
        if QMessageBox.question(self, "Salva il PDF", f"Salvato {Path(percorso).name}. Aprirlo ora?") \
                == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(percorso))

    def done(self, risultato: int) -> None:
        self.documento.close()
        super().done(risultato)


def mostra(parent: QWidget, contenuto_docx: bytes, titolo: str, nome_file: str,
           apri_word: Callable[[], None] | None = None) -> None:
    """Converte in PDF (in sottofondo, con l'attesa) e mostra l'anteprima; senza Word né LibreOffice lo dice."""
    from sicurcantiere.ui.importa_psc import in_background

    if not pdf.disponibile():
        QMessageBox.information(parent, "Anteprima", "Per l'anteprima e il PDF serve Microsoft Word oppure LibreOffice "
                                                     "installato su questo computer.")
        return

    def converti(_avanzamento):
        return pdf.converti_dati(contenuto_docx, "documento")

    def fatto(contenuto_pdf: bytes) -> None:
        DialogoAnteprima(contenuto_pdf, titolo, nome_file, apri_word, parent).exec()

    in_background(parent, "Anteprima", "Preparazione dell'anteprima (conversione in PDF)...", converti, fatto)
