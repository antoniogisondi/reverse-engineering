"""Immagini per i documenti disegnate con Qt: pagine dei PDF allegati, conversione in PNG."""

from __future__ import annotations

import os
from pathlib import Path


def applicazione():
    """Qt serve per disegnare: nel programma c'è già; altrove (prove) se ne crea una senza finestre."""
    from PySide6.QtWidgets import QApplication  # completa: chi viene dopo può aprire anche finestre

    app = QApplication.instance()
    if app is None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        app = QApplication(["sicurcantiere"])
        applicazione.tenuta = app  # resta viva finché serve
    return app


def png(immagine) -> bytes:
    """QImage in PNG."""
    from PySide6.QtCore import QBuffer, QByteArray, QIODevice

    dati = QByteArray()
    buffer = QBuffer(dati)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    immagine.save(buffer, "PNG")
    buffer.close()
    return bytes(dati.data())


def pagine_pdf(percorso: str | Path, dpi: int = 150, massimo: int = 30) -> list[tuple[bytes, bool]]:
    """Pagine di un PDF come PNG, con l'indicazione se la pagina è orizzontale (al massimo `massimo` pagine)."""
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QColor, QImage, QPainter
    from PySide6.QtPdf import QPdfDocument

    applicazione()
    documento = QPdfDocument(None)
    if documento.load(str(percorso)) != QPdfDocument.Error.None_:
        return []
    risultato = []
    for n in range(min(documento.pageCount(), massimo)):
        punti = documento.pagePointSize(n)
        dimensione = QSize(max(1, round(punti.width() / 72 * dpi)), max(1, round(punti.height() / 72 * dpi)))
        pagina = documento.render(n, dimensione)
        fondo = QImage(pagina.size(), QImage.Format.Format_RGB32)
        fondo.fill(QColor("#FFFFFF"))  # le pagine dei PDF hanno lo sfondo trasparente
        pittore = QPainter(fondo)
        pittore.drawImage(0, 0, pagina)
        pittore.end()
        risultato.append((png(fondo), punti.width() > punti.height()))
    documento.close()
    return risultato
