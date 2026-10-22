"""Organigramma del cantiere come immagine per il PSC.

In alto il committente; sotto, su tre colonne collegate, i soggetti del committente (responsabile dei lavori,
progettisti, direzione lavori...), i coordinatori per la sicurezza e le imprese, con le subappaltatrici e i
lavoratori autonomi sotto l'impresa affidataria da cui dipendono.
"""

from __future__ import annotations

from typing import Any

from sicurcantiere import anagrafiche
from sicurcantiere.documenti.immagini import applicazione, png

DPI = 200
LARGHEZZA_CM = 17.4


def _px(cm: float) -> float:
    return cm / 2.54 * DPI


def immagine(soggetti: list[dict[str, Any]], imprese: list[dict[str, Any]], accento: str = "#A44C0C",
             tinta: str = "#FDEEE2") -> bytes | None:
    """PNG dell'organigramma; None se non c'è nessun soggetto né impresa."""
    soggetti = [s for s in soggetti if s["nome"].strip()]
    imprese = [i for i in imprese if i["ragione_sociale"].strip()]
    if not soggetti and not imprese:
        return None
    applicazione()
    from PySide6.QtCore import QPointF, QRectF, Qt
    from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen

    committenti = [s for s in soggetti if s["ruolo"] == anagrafiche.COMMITTENTE]
    coordinatori = [s for s in soggetti if s["ruolo"] in (anagrafiche.CSP, anagrafiche.CSE)]
    altri = [s for s in soggetti if s not in committenti and s not in coordinatori]
    ids = {i["id"] for i in imprese}
    principali = [i for i in imprese if not i.get("affidataria_id") or i["affidataria_id"] not in ids]
    colonna_imprese: list[tuple[dict[str, Any], int]] = []
    for i in principali:
        colonna_imprese.append((i, 0))
        colonna_imprese += [(s, 1) for s in imprese if s.get("affidataria_id") == i["id"]]

    colonne = [("Soggetti del committente", [(s["ruolo"], s["nome"], 0) for s in altri]),
               ("Coordinamento della sicurezza", [(s["ruolo"].replace(" (CSP)", "").replace(" (CSE)", ""),
                                                   s["nome"], 0) for s in coordinatori]),
               ("Imprese e lavoratori autonomi", [(i.get("tipo") or "Impresa", i["ragione_sociale"], livello)
                                                  for i, livello in colonna_imprese])]
    colonne = [c for c in colonne if c[1]] or [("Soggetti", [])]

    larghezza = round(_px(LARGHEZZA_CM))
    margine, scatola_h, spazio = _px(0.3), _px(1.15), _px(0.28)
    alto_radice = _px(1.35)
    righe = max(len(v) for _, v in colonne)
    y_colonne = margine + alto_radice + _px(0.9)
    altezza = round(y_colonne + _px(0.8) + max(righe, 1) * (scatola_h + spazio) + margine)

    img = QImage(larghezza, altezza, QImage.Format.Format_ARGB32)
    img.setDotsPerMeterX(round(DPI / 0.0254))
    img.setDotsPerMeterY(round(DPI / 0.0254))
    img.fill(QColor("#FFFFFF"))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    def carattere(punti: float, grassetto: bool = False) -> QFont:
        f = QFont("Ubuntu")
        f.setStyleHint(QFont.StyleHint.SansSerif)
        f.setPixelSize(max(1, round(punti / 72 * DPI)))
        f.setBold(grassetto)
        return f

    colore_accento, colore_tinta = QColor(accento), QColor(tinta)
    inchiostro, testo3, linea = QColor("#17202A"), QColor("#6B7785"), QColor("#B9C3CD")

    def scatola(rett: QRectF, ruolo: str, nome: str, evidenziata: bool = False) -> None:
        p.setPen(QPen(colore_accento if evidenziata else linea, 3 if evidenziata else 2))
        p.setBrush(colore_tinta if evidenziata else QColor("#FFFFFF"))
        p.drawRoundedRect(rett, _px(0.12), _px(0.12))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(colore_accento)
        p.drawRect(QRectF(rett.x(), rett.y() + _px(0.1), _px(0.08), rett.height() - _px(0.2)))
        interno = rett.adjusted(_px(0.25), _px(0.1), -_px(0.15), -_px(0.1))
        p.setFont(carattere(6.3))
        p.setPen(testo3)
        p.drawText(QRectF(interno.x(), interno.y(), interno.width(), interno.height() / 2),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                   p.fontMetrics().elidedText(ruolo, Qt.TextElideMode.ElideRight, int(interno.width())))
        p.setFont(carattere(7.6, True))
        p.setPen(inchiostro)
        p.drawText(QRectF(interno.x(), interno.y() + interno.height() / 2, interno.width(), interno.height() / 2),
                   Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                   p.fontMetrics().elidedText(nome, Qt.TextElideMode.ElideRight, int(interno.width())))

    # radice: il committente
    larghezza_radice = _px(7.5)
    radice = QRectF((larghezza - larghezza_radice) / 2, margine, larghezza_radice, alto_radice)
    scatola(radice, "Committente", ", ".join(s["nome"] for s in committenti) or "da indicare", True)

    n = len(colonne)
    larghezza_colonna = (larghezza - 2 * margine - (n - 1) * _px(0.4)) / n
    y_barra = radice.bottom() + _px(0.45)
    p.setPen(QPen(linea, 3))
    p.drawLine(QPointF(radice.center().x(), radice.bottom()), QPointF(radice.center().x(), y_barra))
    centri = [margine + k * (larghezza_colonna + _px(0.4)) + larghezza_colonna / 2 for k in range(n)]
    if n > 1:
        p.drawLine(QPointF(centri[0], y_barra), QPointF(centri[-1], y_barra))
    for k, (titolo, voci) in enumerate(colonne):
        x = margine + k * (larghezza_colonna + _px(0.4))
        p.setPen(QPen(linea, 3))
        p.drawLine(QPointF(centri[k], y_barra), QPointF(centri[k], y_colonne))
        p.setFont(carattere(6.8, True))
        p.setPen(colore_accento)
        p.drawText(QRectF(x, y_colonne, larghezza_colonna, _px(0.6)), Qt.AlignmentFlag.AlignCenter, titolo.upper())
        y = y_colonne + _px(0.8)
        for ruolo, nome, livello in voci:
            rientro = _px(0.6) * livello
            rett = QRectF(x + rientro, y, larghezza_colonna - rientro, scatola_h)
            if livello:
                p.setPen(QPen(linea, 2))
                p.drawLine(QPointF(x + _px(0.25), y - spazio), QPointF(x + _px(0.25), y + scatola_h / 2))
                p.drawLine(QPointF(x + _px(0.25), y + scatola_h / 2), QPointF(rett.x(), y + scatola_h / 2))
            scatola(rett, ruolo, nome)
            y += scatola_h + spazio
    p.end()
    return png(img)
