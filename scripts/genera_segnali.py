"""Disegna i cartelli di sicurezza e le icone dei DPI usati nei documenti (sicurcantiere/risorse/segnali).

Pittogrammi disegnati per SicurCantiere con forme semplici, nei colori e nelle forme della
segnaletica di sicurezza. Uso: python scripts/genera_segnali.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QBrush, QColor, QGuiApplication, QImage, QPainter, QPainterPath, QPen, QPolygonF  # noqa: E402

from sicurcantiere.segnaletica import (  # noqa: E402
    ANTINCENDIO,
    AVVERTIMENTO,
    CARTELLA,
    DIVIETO,
    OBBLIGO,
    SEGNALI,
    SOCCORSO,
)

LATO = 320
BLU, ROSSO, GIALLO, VERDE = QColor("#1F5FA6"), QColor("#C8102E"), QColor("#F6B40E"), QColor("#00875A")
NERO, BIANCO = QColor("#111111"), QColor("#FFFFFF")


def _poligono(*punti: tuple[float, float]) -> QPolygonF:
    return QPolygonF([QPointF(x, y) for x, y in punti])


# --- pittogrammi, disegnati in una griglia 100 x 100 ---

def p_casco(p: QPainter) -> None:
    calotta = QPainterPath()
    calotta.moveTo(16, 70)
    calotta.cubicTo(14, 22, 86, 22, 84, 70)
    calotta.closeSubpath()
    p.drawPath(calotta)
    p.drawRoundedRect(QRectF(6, 66, 88, 12), 6, 6)  # tesa
    p.save()
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
    p.drawRect(QRectF(30, 40, 4, 26))  # nervature della calotta
    p.drawRect(QRectF(66, 40, 4, 26))
    p.restore()


def p_guanti(p: QPainter) -> None:
    p.drawRoundedRect(QRectF(30, 44, 40, 42), 8, 8)  # palmo
    for i, (x, h) in enumerate(((31, 30), (41, 36), (51, 34), (61, 28))):
        p.drawRoundedRect(QRectF(x, 46 - h, 8.5, h + 6), 4.2, 4.2)
    pollice = QPainterPath()
    pollice.addRoundedRect(QRectF(16, 52, 22, 9), 4.5, 4.5)
    p.save()
    p.translate(27, 56)
    p.rotate(-35)
    p.translate(-27, -56)
    p.drawPath(pollice)
    p.restore()
    p.drawRect(QRectF(32, 86, 36, 8))  # polsino


def p_calzature(p: QPainter) -> None:
    scarpa = QPainterPath()
    scarpa.moveTo(30, 18)
    scarpa.lineTo(52, 18)
    scarpa.lineTo(54, 56)
    scarpa.cubicTo(70, 58, 88, 62, 88, 74)
    scarpa.lineTo(88, 80)
    scarpa.lineTo(24, 80)
    scarpa.lineTo(24, 40)
    scarpa.closeSubpath()
    p.drawPath(scarpa)
    p.drawRect(QRectF(22, 82, 68, 7))  # suola


def p_udito(p: QPainter) -> None:
    p.save()
    pen = QPen(p.brush().color(), 7)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    archetto = QPainterPath()
    archetto.moveTo(24, 52)
    archetto.cubicTo(24, 10, 76, 10, 76, 52)
    p.drawPath(archetto)
    p.restore()
    p.drawRoundedRect(QRectF(12, 46, 22, 34), 10, 10)
    p.drawRoundedRect(QRectF(66, 46, 22, 34), 10, 10)


def p_occhiali(p: QPainter) -> None:
    p.drawRoundedRect(QRectF(10, 38, 36, 26), 10, 10)
    p.drawRoundedRect(QRectF(54, 38, 36, 26), 10, 10)
    p.drawRect(QRectF(44, 44, 12, 6))
    p.drawRect(QRectF(4, 42, 8, 5))
    p.drawRect(QRectF(88, 42, 8, 5))


def p_visiera(p: QPainter) -> None:
    p.drawEllipse(QRectF(32, 20, 36, 44))  # testa
    p.drawRect(QRectF(42, 60, 16, 10))  # collo
    p.drawRoundedRect(QRectF(20, 70, 60, 26), 10, 10)  # spalle
    p.drawRoundedRect(QRectF(22, 10, 56, 9), 4, 4)  # fascia di sostegno
    p.save()
    p.setOpacity(0.5)
    p.drawPolygon(_poligono((22, 19), (78, 19), (84, 66), (16, 66)))  # schermo trasparente
    p.restore()


def p_maschera(p: QPainter) -> None:
    p.drawEllipse(QRectF(28, 10, 44, 52))  # testa
    p.drawRoundedRect(QRectF(22, 70, 56, 22), 8, 8)
    p.drawRect(QRectF(40, 60, 20, 12))
    p.save()
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
    p.drawRoundedRect(QRectF(33, 37, 34, 24), 10, 10)  # stacco attorno al facciale
    p.restore()
    p.drawRoundedRect(QRectF(37, 41, 26, 16), 7, 7)  # facciale filtrante
    p.drawRect(QRectF(20, 44, 16, 4))  # elastici
    p.drawRect(QRectF(64, 44, 16, 4))


def p_persona(p: QPainter, x: float = 50, y: float = 10, s: float = 1.0) -> None:
    p.drawEllipse(QRectF(x - 8 * s, y, 16 * s, 16 * s))
    p.drawRoundedRect(QRectF(x - 11 * s, y + 18 * s, 22 * s, 32 * s), 6 * s, 6 * s)
    p.drawRoundedRect(QRectF(x - 11 * s, y + 46 * s, 9 * s, 34 * s), 4 * s, 4 * s)
    p.drawRoundedRect(QRectF(x + 2 * s, y + 46 * s, 9 * s, 34 * s), 4 * s, 4 * s)


def p_imbracatura(p: QPainter) -> None:
    p_persona(p)
    p.save()
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
    pen = QPen(QColor(0, 0, 0), 4)
    p.setPen(pen)
    p.drawLine(QPointF(40, 30), QPointF(60, 58))
    p.drawLine(QPointF(60, 30), QPointF(40, 58))
    p.drawLine(QPointF(38, 56), QPointF(62, 56))
    p.restore()
    p.save()
    p.setPen(QPen(p.brush().color(), 4))
    p.drawLine(QPointF(60, 30), QPointF(78, 8))  # cordino
    p.restore()
    p.drawEllipse(QRectF(74, 4, 8, 8))


def p_altavisibilita(p: QPainter) -> None:
    gilet = QPainterPath()
    gilet.moveTo(30, 14)
    gilet.lineTo(42, 14)
    gilet.lineTo(50, 34)
    gilet.lineTo(58, 14)
    gilet.lineTo(70, 14)
    gilet.lineTo(84, 30)
    gilet.lineTo(78, 90)
    gilet.lineTo(22, 90)
    gilet.lineTo(16, 30)
    gilet.closeSubpath()
    p.drawPath(gilet)
    p.save()
    p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
    p.drawRect(QRectF(16, 56, 70, 5))
    p.drawRect(QRectF(16, 72, 70, 5))
    p.restore()


def p_indumenti(p: QPainter) -> None:
    tuta = QPainterPath()
    tuta.moveTo(36, 10)
    tuta.lineTo(64, 10)
    tuta.lineTo(86, 26)
    tuta.lineTo(80, 40)
    tuta.lineTo(68, 32)
    tuta.lineTo(68, 92)
    tuta.lineTo(53, 92)
    tuta.lineTo(50, 62)
    tuta.lineTo(47, 92)
    tuta.lineTo(32, 92)
    tuta.lineTo(32, 32)
    tuta.lineTo(20, 40)
    tuta.lineTo(14, 26)
    tuta.closeSubpath()
    p.drawPath(tuta)


def p_camminatore(p: QPainter) -> None:
    p.drawEllipse(QRectF(46, 6, 16, 16))
    p.drawPolygon(_poligono((44, 24), (60, 24), (62, 54), (46, 54)))
    p.drawPolygon(_poligono((46, 52), (56, 54), (44, 92), (34, 90)))  # gamba avanti
    p.drawPolygon(_poligono((52, 52), (62, 52), (72, 90), (62, 92)))  # gamba dietro
    p.drawPolygon(_poligono((44, 26), (50, 30), (36, 52), (30, 48)))  # braccio
    p.drawPolygon(_poligono((56, 26), (62, 30), (74, 48), (68, 52)))


def p_gancio_carico(p: QPainter, sotto_persona: bool = False) -> None:
    p.drawRect(QRectF(46, 0, 8, 14))  # fune
    p.drawEllipse(QRectF(42, 12, 16, 16))  # gancio
    p.drawPolygon(_poligono((50, 26), (26, 48), (74, 48)))  # brache
    altezza = 18 if sotto_persona else 34
    p.drawRect(QRectF(20, 48, 60, altezza))  # carico
    if sotto_persona:
        p_persona(p, 50, 68, 0.4)


def p_fiamma(p: QPainter) -> None:
    fiamma = QPainterPath()
    fiamma.moveTo(50, 8)
    fiamma.cubicTo(70, 32, 82, 48, 76, 70)
    fiamma.cubicTo(72, 86, 60, 92, 50, 92)
    fiamma.cubicTo(36, 92, 24, 82, 24, 66)
    fiamma.cubicTo(24, 50, 38, 44, 40, 28)
    fiamma.cubicTo(46, 38, 50, 44, 54, 48)
    fiamma.cubicTo(56, 36, 54, 22, 50, 8)
    p.drawPath(fiamma)


def p_esclamativo(p: QPainter) -> None:
    p.drawPolygon(_poligono((43, 22), (57, 22), (54, 70), (46, 70)))
    p.drawEllipse(QRectF(43, 76, 14, 14))


def p_fulmine(p: QPainter) -> None:
    p.drawPolygon(_poligono((56, 6), (30, 56), (48, 56), (38, 94), (72, 40), (54, 40), (66, 6)))


def p_caduta(p: QPainter) -> None:
    p.drawPolygon(_poligono((0, 30), (44, 30), (44, 100), (36, 100), (36, 38), (0, 38)))  # bordo e parete
    p.save()
    p.translate(70, 58)
    p.rotate(-35)
    p.translate(-50, -50)
    p_persona(p, 50, 6, 1.0)
    p.restore()


def p_mezzi(p: QPainter) -> None:
    p.drawRect(QRectF(8, 44, 60, 28))  # cassone
    p.drawPolygon(_poligono((68, 50), (84, 50), (94, 62), (94, 72), (68, 72)))  # cabina
    p.drawEllipse(QRectF(16, 66, 18, 18))
    p.drawEllipse(QRectF(70, 66, 18, 18))
    p_persona(p, 40, 4, 0.42)


def p_scavo(p: QPainter) -> None:
    p.drawPolygon(_poligono((2, 52), (36, 52), (40, 92), (60, 92), (64, 52), (98, 52), (98, 96), (2, 96)))
    p.save()
    p.translate(50, 54)
    p.rotate(20)
    p.translate(-50, -30)
    p_persona(p, 50, 6, 0.55)
    p.restore()


def p_croce(p: QPainter) -> None:
    p.drawRect(QRectF(38, 14, 24, 72))
    p.drawRect(QRectF(14, 38, 72, 24))


def p_estintore(p: QPainter) -> None:
    p.drawRoundedRect(QRectF(36, 30, 28, 62), 10, 10)
    p.drawRect(QRectF(44, 18, 12, 14))
    p.drawPolygon(_poligono((40, 18), (70, 12), (72, 18), (44, 24)))
    p.save()
    p.setPen(QPen(p.brush().color(), 4))
    p.setBrush(Qt.BrushStyle.NoBrush)
    tubo = QPainterPath()
    tubo.moveTo(56, 22)
    tubo.cubicTo(80, 26, 82, 56, 70, 70)
    p.drawPath(tubo)
    p.restore()


PITTOGRAMMI = {
    "casco": p_casco, "guanti": p_guanti, "calzature": p_calzature, "udito": p_udito,
    "occhiali": p_occhiali, "visiera": p_visiera, "maschera": p_maschera, "imbracatura": p_imbracatura,
    "altavisibilita": p_altavisibilita, "indumenti": p_indumenti,
    "accesso": p_camminatore, "sotto_carichi": lambda p: p_gancio_carico(p, True), "fiamme": p_fiamma,
    "pericolo": p_esclamativo, "tensione": p_fulmine, "carichi": p_gancio_carico, "caduta": p_caduta,
    "mezzi": p_mezzi, "scavo": p_scavo, "soccorso": p_croce, "estintore": p_estintore,
}


def _area(p: QPainter, riquadro: QRectF, colore: QColor) -> None:
    """Prepara il pittore per disegnare un pittogramma della griglia 100x100 nel riquadro."""
    p.translate(riquadro.topLeft())
    p.scale(riquadro.width() / 100, riquadro.height() / 100)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(colore))


def disegna(chiave: str, tipo: str) -> QImage:
    img = QImage(LATO, LATO, QImage.Format.Format_ARGB32)
    img.fill(Qt.GlobalColor.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    L = float(LATO)
    pittogramma = QImage(LATO, LATO, QImage.Format.Format_ARGB32)
    pittogramma.fill(Qt.GlobalColor.transparent)

    def disegna_pittogramma(riquadro: QRectF, colore: QColor) -> None:
        # Il pittogramma si disegna su un livello a parte, così i «tagli» non bucano lo sfondo.
        q = QPainter(pittogramma)
        q.setRenderHint(QPainter.RenderHint.Antialiasing)
        _area(q, riquadro, colore)
        PITTOGRAMMI[chiave](q)
        q.end()
        p.drawImage(0, 0, pittogramma)

    if tipo == OBBLIGO:
        p.setPen(QPen(BIANCO, L * 0.02))
        p.setBrush(BLU)
        p.drawEllipse(QRectF(L * 0.03, L * 0.03, L * 0.94, L * 0.94))
        disegna_pittogramma(QRectF(L * 0.2, L * 0.2, L * 0.6, L * 0.6), BIANCO)
    elif tipo == DIVIETO:
        spessore = L * 0.1
        p.setPen(QPen(ROSSO, spessore))
        p.setBrush(BIANCO)
        r = QRectF(spessore / 2 + 4, spessore / 2 + 4, L - spessore - 8, L - spessore - 8)
        p.drawEllipse(r)
        disegna_pittogramma(QRectF(L * 0.2, L * 0.2, L * 0.6, L * 0.6), NERO)
        p.setPen(QPen(ROSSO, spessore * 0.85, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        centro, raggio = r.center(), r.width() / 2
        d = raggio * 0.7071
        p.drawLine(QPointF(centro.x() - d, centro.y() - d), QPointF(centro.x() + d, centro.y() + d))
    elif tipo == AVVERTIMENTO:
        triangolo = _poligono((L / 2, L * 0.06), (L * 0.97, L * 0.9), (L * 0.03, L * 0.9))
        p.setPen(QPen(NERO, L * 0.05, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        p.setBrush(GIALLO)
        p.drawPolygon(triangolo)
        disegna_pittogramma(QRectF(L * 0.27, L * 0.33, L * 0.46, L * 0.5), NERO)
    else:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(VERDE if tipo == SOCCORSO else ROSSO)
        p.drawRoundedRect(QRectF(L * 0.04, L * 0.04, L * 0.92, L * 0.92), L * 0.06, L * 0.06)
        disegna_pittogramma(QRectF(L * 0.18, L * 0.18, L * 0.64, L * 0.64), BIANCO)
    p.end()
    return img


def main() -> None:
    app = QGuiApplication.instance() or QGuiApplication([])  # noqa: F841 - serve a QPainter
    CARTELLA.mkdir(parents=True, exist_ok=True)
    for chiave, segnale in SEGNALI.items():
        assert chiave in PITTOGRAMMI, chiave
        disegna(chiave, segnale.tipo).save(str(segnale.file))
    print(f"{len(SEGNALI)} cartelli in {CARTELLA}")


if __name__ == "__main__":
    main()
