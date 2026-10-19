"""Icone vettoriali dell'applicazione (disegnate per SicurCantiere).

Ogni icona è un frammento SVG su griglia 24x24 a tratto; il colore viene
applicato al momento della creazione, così le stesse icone funzionano con
il tema chiaro e con quello scuro.
"""

from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_FORME: dict[str, str] = {
    # gru a torre con carico
    "cantiere": '<path d="M4 21h8M7 21V5M7 5h13M7 5l-3 4M7 9l4-4M16 5v5"/><rect x="14" y="10" width="4" height="3"/>',
    # due persone
    "soggetti": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/>'
                '<circle cx="17" cy="9" r="2.5"/><path d="M16 14.2c2.8.3 5 2.6 5 5.8"/>',
    # edificio con elmetto
    "imprese": '<path d="M4 21V9l8-5 8 5v12M4 21h16"/><path d="M9 21v-5h6v5"/><path d="M8 12h2M14 12h2"/>',
    # barre del Gantt
    "fasi": '<path d="M3 4v16h18"/><rect x="6" y="6" width="7" height="3" rx="1"/>'
            '<rect x="10" y="11" width="8" height="3" rx="1"/><rect x="7" y="16" width="5" height="2" rx="1"/>',
    # triangolo di pericolo
    "interferenze": '<path d="M12 3 2 20h20L12 3z"/><path d="M12 10v4M12 17h.01"/>',
    # simbolo dell'euro
    "costi": '<path d="M17 6.5A6.5 6.5 0 1 0 17 17.5"/><path d="M4 10h9M4 14h9"/>',
    # documento con righe
    "relazione": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 11h7M9 14h7M9 17h5"/>',
    # raccoglitore
    "fascicolo": '<path d="M3 6h6l2 2h10v12H3z"/><path d="M3 10h18"/>',
    # stampa
    "documenti": '<path d="M7 8V3h10v5"/><rect x="3" y="8" width="18" height="9" rx="2"/>'
                 '<path d="M7 14h10v7H7z"/>',
    # persona che solleva una cassa
    "valutazioni": '<circle cx="9" cy="4.5" r="2"/><path d="M9 7v6l-3 7M9 13l3 7M9 9l4 2"/>'
                   '<rect x="13" y="9" width="7" height="6" rx="1"/>',
    # ponteggio: montanti, traversi e diagonali
    "ponteggi": '<path d="M5 3v18M12 3v18M19 3v18M5 8h14M5 14h14M5 20h14M5 8l7 6M12 8l7 6"/>',
    # stelline dell'assistente AI
    "ai": '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/>'
          '<path d="M18 15l.9 2.1L21 18l-2.1.9L18 21l-.9-2.1L15 18l2.1-.9z"/>',
    "nuovo": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M12.5 11v6M9.5 14h6"/>',
    "apri": '<path d="M3 19V5h6l2 2h8v3"/><path d="M3 19l3-9h16l-3 9z"/>',
    "salva": '<path d="M5 3h11l3 3v15H5z"/><path d="M8 3v5h7V3M8 21v-7h8v7"/>',
    # documento con spunta
    "psc": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 14l2.5 2.5L16 12"/>',
    "controlli": '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    "tema": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
}

NOMI = tuple(_FORME)


def svg(nome: str, colore: str) -> bytes:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="{colore}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
        f"{_FORME[nome]}</svg>"
    ).encode()


@lru_cache(maxsize=None)
def icona(nome: str, colore: str = "#1F3A5F", lato: int = 48) -> QIcon:
    renderer = QSvgRenderer(QByteArray(svg(nome, colore)))
    pixmap = QPixmap(lato, lato)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(p, QRectF(0, 0, lato, lato))
    p.end()
    return QIcon(pixmap)


def immagine_applicazione(lato: int = 256) -> QPixmap:
    """Icona del programma: gru bianca su quadrato arancio arrotondato."""
    pixmap = QPixmap(lato, lato)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("#E8792B"))
    p.drawRoundedRect(QRectF(0, 0, lato, lato), lato * 0.22, lato * 0.22)
    margine = lato * 0.16
    renderer = QSvgRenderer(QByteArray(svg("cantiere", "#FFFFFF")))
    renderer.render(p, QRectF(margine, margine, lato - 2 * margine, lato - 2 * margine))
    p.end()
    return pixmap


def icona_applicazione() -> QIcon:
    icona_app = QIcon()
    for lato in (16, 24, 32, 48, 64, 128, 256):
        icona_app.addPixmap(immagine_applicazione(lato))
    return icona_app
