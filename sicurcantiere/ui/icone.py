"""Icone vettoriali dell'applicazione (disegnate per SicurCantiere).

Ogni icona è un frammento SVG su griglia 24x24 a tratto; il colore viene
applicato al momento della creazione, così le stesse icone funzionano con
il tema chiaro e con quello scuro.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

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
    # beuta da laboratorio
    "sostanze": '<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2h12.4a1.5 1.5 0 0 0 1.3-2L14 9V3"/>'
                '<path d="M7 15h10"/>',
    # ponteggio: montanti, traversi e diagonali
    "ponteggi": '<path d="M5 3v18M12 3v18M19 3v18M5 8h14M5 14h14M5 20h14M5 8l7 6M12 8l7 6"/>',
    # stelline dell'assistente AI
    "ai": '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/>'
          '<path d="M18 15l.9 2.1L21 18l-2.1.9L18 21l-.9-2.1L15 18l2.1-.9z"/>',
    "nuovo": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M12.5 11v6M9.5 14h6"/>',
    "apri": '<path d="M3 19V5h6l2 2h8v3"/><path d="M3 19l3-9h16l-3 9z"/>',
    "salva": '<path d="M5 3h11l3 3v15H5z"/><path d="M8 3v5h7V3M8 21v-7h8v7"/>',
    # dischetto con matita: salva con nome
    "salva_con_nome": '<path d="M12 21H4V3h10l3 3v4"/><path d="M7 3v5h6V3"/>'
                      '<path d="M14 21l1-3 5-5 2 2-5 5z"/>',
    # documento con spunta
    "psc": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 14l2.5 2.5L16 12"/>',
    "controlli": '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    "tema": '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5h.01"/>',
    "errore": '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5M12 16.5h.01"/>',
    "avviso": '<path d="M12 3.5 21.5 20h-19z"/><path d="M12 10v4.5M12 17.5h.01"/>',
    "annulla": '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
    "ripeti": '<path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0 0 11H13"/>',
    "cerca": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    "anteprima": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "modello": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>'
               '<rect x="3" y="14" width="7" height="7" rx="1"/><path d="M17.5 14v7M14 17.5h7"/>',
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


def immagine_applicazione(lato: int = 256, colore: str = "#E8792B") -> QPixmap:
    """Icona del programma: gru bianca su quadrato colorato arrotondato."""
    pixmap = QPixmap(lato, lato)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(colore))
    p.drawRoundedRect(QRectF(0, 0, lato, lato), lato * 0.22, lato * 0.22)
    margine = lato * 0.16
    renderer = QSvgRenderer(QByteArray(svg("cantiere", "#FFFFFF")))
    renderer.render(p, QRectF(margine, margine, lato - 2 * margine, lato - 2 * margine))
    p.end()
    return pixmap


# Logo di SicurCantiere (casco e ingranaggio), uguale per tutti i programmi della suite.
FILE_LOGO = Path(__file__).resolve().parent.parent / "risorse" / "logo" / "sicurcantiere.ico"


def icona_applicazione(colore: str = "#E8792B", chiave: str = "") -> QIcon:
    """Icona delle finestre: il logo con la sigla del programma (PSC, POS, PiMUS), oppure il logo della
    suite; senza i file, l'icona disegnata nel colore del programma."""
    for file in ((FILE_LOGO.with_name(f"sicurcantiere-{chiave}.ico"),) if chiave else ()) + (FILE_LOGO,):
        if not file.is_file():
            continue
        logo = QIcon(str(file))
        if not logo.isNull():
            return logo
    icona_app = QIcon()
    for lato in (16, 24, 32, 48, 64, 128, 256):
        icona_app.addPixmap(immagine_applicazione(lato, colore))
    return icona_app
